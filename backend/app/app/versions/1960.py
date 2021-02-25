"""Calendar class for the 1960 calendar."""

import itertools

from app import models

from . import CalendarBase


class CalendarError(Exception):
    pass


class Version1960(CalendarBase):
    """A class to represent the 1960 calendar."""

    def resolve(self, *objs):
        # check all objs of the same kind
        if not all((isinstance(x, y) for x, y in itertools.combinations(objs))):
            raise CalendarError("Not all objects of same kind")

        if isinstance(objs[0], models.Martyrology):
            base = max(objs)
            objs.remove(base)
            for obj in sorted(objs, reverse=True):
                base.parts = obj.parts + base.parts
            return base
