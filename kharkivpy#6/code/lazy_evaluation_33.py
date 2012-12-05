############################################
## Topic:
## Lazy evaluation and declarative approach
## to pathfinding algorithms implementation
## 
## Author:
## Alexey Kachayev, <kachayev@gmail.com>
## 
## Task:
## "Pouring water problem",
## http://www.codechef.com/problems/POUR1
## 
## Link:
## https://github.com/kachayev/talks/blob/master/kharkivpy%236/code/lazy_evaluation_33.py
## 
## P.S. Python 3.3+
############################################

from functools import reduce
from itertools import islice, chain, starmap
from operator  import attrgetter as attr

############################################
## Utils and helper functions
############################################

def named(fn):
    """Wrap function with readable __name__ in order to simplify debug"""
    def inner(*args, **kwargs):
        wrapped = fn(*args, **kwargs)
        args_repr = ", ".join(map(str, args))
        wrapped.__name__ = "{fn}({args})".format(fn = fn.__name__, args=args_repr)
        return wrapped
    return inner

def update(container, *pairs):
    """Create copy of given container, chagning one (or more) elements.
    
    Creating of new list is necessary here, cause we don't want to
    deal with mutable data structure in current situation - it will
    be too problematic to keep everything working with many map/reduce
    operations if data will be mutable.
    """ 
    def pair(left, right):
        pos, el = right
        # todo: use takewhile/dropwhile or write "split-at" helper
        return [(s if i != pos else el) for i, s in enumerate(left)]
    return reduce(pair, pairs, container)

def foldr(l, r):
    """Helper function to switch from reduce to right folding"""
    return r(l)

class lazy:
    def __init__(self, origin, state=None):
        self._origin = origin() if callable(origin) else origin
        self._state = state or []
        self._finished = False
    def __iter__(self):
        return self if not self._finished else iter(self._state)
    def __next__(self):
        try:
            n = next(self._origin)
        except StopIteration as e:
            self._finished = True
            raise e
        else:
            self._state.append(n)
            return n

############################################
## Solution
############################################

capacity = (4, 9)
initial  = tuple([0] * len(capacity))
glasses  = range(len(capacity))

## description of all possible moves

@named
def empty(glass):
    def inner(state):
        return update(state, (glass, 0))
    return inner 

@named
def fill(glass):
    def inner(state):
        return update(state, (glass, capacity[glass]))
    return inner

@named
def pour(from_, to):
    def inner(state):
        amount = min(state[from_], capacity[to]-state[to])
        return update(state, (from_, state[from_]-amount), (to, state[to]+amount))
    return inner

def moves():
    yield from map(empty, glasses)
    yield from map(fill, glasses)
    yield from starmap(pour, ((f, t) for f in glasses for t in glasses if f != t))

## lazy evaluated value with list of all possible moves
moves = lazy(moves)

## calculation for end state for given path
def lead_to(path):
    return tuple(reduce(foldr, path, initial))

## check that lead_to function works as we expect
assert lead_to([fill(0), fill(1)]) == (4, 9)
assert lead_to([fill(0), fill(0)]) == (4, 0)
assert lead_to([fill(0), empty(0)]) == (0, 0)
assert lead_to([fill(0), pour(0, 1)]) == (0, 4)
assert lead_to([fill(0), empty(0), fill(1)]) == (0, 9)

## printable representation for path
def dump_path(path):
    p = ", ".join(map(attr("__name__"), path))
    return "{path} ==> {end}".format(path = p, end = lead_to(path))

def started_at(path_sets, explored):
    more = lazy(filter(
        lambda p: lead_to(p) not in explored,
        (path+[m] for path in path_sets for m in moves)
    ))
    
    yield from more
    yield from started_at(more, explored.union(set(map(lead_to, more))))

## lazy evaluated "list" with all possible 
## pathes from initial state to end one 
path_sets = started_at([[]], set([initial]))

## all possible solutions
def solutions(target):
    return lazy(filter(lambda p: target in lead_to(p), path_sets))

## as short solution as possible
def solution(target):
    return next(solutions(target))

## how to use this...
print(dump_path(solution(6)))
# output:
# fill(1), pour(1, 0), empty(0), pour(1, 0), empty(0), pour(1, 0), fill(1), pour(1, 0) ==> (4, 6)

##########################################################
## Solution based on class Path for history representation
##########################################################

class Path(list):
    _lead_to = None

    @property
    def lead_to(self):
        if not self._lead_to:
            self._lead_to = tuple(reduce(foldr, self, initial))
        return self._lead_to

    def __str__(self):
        path = ", ".join(map(attr("__name__"), self))
        return "{path} ==> {end}".format(path = path, end = self.lead_to)

    def extend(self, move):
        return Path(self + [move])

## check that Path abstraction works as we expect
assert Path([fill(0), fill(1)]).lead_to == (4, 9)
assert Path([fill(0), fill(0)]).lead_to == (4, 0)
assert Path([fill(0), empty(0)]).lead_to == (0, 0)
assert Path([fill(0), pour(0, 1)]).lead_to == (0, 4)
assert Path([fill(0), empty(0), fill(1)]).lead_to == (0, 9)

def started_at(path_sets, explored):
    more = lazy(filter(
        lambda p: p.lead_to not in explored,
        (path.extend(m) for path in path_sets for m in moves) 
    ))

    yield from more
    yield from started_at(more, explored.union(set(map(attr("lead_to"), more))))

## lazy evaluated "list" with all possible 
## pathes from initial state to end one 
path_sets = started_at([Path()], set([initial]))

## all possible solutions
def solutions(target):
    return lazy(filter(lambda p: target in p.lead_to, path_sets))

assert solution(5).lead_to == (4, 5)
assert solution(1).lead_to == (4, 1)
assert len(solution(1)) == 5

print(solution(7))
# output:
# fill(0), pour(0, 1), fill(0), pour(0, 1), fill(0), pour(0, 1), empty(1), pour(0, 1), fill(0), pour(0, 1) ==> (0, 7)
