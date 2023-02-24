import asyncio
from utils import silence_event_loop_closed
from asyncio.proactor_events import _ProactorBasePipeTransport
from get_data_stats_files import *
from data_analysis import show_top_scorer_stats_from_schedule_matches, show_off_fire_scorer_stats_from_schedule_matches

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)

SCHEDULE_DATE = "2023-01-02"  # must be yyyy-MM-dd format


async def main(schedule_date: str = None) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    # get schedule
    if schedule_date:
        schedule_file = await get_schedule_file(schedule_date)
        teams_files, matches = load_matches_from_schedule(schedule_file)
    else:
        teams_file, _ = load_all_team_rosters("all_teams")
        matches = None

    # get player stats
    player_files = await get_player_stats(teams_files)

    # load player stats into Dataframe
    concat_data = [load_player_stats_into_dataframe(file) for file in player_files]
    df_agg = pd.concat(concat_data)

    df_on_fire_scorers = show_top_scorer_stats_from_schedule_matches(data=df_agg)
    df_off_fire_scorers = show_off_fire_scorer_stats_from_schedule_matches(data=df_agg)

    return df_on_fire_scorers, df_off_fire_scorers, matches


if __name__ == "__main__":
    # df, matches = asyncio.run(main(schedule_date=SCHEDULE_DATE))

    teams_file, _ = load_all_team_rosters("all_teams")
    result = asyncio.run(get_player_stats(teams_file))
    print(result)
    # print(matches)
    # print(df)






