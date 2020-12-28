import logging.config
import os

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
        },
        'loggers': {
            '': {
                'handlers': ['default_handler'],
                'level': 'DEBUG',
                'propagate': False
            }
        }
    }
    logging.config.dictConfig(logging_config)


if __name__ == '__main__':
    init_logger()
    year: int = 2014
    month: int = 1
    data_manager = Manager(year, month)
    games = get_n_games_with_filter(data_manager, num_games_needed=500, filter_f=f.OR(
            f.AND(
                # 2700+ with any time control
                gf.get_filter_by_avg_rating(min_rating=2700),
            ),
            f.AND(
                # 2500+ with > 5+0 or > 3+2
                gf.get_filter_by_avg_rating(min_rating=2500),
                f.OR(
                    gf.get_filter_by_time_control(min_time=5 * 60),
                    gf.get_filter_by_time_control(min_time=3 * 60, min_increment=2)
                )
            ),
            f.AND(
                # 2100+ with > 10+0 or > 5+3
                gf.get_filter_by_avg_rating(min_rating=2100),
                f.OR(
                    gf.get_filter_by_time_control(min_time=10 * 60),
                    gf.get_filter_by_time_control(min_time=5 * 60, min_increment=3)
                )
            ),
            f.AND(
                # 1950+ with > 15+0 or > 10+2
                gf.get_filter_by_avg_rating(min_rating=1950),
                f.OR(
                    gf.get_filter_by_time_control(min_time=15 * 60),
                    gf.get_filter_by_time_control(min_time=10 * 60, min_increment=2)
                )
            )
          )
    )
