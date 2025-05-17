# SQL Database Generator

## Project Description
This project implements a Python generator that streams rows from a MySQL database one by one. It includes functions to set up a database, create tables, and load data from a CSV file.

## Features
- Connect to MySQL database server
- Create database and tables
- Import data from CSV files
- Stream database rows using Python generator

## Implementation Details
The implementation includes the following components:

1. **Database Connection**: Functions to establish connections to the MySQL server and the ALX_prodev database
2. **Schema Creation**: Functions to create the database and user_data table with the specified schema
3. **Data Import**: Function to import user data from a CSV file into the database
4. **Row Generator**: Generator function that streams database rows one by one for efficient processing

## Usage
To use this generator:

```python
# Import the seed module
import seed

# Connect to the database
connection = seed.connect_to_prodev()

# Use the generator to stream rows
for row in seed.row_generator(connection):
    # Process each row
    print(row)

# Close the connection when done
connection.close()
```

## Requirements
- Python 3.x
- MySQL server
- mysql-connector-python package

## Installation
```
pip install mysql-connector-python
```

## Database Schema
- **Table**: user_data
- **Fields**:
  - user_id (VARCHAR(36), PRIMARY KEY, INDEXED)
  - name (VARCHAR(255), NOT NULL)
  - email (VARCHAR(255), NOT NULL)
  - age (DECIMAL, NOT NULL)