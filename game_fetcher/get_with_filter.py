from typing import Callable
import logging

from parser.lichess_parser import parse_file_gen
from data_manager.manager import Manager


logger = logging.getLogger(__name__)


def get_n_games_with_filter(manager: Manager, num_games_needed: int, filter_f: Callable):
    filtered_games = []
    num_errors, num_games = 0, 0
    with manager as fl:
        for i, game in enumerate(parse_file_gen(fl)):
            if len(game.errors) > 0:
                num_errors += 1
                logger.warning(f"could not parse, had error, so far {num_errors} errors: {game.headers.get('Site')}")
            if num_games == num_games_needed:
                break
            if filter_f(game):
                filtered_games.append(game)
                num_games += 1
            if i % 1000 == 0 and i != 0:
                logger.info(f"at game {i}, filtered {len(filtered_games)} "
                            f"({round(100 * len(filtered_games) / (i + 1), 2)}%) games successfully")
    return filtered_games
