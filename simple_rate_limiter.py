import datetime
import time


class Node:

    def __init__(self, value):
        self.value = value
        self.next = None
class RateLimiter:

    def __init__(self,max_posts, seconds):
        self.max_posts = max_posts
        self.seconds = seconds 
        self.current_node = None
        self.posts_count = 0 
        self.tail = self.current_node
        self.size = 0 

    def print(self):
        s = ""
        
        node = self.current_node
        while node:
            s += str(node.value)
            s += "-->"
            node = node.next

        s += "None"
        print(s)

    
    def delete_nodes(self, new_post_time):
        
        while  self.current_node and (new_post_time - self.current_node.value).total_seconds() > self.seconds:
            self.current_node = self.current_node.next
            self.size -= 1  

            if not self.current_node:
                self.tail = None


    def allowed(self, current_time):
        new_node = Node(current_time)

        if self.size == 0 :
            self.current_node = Node(current_time)
            self.tail = self.current_node
            self.size += 1
            return True
        
        self.delete_nodes(current_time)

        if  self.size < self.max_posts:
            
            self.tail.next = Node(current_time)
            self.tail = self.tail.next
            
            self.size += 1
            return True
        return False

    

if __name__=="__main__":
    rl = RateLimiter(2, 4)
    
    print(rl.allowed(datetime.datetime.now()))
    
    rl.print()
    print("------------")
    time.sleep(1)
    print(rl.allowed(datetime.datetime.now()))
    rl.print()
    print("------------")
    time.sleep(1)
    print(rl.allowed(datetime.datetime.now()))
    rl.print()
    print("------------")
    time.sleep(1)
    print(rl.allowed(datetime.datetime.now()))
    rl.print()
    print("------------")
    time.sleep(1)
    print(rl.allowed(datetime.datetime.now()))
    rl.print()