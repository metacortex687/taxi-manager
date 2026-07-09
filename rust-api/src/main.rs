mod batch_models;
mod batch_models_read;
mod batch_models_write;

use actix_web::{
    get, post,
    web::{Data, Json, Path},
    App, HttpResponse, HttpServer, Responder,
};
use batch_models::{CreateModelRequest, ModelResponse};
use batch_models_read::{get_model_batch, start_read_batch_worker};
use batch_models_write::{create_model_batch, start_batch_worker};
use sqlx::{postgres::PgPoolOptions, PgPool};
use std::env;

#[get("/healthz")]
async fn healthz() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "ok"
    }))
}

#[get("/models/{id}/")]
async fn get_model_by_id(
    pool: Data<PgPool>,
    id: Path<i64>,
) -> actix_web::Result<HttpResponse> {
    let model = sqlx::query_as::<_, ModelResponse>(
        r#"
        SELECT id::bigint AS id, name
        FROM vehicle_model
        WHERE id = $1
        "#,
    )
    .bind(id.into_inner())
    .fetch_optional(pool.get_ref())
    .await
    .map_err(|error| {
        log::error!("failed to get model by id: {error}");
        actix_web::error::ErrorInternalServerError("failed to get model")
    })?;

    match model {
        Some(model) => Ok(HttpResponse::Ok().json(model)),
        None => Ok(HttpResponse::NotFound().json(serde_json::json!({
            "detail": "Not found."
        }))),
    }
}

#[post("/models/")]
async fn create_model(
    pool: Data<PgPool>,
    payload: Json<CreateModelRequest>,
) -> actix_web::Result<HttpResponse> {
    let new_model = match payload.into_inner().into_new_model() {
        Ok(new_model) => new_model,
        Err(response) => return Ok(response),
    };

    let model = sqlx::query_as::<_, ModelResponse>(
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
        VALUES ($1, $2, $3, $4, $5, '', NOW(), NOW())
        RETURNING id::bigint AS id, name
        "#,
    )
    .bind(new_model.name)
    .bind(new_model.type_)
    .bind(new_model.number_of_seats)
    .bind(new_model.tank_capacity_l)
    .bind(new_model.load_capacity_kg)
    .fetch_one(pool.get_ref())
    .await
    .map_err(|error| {
        log::error!("failed to create model: {error}");
        actix_web::error::ErrorInternalServerError("failed to create model")
    })?;

    log::info!(
        "rust-api created model: id={}, name={}",
        model.id,
        model.name
    );

    Ok(HttpResponse::Created().json(model))
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();

    let database_url = env::var("DATABASE_URL")
        .expect("DATABASE_URL environment variable is required");

    let bind_addr = env::var("RUST_API_BIND")
        .unwrap_or_else(|_| "0.0.0.0:8080".to_string());

    let max_connections = env_u32("RUST_API_DB_MAX_CONNECTIONS", 10);
    let workers = env_usize("RUST_API_WORKERS", 3);

    let write_batch_size = env_usize_with_fallback(
        "RUST_API_WRITE_BATCH_SIZE",
        "RUST_API_BATCH_SIZE",
        100,
    );
    let read_batch_size = env_usize_with_fallback(
        "RUST_API_READ_BATCH_SIZE",
        "RUST_API_BATCH_SIZE",
        500,
    );

    let write_batch_flush_interval_ms = env_u64_with_fallback(
        "RUST_API_WRITE_BATCH_FLUSH_INTERVAL_MS",
        "RUST_API_BATCH_FLUSH_INTERVAL_MS",
        50,
    );
    let read_batch_flush_interval_ms = env_u64_with_fallback(
        "RUST_API_READ_BATCH_FLUSH_INTERVAL_MS",
        "RUST_API_BATCH_FLUSH_INTERVAL_MS",
        50,
    );

    let write_batch_queue_capacity = env_usize_with_fallback(
        "RUST_API_WRITE_BATCH_QUEUE_CAPACITY",
        "RUST_API_BATCH_QUEUE_CAPACITY",
        10_000,
    );
    let read_batch_queue_capacity = env_usize_with_fallback(
        "RUST_API_READ_BATCH_QUEUE_CAPACITY",
        "RUST_API_BATCH_QUEUE_CAPACITY",
        10_000,
    );

    let pool = PgPoolOptions::new()
        .max_connections(max_connections)
        .connect(&database_url)
        .await
        .expect("failed to connect to database");

    let batch_inserter = start_batch_worker(
        pool.clone(),
        write_batch_size,
        write_batch_flush_interval_ms,
        write_batch_queue_capacity,
    );

    let batch_reader = start_read_batch_worker(
        pool.clone(),
        read_batch_size,
        read_batch_flush_interval_ms,
        read_batch_queue_capacity,
    );

    log::info!(
        "starting rust-api on {bind_addr}, workers={workers}, db_max_connections={max_connections}, write_batch_size={write_batch_size}, write_batch_flush_interval_ms={write_batch_flush_interval_ms}, write_batch_queue_capacity={write_batch_queue_capacity}, read_batch_size={read_batch_size}, read_batch_flush_interval_ms={read_batch_flush_interval_ms}, read_batch_queue_capacity={read_batch_queue_capacity}"
    );

    HttpServer::new(move || {
        App::new()
            .app_data(Data::new(pool.clone()))
            .app_data(Data::new(batch_inserter.clone()))
            .app_data(Data::new(batch_reader.clone()))
            .service(healthz)
            .service(get_model_by_id)
            .service(create_model)
            .service(create_model_batch)
            .service(get_model_batch)
    })
    .workers(workers)
    .bind(bind_addr)?
    .run()
    .await
}

fn env_usize(name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(default)
}

fn env_u32(name: &str, default: u32) -> u32 {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<u32>().ok())
        .unwrap_or(default)
}

fn env_usize_with_fallback(name: &str, fallback_name: &str, default: usize) -> usize {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .or_else(|| {
            env::var(fallback_name)
                .ok()
                .and_then(|value| value.parse::<usize>().ok())
        })
        .unwrap_or(default)
}

fn env_u64_with_fallback(name: &str, fallback_name: &str, default: u64) -> u64 {
    env::var(name)
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .or_else(|| {
            env::var(fallback_name)
                .ok()
                .and_then(|value| value.parse::<u64>().ok())
        })
        .unwrap_or(default)
}