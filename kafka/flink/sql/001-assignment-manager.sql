SET 'execution.runtime-mode' = 'streaming';
SET 'pipeline.name' = 'assignment-manager-transform';
SET 'parallelism.default' = '1';
SET 'execution.checkpointing.interval' = '10 s';

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

-- Результат: ключ Kafka = user_uuid, value = JSON с before и after.
CREATE TABLE assignment_managers (
    `message_key` STRING,
    `before` ROW<
        `uuid` STRING,
        `enterprise_uuid` STRING,
        `user_uuid` STRING
    >,
    `after` ROW<
        `uuid` STRING,
        `enterprise_uuid` STRING,
        `user_uuid` STRING
    >
) WITH (
    'connector' = 'kafka',
    'topic' = 'taxi_manager.assignment_managers',
    'properties.bootstrap.servers' = 'kafka:9092',
    'key.format' = 'raw',
    'key.fields' = 'message_key',
    'value.format' = 'json',
    'value.fields-include' = 'EXCEPT_KEY',
    'sink.delivery-guarantee' = 'at-least-once'
);

INSERT INTO assignment_managers
SELECT
    CASE `op`
        WHEN 'd' THEN `before`.`user_uuid`
        ELSE `after`.`user_uuid`
    END AS `message_key`,
    `before`,
    `after`
FROM manager_cdc
WHERE `op` IN ('c', 'r', 'u', 'd');