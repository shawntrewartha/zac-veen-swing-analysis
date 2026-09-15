"""Bat tracking analysis for Zac Veen: swing metrics by year and pitch category."""

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle

INPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sample_data', 'zac_veen_bat_tracking.csv')

VALUE_ORDER = ['attack_direction',
               'attack_angle', 'launch_angle', 'launch_speed',
               'intercept_ball_minus_batter_pos_x_inches', 'intercept_ball_minus_batter_pos_y_inches',
               'bat_speed', 'swing_length', 'swing_path_tilt',
               'miss_distance']

VALUE_ORDER_TOP10 = ['attack_direction',
                      'attack_angle', 'launch_angle', 'launch_speed',
                      'intercept_ball_minus_batter_pos_x_inches', 'intercept_ball_minus_batter_pos_y_inches',
                      'bat_speed', 'swing_length', 'swing_path_tilt']


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


# --- analysis ------------------------------------------------------------

def swing_percentage_by_year(df):
    """Swing % grouped by year."""
    return df.groupby('year')['swing'].mean() * 100


def hitting_metrics_by_year(df, value_order):
    """Mean hitting metrics grouped by year, in the given column order."""
    pivot = df.pivot_table(index='year', values=value_order, aggfunc='mean')
    return pivot[value_order]


def hitting_metrics_by_pitch_category(df, value_order, index_order=('FB', 'BB', 'OS')):
    """Mean hitting metrics grouped by pitch category and year."""
    pivot = df.pivot_table(index='pitch_cat', columns='year', values=value_order, aggfunc='mean')
    return pivot.reindex(index=list(index_order)).reindex(columns=value_order, level=0)


def top_n_metric_means(df, metric, value_order, n=10):
    """Return (mean of value_order columns, the rows themselves) for the top-n rows by metric."""
    df_top = df.nlargest(n, metric)
    return df_top[value_order].mean(), df_top


# --- plots -----------------------------------------------------------------

def plot_point_of_contact(df, player_name):
    # average point of contact by year
    intercept_x_2026 = df[df['year'] == 2026]['intercept_ball_minus_batter_pos_x_inches'].mean()
    intercept_y_2026 = df[df['year'] == 2026]['intercept_ball_minus_batter_pos_y_inches'].mean()
    intercept_x_2025 = df[df['year'] == 2025]['intercept_ball_minus_batter_pos_x_inches'].mean()
    intercept_y_2025 = df[df['year'] == 2025]['intercept_ball_minus_batter_pos_y_inches'].mean()

    # color scheme
    background_color = '#1A0D2E'
    low_ellipse_color = '#FF6B6B'
    above_ellipse_color = '#06D6A0'
    high_ellipse_color = '#C77DFF'

    # home plate geometry (standard MLB dimensions, inches)
    # front edge (facing pitcher) is 17" wide, centered on x=0, at y=0
    # two 8.5" sides run back to y=-8.5, then two 12" angled sides meet at the back tip
    half_width = 8.5
    side_length = 8.5
    back_tip_y = -(side_length + 12 * np.cos(np.radians(45)))  # ~ -17
    gap = 6
    half_side_box = 36
    top_box = 48

    plate_vertices = [
        (-half_width, 0),
        (half_width, 0),
        (half_width, -side_length),
        (0, back_tip_y),
        (-half_width, -side_length),
    ]

    l_box_vertices = [
        (half_width + gap, half_side_box),
        (half_width + gap + top_box, half_side_box),
        (half_width + gap + top_box, -half_side_box),
        (half_width + gap, -half_side_box)
    ]

    r_box_vertices = [
        (-half_width - gap, half_side_box),
        (-half_width - gap - top_box, half_side_box),
        (-half_width - gap - top_box, -half_side_box),
        (-half_width - gap, -half_side_box)
    ]

    # reference lines
    horizontal_line_y = back_tip_y - 11.7   # 11.7" behind the back tip of the plate
    vertical_line_x = half_width + 29.3     # 29.3" right of the plate's right edge

    # data points
    point_2026 = (
        vertical_line_x - intercept_x_2026,
        horizontal_line_y + intercept_y_2026,
    )
    point_2025 = (
        vertical_line_x - intercept_x_2025,
        horizontal_line_y + intercept_y_2025,
    )
    center_of_mass = (
        vertical_line_x,
        horizontal_line_y
    )

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    plate = Polygon(plate_vertices, closed=True, facecolor='white',
                     edgecolor='white', linewidth=1.5, alpha=0.9, zorder=2)
    ax.add_patch(plate)

    l_box = Polygon(l_box_vertices, closed=True, facecolor='none',
                     edgecolor='white', linewidth=3, zorder=1)
    ax.add_patch(l_box)

    r_box = Polygon(r_box_vertices, closed=True, facecolor='none',
                     edgecolor='white', linewidth=3, zorder=1)
    ax.add_patch(r_box)

    ax.axhline(horizontal_line_y, color='red', linewidth=1.5, zorder=1)
    ax.axvline(vertical_line_x, color='red', linewidth=1.5, zorder=1)

    ax.scatter(*point_2026, s=150, color=high_ellipse_color, edgecolor='white', zorder=3)
    ax.scatter(*point_2025, s=150, color=above_ellipse_color, edgecolor='white', zorder=3)
    ax.scatter(*center_of_mass, s=150, color=low_ellipse_color, edgecolor='white', zorder=3)

    ax.annotate(f'2026 ({intercept_y_2026:.1f}")', point_2026, textcoords='offset points',
                xytext=(0, 12), ha='center', va='bottom',
                color='white', fontsize=11, fontweight='bold')
    ax.annotate(f'2025 ({intercept_y_2025:.1f}")', point_2025, textcoords='offset points',
                xytext=(0, -12), ha='center', va='top',
                color="black", fontsize=11, fontweight='bold')
    ax.annotate('Center of Mass', center_of_mass, textcoords='offset points', xytext=(10, 8),
                color='white', fontsize=11, fontweight='bold')

    ax.set_xlim(vertical_line_x - 60, vertical_line_x + 30)
    ax.set_ylim(horizontal_line_y - 15, 40)
    ax.set_aspect('equal')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_color('white')

    ax.set_xlabel('Inches', color='white')
    ax.set_ylabel('Inches', color='white')
    ax.set_title(f'{player_name} - Average Point of Contact Relative to Center of Mass', color='white')

    plt.show()


def plot_attack_angle_by_year(df, player_name):
    # color scheme
    background_color = '#1A0D2E'
    above_ellipse_color = '#06D6A0'
    high_ellipse_color = '#C77DFF'
    bat_color = 'saddlebrown'
    ball_color = 'white'

    # gather attack angle data by year (rounded to 1 decimal place)
    angle_2026 = round(df[df['year'] == 2026]['attack_angle'].mean(), 1)
    angle_2025 = round(df[df['year'] == 2025]['attack_angle'].mean(), 1)

    vertex = (0, 0)          # point of contact
    bat_radius = 6
    ball_radius = 4
    line_length_right = 40   # follow-through, solid
    line_length_left = 20    # approach path, dotted, extends past the ball

    # bat and ball are tangent at the vertex (touching, not overlapping)
    bat_center = (vertex[0], vertex[1])
    ball_center = (vertex[0] + bat_radius + ball_radius, vertex[1] + 3)

    def angle_point(origin, angle_deg, length):
        angle_rad = np.radians(angle_deg)
        return (origin[0] + length * np.cos(angle_rad), origin[1] + length * np.sin(angle_rad))

    def plot_swing_line(ax, angle_deg, color, label):
        right_end = angle_point(vertex, angle_deg, line_length_right)
        left_end = angle_point(vertex, angle_deg + 180, line_length_left)
        ax.plot([vertex[0], right_end[0]], [vertex[1], right_end[1]],
                color=color, linewidth=2.5, zorder=2, label=label)
        ax.plot([vertex[0], left_end[0]], [vertex[1], left_end[1]],
                color=color, linewidth=2.5, linestyle=':', zorder=2)
        ax.annotate(f'{angle_deg}°', right_end, textcoords='offset points', xytext=(8, 4),
                    color='white', fontsize=11, fontweight='bold')

    fig, ax = plt.subplots(figsize=(8, 8))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor(background_color)

    plot_swing_line(ax, angle_2025, above_ellipse_color, f'2025 ({angle_2025}°)')
    plot_swing_line(ax, angle_2026, high_ellipse_color, f'2026 ({angle_2026}°)')

    bat = Circle(bat_center, radius=bat_radius, facecolor=bat_color, alpha=0.8, edgecolor='white', linewidth=1.5, zorder=3)
    ax.add_patch(bat)

    ball = Circle(ball_center, radius=ball_radius, facecolor=ball_color, alpha=0.8, edgecolor='black', linewidth=1.4, zorder=4)
    ax.add_patch(ball)

    axis_radius = line_length_right + 10
    boundary = Circle(vertex, radius=axis_radius, facecolor='none', edgecolor='white', linewidth=1.2, alpha=0.6, zorder=0)
    ax.add_patch(boundary)

    ax.set_xlim(vertex[0] - axis_radius - 5, vertex[0] + axis_radius + 5)
    ax.set_ylim(vertex[1] - axis_radius - 5, vertex[1] + axis_radius + 5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_title(f'{player_name} - Attack Angle by Year', color='white')
    ax.legend(facecolor=background_color, edgecolor='white', labelcolor='white', loc='upper left')

    plt.show()


def main():
    player_name = "Zac Veen"

    df = pd.read_csv(INPUT_FILE)
    df = add_year_column(df)
    df = add_swing_column(df)
    df = add_pitch_category_column(df)

    print("Swing % by year:")
    print(swing_percentage_by_year(df))

    print("\nHitting metrics by year:")
    print(hitting_metrics_by_year(df, VALUE_ORDER))

    print("\nHitting metrics by pitch category:")
    print(hitting_metrics_by_pitch_category(df, VALUE_ORDER))

    top10_means, df_top10 = top_n_metric_means(df, 'estimated_slg_using_speedangle', VALUE_ORDER_TOP10, n=10)
    print("\nTop 10 estimated_slg_using_speedangle - mean metrics:")
    print(top10_means)
    print("\nTop 10 rows by year:")
    print(df_top10['year'].value_counts())

    plot_point_of_contact(df, player_name)
    plot_attack_angle_by_year(df, player_name)


if __name__ == "__main__":
    main()
