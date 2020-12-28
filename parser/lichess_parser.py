import io
import logging

import chess.pgn

logger = logging.getLogger(__name__)


def parse_headers(line):
    line = line.replace("[", "").replace("]", "").replace('"', '').strip()
    key_value_splitter = line.find(" ")
    key = line[:key_value_splitter]
    value = line[key_value_splitter + 1:].strip()
    return key, value


def parse_game(lines):
    headers = {}
    for line in lines[:-1]:  # all but last line
        if "1. " in line:
            logger.error(f"got 1. in {lines}")
            raise ValueError(f"got 1. in {lines}")
        k, v = parse_headers(line)
        headers[k] = v
    game = chess.pgn.read_game(io.StringIO(''.join(lines[-1])))
    for k in ['0-']:
        if k in headers:
            del headers[k]
    try:
        game.headers.update(headers)
    except ValueError as ve:
        logger.error(f"had error for headers: {headers} updating {game.headers}, {ve}")
        raise ve
    return game


def parse_file_gen(lines):
    # TODO: can chess.pgn read multiple games, if yes switch to that
    lines_so_far = []
    for line in lines:
        line = line.strip()
        if line != "":
            lines_so_far.append(line)
        if "1. " in line:
            game = parse_game(lines_so_far)
            yield game
            lines_so_far = []
        elif line.strip() in ["0-1", "1-0", "1/2-1/2"]:
            game = parse_game(lines_so_far)
            yield game
            lines_so_far = []
        elif len(lines_so_far) > 30:
            print(lines_so_far)
            raise ValueError("are you sure there are this many lines?")
    if len(lines_so_far):  # the last game
        game = parse_game(lines_so_far)
        yield game
