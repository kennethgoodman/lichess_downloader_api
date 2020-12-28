from python_chess_utils.header_utils import get_avg_rating, get_time_control, get_result


def get_filter_by_result(result_wanted: str):
	return lambda game: get_result(game) == result_wanted


def get_filter_by_avg_rating(min_rating=0, max_rating=float('inf')):
	return lambda game: min_rating <= get_avg_rating(game) <= max_rating


def get_filter_by_time_control(min_time=0, min_increment=0, max_time=float('inf'), max_increment=float('inf')):
	return lambda game: get_time_control(game).in_between(
		min_time=min_time,
		min_increment=min_increment,
		max_time=max_time,
		max_increment=max_increment
	)