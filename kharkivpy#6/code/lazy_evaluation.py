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
## version for Python 2.7+ 
## version for Python 3.3+ is coming..
############################################

from itertools import imap, islice, chain
from operator import attrgetter

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
    def pair(left, (pos, el)):
        return [(s if i != pos else el) for i, s in enumerate(left)]
    return reduce(pair, pairs, container)

class lazy(object):
    def __init__(self, gen):
        self.gen = gen() if callable(gen) else gen
        self._state = []
        self._finished = False
    def __iter__(self):
        return self if not self._finished else iter(self._state)
    def next(self):
        try:
            n = next(self.gen)
        except StopIteration, e:
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
    for glass in glasses:
        yield empty(glass)
        yield fill(glass)
        
    for (f, t) in ((f, t) for f in glasses for t in glasses if f != t):
        yield pour(f, t)

## lazy evaluated value with list of all possible moves
moves = lazy(moves)

## calculation for end state for given path
def lead_to(path):
    return tuple(reduce(lambda l, r: r(l), path, initial))

## printable representation for path
def dump_path(path):
    p = ", ".join(map(attrgetter("__name__"), path))
    return "{path} ==> {end}".format(path = p, end = lead_to(path))

## check that lead_to function works as we expect
assert lead_to([fill(0), fill(1)]) == (4, 9)
assert lead_to([fill(0), fill(0)]) == (4, 0)
assert lead_to([fill(0), empty(0)]) == (0, 0)
assert lead_to([fill(0), pour(0, 1)]) == (0, 4)
assert lead_to([fill(0), empty(0), fill(1)]) == (0, 9)

def started_at(path_sets, explored):
    more =  lazy(path + [m] for path in path_sets 
                            for m in moves 
                            if lead_to(path + [m]) not in explored)    

    for el in more: yield el
    explored = explored.union(set(imap(lead_to, more)))
    for el in started_at(more, explored): yield el

## lazy evaluated "list" with all possible 
## pathes from initial state to end one 
path_sets = started_at([[]], set([initial]))

## all possible solutions
def solutions(target):
    return lazy(path for path in path_sets if target in lead_to(path))

## as short solution as possible
def solution(target):
    return next(solutions(target))

## how to use this...
print dump_path(solution(6))
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
            self._lead_to = tuple(reduce(lambda l, r: r(l), self, initial))
        return self._lead_to

    def __str__(self):
        path = ", ".join(map(attrgetter("__name__"), self))
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
    more =  lazy(path.extend(m) for path in path_sets 
                                for m in moves 
                                if path.extend(m).lead_to not in explored)    

    for el in more: yield el
    explored = explored.union(set(imap(attrgetter("lead_to"), more)))
    for el in started_at(more, explored): yield el

## lazy evaluated "list" with all possible 
## pathes from initial state to end one 
path_sets = started_at([Path()], set([initial]))

## all possible solutions
def solutions(target):
    return lazy(path for path in path_sets if target in path.lead_to)

print solution(7)
# output:
# fill(0), pour(0, 1), fill(0), pour(0, 1), fill(0), pour(0, 1), empty(1), pour(0, 1), fill(0), pour(0, 1) ==> (0, 7)

############################################
## Other solution base on streams processing
############################################

# class Stream(object):
#     def __init__(self, *gens):
#         self._stream = chain(*gens) if len(gens) else iter([])
#     def __iter__(self):
#         return self._stream
#     def __add__(self, other):
#         return self.__class__(self._stream, other)
# 
# def started_at(path_sets, explored):
#     more =  lazy(path + [m] for path in path_sets for m in moves if lead_to(path + [m]) not in explored)
#     return path_sets + started_at(more, explored.union(set(imap(lead_to, more))))
# 
# ## lazy evaluated "list" with all possible 
# ## pathes from initial state to end one 
# path_sets = started_at(Stream([[]]), set([initial]))
# 
# print dump_path(solution(6))