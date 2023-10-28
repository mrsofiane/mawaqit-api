from redis import Redis
redisClient = Redis(host='localhost', port=6379, decode_responses=True)
