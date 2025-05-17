#!/usr/bin/python3
"""
Module for batch processing of user data from database
"""
from seed import connect_to_prodev


def stream_users_in_batches(batch_size):
    """
    Generator function to fetch rows in batches from the user_data table
    
    Args:
        batch_size: Number of rows to fetch in each batch
        
    Yields:
        List of dictionaries containing user data for each batch
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        offset = 0
        
        while True:
            cursor.execute(
                "SELECT * FROM user_data LIMIT %s OFFSET %s",
                (batch_size, offset)
            )
            batch = cursor.fetchall()
            
            if not batch:
                break
                
            yield batch
            offset += batch_size
            
    except Exception as e:
        print(f"Error streaming users in batches: {e}")
    finally:
        if connection:
            connection.close()


def batch_processing(batch_size):
    """
    Processes each batch of users to filter users over the age of 25
    
    Args:
        batch_size: Number of rows to process in each batch
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user['age'] > 25:
                print(f"\n{user}")