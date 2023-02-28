from enum import Enum


class Topic(str, Enum):
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SCIENCE = "science"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
