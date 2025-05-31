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

@with_db_connection 
def get_user_by_id(conn, user_id): 
    cursor = conn.cursor() 
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)) 
    return cursor.fetchone() 

#### Fetch user by ID with automatic connection handling 
user = get_user_by_id(user_id=1)
print(user)