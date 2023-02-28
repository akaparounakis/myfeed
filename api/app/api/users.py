from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.common import Topic
from app.database import db

users_collection = db['users']

router = APIRouter()

omit_id = {'_id': False}


class User(BaseModel):
    username: str
    topics: List[Topic]
    created_at: datetime = datetime.now()


class UserUpdateTopics(BaseModel):
    topics: List[Topic]


@router.post('/', status_code=201)
async def create_user(user: User):
    existing_user = users_collection.find_one({'username': user.username})
    if not existing_user:
        users_collection.insert_one(user.dict())
    else:
        raise HTTPException(status_code=409, detail=f'User with username @{user.username} already exists')


@router.get('/@{username}')
async def get_user_by_username(username: str):
    user = users_collection.find_one({'username': username}, omit_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail=f'User with username @{username} not found')


@router.put('/@{username}')
async def update_user_topics(username: str, user_topics: UserUpdateTopics):
    existing_user = users_collection.find_one({'username': username})
    if existing_user:
        users_collection.update_one({'username': username}, {'$set': {'topics': user_topics.topics}})
    else:
        raise HTTPException(status_code=404, detail=f'User with username @{username} not found')


@router.delete('/@{username}')
async def delete_user_by_username(username: str):
    user = users_collection.find_one({'username': username})
    if user:
        users_collection.delete_one({'username': username})
    else:
        raise HTTPException(status_code=404, detail=f'User with username @{username} not found')
