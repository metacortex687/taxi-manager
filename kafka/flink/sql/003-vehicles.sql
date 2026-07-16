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
    `op` STRING
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

-- Результат: ключ Kafka = uuid, value = JSON с данными автомобиля.
CREATE TABLE vehicles (
    `price` STRING,
    `year_of_manufacture` INT,
    `mileage` INT,
    `number` STRING,
    `vin` STRING,
    `model_uuid` STRING,
    `enterprise_uuid` STRING,
    `uuid` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'vehicles',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'uuid',
    'value.format' = 'json',
    'value.fields-include' = 'ALL',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO vehicles
SELECT
    COALESCE(`after`.`price`, `before`.`price`) AS `price`,
    COALESCE(`after`.`year_of_manufacture`, `before`.`year_of_manufacture`) AS `year_of_manufacture`,
    COALESCE(`after`.`mileage`, `before`.`mileage`) AS `mileage`,
    COALESCE(`after`.`number`, `before`.`number`) AS `number`,
    COALESCE(`after`.`vin`, `before`.`vin`) AS `vin`,
    COALESCE(`after`.`model_uuid`, `before`.`model_uuid`) AS `model_uuid`,
    COALESCE(`after`.`enterprise_uuid`, `before`.`enterprise_uuid`) AS `enterprise_uuid`,
    COALESCE(`after`.`uuid`, `before`.`uuid`) AS `uuid`
FROM vehicle_cdc
WHERE `op` IN ('c', 'r', 'u');