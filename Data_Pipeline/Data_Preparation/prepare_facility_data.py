import pandas as pd

# Paths
FACILITY_DATA_PATH = './Data/Raw Data/facility_data.csv'
OUTPUT_PATH = './Data/Processed Data/filtered_facility_data.csv'

# Postcodes to filter
POSTCODES_TO_FILTER = [3052, 3054, 3053, 3051, 3031, 3003, 3008, 3006, 3141, 3002, 3000]

def prepare_facility_data():
    # Load raw facility data
    df = pd.read_csv(FACILITY_DATA_PATH)

    # Filter and clean data
    df['pcode'] = df['pcode'].astype(str).str.replace('.0', '', regex=False).astype(int)
    filtered_df = df[df['pcode'].isin(POSTCODES_TO_FILTER)]

    # Save filtered data
    filtered_df.to_csv(OUTPUT_PATH, index=False)
    print(f"Filtered facility data saved to {OUTPUT_PATH}")

if __name__ == '__main__':
    prepare_facility_data()
