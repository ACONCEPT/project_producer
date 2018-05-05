import os
import sys
sys.path.append(os.environ["PROJECT_HOME"])
import psycopg2
from postgreslib.database_connection import DBConnection
from config.config import BOOTSTRAP_SERVERS,ZOOKEEPER_SERVERS,TESTING_SERVER
from config.database_connections import source_databases
from helpers.kafka import KafkaWriter, get_topic
import json

class IngestionProducer(KafkaWriter):
    def __init__(self,bootstrap_servers,datasource):
        super().__init__(bootstrap_servers)
        self.datasource = datasource
        self.db = DBConnection(datasource)

    def publish_to_topic(self, datasource, table, data):
        self.producer.send(topic,json.dumps(data))
        self.producer.flush()

    def get_ingestion_data(self,table):
        self.data , self.header = self.db.stream_table(table)

    def ingest_data(self,table):
        self.get_ingestion_data(table)
        generator,header = self.db.stream_table("sales_orders")
        data = {}

        data["meta"] = {"table":table}
        topic = get_topic(self.datasource,table)
        print("streaming data from table {} to topic {}".format(table,topic))
        for record in generator:
            data["record"] = {str(h.name):str(v) for h,v in zip(header,record)}
            self.producer.send(topic,json.dumps(data))

        self.producer.send_debug

def main(bootstrap_servers,table):
    print("main table {}".format(table))
    producer = IngestionProducer(bootstrap_servers,"test_database")
    producer.ingest_data(table)

if __name__ == '__main__':
    if "joe" in os.environ.get("HOME"):
        print("setting bootstrap to localhost in producer")
        bootstrap_servers = TESTING_SERVER
    else:
        bootstrap_servers = BOOTSTRAP_SERVERS
    topic = sys.argv[1].strip()
    main(bootstrap_servers,topic)
