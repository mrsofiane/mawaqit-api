import os
from redis import Redis
from config.settings import settings

# Conditionally initialize Redis client
if settings.ENABLE_REDIS:
    redisClient = Redis.from_url(settings.REDIS_URI)
else:
    redisClient = None