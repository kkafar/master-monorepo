from dataclasses import dataclass


@dataclass
class InstanceMetadata:
    id: str
    ref: str
    jobs: int
    machines: int
    lower_bound: int
    best_known_solution: int


EventName = str


@dataclass
class EventConfig:
    name: EventName
    record_schema: list[str]
    raw_columns: list[int]


class Event:
    NEW_BEST = 'newbest'
    BEST_IN_GEN = 'bestingen'
    DIVERSITY = 'diversity'
    POP_GEN_TIME = 'popgentime'
    ITER_INFO = 'iterinfo'

    ALL_EVENTS = [
        NEW_BEST,
        BEST_IN_GEN,
        DIVERSITY,
        POP_GEN_TIME,
        ITER_INFO,
    ]


class Col:
    EVENT = 'event'
    GENERATION = 'gen'
    TIME = 'time'
    FITNESS = 'fitness'
    POP_SIZE = 'popsize'
    DIVERSITY = 'diversity'
    EVAL_TIME = 'eval_time'
    SEL_TIME = 'sel_time'
    CROSS_TIME = 'cross_time'
    MUT_TIME = 'mut_time'
    REPL_TIME = 'repl_time'
    ITER_TIME = 'iter_time'
    SID = 'sid'

    ALL_COLLS = [
        EVENT,
        GENERATION,
        TIME,
        FITNESS,
        POP_SIZE,
        DIVERSITY,
        EVAL_TIME,
        SEL_TIME,
        CROSS_TIME,
        MUT_TIME,
        REPL_TIME,
        ITER_TIME,
        SID,
    ]


EVENT_COL_INDEX = 0
SID_COL_INDEX = -1


# We append series_id column which is not present in original result
SCHEMA_FOR_EVENT = dict(map(lambda kv: (kv[0], [Col.EVENT] + kv[1] + [Col.SID]), [
    (Event.NEW_BEST, [Col.GENERATION, Col.TIME, Col.FITNESS]),
    (Event.DIVERSITY, [Col.GENERATION, Col.TIME, Col.POP_SIZE, Col.DIVERSITY]),
    (Event.BEST_IN_GEN, [Col.GENERATION, Col.TIME, Col.FITNESS]),
    (Event.POP_GEN_TIME, [Col.TIME]),
    (Event.ITER_INFO, [Col.GENERATION, Col.EVAL_TIME, Col.SEL_TIME,
                       Col.CROSS_TIME, Col.MUT_TIME, Col.REPL_TIME, Col.ITER_TIME])
]))

COLUMN_INDICES_FOR_EVENT = dict(map(lambda kv: (kv[0], [EVENT_COL_INDEX] + kv[1] + [SID_COL_INDEX]), [
    (Event.NEW_BEST, [1, 2, 3]),
    (Event.DIVERSITY, [1, 2, 3, 4]),
    (Event.BEST_IN_GEN, [1, 2, 3]),
    (Event.POP_GEN_TIME, [1]),
    (Event.ITER_INFO, list(range(1, 7 + 1)))
]))


def schema_for_event(event: EventName) -> list[str]:
    return SCHEMA_FOR_EVENT[event]


def column_indices_for_event(event: EventName) -> list[int]:
    return COLUMN_INDICES_FOR_EVENT[event]


EVENT_CONFIGS = dict([
    (name, EventConfig(name, SCHEMA_FOR_EVENT[name], COLUMN_INDICES_FOR_EVENT[name]))
    for name in Event.ALL_EVENTS
])


def config_for_event(event: EventName) -> EventConfig:
    return EVENT_CONFIGS[event]
