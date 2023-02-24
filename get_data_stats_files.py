"""Module storing few specific functions for running a program."""
import re
from typing import Tuple, List, Dict
import json
from pathlib import Path
import pandas as pd
from utils import FrozenJSON, fetch_files, FILES_DIR

# base URL for accessing NHL api endpoints
BASE_URL = "https://statsapi.web.nhl.com/"


async def get_schedule_file(start_date: str, end_date: str = None) -> str:
    """Get list of matches for a selected date range.

    :param start_date: start date (day) of the date range
    :param end_date: end date (day) of the date range; if not selected start_date is used

    :return: name of the data filename (without extension)
    """
    filename = f"schedule_{start_date}"
    if end_date:
        filename += f"_{end_date}"
    else:
        end_date = start_date

    url = BASE_URL + f"api/v1/schedule?startDate={start_date}&endDate={end_date}"

    await fetch_files([url], [filename], "schedule")

    return filename


async def get_teams_file() -> str:
    """Get high-level data of all teams.

    :return: name of the data filename (without extension)
    """
    url = BASE_URL + f"api/v1/teams"
    filename = "all_teams"

    await fetch_files([url], [filename], "schedule")

    return filename


async def get_schedule_team_rosters(filename: str) -> Tuple[list, dict]:
    """Get team roster data based on given schedule.

    NOTES
    -----
    Its not necessary to download team roster on every program run, only when roster changes are expected.

    :param filename: name of the schedule filename (without extension)

    :return: tuple with list of team roster filenames and list of schedule matches
    """
    # get schedule data
    schedule_file = FILES_DIR / "schedule" / (filename + ".json")
    with open(schedule_file, encoding="utf-8") as fh:
        data = json.load(fh)

    # store json data into FrozenJSON for easier attributes navigation
    json_navigator = FrozenJSON(data)

    # get list of URLs for requests and filenames for teams data
    number_of_games = json_navigator.dates[0].totalGames
    away_links = [BASE_URL + json_navigator.dates[0].games[i].teams.away.team.link + "/roster" for i in range(number_of_games)]
    away_names = [json_navigator.dates[0].games[i].teams.away.team.name + "_roster" for i in range(number_of_games)]
    home_links = [BASE_URL + json_navigator.dates[0].games[i].teams.home.team.link + "/roster" for i in range(number_of_games)]
    home_names = [json_navigator.dates[0].games[i].teams.home.team.name + "_roster" for i in range(number_of_games)]

    urls = home_links + away_links
    filenames = home_names + away_names
    await fetch_files(urls, filenames, "team_roster")

    filenames = [file.lower() for file in filenames]
    matches = {f"Match ({index})": [teams[0].replace("_roster", ""), teams[1].replace("_roster", "")]
               for index, teams in enumerate(zip(home_names, away_names))}

    return filenames, matches


def load_matches_from_schedule(filename: str) -> Tuple[list, dict]:
    """Prepare matches based on given schedule and team roster filenames for getting player stats in next steps.

    :param filename: name of the schedule filename (without extension)

    :return: tuple with list of team roster filenames and list of schedule matches
    """
    schedule_file = FILES_DIR / "schedule" / (filename + ".json")
    with open(schedule_file, encoding="utf-8") as fh:
        data = json.load(fh)

    json_navigator = FrozenJSON(data)

    number_of_games = json_navigator.dates[0].totalGames
    home_teams = [json_navigator.dates[0].games[i].teams.home.team.name for i in range(number_of_games)]
    away_teams = [json_navigator.dates[0].games[i].teams.away.team.name for i in range(number_of_games)]
    teams = home_teams + away_teams

    matches = {f"Match ({index})": [teams[0], teams[1]]
               for index, teams in enumerate(zip(home_teams, away_teams), start=1)}
    filenames = [file.lower() + "_roster" for file in teams]

    return filenames, matches


async def get_all_players_bio(filenames: list) -> List[str]:
    """Get player stats data for list of teams.

    :param filenames: list of team roster filenames (without extension)

    :return: list of player stats filenames
    """
    # prepare lists for storing player URLs & names
    player_links = []
    player_names = []

    # loop through all team rosters
    for file in filenames:
        player_file = FILES_DIR / "team_roster" / (file + ".json")
        with open(player_file, encoding="utf-8") as fh:
            data = json.load(fh)

        json_navigator = FrozenJSON(data)

        links = [BASE_URL + json_navigator.roster[i].person.link for i in
                 range(len(json_navigator.roster))]
        names = [json_navigator.roster[i].person.fullName for i in range(len(json_navigator.roster))]
        player_links += links
        player_names += names

    player_filenames = [name for name in player_names]

    await fetch_files(player_links, player_filenames, "players")

    return player_filenames


async def get_all_team_rosters(filename: str) -> List[str]:
    """Get team roster data for all teams.

    NOTES
    -----
    This function can be used, when we need to get data for all teams and not considering a certain schedule.

    :param filename: name of the filename with all teams data (without extension)

    :return: list of team roster filenames
    """
    filenames, json_navigator = load_all_team_rosters(filename)

    number_of_teams = len(json_navigator.teams)
    urls = [BASE_URL + json_navigator.teams[i].link + "/roster" for i in range(number_of_teams)]

    await fetch_files(urls, filenames, "team_roster")
    filenames = [file.lower() for file in filenames]

    return filenames


def load_all_team_rosters(filename: str) -> Tuple[List[str], FrozenJSON]:
    """Prepare team roster filenames for all teams.

    :param filename: name of the filename with all teams data (without extension)

    :return: list of team roster filenames
    """
    schedule_file = FILES_DIR / "schedule" / (filename + ".json")
    with open(schedule_file, encoding="utf-8") as fh:
        data = json.load(fh)

    json_navigator = FrozenJSON(data)

    number_of_teams = len(json_navigator.teams)
    filenames = [str(json_navigator.teams[i].name + "_roster").lower() for i in range(number_of_teams)]

    filenames = [file.lower() for file in filenames]

    return filenames, json_navigator


async def get_player_stats(filenames: list) -> List[str]:
    """Get player stats data for list of teams.

    :param filenames: list of team roster filenames (without extension)

    :return: list of player stats filenames
    """
    # prepare lists for storing player URLs & names
    player_links = []
    player_names = []

    # loop through all team rosters
    for file in filenames:
        player_file = FILES_DIR / "team_roster" / (file + ".json")
        with open(player_file, encoding="utf-8") as fh:
            data = json.load(fh)

        json_navigator = FrozenJSON(data)

        links = [BASE_URL + json_navigator.roster[i].person.link + "/stats?stats=gameLog"
                 for i in range(len(json_navigator.roster)) if json_navigator.roster[i].position.name != "Goalie"]
        names = [json_navigator.roster[i].person.fullName + f"_{json_navigator.roster[i].person.id}"
                 for i in range(len(json_navigator.roster)) if json_navigator.roster[i].position.name != "Goalie"]
        player_links += links
        player_names += names

    player_filenames = [name + "_stats" for name in player_names]

    await fetch_files(player_links, player_filenames, "player_stats")

    return player_filenames


def load_player_stats_into_dataframe(filename: str) -> pd.DataFrame:
    """Load player stats data from JSON into Dataframe.

    :param filename: player stats filename (without extension)

    :return: Dataframe with player stats data
    """
    filepath = Path().cwd() / "files" / "player_stats" / (filename + ".json")
    with open(filepath, encoding="utf-8") as fh:
        data = json.load(fh)

    json_navig = FrozenJSON(data)

    # get player name from filename
    player_name = re.search(r"^(\D+)_", filename)[1]

    # {"team": json_navig.stats[0].splits[0].team.name} => splits[0] index should ensure, that current team name for
    # player will be picked up (this can happen in case of trades during the season)
    stats = [{"name": player_name} | {"team": json_navig.stats[0].splits[0].team.name} |
             {"opponent": json_navig.stats[0].splits[i].opponent.name} |
             {"match_date": json_navig.stats[0].splits[i].date} |
             data["stats"][0]["splits"][i]["stat"]
             for i in range(len(json_navig.stats[0].splits))]

    df = pd.DataFrame(stats)

    return df
