"""Pull Zac Veen's Statcast pitch-by-pitch data and save it to CSV."""

import os
import time

import pandas as pd
from pybaseball import statcast, playerid_reverse_lookup

PLAYER_NAME = "Zac Veen"
OUTPUT_FILE = "zac_veen_2025_2026.csv"


def load_pitch_data(start_year=2021, end_year=2026):
    """Pull full-season Statcast data for each year in the range and concat it."""
    dfs = []
    for year in range(start_year, end_year + 1):
        print(f"Pulling {year}...")
        try:
            year_df = statcast(
                start_dt=f"{year}-03-01",
                end_dt=f"{year}-10-31",
                verbose=False
            )
            dfs.append(year_df)
            time.sleep(5)  # be nice to Savant
        except Exception as e:
            print(f"Failed for {year}: {e}")

    return pd.concat(dfs, ignore_index=True)


def add_batter_names(df):
    """Map batter MLBAM ids to full names via a reverse lookup."""
    ids = df['batter'].unique().tolist()
    lookup = playerid_reverse_lookup(ids, key_type='mlbam')
    lookup['full_name'] = lookup['name_first'].str.title() + ' ' + lookup['name_last'].str.title()
    name_map = lookup.set_index('key_mlbam')['full_name'].to_dict()
    df = df.copy()
    df['batter_name'] = df['batter'].map(name_map)
    return df


def main():
    df = load_pitch_data(start_year=2025, end_year=2026)
    df = add_batter_names(df)
    df = df[df['batter_name'] == PLAYER_NAME]

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sample_data', OUTPUT_FILE)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} rows to {output_path}")


if __name__ == "__main__":
    main()
