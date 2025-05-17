#!/usr/bin/python3
"""
Module for memory-efficient aggregation of user ages using generators
"""
from seed import connect_to_prodev


def stream_user_ages():
    """
    Generator function to yield user ages one by one
    
    Yields:
        The age of each user as an integer/decimal
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT age FROM user_data")
        
        for row in cursor:
            yield row['age']
            
    except Exception as e:
        print(f"Error streaming user ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def calculate_average_age():
    """
    Calculates the average age of users using the stream_user_ages generator
    without loading the entire dataset into memory
    
    Returns:
        The average age of all users in the database
    """
    total_age = 0
    count = 0
    
    for age in stream_user_ages():
        total_age += age
        count += 1
        
    if count == 0:
        return 0
        
    return total_age / count


if __name__ == "__main__":
    avg_age = calculate_average_age()
    print(f"Average age of users: {avg_age:.2f}")