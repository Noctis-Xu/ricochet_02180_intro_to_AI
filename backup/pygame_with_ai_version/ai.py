import consts


def play(state):
    print("AI is thinking...")
    board = state["board"]
    robots = state["robots"]
    target = state["target"]  # (target color, (x, y))
    print(board)
    print(robots)
    print(target)
    path = [
        (consts.RED, consts.RIGHT),
        (consts.GREEN, consts.UP),
        (consts.BLUE, consts.UP),
        (consts.YELLOW, consts.UP)
    ]
    return path
