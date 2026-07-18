SET 'execution.runtime-mode' = 'streaming';
SET 'pipeline.name' = 'vehicle-models-transform';
SET 'parallelism.default' = '1';
SET 'execution.checkpointing.interval' = '10 s';

-- Исходный Debezium topic с моделями автомобилей.
CREATE TABLE vehicle_model_cdc (
    `before` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `after` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `op` STRING,
    `ts_ms` BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'raw_taxi_manager.public.vehicle_model',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-vehicle-models-v1',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true'
);

-- Результат: ключ Kafka = uuid, value = JSON с before, after, timestamp и op.
CREATE TABLE vehicle_models (
    `message_key` STRING,
    `before` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `after` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `timestamp` BIGINT,
    `op` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'taxi_manager.vehicle_models',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'message_key',
    'value.format' = 'json',
    'value.fields-include' = 'EXCEPT_KEY',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO vehicle_models
SELECT
    CASE `op`
        WHEN 'd' THEN `before`.`uuid`
        ELSE `after`.`uuid`
    END AS `message_key`,
    `before`,
    `after`,
    `ts_ms` AS `timestamp`,
    CASE `op`
        WHEN 'c' THEN 'create'
        WHEN 'r' THEN 'create'
        WHEN 'u' THEN 'update'
        WHEN 'd' THEN 'delete'
    END AS `op`
FROM vehicle_model_cdc
WHERE `op` IN ('c', 'r', 'u', 'd');
