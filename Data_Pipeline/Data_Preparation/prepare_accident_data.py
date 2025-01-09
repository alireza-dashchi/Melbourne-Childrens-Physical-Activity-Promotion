import pandas as pd

# Paths
ACCIDENT_DATA_PATH = './Data/Raw Data/accident_data.csv'
OUTPUT_PATH = './Data/Processed Data/filtered_accident_data_with_suburb_id.csv'

# Suburb data mapping
SUBURB_DATA = {
    '3052': {'Parkville': 1},
    '3054': {'Carlton North': 2, 'Princess Hill': 14},
    '3053': {'Carlton': 3},
    '3051': {'North Melbourne': 4},
    '3031': {'Flemington': 5, 'Kensington': 6},
    '3003': {'West Melbourne': 7},
    '3008': {'Docklands': 8},
    '3006': {'Southbank': 9},
    '3141': {'South Yarra': 10},
    '3002': {'East Melbourne': 11},
    '3000': {'Melbourne': 12},
    '3004': {'Melbourne': 13},
    '3207': {'Port Melbourne': 15},
    '3065': {'Fitzroy': 16}
}

def prepare_accident_data():
    # Load accident data
    df = pd.read_csv(ACCIDENT_DATA_PATH)
    df['postcode'] = df['postcode'].astype(str)

    # Prepare suburb mapping
    suburb_id_map = [
        {'postcode': postcode, 'suburb': suburb, 'suburb_id': suburb_id}
        for postcode, suburbs in SUBURB_DATA.items()
        for suburb, suburb_id in suburbs.items()
    ]
    suburb_id_df = pd.DataFrame(suburb_id_map)

    # Merge and filter data
    filtered_df = df.merge(suburb_id_df, on='postcode', how='inner')
    filtered_df = filtered_df[['total_accidents', 'suburb_id']]

    # Save to CSV
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Filtered accident data saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    prepare_accident_data()
