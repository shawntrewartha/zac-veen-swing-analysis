"""Statcast plate discipline analysis for Zac Veen: swing/whiff rates by year, pitch category, and zone."""

import os

import numpy as np
import pandas as pd

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sample_data', 'zac_veen_2025_2026.csv')


# --- data cleaning -----------------------------------------------------

def add_year_column(df, date_col='game_date'):
    """Convert date_col to datetime and add a 'year' column derived from it."""
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df['year'] = df[date_col].dt.year
    return df


def add_swing_column(df):
    """Flag pitches that were swung at, excluding automatic ball/strike calls."""
    swing_events = ['swinging_strike', 'foul', 'hit_into_play',
                     'swinging_strike_blocked', 'foul_tip', 'foul_bunt', 'bunt_foul_tip']
    df = df[~df['description'].isin(['automatic_ball', 'automatic_strike'])].copy()
    df['swing'] = df['description'].isin(swing_events).astype(int)
    return df


def add_swing_and_miss_column(df):
    """Flag swings that resulted in a miss."""
    df = df.copy()
    df['swing_and_miss'] = df['description'].isin(
        ['swinging_strike', 'swinging_strike_blocked', 'foul_tip', 'bunt_foul_tip']
    ).astype(int)
    return df


def add_pitch_category_column(df):
    """Bucket pitch_type into FB (fastballs), BB (breaking balls), OS (off-speed)."""
    FB = ['FF', 'FC', 'SI']
    BB = ['SL', 'CU', 'KC', 'ST', 'SV', 'EP']
    OS = ['CH', 'FS']
    df = df.copy()
    df['pitch_cat'] = np.select(
        [df['pitch_type'].isin(FB), df['pitch_type'].isin(BB), df['pitch_type'].isin(OS)],
        ['FB', 'BB', 'OS'],
        default='Other'
    )
    return df


def add_in_zone_column(df):
    """Flag pitches thrown in the strike zone (Statcast zones 1-9)."""
    in_zone_values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
    df = df.copy()
    df['in_zone'] = df['zone'].isin(in_zone_values).astype(int)
    return df


# --- analysis ------------------------------------------------------------

def swing_percentage_by_year(df):
    """Swing % grouped by year."""
    return df.groupby('year')['swing'].mean() * 100


def swing_and_miss_percentage_by_year(df):
    """Whiff % (of swings) grouped by year."""
    df_swings = df[df['swing'] == 1]
    return df_swings.groupby('year')['swing_and_miss'].mean() * 100


def swing_percentage_by_pitch_category(df):
    """Swing % grouped by year and pitch category."""
    return df.groupby(['year', 'pitch_cat'])['swing'].mean() * 100


def swing_and_miss_percentage_by_pitch_category(df):
    """Whiff % (of swings) grouped by year and pitch category."""
    df_swings = df[df['swing'] == 1]
    return df_swings.groupby(['year', 'pitch_cat'])['swing_and_miss'].mean() * 100


def total_pitches_by_pitch_category(df):
    """Pitch counts grouped by year and pitch category."""
    return df.groupby(['year', 'pitch_cat']).size()


def swing_percentage_by_zone(df):
    """Swing % grouped by zone location, pitch category, and year."""
    return df.groupby(['in_zone', 'pitch_cat', 'year'])['swing'].mean() * 100


def swing_and_miss_percentage_by_zone(df):
    """Whiff % (of swings) grouped by zone location, pitch category, and year."""
    df_swings = df[df['swing'] == 1]
    return df_swings.groupby(['in_zone', 'pitch_cat', 'year'])['swing_and_miss'].mean() * 100


def main():
    df = pd.read_csv(INPUT_FILE)
    df = df[df['game_type'] == 'R']  # regular season only

    df = add_swing_column(df)
    df = add_swing_and_miss_column(df)
    df = add_year_column(df)
    df = add_pitch_category_column(df)
    df = add_in_zone_column(df)

    print("Swing % by year:")
    print(swing_percentage_by_year(df))

    print("\nSwing-and-miss % by year:")
    print(swing_and_miss_percentage_by_year(df))

    print("\nSwing-and-miss % by pitch category:")
    print(swing_and_miss_percentage_by_pitch_category(df))

    print("\nSwing % by pitch category:")
    print(swing_percentage_by_pitch_category(df))

    print("\nTotal pitches by pitch category:")
    print(total_pitches_by_pitch_category(df))

    print("\nSwing % by zone location:")
    print(swing_percentage_by_zone(df))

    print("\nSwing-and-miss % by zone location:")
    print(swing_and_miss_percentage_by_zone(df))


if __name__ == "__main__":
    main()
