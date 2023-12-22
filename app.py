import os
import pandas as pd
from sqlalchemy import create_engine, types,text
from datetime import datetime

# Replace 'your_username', 'your_password', 'your_host', and 'your_port' with your actual database credentials
db_credentials = {
    'username': 'admin',
    'password': 'Jayesh123',
    'host': 'cardstatus.cpee4kui2bz9.eu-north-1.rds.amazonaws.com',
    'port': '3306',
    'database': 'Adi'
}

# Replace 'card' with your actual table name
table_name = 'Card'

# Replace 'data' with your actual folder name
folder_path = 'data'

# Create a database connection
engine = create_engine(
    f"mysql://{db_credentials['username']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}")

# Define the mapping dictionary for the "Pickup.csv" file
common_mapping = {
    'Card ID': 'Card Id',
    'User contact': 'Contact Number',
    'Timestamp': 'Last Update'
}
# Define the mapping dictionary for the "Returned.csv" file
delivery_exception_mapping = {
    'Card ID': 'Card Id',
    'User contact': 'Contact Number',
    'Timestamp': 'Last Update',
    'Comment': 'Comment'
}

Pickup_mapping = {
    'Card ID': 'Card Id',
    'User Mobile': 'Contact Number',
    'Timestamp': 'Last Update',
    'Comment': 'Comment'
}

# Iterate through CSV files in the specified folder and update the database
status_value = 'NA'
file_order = ['Pickup.csv', 'Delivery exception.csv', 'Delivered.csv', 'Returned.csv']
for filename in file_order:
    # Read CSV file into a pandas DataFrame
    file_path = os.path.join(folder_path, filename)
    df = pd.read_csv(file_path)
    id_columns = [col for col in df.columns if col.strip().lower() == 'id']
    df = df.drop(id_columns, axis=1, errors='ignore')
    status_value = None
    if filename == 'Delivery exception.csv':
        df = df.rename(columns=delivery_exception_mapping)
        status_value = 'Delivery Failed'
    elif filename == 'Delivered.csv':
        df = df.rename(columns=common_mapping)
        status_value = 'Card Delivered'
        df['Comment'] = 'None'
    elif filename == 'Pickup.csv':
        df = df.rename(columns=Pickup_mapping)
        status_value = 'Card Pickup Successful'
        df['Comment'] = 'None'
    elif filename == 'Returned.csv':
        df = df.rename(columns=common_mapping)
        status_value = 'Card Returned'
        df['Comment'] = 'None'
    # Define the data types and lengths for the database table columns
    table_dtypes = {
            'Card Id': types.VARCHAR(length=255),
            'Contact Number': types.VARCHAR(length=255),
            'Last Update': types.DATETIME(),
            'Status': types.VARCHAR(length=255),
            'Comment': types.VARCHAR(length=255)
        }
    # Set the 'Status' and 'Comment' values for the current CSV file
    df['Status'] = status_value
    print(df)
    print('\n')
    for index, row in df.iterrows():
        card_id = row['Card Id']

        # Check if a row with the same 'Card Id' already exists in the database
        existing_entry = pd.read_sql_query(
            f"SELECT * FROM {table_name} WHERE `Card Id` = '{card_id}'", engine)

        if existing_entry.empty:
            # If no existing entry, append the row to the database
            pd.DataFrame([row]).to_sql(
                name=table_name, con=engine, if_exists='append', index=False, dtype=table_dtypes)
        else:
            # If an existing entry is found, update the values
            existing_entry_index = existing_entry.index[0]
            existing_entry['Last Update'] = row['Last Update']
            existing_entry['Status'] = status_value
            existing_entry['Comment'] = row['Comment']
            existing_entry.to_sql(
                name=table_name, con=engine, if_exists='replace', index=False, dtype=table_dtypes)
engine.dispose()
