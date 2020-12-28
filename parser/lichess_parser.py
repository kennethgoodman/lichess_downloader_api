import chess.pgn
import io


def parse_headers(line):
    line = line.replace("[", "").replace("]", "").replace('"', '').strip()
    key_value_splitter = line.find(" ")
    key = line[:key_value_splitter]
    value = line[key_value_splitter + 1:].strip()
    return key, value


def parse_game(lines):
    headers = {}
    for line in lines[:-1]: # all but last line
        k, v = parse_headers(line)
        headers[k] = v
    game = chess.pgn.read_game(io.StringIO(''.join(lines[-1])))
    game.headers.update(headers)
    return game


def parse_file_gen(lines):
    # TODO: chess.pgn can read multiple games, switch to that
    lines_so_far = []
    for line in lines:
        line = line.strip()
        if line[:6] == "[Event":
            if len(lines_so_far):
                game = parse_game(lines_so_far)
                yield game
                lines_so_far = []
        elif line != "":
            lines_so_far.append(line)

        if len(lines_so_far) > 30:
            print(lines_so_far)
            raise ValueError("are you sure there are this many lines?")
    if len(lines_so_far):  # the last game
        game = parse_game(lines_so_far)
        yield game
