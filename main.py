import logging.config
import os
import pickle
import pandas as pd

import filters.filter_utils as f
import filters.game_filters as gf
from data_manager.manager import Manager
from game_fetcher.get_with_filter import get_n_games_with_filter


def init_logger():
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default_handler': {
                'class': 'logging.FileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': os.path.join('logs', 'application.log'),
                'encoding': 'utf8'
            },
            'default_stdout': {
                'level': 'DEBUG',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stdout',  # Default is stderr
            },
        },
        'loggers': {
            '': {
                'handlers': ['default_handler', 'default_stdout'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)

def main():
    year: int = 2014
    month: int = 1
    data_manager = Manager(year, month)
    games = get_n_games_with_filter(data_manager, num_games_needed=5, filter_f=f.OR(
            f.AND(
                # 2400+ with any time control
                gf.get_filter_by_avg_rating(min_rating=2400),
            ),
            f.AND(
                # 2100+ with > 5+0 or > 3+2
                gf.get_filter_by_avg_rating(min_rating=2100),
                f.OR(
                    gf.get_filter_by_time_control(min_time=5 * 60),
                    gf.get_filter_by_time_control(min_time=3 * 60, min_increment=2)
                )
            ),
            f.AND(
                # 1950+ with > 10+0 or > 8+2
                gf.get_filter_by_avg_rating(min_rating=1950),
                f.OR(
                    gf.get_filter_by_time_control(min_time=10 * 60),
                    gf.get_filter_by_time_control(min_time=8 * 60, min_increment=2)
                )
            )
        )
    )
    print(games)


def main2():
    from data_manager.download_data_utils import inc_download_and_unzip
    from lichess_parser.lichess_parser import parse_file_gen, parse_game_get_total_time
    year: int = 2021
    month: int = 3
    prev = []
    new_games = []
    total_games = 0
    from collections import Counter
    error_counter = Counter()
    with open(f'data/lichess.games.{year}.{month}.dict', 'wb') as f:
        for games in inc_download_and_unzip(year, month, save_file=False):
            games = games.decode().split("\n")
            for i in range(len(games) - 1, 0, -1):
                if games[i] == "":
                    new_games = prev + games[:i]
                    prev = games[i:]
                    break
            for i, game in enumerate(parse_file_gen(new_games, parse_game_get_total_time)):
                if isinstance(game, str):
                    error_counter[game] += 1
                    continue
                total_games += 1
                pickle.dump(game, f)
                if total_games % 100 == 0:
                    print(total_games, error_counter)
                if total_games % 1000000 == 0:
                    return


def main3():
    year: int = 2021
    month: int = 3
    datas = []
    with open(f'data/lichess.games.{year}.{month}.dict', 'rb') as f:
        while True:
            try:
                datas.append(pickle.load(f))
            except EOFError:
                break
    df = pd.DataFrame(list(filter(None, datas)))
    print(df.describe())
    df.to_csv(f"data/{year}.{month}.df.csv", index=False)
    # print(data[0])

if __name__ == '__main__':
    init_logger()
    main3()
