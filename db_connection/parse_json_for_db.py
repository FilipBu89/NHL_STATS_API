from typing import List, Tuple, Any, Union
import json
from pathlib import Path
from utils import FILES_DIR, FrozenJSON
import re


def parse_teams_insert(filename: str) -> List[Tuple[Any, ...]]:
    # get teams file
    teams_file = FILES_DIR / "schedule" / (filename + ".json")
    with open(teams_file, encoding="utf-8") as fh:
        data = json.load(fh)

    # store json data into FrozenJSON for easier attributes navigation
    json_navigator = FrozenJSON(data)

    insert_records = [(team.id, team.name, team.abbreviation, team.division.name, team.conference.name)
                      for team in json_navigator.teams]

    return insert_records


def parse_player_insert(file: Path) -> Tuple[Any, ...]:
    # get teams file
    with open(file, encoding="utf-8") as fh:
        data = json.load(fh)

    # store json data into FrozenJSON for easier attributes navigation
    json_navigator = FrozenJSON(data)

    people = json_navigator.people[0]
    current_team = people.currentTeam
    position = people.primaryPosition

    insert_records = (current_team.id, people.id, people.firstName, people.lastName, people.birthDate, people.nationality,
                      people.captain, people.alternateCaptain, position.name, position.type)

    return insert_records


def parse_player_stats_insert(file: Path) -> Tuple[List[str], List[Tuple[Any, ...]]]:
    def format_attribute(name: str) -> str:
        new = ""
        for letter in name:
            if str(letter).isupper():
                new += f"_{letter.lower()}"
            else:
                new += letter
        return new

    # get teams file
    with open(file, encoding="utf-8") as fh:
        data = json.load(fh)

    # store json data into FrozenJSON for easier attributes navigation
    json_navigator = FrozenJSON(data)

    splits: List[dict] = json_navigator.stats[0].splits
    my_dict: dict

    # insert_command: str = "INSERT INTO player_stats({})\nVALUES(%s{})"
    insert_command: str = "INSERT INTO player_stats({})\nVALUES({})"

    # get player api id name from filename

    player_api_id: str = re.search(r"(?=_*)\d+(?=)", file.name).group(0)
    insert_records_dict = [{
                            "season": splits[i].season,
                            "player_api_id": int(player_api_id),
                            "team_api_id": splits[i].team.id,
                            "opponent_api_id": splits[i].opponent.id
                           } |
                           {format_attribute(key): splits[i].stat.get(key) for key in splits[i].stat.keys()} |
                           {
                            "match_date": splits[i].date,
                            "is_home": splits[i].isHome,
                            "is_win": splits[i].isWin,
                            "is_ot": splits[i].isOT
                           }
                           for i in range(len(splits))]

    insert_records_statements = [
        # insert_command.format(", ".join(key for key in record_dict), ", %s" * (len(record_dict) - 1))
        insert_command.format(", ".join(key for key in record_dict),
                              ", ".join(f"${i}" for i in list(range(1, len(record_dict) + 1))))
        for record_dict in insert_records_dict
    ]

    insert_records_values = [
        tuple(record_dict.values()) for record_dict in insert_records_dict
    ]

    return insert_records_statements, insert_records_values
