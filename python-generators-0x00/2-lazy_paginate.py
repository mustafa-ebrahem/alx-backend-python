#!/usr/bin/python3
"""
Module that implements lazy pagination for user data using generators
"""
seed = __import__('seed')


def paginate_users(page_size, offset):
    """
    Fetches paginated results from the user_data table
    
    Args:
        page_size: Number of rows to fetch per page
        offset: Starting offset for pagination
        
    Returns:
        List of user dictionaries for the requested page
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    connection.close()
    return rows


def lazy_pagination(page_size):
    """
    Generator function that lazily loads each page of user data
    
    Args:
        page_size: Number of records to fetch per page
        
    Yields:
        A page of user data (list of dictionaries) when requested
    """
    offset = 0
    
    while True:
        page = paginate_users(page_size, offset)
        if not page:
            break
            
        yield page
        offset += page_size