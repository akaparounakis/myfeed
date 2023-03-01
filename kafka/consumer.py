import datetime
import json
import os
from enum import Enum

import pymongo
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()


class Topic(Enum):
    BUSINESS = 'business'
    ENTERTAINMENT = 'entertainment'
    HEALTH = 'health'
    SCIENCE = 'science'
    SPORTS = 'sports'
    TECHNOLOGY = 'technology'


class Consumer:
    def __init__(self, mongodb_uri: str, mongodb_db: str, kafka_hostname: str):
        self.consumer = KafkaConsumer(*[topic.value for topic in Topic], 'source', bootstrap_servers=kafka_hostname, value_deserializer=lambda m: json.loads(m.decode('utf-8')))
        self.articles = pymongo.MongoClient(mongodb_uri)[mongodb_db]['articles']

    def run(self):
        print('Consumer is running...')
        for message in self.consumer:
            message = message.value
            message['publishedAt'] = datetime.datetime.strptime(message['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
            keep_fields = ['author', 'source', 'topic', 'title', 'url', 'publishedAt']
            article = {k: message[k] for k in keep_fields if k in message}
            self.articles.insert_one(article)


if __name__ == "__main__":
    producer = Consumer(os.getenv('MONGODB_URI'), os.getenv('MONGODB_DB'), os.getenv('KAFKA_HOSTNAME'))
    producer.run()
