from typing import Callable
import logging

from python_chess_utils.header_utils import get_game_id
from lichess_parser.lichess_parser import parse_file_gen
from data_manager.manager import Manager
from models.games import Games

logger = logging.getLogger(__name__)


def get_n_games_with_filter(manager: Manager, num_games_needed: int, filter_f: Callable):
    filtered_games = Games()
    num_errors, num_games = 0, 0
    with manager as fl:
        for i, game in enumerate(parse_file_gen(fl)):
            if len(game.errors) > 0:
                num_errors += 1
                logger.warning(f"could not parse, had error, so far {num_errors} errors: {game.headers.get('Site')}")
            if num_games == num_games_needed:
                break
            if filter_f(game):
                filtered_games.add_game(game)
                num_games += 1
            if i % 1000 == 0 and i != 0:
                logger.info(f"at game {i}, filtered {len(filtered_games)} "
                            f"({round(100 * len(filtered_games) / (i + 1), 2)}%) games successfully")
    return filtered_games


def get_n_games_with_filter_gen(manager: Manager, num_games_needed: int, filter_f: Callable):
    num_errors, num_filtered_games = 0, 0
    with manager as fl:
        for i, game in enumerate(parse_file_gen(fl)):
            if len(game.errors) > 0:
                num_errors += 1
                logger.warning(f"could not parse, had error, so far {num_errors} errors: {game.headers.get('Site')}")
            if num_filtered_games == num_games_needed:
                break
            if filter_f(game):
                yield get_game_id(game), game
                num_filtered_games += 1
            if i % 1000 == 0 and i != 0:
                logger.info(f"at game {i}, filtered {num_filtered_games} "
                            f"({round(100 * num_filtered_games / (i + 1), 2)}%) games successfully")
