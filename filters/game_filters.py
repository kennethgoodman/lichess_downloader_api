def get_filter_by_result(result_wanted):
	return lambda game: game.props.get_prop("Result") == result_wanted

def get_filter_by_avg_rating(min_rating=0, max_rating=float('inf')):
	get_avg_rating = lambda game: (game.get_white_elo() + game.get_black_elo())/2.0
	return lambda game: min_rating <= get_avg_rating(game) <= max_rating

def get_filter_by_time_control(min_time=0, min_increment=0, max_time=float('inf'), max_increment=float('inf')):
	return lambda game: min_time <= game.get_time_control().base <= max_time and (
		min_increment <= game.get_time_control().increment <= max_increment if game.get_time_control().increment is not None else True
	)