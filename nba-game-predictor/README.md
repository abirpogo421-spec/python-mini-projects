# NBA Game Predictor

Predicts the winner of an NBA game using XGBoost. Each game is described by the difference between the home and away teams in:

- averages over their last 5 games
- season-to-date averages
- the four factors (effective FG%, turnover ratio, free throw rate, offensive rebound %)
- win percentage, days of rest and current win streak

Only games played before a matchup are used to build its features. Early-season games, which have no history yet, borrow each team's last 5 games from the previous season.

## Results

Trained on 2000-2019 and tested on the 2019-20 season through the 2023 Finals:

| Metric | Value |
| --- | --- |
| Accuracy | 62.3% |
| ROC AUC | 0.662 |
| Always picking the home team | 55.5% |

[`nba_predictor.ipynb`](nba_predictor.ipynb) has the full evaluation, feature importances and a simulation of the 2023 Finals.

## Usage

Interactive predictions for any matchup and date in the data:

```bash
python nba_predictor.py
```

```
Home team: LAL
Away team: BOS
Date (YYYY-MM-DD): 2023-01-15
LAL 35.9%  vs  BOS 64.1%  ->  predicted winner: BOS
```

## Data

`data/game.csv` is the `game` table from the [NBA Database](https://www.kaggle.com/datasets/wyattowalsh/basketball) on Kaggle, with box scores for every game since 1946.
