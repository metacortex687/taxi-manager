use actix_web::{
    get,
    web::{Data, Path},
    HttpResponse,
};
use sqlx::{PgPool, Postgres, QueryBuilder};
use std::{collections::HashMap, time::Duration};
use tokio::sync::{mpsc, oneshot};
use tokio::time;

use crate::batch_models::ModelResponse;

struct ReadBatchItem {
    id: i64,
    respond_to: oneshot::Sender<Result<Option<ModelResponse>, String>>,
}

#[derive(Clone)]
pub struct BatchReader {
    sender: mpsc::Sender<ReadBatchItem>,
}

impl BatchReader {
    async fn get(&self, id: i64) -> Result<Option<ModelResponse>, String> {
        let (respond_to, response_from_worker) = oneshot::channel();

        let item = ReadBatchItem {
            id,
            respond_to,
        };

        self.sender
            .send(item)
            .await
            .map_err(|_| "batch read worker is stopped".to_string())?;

        response_from_worker
            .await
            .map_err(|_| "batch read worker dropped response".to_string())?
    }
}

pub fn start_read_batch_worker(
    pool: PgPool,
    batch_size: usize,
    flush_interval_ms: u64,
    queue_capacity: usize,
) -> BatchReader {
    let (sender, receiver) = mpsc::channel::<ReadBatchItem>(queue_capacity);

    tokio::spawn(run_read_batch_worker(
        pool,
        receiver,
        batch_size,
        Duration::from_millis(flush_interval_ms),
    ));

    BatchReader {
        sender,
    }
}

#[get("/models/batch-queue/{id}/")]
pub async fn get_model_batch(
    batch_reader: Data<BatchReader>,
    id: Path<i64>,
) -> actix_web::Result<HttpResponse> {
    let id = id.into_inner();

    let model = batch_reader
        .get(id)
        .await
        .map_err(|error| {
            log::error!("failed to get model by read batch: id={id}, error={error}");
            actix_web::error::ErrorInternalServerError("failed to get model")
        })?;

    match model {
        Some(model) => Ok(HttpResponse::Ok().json(model)),
        None => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "detail": "Not found."
        }))),
    }
}

async fn run_read_batch_worker(
    pool: PgPool,
    mut receiver: mpsc::Receiver<ReadBatchItem>,
    batch_size: usize,
    flush_interval: Duration,
) {
    let mut buffer: Vec<ReadBatchItem> = Vec::with_capacity(batch_size);

    loop {
        if buffer.is_empty() {
            match receiver.recv().await {
                Some(item) => buffer.push(item),
                None => break,
            }
        }

        let flush_deadline = time::sleep(flush_interval);
        tokio::pin!(flush_deadline);

        loop {
            if buffer.len() >= batch_size {
                break;
            }

            tokio::select! {
                maybe_item = receiver.recv() => {
                    match maybe_item {
                        Some(item) => buffer.push(item),
                        None => break,
                    }
                }
                _ = &mut flush_deadline => {
                    break;
                }
            }
        }

        let items = std::mem::take(&mut buffer);
        flush_read_batch(&pool, items).await;
    }

    log::warn!("batch read worker stopped");
}

async fn flush_read_batch(pool: &PgPool, items: Vec<ReadBatchItem>) {
    if items.is_empty() {
        return;
    }

    let batch_len = items.len();
    let ids: Vec<i64> = items.iter().map(|item| item.id).collect();
    let result = select_models_batch(pool, &ids).await;

    match result {
        Ok(models) => {
            log::info!("rust-api selected models batch: size={batch_len}");

            let mut model_by_id: HashMap<i64, ModelResponse> =
                HashMap::with_capacity(models.len());

            for model in models {
                model_by_id.insert(model.id, model);
            }

            for item in items {
                let response = Ok(model_by_id.get(&item.id).cloned());
                let _ = item.respond_to.send(response);
            }
        }
        Err(error) => {
            log::error!(
                "failed to select models batch: size={batch_len}, error={error}"
            );

            for item in items {
                let _ = item.respond_to.send(Err(error.to_string()));
            }
        }
    }
}

async fn select_models_batch(
    pool: &PgPool,
    ids: &[i64],
) -> Result<Vec<ModelResponse>, sqlx::Error> {
    let mut query_builder = QueryBuilder::<Postgres>::new(
        r#"
        SELECT id::bigint AS id, name
        FROM vehicle_model
        WHERE id IN (
        "#,
    );

    let mut separated = query_builder.separated(", ");

    for id in ids {
        separated.push_bind(id);
    }

    separated.push_unseparated(")");

    query_builder
        .build_query_as::<ModelResponse>()
        .fetch_all(pool)
        .await
}