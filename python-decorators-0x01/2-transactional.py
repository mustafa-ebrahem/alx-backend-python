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

def transactional(func):
    """Decorator to add db transaction handling"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Start transaction
            conn.execute("BEGIN")
            result = func(conn, *args, **kwargs)
            # Commit transaction
            conn.commit()
            return result
        except Exception as e:
            # Rollback transaction on error
            conn.rollback()
            print(f"Transaction failed: {e}")
            raise
    return wrapper

@with_db_connection 
@transactional 
def update_user_email(conn, user_id, new_email): 
    cursor = conn.cursor() 
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id)) 
    #### Update user's email with automatic transaction handling 

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')