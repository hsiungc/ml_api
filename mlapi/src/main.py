import logging
import os
import string

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel, conlist, validator
from redis import asyncio as aioredis
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

model_path = "./distilbert-base-uncased-finetuned-sst2"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(model_path)
classifier = pipeline(
    task="text-classification", model=model, tokenizer=tokenizer, device=-1, top_k=None
)

logger = logging.getLogger(__name__)
LOCAL_REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
app = FastAPI()


@app.on_event("startup")
async def startup():
    logging.debug(LOCAL_REDIS_URL)
    redis = aioredis.from_url(LOCAL_REDIS_URL, encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="mlapi-cache")


class SentimentRequest(BaseModel):
    text: conlist(str, min_items=1)

    @validator("text", each_item=True)
    def check_token_count(cls, val):
        assert len(val) <= 256, "Inputs must have less than 256 characters."
        return val

    @validator("text", each_item=True)
    def check_str(cls, val):
        assert val != "", "Inputs cannot be empty strings."
        return val

    @validator("text", each_item=True)
    def check_num(cls, val):
        if val.isnumeric():
            raise ValueError("Inputs cannot be pure numbers.")
        return val

    @validator("text", each_item=True)
    def check_punc(cls, val):
        if all(v in string.punctuation for v in val):
            raise ValueError("Inputs cannot be pure punctuation.")
        return val


class Sentiment(BaseModel):
    label: str
    score: float


class SentimentResponse(BaseModel):
    predictions: list[list[Sentiment]]


@app.post("/predict", response_model=SentimentResponse)
@cache(expire=90)
async def predict(sentiments: SentimentRequest):
    return {"predictions": classifier(sentiments.text)}


@app.get("/health")
async def health():
    return {"status": "healthy"}
