from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import time
import redis
import pickle

app = FastAPI()

# Initialize Redis connection (make sure Redis is running on localhost:6379)
r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=False)

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

    def to_dict(self):
        return {
            'value': self.value.isoformat(),  # store datetime as string
            'next': None  # 'next' can be handled via linked list in Redis
        }

    @staticmethod
    def from_dict(data):
        node = Node(datetime.datetime.fromisoformat(data['value']))
        # Handle 'next' in linked list structure within Redis
        return node

class RateLimiter:
    def __init__(self, max_posts, seconds, redis_client):
        self.max_posts = max_posts
        self.seconds = seconds
        self.redis = redis_client
        self.size_key = "rate_limiter_size"
        self.head_key = "rate_limiter_head"
        self.tail_key = "rate_limiter_tail"

    def delete_nodes(self, new_post_time):
        # Get all nodes from Redis and delete expired nodes
        head_node = self.redis.hgetall(self.head_key)
        if not head_node:
            return

        current_node = pickle.loads(head_node)
        while current_node and (new_post_time - current_node.value).total_seconds() > self.seconds:
            current_node = current_node.next

        # Update the head node in Redis
        self.redis.hset(self.head_key, "value", pickle.dumps(current_node))

    def allowed(self, current_time):
        # Retrieve the current head and tail nodes from Redis
        head_node = self.redis.hgetall(self.head_key)
        tail_node = self.redis.hgetall(self.tail_key)

        head = None
        tail = None

        if head_node:
            head = pickle.loads(head_node)
        if tail_node:
            tail = pickle.loads(tail_node)

        if not head:
            head = Node(current_time)
            self.redis.hset(self.head_key, "value", pickle.dumps(head))
            self.redis.set(self.size_key, 1)
            self.redis.hset(self.tail_key, "value", pickle.dumps(head))
            return True

        self.delete_nodes(current_time)

        # Retrieve current size
        size = int(self.redis.get(self.size_key) or 0)

        if size < self.max_posts:
            # Add new node to the list and update the tail
            new_node = Node(current_time)
            tail.next = new_node
            self.redis.hset(self.tail_key, "value", pickle.dumps(new_node))
            self.redis.incr(self.size_key)
            return True

        return False

class PostRequest(BaseModel):
    time: datetime.datetime


# Create an instance of RateLimiter
rate_limiter = RateLimiter(max_posts=2, seconds=4, redis_client=r)

@app.post("/rate_limit")
async def rate_limit(post_request: PostRequest):
    current_time = post_request.time

    if rate_limiter.allowed(current_time):
        return {"allowed": True}
    else:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
