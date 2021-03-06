from __future__ import unicode_literals

import weakref

from .data import data
from ._compat import unicode_compatible, unicode_type, PY2


@unicode_compatible
class Division(object):
    """The administrative division."""

    _identity_map = weakref.WeakValueDictionary()

    def __init__(self, code, name):
        self.code = unicode_type(code)
        self.name = unicode_type(name)

    def __repr__(self):
        return 'gb2260.get(%r)' % self.code

    def __str__(self):
        name = 'GB2260'
        humanize_name = '/'.join(x.name for x in self.stack())
        return '<%s %s %s>' % (name, self.code, humanize_name)

    def __hash__(self):
        return hash((self.__class__, self.code))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.code == other.code

    @classmethod
    def get(cls, code):
        """Gets an administrative division by its code.

        :param code: The division code.
        :returns: A :class:`gb2260.Division` object.
        """
        key = int(code)
        cache = cls._identity_map
        store = data

        if key in cache:
            return cache[key]

        if key in store:
            instance = cls(code, store[key])
            cache[key] = instance
            return instance

        raise ValueError('%r is not valid division code' % code)

    @classmethod
    def search(cls, code, name=None):
        """Searches administrative division by its code in all revision.

        :param code: The division code.
        :param name: search name.
        :returns: A :class:`gb2260.Division` object or ``None``.
        """
        code = str(code)
        result = []
        # sorts from latest to oldest, and ``None`` means latest
        for (key, value) in data.items():
            if str(key)[:len(code)] == code:
                if name is None:
                    result.append(cls.get(key))
                else:
                    if PY2:
                        value = value.encode('utf-8')

                    if name == value or value.find(name) != -1 or name.find(value) != -1:
                        result.append(cls.get(key))

        return result

    @property
    def province(self):
        return self.get(self.code[:2] + '0000')

    @property
    def is_province(self):
        return self.province == self

    @property
    def prefecture(self):
        if self.is_province:
            return
        return self.get(self.code[:4] + '00')

    @property
    def is_prefecture(self):
        return self.prefecture == self

    @property
    def county(self):
        if self.is_province or self.is_prefecture:
            return
        return self

    @property
    def is_county(self):
        return self.county is not None

    def stack(self):
        yield self.province
        if self.is_prefecture or self.is_county:
            yield self.prefecture
        if self.is_county:
            yield self
