use actix_web::{
    get, post,
    web::{self, Data, Json},
    App, HttpResponse, HttpServer, Responder,
};
use serde::{Deserialize, Serialize};
use sqlx::{postgres::PgPoolOptions, FromRow, PgPool};
use std::env;

#[derive(Debug, Deserialize)]
struct CreateModelRequest {
    name: Option<String>,

    #[serde(rename = "type")]
    type_: Option<String>,

    number_of_seats: Option<i32>,
    tank_capacity_l: Option<f64>,
    load_capacity_kg: Option<f64>,
}

#[derive(Debug, Serialize, FromRow)]
struct ModelResponse {
    id: i64,
    name: String,
}

#[derive(Debug, Serialize)]
struct ValidationError {
    detail: String,
}

#[get("/healthz")]
async fn healthz() -> impl Responder {
    HttpResponse::Ok().json(serde_json::json!({
        "status": "ok"
    }))
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

    let number_of_seats = match payload.number_of_seats {
        Some(value) => value,
        None => {
            return Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "number_of_seats": ["This field is required."]
            })));
        }
    };

    let type_ = payload.type_.clone().unwrap_or_default();

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
    .bind(payload.tank_capacity_l)
    .bind(payload.load_capacity_kg)
    .fetch_one(pool.get_ref())
    .await
    .map_err(|error| {
        log::error!("failed to create model: {error}");
        actix_web::error::ErrorInternalServerError("failed to create model")
    })?;

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

    let pool = PgPoolOptions::new()
        .max_connections(max_connections)
        .connect(&database_url)
        .await
        .expect("failed to connect to database");

    log::info!("starting rust-api on {bind_addr}");

    HttpServer::new(move || {
        App::new()
            .app_data(Data::new(pool.clone()))
            .service(healthz)
            .service(create_model)
    })
    .bind(bind_addr)?
    .run()
    .await
}