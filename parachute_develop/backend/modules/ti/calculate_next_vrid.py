import pandas as pd
from dateutil import parser
import pytz

# Define a dictionary for mapping timezone abbreviations to UTC offsets using pytz
tzinfos = {
    'EDT': pytz.timezone('US/Eastern'),  # Eastern Daylight Time (UTC-4)
    'EST': pytz.timezone('US/Eastern'),  # Eastern Standard Time (UTC-5)
    # Add other timezones as needed
}

def calculate_next_vrid():
    # Load the CSV file
    file_path = 'AFT Transshipment Hub.csv'
    df = pd.read_csv(file_path)

    # Ensure YMS Arrival Time is parsed as datetime with timezone information
    def parse_time(x):
        try:
            return parser.parse(str(x), tzinfos=tzinfos)
        except Exception as e:
            return pd.NaT  # Return a NaT for parsing errors

    df['YMS Arrival Time'] = df['YMS Arrival Time'].apply(parse_time)

    # Sort the DataFrame by 'Source FC' and 'YMS Arrival Time'
    df.sort_values(by=['Source FC', 'YMS Arrival Time'], inplace=True)

    # Initialize 'Next VRID' column
    df['Next VRID'] = None

    # Iterate over each unique 'Source FC'
    for source_fc in df['Source FC'].unique():
        # Get the subset of the dataframe for the current 'Source FC'
        subset = df[df['Source FC'] == source_fc]

        # Iterate over each load in this subset
        for idx, row in subset.iterrows():
            # Find the first load with '% Remaining' > 0.8
            next_load = subset[(subset['% Remaining'] > 0.8) & (subset['YMS Arrival Time'] > row['YMS Arrival Time'])]

            # Get the 'Load ID' of the first matching load, if it exists
            if not next_load.empty:
                next_vrid = next_load.iloc[0]['Load ID']
                df.at[idx, 'Next VRID'] = next_vrid

    # Save the updated DataFrame back to the CSV file
    df.to_csv(file_path, index=False)

if __name__ == "__main__":
    calculate_next_vrid()
