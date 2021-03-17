"""Dedup objects intelligently."""
from copy import deepcopy
from typing import Dict, List

from deepdiff import DeepDiff
from devtools import debug

english_names = {
    "MartyrologyCreate": "Martyrologies",
    "PrayerCreate": "Prayers",
    "AntiphonCreate": "Antiphons",
}


def dedup(things: List) -> Dict:
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
    for index, thing in enumerate(things):
        if not isinstance(thing, list):
            thing = [thing]

        for obj in thing:
            appended = False
            debug("New obj")
            kind = english_names[type(obj).__name__]

            if obj in deduped[kind]:
                debug("Skipping")
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
                            set(obj.versions + deduped[kind][obj_index].versions)
                        )
                        debug("Appending")
                        appended = True
                        break
            if not appended:
                debug("Adding")
                deduped[kind].append(obj)
                unversioned[index] = unversion
                indexes[index] = len(deduped[kind]) - 1  # index pointing to obj

    deduped = {k: v for k, v in deduped.items() if v}
    debug()
    return deduped
