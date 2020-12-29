import chess.pgn

from models.game_stats import GameStats
from python_chess_utils.header_utils import get_game_id, get_white_elo, get_black_elo, get_time_control


class Games:
    _num_game_limit: int = 15

    def __init__(self):
        self.games = {}
        self.game_stats = GameStats()

    def add_game(self, game: chess.pgn.Game):
        self.game_stats.add_game(game)
        self.games[get_game_id(game)] = game

    def __repr__(self) -> str:
        def _repr_game(game: chess.pgn.Game) -> str:
            return f"{game.headers['White']} ({get_white_elo(game)}) v " \
                   f"{game.headers['Black']} ({get_black_elo(game)}) - " \
                   f"{get_time_control(game)}"
        games_to_repr: list = []
        for i, (game_id, game) in enumerate(self.games.items()):
            if i == self._num_game_limit:
                break
            games_to_repr.append(f'{game_id}: {_repr_game(game)}')
        nl = '\n'
        return f'Stats: {repr(self.game_stats)}\npreview of {self._num_game_limit} games:\n' \
               f'{nl.join(games_to_repr)}'

    def __len__(self) -> int:
        return len(self.games)

    def __setitem__(self, _, __):
        raise NotImplementedError("not implemented because there is add_Game that will handle the key")

    def __getitem__(self, game_id: str) -> chess.pgn.Game:
        return self.games[game_id]

    def __delitem__(self, game_id: str) -> None:
        self.game_stats.delete_game(self.games[game_id])
        del self.games[game_id]

    def __iter__(self):
        return iter(self.games)
