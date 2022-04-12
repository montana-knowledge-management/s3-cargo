__all__ = ("green", "red", "warning", "bold", "underline", "success", "fail")


def green(str_):
    return f"\033[92m{str_}\033[0m"


def red(str_):
    return f"\033[91m{str_}\033[0m"


def warning(str_):
    return f"\033[93m{str_}\033[0m"


def bold(str_):
    return f"\033[1m{str_}\033[0m"


def underline(str_):
    return f"\033[4m{str_}\033[0m"


def success(str_):
    return green(bold(str_))


def fail(str_):
    return red(bold(str_))
