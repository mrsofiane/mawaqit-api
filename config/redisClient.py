import os
from redis import Redis
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read the environment variable USE_REDIS
USE_REDIS = os.getenv('USE_REDIS', 'False').lower() == 'true'

# Get Redis configuration from environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Conditionally initialize Redis client
if USE_REDIS:
    redisClient = Redis(host=redis_host, port=redis_port, decode_responses=True)
else:
    redisClient = None