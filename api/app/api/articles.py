from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.database import db
from app.graph import Graph

articles_collection = db['articles']
users_collection = db['users']

router = APIRouter()

graph = Graph()

omit_id = {'_id': False}


@router.get('/recommended')
async def get_user_recommended_articles_by_username(username: str):
    user = users_collection.find_one({'username': username})
    if not user:
        raise HTTPException(status_code=404, detail=f'User with username @{username} not found')

    user_topics = user.get('topics')
    user_recommended_articles = articles_collection.aggregate([
        {'$match': {'topic': {'$in': user_topics}}},
        {'$addFields': {'_id': {'$toString': '$_id'}}},
        {'$group': {'_id': '$source.name', 'articles': {'$push': '$$ROOT'}}}
    ])

    return list(user_recommended_articles)


@router.get('/{article_id}')
async def get_article_by_id(article_id: str):
    article = articles_collection.find_one({'_id': ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail=f'Article with id {article_id} not found')

    article['_id'] = str(article['_id'])
    recommended_article_id = graph.recommend(article_id)
    recommended_article = articles_collection.find_one({'_id': ObjectId(recommended_article_id)})
    recommended_article['_id'] = str(recommended_article['_id'])
    return {
        'article': article,
        'recommendedArticle': recommended_article
    }
