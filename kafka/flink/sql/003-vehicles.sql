SET 'execution.runtime-mode' = 'streaming';
SET 'pipeline.name' = 'vehicles-transform';
SET 'parallelism.default' = '1';
SET 'execution.checkpointing.interval' = '10 s';

-- Исходный Debezium topic с автомобилями.
CREATE TABLE vehicle_cdc (
    `before` ROW<
        `price` STRING,
        `year_of_manufacture` INT,
        `mileage` INT,
        `number` STRING,
        `vin` STRING,
        `model_uuid` STRING,
        `enterprise_uuid` STRING,
        `uuid` STRING
    >,
    `after` ROW<
        `price` STRING,
        `year_of_manufacture` INT,
        `mileage` INT,
        `number` STRING,
        `vin` STRING,
        `model_uuid` STRING,
        `enterprise_uuid` STRING,
        `uuid` STRING
    >,
    `op` STRING,
    `ts_ms` BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'raw_taxi_manager.public.vehicle_vehicle',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-vehicles-v1',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true'
);

-- Результат: ключ Kafka = uuid, value = JSON с before, after, timestamp и op.
CREATE TABLE vehicles (
    `message_key` STRING,
    `before` ROW<
        `price` STRING,
        `year_of_manufacture` INT,
        `mileage` INT,
        `number` STRING,
        `vin` STRING,
        `model_uuid` STRING,
        `enterprise_uuid` STRING,
        `uuid` STRING
    >,
    `after` ROW<
        `price` STRING,
        `year_of_manufacture` INT,
        `mileage` INT,
        `number` STRING,
        `vin` STRING,
        `model_uuid` STRING,
        `enterprise_uuid` STRING,
        `uuid` STRING
    >,
    `timestamp` BIGINT,
    `op` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'taxi_manager.vehicles',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'message_key',
    'value.format' = 'json',
    'value.fields-include' = 'EXCEPT_KEY',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO vehicles
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
FROM vehicle_cdc
WHERE `op` IN ('c', 'r', 'u', 'd');