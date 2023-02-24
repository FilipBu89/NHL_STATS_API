CREATE_TEAMS_TABLE_QUERY: str = """
DROP TABLE IF EXISTS teams CASCADE;
CREATE TABLE teams
(
    team_id SERIAL PRIMARY KEY,
    api_id INT UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    abbreviation CHAR(3) NOT NULL,
    division VARCHAR(255) NOT NULL,
    conference VARCHAR(255) NOT NULL
);
"""

INSERT_INTO_TEAMS_TABLE_QUERY: str = """
INSERT INTO teams(api_id, name, abbreviation, division, conference) VALUES(%s, %s, %s, %s, %s)
"""

INSERT_INTO_PLAYERS_TABLE_QUERY: str = """
INSERT INTO players(team_api_id, api_id, first_name, last_name, birth_date, nationality, is_captain, is_alternate_captain,
                  position_name, position_type) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

CREATE_PLAYERS_TABLE_QUERY: str = """
DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players
(
    player_id SERIAL PRIMARY KEY,
    team_api_id INT NOT NULL,
    api_id INT UNIQUE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    birth_date VARCHAR(255) NOT NULL,
    nationality VARCHAR(255) NOT NULL,
    is_captain BOOL NOT NULL,
    is_alternate_captain BOOL NOT NULL,
    position_name VARCHAR(255) NOT NULL,
    position_type VARCHAR(255) NOT NULL,
    CONSTRAINT fk_team
        FOREIGN KEY (team_api_id)
            REFERENCES teams(api_id)  
);
"""

INSERT_INTO_PLAYER_STATS_TABLE_QUERY: str = """
INSERT INTO player_stats(season, team_api_id, opponent_api_id, time_on_ice, assists, goals, pim, shots, games, hits,
power_play_goals, power_play_points, power_play_time_on_ice, even_time_on_ice, penalty_minutes, game_winning_goals, 
over_time_goals, short_handed_goals, short_handed_points, short_handed_time_on_ice, blocked, plus_minus, points, shifts, 
shot_percentage, face_off_percentage, match_date, is_home, is_win, is_ot) 
VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

CREATE_PLAYERS_STATS_TABLE_QUERY: str = """
DROP TABLE IF EXISTS player_stats CASCADE;
CREATE TABLE player_stats
(
    player_stats_id SERIAL PRIMARY KEY,
    season VARCHAR(8) NOT NULL,
    player_api_id INT NOT NULL,
    team_api_id INT NOT NULL,
    opponent_api_id INT NOT NULL,
    time_on_ice VARCHAR(5) NOT NULL,
    assists INT NOT NULL,
    goals SMALLINT NOT NULL,
    pim SMALLINT NOT NULL,
    shots SMALLINT NOT NULL,
    games SMALLINT NOT NULL,
    hits SMALLINT NOT NULL,
    power_play_goals SMALLINT NOT NULL,
    power_play_points SMALLINT NOT NULL,
    power_play_time_on_ice VARCHAR(5) NOT NULL,
    even_time_on_ice VARCHAR(5) NOT NULL,
    penalty_minutes VARCHAR(5) NOT NULL,
    shot_pct FLOAT,
    face_off_pct FLOAT,
    game_winning_goals SMALLINT NOT NULL,
    over_time_goals SMALLINT NOT NULL,
    short_handed_goals SMALLINT NOT NULL,
    short_handed_points SMALLINT NOT NULL,
    short_handed_time_on_ice VARCHAR(5) NOT NULL,
    blocked SMALLINT NOT NULL,
    plus_minus INT NOT NULL,
    points SMALLINT NOT NULL,
    shifts SMALLINT NOT NULL,
    match_date VARCHAR(10) NOT NULL,
    is_home BOOL NOT NULL,
    is_win BOOL NOT NULL,
    is_ot BOOL NOT NULL,
    CONSTRAINT fk_team
        FOREIGN KEY (team_api_id)
            REFERENCES teams(api_id),
    CONSTRAINT fk_opponent
        FOREIGN KEY (opponent_api_id)
            REFERENCES teams(api_id)
);
"""