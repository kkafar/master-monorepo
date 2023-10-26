import os

RT_LOCAL = 'local'
RT_ARES = 'ares'
RT_UNKNOWN = 'unknown'


def get_runtime_name() -> str:
    """ Hacky way to detect whether we are running on Ares or not """
    username = os.getenv('USER', None)
    if username is None:
        return RT_UNKNOWN
    elif username.startswith('plg'):
        return RT_ARES
    else:
        return RT_LOCAL


def is_running_on_ares() -> bool:
    return get_runtime_name() == RT_ARES

