from collections import Counter

import chess.pgn

from python_chess_utils.header_utils import get_time_control, get_avg_rating


class GameStats:
    def __init__(self):
        self.total_games = 0
        self.time_control: Counter = Counter()
        self.avg_rating_bucketed: Counter = Counter()

    def _add_remove_game(self, game: chess.pgn.Game, direction: int):
        self.total_games += direction
        self.time_control[get_time_control(game)] += direction
        self.avg_rating_bucketed[
            round(get_avg_rating(game), -2)  # to the 100's place
        ] += direction

    def add_game(self, game: chess.pgn.Game) -> None:
        self._add_remove_game(game, 1)

    def delete_game(self, game: chess.pgn.Game) -> None:
        self._add_remove_game(game, -1)

    def __repr__(self) -> str:
        return f"Total Games: {self.total_games}\n" \
               f"Time Control: {self.time_control.most_common(10)}\n" \
               f"Rating Bucket: {self.avg_rating_bucketed.most_common(15)}"
