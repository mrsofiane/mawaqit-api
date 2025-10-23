import os
from redis import Redis

# Read the environment variable ENABLE_REDIS
ENABLE_REDIS = os.getenv('ENABLE_REDIS', 'False').lower() == 'true'

# Get Redis uri configuration from environment variables
REDIS_URI = os.getenv('REDIS_URI', 'redis://localhost:6379')

# Conditionally initialize Redis client
if ENABLE_REDIS:
    redisClient = Redis.from_url(REDIS_URI)
else:
    redisClient = None