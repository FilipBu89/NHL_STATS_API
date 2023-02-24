"""Module storing few functions for analyzing data retrieved from NHL API"""
import numpy as np
import pandas as pd
import re
from typing import Dict, List

# number of matches, which should be considering for some stats
AVERAGE_STATS_PERIOD: int = 5
OFF_FIRE_PERIOD: int = 3


def convert_time_to_seconds(data: pd.DataFrame, column_name: str) -> int:
    """Small transformation function for converting time from mm:ss format into seconds.

    :param data: Dataframe
    :param column_name: name of the column storing time data

    :return: time converted to number of seconds
    """
    time = data[column_name]
    try:
        m = int(str(time[:2]).lstrip("0"))
        s = int(str(time[3:]).lstrip("0"))
    except (ValueError, TypeError):
        m = 0
        s = 0

    total_s = m*60 + s

    return total_s


def show_top_scorer_stats_from_schedule_matches(data: pd.DataFrame, top_n_players: int = 5,
                                                average_stats_period: int = AVERAGE_STATS_PERIOD) -> pd.DataFrame:
    """

    :param data:
    :param matches:
    :param top_n_players:
    :param average_stats_period:

    :return: new Dataframe with top scorers stats
    """
    df = data.reset_index()
    df["time_on_ice_seconds"] = df.apply(convert_time_to_seconds, args=("timeOnIce",), axis=1)
    df["time_power_play_seconds"] = df.apply(convert_time_to_seconds, args=("powerPlayTimeOnIce",), axis=1)
    df_agg = df.assign(
        goals_total=df["goals"],
        assists_total=df["assists"],
        goals_last_5=df[df["index"] < 5]["goals"],
        goals_last_10=df[df["index"] < 10]["goals"],
        time_on_ice_min=df[df["index"] < average_stats_period]["time_on_ice_seconds"],
        powerplay_time_min=df[df["index"] < average_stats_period]["time_power_play_seconds"],
        shot_efficiency=df[df["index"] < average_stats_period]["shotPct"],
        shots_avg=df[df["index"] < average_stats_period]["shots"]
    ).groupby(["name", "team"]).agg({"goals_total": sum, "goals_last_5": sum, "goals_last_10": sum, "assists_total": sum,
                                     "shot_efficiency": np.mean, "shots_avg": np.mean,
                                     "time_on_ice_min": lambda x: np.mean(x)/60,
                                     "powerplay_time_min": lambda x: np.mean(x)/60}).reset_index()
    df_agg.sort_values(["team", "goals_last_5", "goals_last_10", "goals_total", "shots_avg", "shot_efficiency",
                        "time_on_ice_min", "powerplay_time_min", ], ascending=False, inplace=True)
    df_agg["group_rank"] = df_agg.groupby("team")["name"].transform("cumcount")

    df_top_scorers = df_agg[df_agg["group_rank"] < top_n_players]

    return df_top_scorers


def show_off_fire_scorer_stats_from_schedule_matches(data: pd.DataFrame, top_n_players: int = 5,
                                                     average_stats_period: int = AVERAGE_STATS_PERIOD,
                                                     off_fire_period: int = OFF_FIRE_PERIOD) -> pd.DataFrame:
    """

    :param data:
    :param matches:
    :param top_n_players:
    :param average_stats_period:
    :param off_fire_period:

    :return: new Dataframe with top scorers stats
    """
    df = data.reset_index()
    df["time_on_ice_seconds"] = df.apply(convert_time_to_seconds, args=("timeOnIce",), axis=1)
    df["time_power_play_seconds"] = df.apply(convert_time_to_seconds, args=("powerPlayTimeOnIce",), axis=1)
    df_agg = df.assign(
        goals_total=df["goals"],
        assists_total=df["assists"],
        assists_last_3=df[df["index"] < off_fire_period]["assists"],
        goals_last_3=df[df["index"] < off_fire_period]["goals"],
        goals_last_15=df[df["index"] < 15]["goals"],
        time_on_ice_min=df[df["index"] < average_stats_period]["time_on_ice_seconds"],
        powerplay_time_min=df[df["index"] < average_stats_period]["time_power_play_seconds"],
        shot_efficiency=df[df["index"] < average_stats_period]["shotPct"],
        shots_avg=df[df["index"] < average_stats_period]["shots"]
    ).groupby(["name", "team"]).agg({"goals_total": sum, "goals_last_15": sum, "assists_total": sum,
                                     "shot_efficiency": np.mean, "shots_avg": np.mean, "goals_last_3": sum,
                                     "time_on_ice_min": lambda x: np.mean(x)/60, "assists_last_3": sum,
                                     "powerplay_time_min": lambda x: np.mean(x)/60}).reset_index()
    df_agg.sort_values(["team", "goals_last_15", "assists_last_3", "goals_total", "shots_avg", "shot_efficiency",
                        "time_on_ice_min", "powerplay_time_min", ], ascending=False, inplace=True)
    df_agg["group_rank"] = df_agg.groupby("team")["name"].transform("cumcount")

    df_top_scorers = df_agg[(df_agg["group_rank"] < top_n_players) & (df_agg["goals_last_3"] == 0)]

    return df_top_scorers
