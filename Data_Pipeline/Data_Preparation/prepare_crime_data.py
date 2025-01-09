import pandas as pd

# Paths
CRIME_DATA_PATH = './Data/Raw Data/crime_data.csv'
SUBURB_INFO_PATH = './Data/Processed Data/suburb_info.csv'
OUTPUT_PATH = './Data/Processed Data/filtered_crime_data_with_suburb_id.csv'

def prepare_crime_data():
    # Load raw crime data
    crime_data = pd.read_csv(CRIME_DATA_PATH)
    suburb_info = pd.read_csv(SUBURB_INFO_PATH)

    # Aggregate incidents
    crime_grouped = crime_data.groupby(['suburb', 'postcode'])['incidents_recorded'].sum().reset_index()
    crime_grouped.columns = ['suburb', 'postcode', 'incidents_recorded_2014_2023']

    # Merge with suburb info
    crime_grouped['postcode'] = crime_grouped['postcode'].astype(str)
    filtered_df = crime_grouped.merge(suburb_info, on=['postcode', 'suburb'])

    # Save to CSV
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Filtered crime data saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    prepare_crime_data()
