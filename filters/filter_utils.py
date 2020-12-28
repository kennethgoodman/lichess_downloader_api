def AND(*filters):
	return lambda game: all(
		f(game) for f in filters
	)

def OR(*filters):
	return lambda game: any(
		f(game) for f in filters
	)