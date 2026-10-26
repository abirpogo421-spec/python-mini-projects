import random
from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBClassifier

DATA_PATH = Path(__file__).parent / "data" / "game.csv"

STATS = [
    "pts", "fg_pct", "fg3_pct", "ft_pct", "reb", "ast", "stl", "blk", "tov", "pf",
    "efg_pct", "tov_ratio", "fta_rate", "oreb_pct",
]
BASE_STATS = STATS + ["win_pct"]
KINDS = ["rolling", "season_avg"]
WINDOW = 5


def load_games(path=DATA_PATH, start="2000-10-31", end="2023-06-12"):
    df = pd.read_csv(path, dtype={"season_id": str, "game_id": str})
    df["game_date"] = pd.to_datetime(df["game_date"], errors="coerce")
    df = df[df["game_date"].between(start, end)].copy()

    # four factors
    for side, other in (("home", "away"), ("away", "home")):
        fga, fta, tov = df[f"fga_{side}"], df[f"fta_{side}"], df[f"tov_{side}"]
        df[f"efg_pct_{side}"] = (df[f"fgm_{side}"] + 0.5 * df[f"fg3m_{side}"]) / fga
        df[f"tov_ratio_{side}"] = tov / (fga + 0.44 * fta + tov)
        df[f"fta_rate_{side}"] = fta / fga
        df[f"oreb_pct_{side}"] = df[f"oreb_{side}"] / (df[f"oreb_{side}"] + df[f"dreb_{other}"])
    return df


def to_team_games(df):
    """One row per team per game, sorted by team and date."""
    rows = []
    for side, other in (("home", "away"), ("away", "home")):
        part = df[["game_id", "game_date", "season_id"]].copy()
        part["team"] = df[f"team_abbreviation_{side}"]
        part["opponent"] = df[f"team_abbreviation_{other}"]
        part["is_home"] = int(side == "home")
        for stat in STATS:
            part[stat] = df[f"{stat}_{side}"]
        part["won"] = (df[f"pts_{side}"] > df[f"pts_{other}"]).astype(int)
        rows.append(part)
    return pd.concat(rows).sort_values(["team", "game_date"]).reset_index(drop=True)


def win_streak(wins):
    streak, out = 0, []
    for w in wins:
        out.append(streak)
        streak = streak + 1 if w else 0
    return out


def add_features(games):
    """Rolling and season-to-date averages using only games played before each row."""
    games = games.copy()
    games["win_pct"] = games["won"]
    by_team = games.groupby("team")
    by_season = games.groupby(["team", "season_id"])

    for stat in BASE_STATS:
        games[f"{stat}_rolling"] = by_team[stat].transform(
            lambda s: s.shift(1).rolling(WINDOW, min_periods=1).mean()
        )
        games[f"{stat}_season_avg"] = by_season[stat].transform(lambda s: s.shift(1).expanding().mean())

    # early-season games have no history yet, so borrow each team's last few games from the prior season
    feature_cols = [f"{s}_{k}" for s in BASE_STATS for k in KINDS]
    seasons = sorted(games["season_id"].unique())
    for prev, curr in zip(seasons, seasons[1:]):
        prev_games = games[games["season_id"] == prev]
        for team, idx in games[games["season_id"] == curr].groupby("team").groups.items():
            tail = prev_games[prev_games["team"] == team].tail(WINDOW)
            if tail.empty:
                continue
            first = idx[:WINDOW]
            games.loc[first, feature_cols] = games.loc[first, feature_cols].fillna(tail[feature_cols].mean())

    games["rest_days"] = by_team["game_date"].diff().dt.days.fillna(0)
    games["win_streak"] = by_team["won"].transform(win_streak)
    return games


def feature_names():
    return [f"{s}_{k}_diff" for s in BASE_STATS for k in KINDS] + ["rest_days_diff", "win_streak_diff"]


def matchup_features(home, away):
    """Home-minus-away differences for two team rows (Series or aligned DataFrames)."""
    out = {}
    for s in BASE_STATS:
        for k in KINDS:
            out[f"{s}_{k}_diff"] = home[f"{s}_{k}"] - away[f"{s}_{k}"]
    out["rest_days_diff"] = home["rest_days"] - away["rest_days"]
    out["win_streak_diff"] = home["win_streak"] - away["win_streak"]
    return out


def build_training_table(games):
    home = games[games["is_home"] == 1].set_index("game_id")
    away = games[games["is_home"] == 0].set_index("game_id")
    home, away = home.align(away, join="inner", axis=0)

    X = pd.DataFrame(matchup_features(home, away))[feature_names()].astype(float)
    y = home["won"]
    meta = pd.DataFrame({"game_date": home["game_date"], "home": home["team"], "away": away["team"]})

    keep = X.notna().all(axis=1)
    return X[keep], y[keep], meta[keep]


def train_model(X, y):
    model = XGBClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.9,
        colsample_bytree=0.9,
        eval_metric="logloss",
        tree_method="hist",
        random_state=42,
    )
    model.fit(X, y)
    return model


def latest_row(games, team, date):
    played = games[(games["team"] == team) & (games["game_date"] <= date)]
    return None if played.empty else played.iloc[-1]


def home_win_probability(model, games, home, away, date):
    h, a = latest_row(games, home, date), latest_row(games, away, date)
    if h is None or a is None:
        raise ValueError(f"No games for {home} or {away} before {date:%Y-%m-%d}")
    X = pd.DataFrame([matchup_features(h, a)])[feature_names()].astype(float).fillna(0.0)
    return float(model.predict_proba(X)[0, 1])


def simulate_series(model, games, team_a, team_b, start_date, seed=None):
    """Best-of-7 with 2-2-1-1-1 home court, team_a holding the advantage."""
    rng = random.Random(seed)
    hosts = [team_a, team_a, team_b, team_b, team_a, team_b, team_a]
    wins = {team_a: 0, team_b: 0}
    date = pd.Timestamp(start_date)

    for host in hosts:
        if max(wins.values()) == 4:
            break
        guest = team_b if host == team_a else team_a
        p = home_win_probability(model, games, host, guest, date)
        wins[host if rng.random() < p else guest] += 1
        date += pd.Timedelta(days=2)

    return max(wins, key=wins.get), wins


def main():
    print("Loading games and training model...")
    games = add_features(to_team_games(load_games()))
    X, y, _ = build_training_table(games)
    model = train_model(X, y)

    teams = sorted(games["team"].unique())
    first, last = games["game_date"].min(), games["game_date"].max()
    print(f"Data covers {first:%Y-%m-%d} to {last:%Y-%m-%d}. Type LIST to see team abbreviations.")

    while True:
        home = input("\nHome team: ").strip().upper()
        if home == "LIST":
            print(", ".join(teams))
            continue
        away = input("Away team: ").strip().upper()
        date = pd.to_datetime(input("Date (YYYY-MM-DD): ").strip(), errors="coerce")

        if home not in teams or away not in teams or home == away:
            print("Invalid team abbreviation.")
        elif pd.isna(date) or not first <= date <= last:
            print("Invalid or out-of-range date.")
        else:
            p = home_win_probability(model, games, home, away, date)
            winner = home if p >= 0.5 else away
            print(f"{home} {p:.1%}  vs  {away} {1 - p:.1%}  ->  predicted winner: {winner}")

        if input("Another prediction? (y/n): ").strip().lower() != "y":
            break


if __name__ == "__main__":
    main()
