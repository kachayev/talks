############################################
## Topic:
## Lazy evaluation and declarative approach
## 
## Author:
## Alexey Kachayev, <kachayev@gmail.com>
## 
## Link:
## https://github.com/kachayev/talks/blob/master/master/kharkivpy%236/code/stream.py
## 
## version for Python 2.7+ 
## version for Python 3.3+:
## https://github.com/kachayev/talks/blob/master/master/kharkivpy%236/code/stream_33.py
############################################

from operator import add
from itertools import islice, imap, chain
from sys import maxint

# shortcuts
def take(limit, base): return islice(base, limit)
def drop(limit, base): return islice(base, limit, None)

class Stream(object):

    __slots__ = ("_last", "_collection", "_origin")

    class _StreamIterator(object):
        
        __slots__ = ("_stream", "_position")

        def __init__(self, stream):
            self._stream = stream
            self._position = -1 # not started yet
            
        def next(self):
            # check if elements are available for next position
            # return next element or raise StopIteration
            self._position += 1
            if self._stream._fill_to(self._position):
                return self._stream._collection[self._position]

            raise StopIteration()

    def __init__(self):
        self._collection = []
        self._last = -1 # not started yet
        self._origin = []

    def __lshift__(self, rvalue):
        iterator = rvalue() if callable(rvalue) else rvalue
        self._origin = chain(self._origin, iterator)
        return self

    def _fill_to(self, index):
        if self._last >= index:
            return True

        while self._last < index:
            try:
                n = next(self._origin)
            except StopIteration:
                return False

            self._last += 1
            self._collection.append(n)

        return True

    def __iter__(self):
        return Stream._StreamIterator(self)

    def __getitem__(self, index):
        if isinstance(index, int):
            # todo: i'm not sure what to do with negative indices
            if index < 0: raise TypeError, "Invalid argument type"
            self._fill_to(index)
        elif isinstance(index, slice):
            # todo: reimplement to work lazy
            low, high, step = index.indices(maxint)
            self._fill_to(max(low, high))
        else:
            raise TypeError, "Invalid argument type"

        return self._collection.__getitem__(index)

#----------------------------------    
# Simple cases 
#----------------------------------    

s = Stream() << [1,2,3,4,5]
assert list(s) == [1,2,3,4,5]
assert s[1] == 2
assert s[0:2] == [1,2]

s = Stream() << range(6) << [6,7]
assert list(s) == [0,1,2,3,4,5,6,7]

def gen():
    yield 1
    yield 2
    yield 3
    
s = Stream() << gen << (4,5)
assert list(s) == [1,2,3,4,5]

#----------------------------------    
# Fibonacci infinite sequence
#----------------------------------    
f = Stream()
fib = f << [0, 1] << imap(add, f, drop(1, f))

assert list(take(10, fib)) == [0,1,1,2,3,5,8,13,21,34]
assert fib[20] == 6765
assert fib[30:35] == [832040,1346269,2178309,3524578,5702887]
