use actix_web::HttpResponse;
use serde::{Deserialize, Serialize};
use sqlx::FromRow;

#[derive(Debug, Deserialize)]
pub struct CreateModelRequest {
    name: Option<String>,

    #[serde(rename = "type")]
    type_: Option<String>,

    number_of_seats: Option<i32>,
    tank_capacity_l: Option<i32>,
    load_capacity_kg: Option<i32>,
}

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct ModelResponse {
    pub id: i64,
    pub name: String,
}

#[derive(Debug, Clone)]
pub struct NewModel {
    pub name: String,
    pub type_: String,
    pub number_of_seats: i32,
    pub tank_capacity_l: i32,
    pub load_capacity_kg: i32,
}

impl CreateModelRequest {
    pub fn into_new_model(self) -> Result<NewModel, HttpResponse> {
        let name = match self.name.as_deref() {
            Some(name) if !name.trim().is_empty() => name.trim().to_string(),
            _ => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "name": ["This field is required."]
                })));
            }
        };

        let type_ = match self.type_.as_deref() {
            Some("PCR") | Some("BUS") | Some("LRR") => self.type_.unwrap(),
            Some(_) => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "type": ["Expected one of: PCR, BUS, LRR."]
                })));
            }
            None => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "type": ["This field is required."]
                })));
            }
        };

        let number_of_seats = match self.number_of_seats {
            Some(value) => value,
            None => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "number_of_seats": ["This field is required."]
                })));
            }
        };

        let tank_capacity_l = match self.tank_capacity_l {
            Some(value) => value,
            None => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "tank_capacity_l": ["This field is required."]
                })));
            }
        };

        let load_capacity_kg = match self.load_capacity_kg {
            Some(value) => value,
            None => {
                return Err(HttpResponse::BadRequest().json(serde_json::json!({
                    "load_capacity_kg": ["This field is required."]
                })));
            }
        };

        Ok(NewModel {
            name,
            type_,
            number_of_seats,
            tank_capacity_l,
            load_capacity_kg,
        })
    }
}