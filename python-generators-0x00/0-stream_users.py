#!/usr/bin/python3
"""
Module that provides a generator function to stream user data from a database
"""
from seed import connect_to_prodev


def stream_users():
    """
    Generator function to fetch rows one by one from the user_data table
    Returns: Yields one row at a time from the user_data table
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_data")
        
        for row in cursor:
            yield row
            
    except Exception as e:
        print(f"Error streaming users: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()