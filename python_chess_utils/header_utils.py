import chess.pgn

from models.time_control import TimeControl

DEFAULT_ELO_RATING = 1500


def get_result(game: chess.pgn.Game) -> str:
    return game.headers["Result"]


def _get_elo(game: chess.pgn.Game, key: str) -> int:
    elo = game.headers.get(key)
    if elo == "?" or elo is None:
        return DEFAULT_ELO_RATING
    return int(elo)


def get_white_elo(game: chess.pgn.Game) -> int:
    return _get_elo(game, "WhiteElo")


def get_black_elo(game: chess.pgn.Game) -> int:
    return _get_elo(game, "BlackElo")


def get_avg_rating(game: chess.pgn.Game) -> float:
    return (get_white_elo(game) + get_black_elo(game)) / 2.0


def get_time_control(game: chess.pgn.Game) -> TimeControl:
    return TimeControl(
        time_control_header=game.headers["TimeControl"]
    )


def get_game_id(game: chess.pgn.Game) -> str:
    return game.headers.get('Site').replace('"', '').replace('https://lichess.org/', '')