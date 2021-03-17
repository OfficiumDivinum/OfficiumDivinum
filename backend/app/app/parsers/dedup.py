"""Dedup objects intelligently."""
from copy import deepcopy
from typing import Dict, List, Union

from devtools import debug
from typer import progressbar

from app.schemas import (
    AntiphonCreate,
    BlockCreate,
    FeastCreate,
    HymnCreate,
    LineBase,
    MartyrologyCreate,
    PrayerCreate,
    ReadingCreate,
    RubricCreate,
    VerseCreate,
    VersicleCreate,
)

CreateTypes = Union[
    AntiphonCreate,
    BlockCreate,
    FeastCreate,
    HymnCreate,
    LineBase,
    MartyrologyCreate,
    PrayerCreate,
    ReadingCreate,
    RubricCreate,
    VerseCreate,
    VersicleCreate,
]

english_names = {
    "MartyrologyCreate": "Martyrologies",
    "PrayerCreate": "Prayers",
    "AntiphonCreate": "Antiphons",
    "BlockCreate": "Blocks",
    "FeastCreate": "Feasts",
    "HymnCreate": "Hymns",
    "LineBase": "Lines",
    "ReadingCreate": "Readings",
    "RubricCreate": "Rubrics",
    "VerseCreate": "Verses",
    "VersicleCreate": "Vesicles",
}


def dedup(
    things: List[Union[List[CreateTypes], CreateTypes]]
) -> Dict[str, CreateTypes]:
    """
    Dedup objs.

    Deduplicates objects, by stripping completely identical objects,
    and extending properties where it makes sense to do so.  Currently
    we extend:

     * versions


    Args:
     : objs: List: objects or lists of objects to dedup.

    Returns:
      : a dict of deduped objects by kind, flattened.  We use nice names defined
    in `english_names.`
    """
    unversioned = {}
    deduped = {v: [] for _, v in english_names.items()}
    indexes = {}
    print(f"Deduplicating at least {len(things)} items.")
    index = -1
    with progressbar(things) as progress:
        for thing in progress:
            index += 1
            if not isinstance(thing, list):
                thing = [thing]

            for obj in thing:
                appended = False
                try:
                    kind = english_names[type(obj).__name__]
                except KeyError:
                    debug(obj)
                    continue

                if obj in deduped[kind]:
                    continue

                if hasattr(obj, "versions"):
                    # I'm bored of try statements, and this is faster than copying first.
                    # Sure, we could do a throwaway access, but what's wrong with hasattr? ;)
                    unversion = deepcopy(obj)
                    unversion.versions = None
                    for i, x in unversioned.items():
                        if x == unversion:
                            obj_index = indexes[i]
                            deduped[kind][obj_index].versions = list(
                                sorted(
                                    set(
                                        obj.versions + deduped[kind][obj_index].versions
                                    )
                                )
                            )
                            appended = True
                            break
                if not appended:
                    deduped[kind].append(obj)
                    unversioned[index] = unversion
                    indexes[index] = len(deduped[kind]) - 1  # index pointing to obj

    print("Stripping empty categories.")
    deduped = {k: v for k, v in deduped.items() if v}
    return deduped
