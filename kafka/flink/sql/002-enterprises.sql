SET 'execution.runtime-mode' = 'streaming';
SET 'pipeline.name' = 'enterprises-transform';
SET 'parallelism.default' = '1';
SET 'execution.checkpointing.interval' = '10 s';

-- Исходный Debezium topic с предприятиями.
CREATE TABLE enterprise_cdc (
    `before` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `after` ROW<
        `uuid` STRING,
        `name` STRING
    >,
    `op` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'raw_taxi_manager.public.enterprise_enterprise',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-enterprises-v1',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true'
);

-- Результат: ключ Kafka = uuid, value = JSON только с полями uuid и name.
CREATE TABLE enterprises (
    `uuid` STRING,
    `name` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'enterprises',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'uuid',
    'value.format' = 'json',
    'value.fields-include' = 'ALL',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO enterprises
SELECT
    COALESCE(`after`.`uuid`, `before`.`uuid`) AS `uuid`,
    COALESCE(`after`.`name`, `before`.`name`) AS `name`
FROM enterprise_cdc
WHERE `op` IN ('c', 'r', 'u');