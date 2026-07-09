mod batch_models;

use actix_web::{
    get, post,
    web::{Data, Json, Path},
    App, HttpResponse, HttpServer, Responder,
};
use batch_models::{create_model_batch, start_batch_worker};
use serde::{Deserialize, Serialize};
use sqlx::{postgres::PgPoolOptions, FromRow, PgPool};
use std::env;

#[derive(Debug, Deserialize)]
struct CreateModelRequest {
    name: Option<String>,

    #[serde(rename = "type")]
    type_: Option<String>,

    number_of_seats: Option<i32>,
    tank_capacity_l: Option<i32>,
    load_capacity_kg: Option<i32>,
}

#[derive(Debug, Serialize, FromRow)]
struct ModelResponse {
    id: i64,
    name: String,
}

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
    .bind(name)
    .bind(type_)
    .bind(number_of_seats)
    .bind(tank_capacity_l)
    .bind(load_capacity_kg)
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

    let max_connections = env::var("RUST_API_DB_MAX_CONNECTIONS")
        .ok()
        .and_then(|value| value.parse::<u32>().ok())
        .unwrap_or(10);

    let workers = env::var("RUST_API_WORKERS")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(3);

    let batch_size = env::var("RUST_API_BATCH_SIZE")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(100);

    let batch_flush_interval_ms = env::var("RUST_API_BATCH_FLUSH_INTERVAL_MS")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(50);

    let batch_queue_capacity = env::var("RUST_API_BATCH_QUEUE_CAPACITY")
        .ok()
        .and_then(|value| value.parse::<usize>().ok())
        .unwrap_or(10_000);

    let pool = PgPoolOptions::new()
        .max_connections(max_connections)
        .connect(&database_url)
        .await
        .expect("failed to connect to database");

    let batch_inserter = start_batch_worker(
        pool.clone(),
        batch_size,
        batch_flush_interval_ms,
        batch_queue_capacity,
    );

    log::info!(
        "starting rust-api on {bind_addr}, workers={workers}, batch_size={batch_size}, batch_flush_interval_ms={batch_flush_interval_ms}, batch_queue_capacity={batch_queue_capacity}"
    );

    HttpServer::new(move || {
        App::new()
            .app_data(Data::new(pool.clone()))
            .app_data(Data::new(batch_inserter.clone()))
            .service(healthz)
            .service(get_model_by_id)
            .service(create_model)
            .service(create_model_batch)
    })
    .workers(workers)
    .bind(bind_addr)?
    .run()
    .await
}