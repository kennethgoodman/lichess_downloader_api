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


def parse_game_get_total_time(lines):
    # TODO: add check for run out of time
    # TODO: check rated game
    headers = {}
    for line in lines[:-1]:  # all but last line
        if "1. " in line:
            logger.error(f"got 1. in {lines}")
            raise ValueError(f"got 1. in {lines}")
        k, v = parse_headers(line)
        v2 = ' '.join(v.split(" ")[:3])
        if k == "Event" and v2 not in [
                                        'Rated UltraBullet game', "Rated Bullet game",
                                        "Rated Blitz game", "Rated Rapid game",
                                        "Rated Classical game",
                                        'Rated UltraBullet tournament', "Rated Bullet tournament",
                                        "Rated Blitz tournament", "Rated Rapid tournament",
                                        "Rated Classical tournament",
                                      ]:
            logger.info(f"Event not correct: {v}, {v2}")
            return "Event not correct"
        if 'tournament' in v:
            headers[k] = v2
            headers['tournamentLink'] = v.split(" ")[3]
        else:
            headers[k] = v
    termination = headers.get('Termination', None)
    if termination == 'Abandoned':
        logger.info(f"skipping because abandoned")
        return "skipping because abandoned"
    elif termination is None:
        logger.info(f"skipping because bad termination: headers={headers}")
        return "skipping because bad termination"
    elif termination == "Rules infraction":
        logger.info(f"skipping because cheating")
        return "skipping because cheating"
    elif headers["Termination"] not in ["Normal", "Time forfeit"]:
        logger.info(f"termination not in normal, time forfeit: {headers['Termination']}, headers={headers}")
        return "termination not in normal, time forfeit"
    elif 'TimeControl' not in headers:
        logger.info(f"skipping because no time control")
        return "skipping because no time control"
    elif '+' not in headers['TimeControl']:
        logger.info(f"skipping because no + in time control")
        return "skipping because no + in time control"
    elif lines[-1] in ["0-1", "1-0"]:
        logger.info(f"skipping because no moves played")
        return "skipping because no moves played"
    last_line = lines[-1]
    rindex = last_line.rindex("[")
    bracket_close = last_line.index("]", rindex)
    time = last_line[rindex + 1:bracket_close].replace("%clk ", "")
    move_number_dot = last_line.rindex(". ", 0, rindex - 1)
    black_last_move = False
    move_number_end = move_number_dot
    if last_line[move_number_dot - 1] == ".":
        move_number_end = move_number_dot - 2
        black_last_move = True
    move_number_start = last_line.rfind(" ", 0, move_number_end)
    if move_number_start == -1:
        # one move game
        logger.info(f"skipping because one move game: headers={headers}")
        return "skipping because one move game"
    move_num = int(last_line[move_number_start:move_number_end])

    rindex2 = last_line.rindex("[", 0, move_number_start - 1)
    bracket_close = last_line.index("]", rindex2)
    time2 = last_line[rindex2 + 1:bracket_close].replace("%clk ", "")
    if headers['Termination'] == "Time forfeit":
        time2 = '0:0:0'
    if black_last_move:
        move_num2 = move_num
    else:
        move_num2 = move_num - 1

    def time_elapsed(total, move_num, increment, t):
        increment = increment or 0
        hours, minutes, seconds = t.split(":")
        # TODO: filter if negative here
        # TODO: any way to check if a player gave another player extra time?
        return int(total) - int(hours) * 60 * 60 - int(minutes) * 60 - int(seconds) + move_num * int(increment)

    total_time, increment = headers['TimeControl'].split("+")
    rtn = {
        "total_time": time_elapsed(total_time, move_num, increment, time) +
                      time_elapsed(total_time, move_num2, increment, time2),
        "move_num": move_num,
        "move_num2": move_num2,
        "black_last_played": black_last_move
    }
    for key in ["Event", "Site", "WhiteElo", "BlackElo", "ECO", "Opening", "Termination", "TimeControl"]:
        rtn[key] = headers.get(key, None)
    return rtn


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


def parse_file_gen(lines, parse_game_callback=parse_game):
    # TODO: can chess.pgn read multiple games, if yes switch to that
    lines_so_far = []
    for line in lines:
        line = line.strip()
        if line != "":
            lines_so_far.append(line)
        if "1. " in line:
            game = parse_game_callback(lines_so_far)
            yield game
            lines_so_far = []
        elif line.strip() in ["0-1", "1-0", "1/2-1/2"]:
            game = parse_game_callback(lines_so_far)
            yield game
            lines_so_far = []
        elif len(lines_so_far) > 30:
            print(lines_so_far)
            raise ValueError("are you sure there are this many lines?")
    if len(lines_so_far):  # the last game
        game = parse_game_callback(lines_so_far)
        yield game
