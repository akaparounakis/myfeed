import json
import os
from enum import Enum
from time import sleep

import requests
from dotenv import load_dotenv
from kafka import KafkaProducer

load_dotenv()


class Topic(Enum):
    BUSINESS = 'business'
    ENTERTAINMENT = 'entertainment'
    HEALTH = 'health'
    SCIENCE = 'science'
    SPORTS = 'sports'
    TECHNOLOGY = 'technology'


class Producer:
    topics = [topic.value for topic in Topic]

    def __init__(self, newsapi_key: str, kafka_hostname: str):
        self.newsapi_key: str = newsapi_key
        self.producer = KafkaProducer(bootstrap_servers=kafka_hostname, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def run(self):
        print('Producer is running...')
        while True:
            for topic in self.topics:
                articles = self.fetch_articles_by_topic(topic)
                for article in articles:
                    wiki_title, wiki_url, wiki_excerpt = self.fetch_wikipedia_page(article['source']['name'])
                    article['source']['wikipediaPage'] = {
                        'title': wiki_title,
                        'url': wiki_url,
                        'excerpt': wiki_excerpt
                    }
                    article['topic'] = topic
                    self.producer.send(topic, article)
            sleep(2700)

    def fetch_articles_by_topic(self, topic: str):
        response = requests.get(f"https://newsapi.org/v2/everything?q={topic}&apiKey={self.newsapi_key}&sortBy=relevancy&pageSize=20")
        return response.json().get('articles', [])

    @classmethod
    def fetch_wikipedia_page(cls, q: str):
        response = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={q}&srprop=size&utf8=1&formatversion=2").json()
        search = response.get("query", {}).get("search", [])
        if not search:
            return None, None, None
        title = search[0]["title"]
        url = f"https://en.wikipedia.org/wiki/{title}"
        response = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&exsentences=2&titles={title}&utf8=1&formatversion=2&explaintext=1&exintro=1").json()
        excerpt = response["query"]["pages"][0]["extract"]
        return title, url, excerpt


if __name__ == "__main__":
    producer = Producer(os.getenv('NEWSAPI_KEY'), os.getenv('KAFKA_HOSTNAME'))
    producer.run()
