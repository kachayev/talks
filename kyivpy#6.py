# Let me start...
name = "Alexey Kachayev"
topic = "Descriptors && OOP"

# Simple non-data descriptor
class Speaker(object):
    def __get__(self, obj, objtype):
        return "Alexey"

# Usage example
class Conf(object):
    speaker = Speaker() ## <--- Descriptor!
    
# Check how it works
Conf.speaker ## <--- attr resolve for class

kyivpy = Conf()
kyivpy.speaker ## <--- attr resolve for class instance

# Let's get little bit more information
class Speaker(object):
    def __get__(self, obj, objtype):
        print self, obj, objtype; return "Alexey"
        
# The same usage example
class Conf(object):
    speaker = Speaker()
    
# Check how it works now
Conf.speaker
Conf().speaker
kyivpy = Conf()
kyivpy.speaker

# Inspect __get__ calls
import inspect
class Speaker(object):
    def __get__(self, obj, objtype):
        print inspect.getframeinfo(inspect.currentframe().f_back); return "Alexey"
        
# The same usage example
class Conf(object):
    speaker = Speaker()
    
# Diving deeper into OOP model...
Conf.speaker
kyivpy = Conf()
Conf.__dict__
Conf.speaker
Conf.__dict__['speaker']
Conf.__dict__['speaker'].__get__(None, Conf)
## REMEMBER about: object.__getattribute__ 
type(kyivpy).__dict__['speaker'].__get__(kyivpy, type(kyivpy))

# Next line will create "speaker" as 
# string object in instance __dict__
kyivpy.speaker = "Alexey K."
kyivpy.__dict__
kyivpy.speaker

# Data descriptor example
class Speaker(object):
    def __get__(self, obj, objtype):
        print "Getting"
        return "Alexey"
    
    def __set__(self, obj, value):
        print "Setting"
        
# The same usage example
class Conf(object):
    speaker = Speaker()
    
kyivpy = Conf()
kyivpy.speaker
# Will work with descriptor instead of instance __dict__
kyivpy.speaker = "Alexey K."
kyivpy.__dict__
kyivpy.__dict__['speaker'] = "Alexey Kachayev"
kyivpy.speaker
kyivpy.__dict__

#
# Descriptor in day-to-day pratice...
# Create API which will look like this:
#
# class XmlDoc(object):
#     name = Field("name")    
#     .. other fields ..
#

class Field(object):
    def __init__(self, name):
        self.name = name
        self.field = "_field_" + name
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return getattr(obj, self.field, "")
    def __set__(self, obj, value):
        setattr(obj, self.field, value)
        
class XmlDoc(object):
    name = Field("name")
    date = Field("date")
    speakers = Field("speakers")
    
# Check how it will work
kyivpy = XmlDoc()
kyivpy.name = "Kyiv #6"
kyivpy.date = "Today"
kyivpy.speakers = "Alexey, Andrey"
kyivpy.__dict__
kyivpy.name

# Add rendering facilities 
class Field(object):
    def __init__(self, name):
        self.name = name
        self.field = "_field_" + name
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return getattr(obj, self.field, "")
    def __set__(self, obj, value):
        setattr(obj, self.field, value)
    def render(self, obj):
        return "<{tag}>{value}</{tag}>".format(tag = self.name, value=getattr(obj, self.field, ""))
    
# Check once more...
class XmlDoc(object):
    name = Field("name")
    date = Field("date")
    speakers = Field("speakers")
    
kyivpy = XmlDoc()
kyivpy.name = "Kyiv #6"
kyivpy.speakers = "Alexey, Andrey"
kyivpy.date = "Today"
kyivpy.__dict__
XmlDoc.__dict__
XmlDoc.__dict__.values()

# Filter all Fields from doc
filter(lambda x: type(x) == Field, XmlDoc.__dict__.values())

# Call rendering function
from operator import methodcaller
map(
    methodcaller("render", kyivpy), 
    filter(lambda x: type(x) == Field, XmlDoc.__dict__.values())
)

# Add ordering functionality
from itertools import count
class Field(object):
    counter = count(1)
    def __init__(self, name):
        self.name = name
        self.field = "_field_" + name
        self.order = Field.counter.next()
        
    def __get__(self, obj, objtype):
        return getattr(obj, self.field, "")
    
    def __set__(self, obj, value):
        setattr(obj, self.field, value)
        
class XmlDoc(object):
    name = Field("name")
    date = Field("date")
    speakers = Field("speakers")
    

# Rendering example with ordering
kyivpy = XmlDoc()
kyivpy.name = "#6"
kyivpy.speakers = "Alexey, ... CO"
kyivpy.date = "Today"

# Filtering
filter(lambda x: type(x) == Field, XmlDoc.__dict__.values())

# Mapping and other stuff...
map(
    attrgetter("order"), 
    filter(lambda x: type(x) == Field, XmlDoc.__dict__.values())
)

map(
    methodcaller("render", kyivpy), 
    sorted(
        filter(lambda x: type(x) == Field, XmlDoc.__dict__.values()), 
        key=attrgetter("order")
    )
)

map(
    attrgetter("name"), 
    sorted(
        filter(lambda x: type(x) == Field, XmlDoc.__dict__.values()), 
        key=attrgetter("order")
    )
)

# Functions/bounded methods/unbounded methods
class Talk(object):
    def __init__(self, name):
        self.name = name
        
    def say(self):
        print self.name, ">> mmm..something"
        
# Check it...
me = Talk("Alexey")
me.say()
me.say 
Talk.say 

# Instance methods
type(me.say)
type(Talk.say)

# How we can get instance method from function object
Talk.__dict__
Talk.__dict__['say']
Talk.__dict__['say'].__get__(None, Talk)
Talk.__dict__['say'].__get__(None, Talk)()
Talk.__dict__['say'].__get__(me,  type(me))
Talk.__dict__['say'].__get__(None, Talk).im_self
print Talk.__dict__['say'].__get__(None, Talk).im_self
print Talk.__dict__['say'].__get__(None, Talk).im_func
Talk.__dict__['say'].__get__(me,  type(me)).im_func
Talk.__dict__['say'].__get__(me,  type(me)).im_self

# Dynamic binding implementation
def finish(self):
    print self.name, "<< finished"    

me.finish = finish
me.finish()
me.__dict__
me.finish = finish.__get__(me, type(me))
me.__dict__
me.finish()
        
# Own implementation for @property
class Property(object):
    def __init__(self, fget, fset):
        self.fget = fget
        self.fset = fset
    def __get__(self, obj, objtype):
        if obj is None:
            return self
        return self.fget(obj)
    def __set__(self, obj, value):
        self.fset(obj, value)
        
# Usage example...
class Talk(object):
    def getname(self):
        return self.__name
    def setname(self, value):
        self.__name = value
    def __init__(self, name):
        self.name = name
    name = Property(getname, setname)
    

me = Talk("Alexey")
me.name
me.__dict__
me.__name
me._Talk__name

# Own implementation for @staticmethod
class StaticMethod(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, objtype):
        return self.f
    
# Usage example...
class Talk(object):
    def start():
        print "Started ..."
        
    start_static = StaticMethod(start)
    

me = Talk()
conf = Talk()
conf.start 
conf.start()
conf.start_static()
conf.start_static 

# Own implementation of @classmethod functionality
class ClassMethod(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, objtype):
        # We need this function in order to call it with type(obj) 
        # as first argument. Partial function execution will 
        # work fine also (functools.partial)
        def wrapper(*args):
            return self.f(objtype, *args)
        return wrapper
    
# Usage example
class Talk(object):
    def __init__(self, name):
        self.name = name
    def from_list(cls, speakers):
        return map(cls, speakers)
    from_list = ClassMethod(from_list)
    
# Common case for working with @classmethod
Talk.from_list(["Alexey", "Vsevolod"])

# Check that everything works fine
map(attrgetter("name"), Talk.from_list(["Alexey", "Vsevolod"]))

# Check that descriptor will return "wrapper" function
Talk.__dict__['from_list']
Talk.__dict__['from_list'].__get__(None, Talk)
Talk.__dict__['from_list'].__get__(None, Talk).__name__

# Here you can find IPython session from conference
git = "github.com/kachayev/talks"

