import time
import sqlite3 
import functools


query_cache = {}

def with_db_connection(func):
    """Decorator that automatically provides a database connection"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Step 1: Create database connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Step 2: Inject connection as first argument
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Step 3: Always close connection (even if error occurs)
            conn.close()
    
    return wrapper

def cache_query(func):
    """Decorator to cache query results"""
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
        
        # If query is cached, return cached result
        if query in query_cache:
            print("Using cached result")
            return query_cache[query]
        
        # Execute the original function
        result = func(*args, **kwargs)
        
        # Cache the result
        query_cache[query] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")