FROM flink:2.2.1-scala_2.12

USER root

ADD https://repo1.maven.org/maven2/org/apache/flink/flink-sql-connector-kafka/5.0.0-2.2/flink-sql-connector-kafka-5.0.0-2.2.jar /opt/flink/lib/flink-sql-connector-kafka-5.0.0-2.2.jar
RUN chmod 0644 /opt/flink/lib/flink-sql-connector-kafka-5.0.0-2.2.jar

USER flink
