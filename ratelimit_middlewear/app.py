from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import time
import redis
import pickle

app = FastAPI()

# Initialize Redis connection (make sure Redis is running on localhost:6379)
r = redis.StrictRedis(host='redis', port=6379, db=0, decode_responses=False)


class RateLimiterRedis:
    def __init__(self, redis_client, max_posts, seconds, key="ratelimiter"):
        """
        Initialize the Redis-based rate limiter.

        :param redis_client: Redis connection object.
        :param max_posts: Maximum allowed requests within the time window.
        :param seconds: Time window in seconds.
        :param key: Redis key for storing request timestamps.
        """
        self.redis_client = redis_client
        self.max_posts = max_posts
        self.seconds = seconds
        self.key = key

    def allowed(self):
        """
        Check if the current request is allowed based on the rate-limiting rules.

        :return: True if the request is allowed, False otherwise.
        """

        current_time = datetime.datetime.now().timestamp()
        # Define the time window
        time_window_start = current_time - self.seconds

        # Remove outdated requests from the Redis sorted set
        self.redis_client.zremrangebyscore(self.key, "-inf", time_window_start)

        # Get the count of requests within the time window
        request_count = self.redis_client.zcard(self.key)

        if request_count < self.max_posts:
            # Add the current request timestamp to the sorted set
            self.redis_client.zadd(self.key, {current_time: current_time})

            # Optionally set an expiry for the key to optimize memory usage
            self.redis_client.expire(self.key, self.seconds)

            return True

        return False



# Create an instance of RateLimiter
rate_limiter = RateLimiterRedis(max_posts=2, seconds=4, redis_client=r)

@app.post("/rate_limit")
async def rate_limit():

    if rate_limiter.allowed():
        return {"allowed": True}
    else:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
