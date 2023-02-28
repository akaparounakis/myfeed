import itertools
from dataclasses import dataclass
from datetime import datetime

import networkx as nx

from app.database import db

articles_collection = db['articles']


@dataclass
class Article:
    id: str
    author: str
    source_name: str
    published_at: datetime


class Graph:
    def __init__(self):
        articles = self.fetch_articles()
        self.graph = self.create_graph(articles)

    def recommend(self, article_id: str):
        article_node_neighbours = self.graph.neighbors(article_id)
        max_degree_node = max(article_node_neighbours, key=self.graph.degree)
        return max_degree_node

    @classmethod
    def create_graph(cls, articles: [Article]):
        G = nx.Graph()
        article_map = {article.id: article for article in articles}
        G.add_nodes_from(article_map.keys())

        connected_nodes = []
        for a1, a2 in itertools.combinations(articles, 2):
            if a1.author == a2.author or a1.source_name == a2.source_name:
                G.add_edge(a1.id, a2.id)
                connected_nodes.append((a1.id, a2.id))

        unconnected_nodes = set(G.nodes()) - set(itertools.chain(*connected_nodes))
        for node in unconnected_nodes:
            closest_node = min(
                articles,
                key=lambda x: abs(
                    (x.published_at - article_map[node].published_at).total_seconds()
                    if x != article_map[node] else float('inf')
                )
            )

            G.add_edge(node, closest_node.id)

        return G

    @classmethod
    def fetch_articles(cls):
        articles = []
        for article in articles_collection.find():
            _id = str(article.get('_id'))
            author = article.get('author')
            source_name = article.get('source', {}).get('name', {})
            published_at = datetime.strptime(article.get('publishedAt'), '%Y-%m-%dT%H:%M:%S%z')
            articles.append(Article(_id, author, source_name, published_at))
        return articles
