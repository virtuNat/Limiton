import weakref
from collections import deque

__singletons = {}

def __singleton_callback(cls, *args, **kwargs):
    if cls not in __singletons:
        instance = object.__new__(cls, *args, **kwargs)
        __singletons[cls] = instance
        return instance
    return __singletons[cls]

class SingletonMeta(type):
    """Metaclass that allows exactly one instance object per member class.
    Extra calls will just return the single instance reference without re-initializing.
    """
    __slots__ = ()
    __call__ = __singleton_callback


class SingletonSuper(object):
    """Superclass that allows exactly one instance object per subclass.
    Extra calls will just return the single instance reference without re-initializing.
    """
    __slots__ = ()
    __new__ = __singleton_callback


class SingletonFactory(object):
    """Object factory that allows exactly one instance object for its product class.
    Extra calls will just return the single instance reference without re-initializing.
    """
    __slots__ = ('_ctype',)

    def __init__(self, ctype):
        self._ctype = ctype

    def __call__(self, *args, **kwargs):
        return __singleton_callback(self._ctype, *args, **kwargs)


class LimitonMeta(type):
    """Metaclass that allows only a limited number of instances of its member classes
    to exist per member class. The number of instances and overflow behavior can be
    defined in the class attributes, defaulting to Singleton behavior if not defined.
    """
    __slots__ = ()

    def __new__(cls, name, bases, attrs):
        if not '_pump' in attrs: attrs['_pump'] = False
        if not '_maxlen' in attrs: attrs['_maxlen'] = 1
        elif not isinstance(attrs['_maxlen'], int):
            attrs['_maxlen'] = attrs['_maxlen'].__index__()
        if attrs['_maxlen'] < 1:
            raise ValueError('Limiton maximum instance limit must be positive.')
        attrs['_refs'] = deque([], maxlen=attrs['_maxlen'])
        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        if len(cls._refs) < cls._maxlen or cls._pump:
            instance = object.__new__(cls, *args, **kwargs)
            cls._refs.append(instance)
            return weakref.proxy(instance)
        if cls._maxlen == 1:
            return weakref.proxy(cls._refs[0])
        raise IndexError('Maximum instance limit reached.')


class LimitonFactory(object):
    """Object factory that allows only a limited number of instances of its product class
    to exist. The class type, number of instances, and overflow behavior are defined upon
    instantiation, and default to Singleton behavior if not defined.
    """
    __slots__ = ('_ctype', '_refs', '_maxlen', '_pump')

    def __init__(self, ctype, *, maxlen=1, pump=False):
        self._ctype = ctype
        self._pump = pump
        if not isinstance(maxlen, int):
            maxlen = maxlen.__index__()
        if maxlen < 1:
            raise ValueError('Limiton maximum instance limit must be positive.')
        self._maxlen = maxlen
        self._refs = deque([], maxlen=maxlen)

    def __call__(self, *args, **kwargs):
        if len(self._refs) < self._maxlen or self._pump:
            instance = self._ctype(*args, **kwargs)
            self._refs.append(instance)
            return weakref.proxy(instance)
        raise IndexError('Maximum instance limit reached.')
