import pyodbc

def get_db_connection():
    try:
        # Define your database connection parameters here
        server = 'NASHUA-WAYNE'
        database = 'NashuaXpressDB'
        username = 'wayne'
        password = 'P@ssw0rd12346'
        driver = '{ODBC Driver 17 for SQL Server}'  

        # Create a connection string
        connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        # Establish the database connection
        conn = pyodbc.connect(connection_string)

        return conn

    except pyodbc.Error as e:
        print(f"Database connection error: {str(e)}")
        return None

# You can add other database-related utility functions or configurations here if needed

def get_remote_db_connection():
    try:
        # Define your database connection parameters here
        server = 'NASHUA-EVA'
        database = 'BPO2_NASH_TEST'
        username = 'sa'
        password = 'Kippey1'
        driver = '{ODBC Driver 17 for SQL Server}'  

        # Create a connection string
        connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};"

        # Establish the database connection
        conn = pyodbc.connect(connection_string)

        return conn

    except pyodbc.Error as e:
        print(f"Database connection error: {str(e)}")
        return None