import time
import sqlite3 
import functools

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

def retry_on_failure(retries=3, delay=1):
    """Decorator to retry a function on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt < retries - 1:
                        time.sleep(delay)
            raise Exception("All attempts failed")
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)

def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

    #### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)