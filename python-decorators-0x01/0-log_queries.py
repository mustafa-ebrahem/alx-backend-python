import sqlite3
import functools
from datetime import datetime

#### decorator to log SQL queries

def log_queries(func):
    """Decorator that logs SQL queries before executing them"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Find the query parameter - could be positional or keyword argument
        query = None
        
        # Check if query is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Check if query is the first positional argument
        elif args:
            query = args[0]
        
        # Log the query with timestamp
        if query:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] Executing query: {query}")
        
        # Execute the original function
        result = func(*args, **kwargs)
        
        return result
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")