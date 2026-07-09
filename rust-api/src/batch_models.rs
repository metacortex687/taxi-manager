use actix_web::{
    post,
    web::{Data, Json},
    HttpResponse,
};
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool, Postgres, QueryBuilder};
use std::{collections::HashMap, time::Duration};
use tokio::sync::{mpsc, oneshot};
use tokio::time;

#[derive(Debug, Deserialize)]
pub struct CreateModelBatchRequest {
    name: Option<String>,

    #[serde(rename = "type")]
    type_: Option<String>,

    number_of_seats: Option<i32>,
    tank_capacity_l: Option<i32>,
    load_capacity_kg: Option<i32>,
}

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct ModelBatchResponse {
    id: i64,
    name: String,
}

#[derive(Debug, Clone)]
struct NewModel {
    name: String,
    type_: String,
    number_of_seats: i32,
    tank_capacity_l: i32,
    load_capacity_kg: i32,
}

struct BatchItem {
    data: NewModel,
    respond_to: oneshot::Sender<Result<ModelBatchResponse, String>>,
}

#[derive(Clone)]
pub struct BatchInserter {
    sender: mpsc::Sender<BatchItem>,
}

impl BatchInserter {
    async fn create(&self, data: NewModel) -> Result<ModelBatchResponse, String> {
        let (respond_to, response_from_worker) = oneshot::channel();

        let item = BatchItem {
            data,
            respond_to,
        };

        self.sender
            .send(item)
            .await
            .map_err(|_| "batch worker is stopped".to_string())?;

        response_from_worker
            .await
            .map_err(|_| "batch worker dropped response".to_string())?
    }
}

pub fn start_batch_worker(
    pool: PgPool,
    batch_size: usize,
    flush_interval_ms: u64,
    queue_capacity: usize,
) -> BatchInserter {
    let (sender, receiver) = mpsc::channel::<BatchItem>(queue_capacity);

    tokio::spawn(run_batch_worker(
        pool,
        receiver,
        batch_size,
        Duration::from_millis(flush_interval_ms),
    ));

    BatchInserter {
        sender,
    }
}

#[post("/models/batch-queue/")]
pub async fn create_model_batch(
    batch_inserter: Data<BatchInserter>,
    payload: Json<CreateModelBatchRequest>,
) -> actix_web::Result<HttpResponse> {
    let name = match payload.name.as_deref() {
        Some(name) if !name.trim().is_empty() => name.trim().to_string(),
        _ => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "name": ["This field is required."]
            })));
        }
    };

    let type_ = match payload.type_.as_deref() {
        Some("PCR") | Some("BUS") | Some("LRR") => payload.type_.clone().unwrap(),
        Some(_) => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "type": ["Expected one of: PCR, BUS, LRR."]
            })));
        }
        None => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "type": ["This field is required."]
            })));
        }
    };

    let number_of_seats = match payload.number_of_seats {
        Some(value) => value,
        None => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "number_of_seats": ["This field is required."]
            })));
        }
    };

    let tank_capacity_l = match payload.tank_capacity_l {
        Some(value) => value,
        None => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "tank_capacity_l": ["This field is required."]
            })));
        }
    };

    let load_capacity_kg = match payload.load_capacity_kg {
        Some(value) => value,
        None => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "load_capacity_kg": ["This field is required."]
            })));
        }
    };

    let new_model = NewModel {
        name,
        type_,
        number_of_seats,
        tank_capacity_l,
        load_capacity_kg,
    };

    let model = batch_inserter
        .create(new_model)
        .await
        .map_err(|error| {
            log::error!("failed to create model by batch: {error}");
            actix_web::error::ErrorInternalServerError("failed to create model")
        })?;

    log::info!(
        "rust-api created model by batch: id={}, name={}",
        model.id,
        model.name
    );

    Ok(HttpResponse::Created().json(model))
}

async fn run_batch_worker(
    pool: PgPool,
    mut receiver: mpsc::Receiver<BatchItem>,
    batch_size: usize,
    flush_interval: Duration,
) {
    let mut buffer: Vec<BatchItem> = Vec::with_capacity(batch_size);

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
        flush_batch(&pool, items).await;
    }

    log::warn!("batch worker stopped");
}

async fn flush_batch(pool: &PgPool, items: Vec<BatchItem>) {
    if items.is_empty() {
        return;
    }

    let batch_len = items.len();

    let result = insert_models_batch(pool, &items).await;

    match result {
        Ok(models) => {
            log::info!("rust-api inserted models batch: size={batch_len}");

            let mut model_by_name: HashMap<String, ModelBatchResponse> =
                HashMap::with_capacity(models.len());

            for model in models {
                model_by_name.insert(model.name.clone(), model);
            }

            for item in items {
                let name = item.data.name.clone();

                let response = model_by_name
                    .remove(&name)
                    .ok_or_else(|| {
                        format!("created model was not returned by database: name={name}")
                    });

                let _ = item.respond_to.send(response);
            }
        }
        Err(error) => {
            log::error!(
                "failed to insert models batch: size={batch_len}, error={error}"
            );

            for item in items {
                let _ = item.respond_to.send(Err(error.to_string()));
            }
        }
    }
}

async fn insert_models_batch(
    pool: &PgPool,
    items: &[BatchItem],
) -> Result<Vec<ModelBatchResponse>, sqlx::Error> {
    let mut query_builder = QueryBuilder::<Postgres>::new(
        r#"
        INSERT INTO vehicle_model (
            name,
            type,
            number_of_seats,
            tank_capacity_l,
            load_capacity_kg,
            color,
            created_at,
            updated_at
        )
        "#,
    );

    query_builder.push_values(items.iter(), |mut builder, item| {
        builder
            .push_bind(&item.data.name)
            .push_bind(&item.data.type_)
            .push_bind(item.data.number_of_seats)
            .push_bind(item.data.tank_capacity_l)
            .push_bind(item.data.load_capacity_kg)
            .push_bind("")
            .push("NOW()")
            .push("NOW()");
    });

    query_builder.push(
        r#"
        RETURNING id::bigint AS id, name
        "#,
    );

    query_builder
        .build_query_as::<ModelBatchResponse>()
        .fetch_all(pool)
        .await
}