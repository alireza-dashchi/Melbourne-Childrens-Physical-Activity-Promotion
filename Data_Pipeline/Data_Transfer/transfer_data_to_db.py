import pandas as pd
import sqlite3

# Database path
DATABASE_PATH = './Data_Pipeline/ILikeToMoveIt.db'

# Paths to processed CSV files
PLAYGROUND_DATA_PATH = './Data/Processed Data/filtered_playground_data.csv'
FACILITY_DATA_PATH = './Data/Processed Data/filtered_facility_data.csv'
CRIME_DATA_PATH = './Data/Processed Data/filtered_crime_data_by_suburb.csv'
ACCIDENT_DATA_PATH = './Data/Processed Data/filtered_accident_by_suburb.csv'
LANDMARK_DATA_PATH = './Data/Processed Data/filtered_landmark_data.csv'


def transfer_data_to_db():
    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_PATH)

    # 1. Transfer filtered_playground_data to Playground table
    playground_data = pd.read_csv(PLAYGROUND_DATA_PATH)
    playground_data.to_sql('Playground', conn, if_exists='replace', index=False)
    print("Playground data transferred.")

    # 2. Transfer filtered_facility_data to Facility table
    facility_data = pd.read_csv(FACILITY_DATA_PATH)
    facility_data.to_sql('Facility', conn, if_exists='replace', index=False)
    print("Facility data transferred.")

    # 3. Transfer filtered_crime_data_by_suburb to Crime table
    crime_data = pd.read_csv(CRIME_DATA_PATH)
    crime_data = crime_data.rename(columns={'suburb_id': 'suburb_id'})
    crime_data[['crime_id', 'incidents_recorded_2014_2023', 'suburb_id']].to_sql(
        'Crime', conn, if_exists='replace', index=False
    )
    print("Crime data transferred.")

    # 4. Transfer filtered_accident_by_suburb to Accident table
    accident_data = pd.read_csv(ACCIDENT_DATA_PATH)
    accident_data.to_sql('Accident', conn, if_exists='replace', index=False)
    print("Accident data transferred.")

    # 5. Transfer filtered_landmark_data to Landmark table
    landmark_data = pd.read_csv(LANDMARK_DATA_PATH)
    landmark_data.to_sql('Landmark', conn, if_exists='replace', index=False)
    print("Landmark data transferred.")

    # Close connection
    conn.close()
    print("All data transferred successfully to the database!")


if __name__ == '__main__':
    transfer_data_to_db()
