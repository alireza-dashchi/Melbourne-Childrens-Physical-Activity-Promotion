import pandas as pd
from geopy.geocoders import Nominatim

# Paths
PLAYGROUND_DATA_PATH = './Data/Raw Data/playground_data.csv'
OUTPUT_PATH = './Data/Processed Data/filtered_playground_data.csv'

def get_location_info(latitude, longitude):
    """
    Fetch suburb name and postcode for gi   ven latitude and longitude using geopy.
    """
    geolocator = Nominatim(user_agent="geoapiExercises")
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True, timeout=10)
        address = location.raw['address']
        suburb = address.get('suburb', '')
        postcode = address.get('postcode', '')
        return suburb, postcode
    except Exception as e:
        print(f"Error fetching location for lat: {latitude}, long: {longitude}. Error: {e}")
        return '', ''

def prepare_playground_data():
    """
    Prepares playground data by enriching it with suburb names and postcodes.
    """
    # Load raw playground data
    df = pd.read_csv(PLAYGROUND_DATA_PATH)

    # Add new columns for suburb_name and postcode
    df['suburb_name'], df['postcode'] = zip(*df.apply(lambda row: get_location_info(row['latitude'], row['longitude']), axis=1))

    # Save the processed data
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Processed playground data saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    prepare_playground_data()
