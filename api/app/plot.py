from datetime import datetime, timedelta

import numpy as np
from matplotlib import pyplot as plt

from app.api.common import Topic
from app.database import db


class Plot:
    def __init__(self):
        self.articles_collection = db['articles']

    def generate(self):
        five_days_ago = datetime.utcnow() - timedelta(days=6)
        pipeline = [
            {"$match": {"topic": {"$in": [topic for topic in Topic]}, "publishedAt": {"$gte": five_days_ago}}},
            {"$group": {
                "_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$publishedAt"}}, "topic": "$topic"},
                "count": {"$sum": 1}}},
            {"$group": {"_id": "$_id.date", "topics": {"$push": {"k": "$_id.topic", "v": "$count"}}}},
            {"$project": {"_id": 0, "date": "$_id", "topics": {"$arrayToObject": "$topics"}}},
            {"$sort": {"date": -1}}
        ]
        data = list(self.articles_collection.aggregate(pipeline))
        topics = sorted(set(t for d in data for t in d['topics']))

        fig, ax = plt.subplots()
        bottom = np.zeros(len(data))
        for t in topics:
            values = np.array([d['topics'].get(t, 0) for d in data])
            if not all(v == 0 for v in values):
                ax.bar([d['date'] for d in data], values, bottom=bottom, label=t)
                bottom += values
                section_heights = bottom - values / 2
                for i, height in enumerate(section_heights):
                    if values[i] != 0:
                        ax.text(i, height, values[i], ha='center', va='center')

        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.show()
