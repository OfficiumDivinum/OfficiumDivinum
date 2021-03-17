"""Dedup objects intelligently."""
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
    deduped = {v: [] for _, v in english_names.items()}
    print(f"Deduplicating at least {len(things)} items.")

    hash_dict = {}

    with progressbar(things) as progress:
        for thing in progress:
            # replace this with hash version:
            # check if hash in hash dict keys.
            # if so, if version not in hash dict versions, append it.
            if not isinstance(thing, list):
                thing = [thing]

            # sometimes we have a list of lists still
            flat_thing = []
            for x in thing:
                if isinstance(x, list):
                    flat_thing == x
                else:
                    flat_thing.append(x)

            for obj in flat_thing:
                obj_hash = obj.__custom_hash__()
                try:
                    hash_dict[obj_hash].versions = list(
                        set(obj.versions + hash_dict[obj_hash].versions)
                    )
                except KeyError:
                    hash_dict[obj_hash] = obj
                except TypeError:
                    continue

    for _, uniq_obj in hash_dict.items():
        category = english_names[type(uniq_obj).__name__]
        deduped[category].append(uniq_obj)

    print("Stripping empty categories.")
    deduped = {k: v for k, v in deduped.items() if v}
    return deduped
