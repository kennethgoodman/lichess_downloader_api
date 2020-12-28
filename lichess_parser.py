import chess.pgn
import io


def parse_game(lines):
    return chess.pgn.read_game(io.StringIO(''.join(lines)))


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
        else:
            lines_so_far.append(line)

        if len(lines_so_far) > 30:
            print(lines_so_far)
            raise ValueError("are you sure there are this many lines?")
