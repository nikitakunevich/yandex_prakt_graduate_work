import redis

from main import app

redis_db = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], db=0, decode_responses=True)
