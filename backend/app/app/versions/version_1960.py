"""Calendar class for the 1960 calendar."""

import itertools

from devtools import debug

from app import models

from .base import VersionBase


class CalendarError(Exception):
    pass


def clear_debug(*args):
    print("\n\n\n")
    debug(*args)
    print("\n\n\n")


class Version1960(VersionBase):
    """A class to represent the 1960 calendar."""

    def resolve(self, *objs):
        # check all objs of the same kind
        objs = list(objs)
        if not all(
            (isinstance(x, type(y)) for x, y in itertools.combinations(objs, 2))
        ):
            raise CalendarError("Not all objects of same kind")

        if isinstance(objs[0], models.Martyrology):
            base = max(objs)
            objs.remove(base)
            for obj in sorted(objs, reverse=True):
                base.parts = obj.parts + base.parts
            return base

        elif isinstance(objs[0], models.Feast):
            base = max(objs)
            objs.remove(base)
            print(jsonable_encoder(objs))
            return base
