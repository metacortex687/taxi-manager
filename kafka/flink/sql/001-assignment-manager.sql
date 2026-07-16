SET 'execution.runtime-mode' = 'streaming';
SET 'pipeline.name' = 'assignment-manager-transform';
SET 'parallelism.default' = '1';
SET 'execution.checkpointing.interval' = '10 s';

-- Исходный Debezium topic.
-- Если в debezium-postgres.json другой topic.prefix, измените topic ниже.
CREATE TABLE manager_cdc (
    `before` ROW<
        `uuid` STRING,
        `enterprise_uuid` STRING,
        `user_uuid` STRING
    >,
    `after` ROW<
        `uuid` STRING,
        `enterprise_uuid` STRING,
        `user_uuid` STRING
    >,
    `op` STRING,
    `ts_ms` BIGINT
) WITH (
    'connector' = 'kafka',
    'topic' = 'raw_taxi_manager.public.enterprise_manager',
    'properties.bootstrap.servers' = 'kafka:9092',
    'properties.group.id' = 'flink-assignment-manager-v1',
    'scan.startup.mode' = 'earliest-offset',
    'format' = 'json',
    'json.fail-on-missing-field' = 'false',
    'json.ignore-parse-errors' = 'true'
);

-- Результат: ключ Kafka = manager_uuid, value = JSON со всеми полями.
CREATE TABLE assignment_managers (
    `user_uuid` STRING,
    `enterprise_uuid` STRING,
    `timestamp` BIGINT,
    `op` STRING
) WITH (
    'connector' = 'kafka',
    'topic' = 'assignment_managers',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'user_uuid',
    'value.format' = 'json',
    'value.fields-include' = 'ALL',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO assignment_managers
SELECT
    COALESCE(`after`.`user_uuid`, `before`.`user_uuid`) AS `user_uuid`,
    COALESCE(`after`.`enterprise_uuid`, `before`.`enterprise_uuid`) AS `enterprise_uuid`,
    `ts_ms` AS `timestamp`,
    CASE `op`
        WHEN 'c' THEN 'create'
        WHEN 'r' THEN 'create'
        WHEN 'u' THEN 'update'
        WHEN 'd' THEN 'delete'
    END AS `op`
FROM manager_cdc
WHERE `op` IN ('c', 'r', 'u', 'd');
