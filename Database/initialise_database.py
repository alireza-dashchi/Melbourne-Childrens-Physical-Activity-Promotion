import sqlite3

def create_database():
    # Connect to SQLite database (creates the file if it doesn't exist)
    conn = sqlite3.connect('ILikeToMoveIt.db')
    cursor = conn.cursor()

    # Create Suburbs_info table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Suburbs_info (
            suburb_id INTEGER PRIMARY KEY,
            suburb_name TEXT NOT NULL,
            postcode TEXT NOT NULL
        )
    ''')

    # Create Location table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Location (
            location_id INTEGER PRIMARY KEY,
            postcode TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            suburb_id INTEGER,
            FOREIGN KEY (suburb_id) REFERENCES Suburbs_info(suburb_id)
        )
    ''')

    # Create Facility table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Facility (
            facility_id TEXT PRIMARY KEY,
            facility_name TEXT NOT NULL,
            sports_played TEXT,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Location(location_id)
        )
    ''')

    # Create Playground table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Playground (
            playground_id INTEGER PRIMARY KEY,
            playground_name TEXT NOT NULL,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Location(location_id)
        )
    ''')

    # Create Landmark table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Landmark (
            landmark_id INTEGER PRIMARY KEY,
            landmark_type TEXT NOT NULL,
            landmark_name TEXT NOT NULL,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Location(location_id)
        )
    ''')

    # Create Photos table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Photos (
            photo_id INTEGER PRIMARY KEY,
            photo_filepath TEXT NOT NULL,
            location_id INTEGER,
            FOREIGN KEY (location_id) REFERENCES Location(location_id)
        )
    ''')

    # Create Accident table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Accident (
            accident_id INTEGER PRIMARY KEY,
            total_accidents INTEGER NOT NULL,
            suburb_id INTEGER,
            FOREIGN KEY (suburb_id) REFERENCES Suburbs_info(suburb_id)
        )
    ''')

    # Create Crime table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Crime (
            crime_id TEXT PRIMARY KEY,
            incidents_recorded_2014_2023 INTEGER NOT NULL,
            suburb_id INTEGER,
            FOREIGN KEY (suburb_id) REFERENCES Suburbs_info(suburb_id)
        )
    ''')

    # Create Guideline table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Guideline (
            guideline_id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            age_group TEXT NOT NULL
        )
    ''')

    # Create First Aid table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS First_Aid (
            first_aid_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            media_link TEXT
        )
    ''')

    # Create Chatbot Training Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Chatbot_Training_Data (
            training_id INTEGER PRIMARY KEY,
            guideline TEXT NOT NULL,
            source_link TEXT
        )
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database 'ILikeToMoveIt.db' created successfully.")

if __name__ == '__main__':
    create_database()
