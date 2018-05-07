import psycopg2
from postgreslib.database_connection import DBConnection
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
        x = 0
        for i,record in enumerate(generator):
            data["record"] = {str(h.name):str(v) for h,v in zip(header,record)}
            self.producer.send(topic,json.dumps(data))
            x = i

        self.produce_debug("completed producing {}, {} records".format(table,x))

def main(bootstrap_servers,db,table):
    print("main table {}".format(table))
    producer = IngestionProducer(bootstrap_servers,db)
    producer.ingest_data(table)

if __name__ == '__main__':
    pass
