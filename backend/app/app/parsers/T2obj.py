"""Parse Divinumofficium's Temporal files into Feast objects."""

from ..DSL import days, months, ordinals, specials

# from ..objects import Date
# from ..objects import Feast
# from ..objects import Octave
# from ..objects import Rank


def parse_DO_sections(lines: list) -> list:
    """
    Parse DO files into lists per section.

    Parameters
    ----------
    lines: list : lines to break into sections.


    Returns
    -------
    A list of sections.
    """
    sections = {}
    current_section = None
    content = []
    for line in lines:
        line = line.strip()
        if line == "_":
            continue
        if line.startswith("[") and line.endswith("]"):
            if current_section:

                try:
                    while content[-1].strip() == "":
                        content.pop()
                except IndexError:
                    content = None

                sections[current_section] = content

            current_section = line.strip("[]")
            content = []
        else:
            content.append(line)
    return sections


# def parse_file(fn: Path, calendar: str) -> Feast:
#     """
#     Parse provided file.

#     Parameters
#     ----------
#     fn: Path : File to parse.

#     calendar : str: Calendar to use (mainly for naming at this stage).


#     Returns
#     -------
#     A Feast object represeting the day.
#     """
#     try:
#         after, day = fn.stem.split("-")
#     except ValueError:
#         return  # give up
#     qualifiers = None
#     name = None
#     try:
#         int(after)
#         date = after[:-1]
#         week = int(after[-1])
#     except ValueError:
#         date, week = re.findall(r"([A-Z][a-z]+)([0-9]+)", after)[0]
#     try:
#         day = int(day)
#     except ValueError:
#         day, qualifiers = re.findall(r"([0-9])(.+)", day)[0]

#     try:
#         date = f"1 {months[int(date) - 1]}"
#     except ValueError:
#         # for non month temporal it the reference *might* be a Sunday (e.g. Easter).
#         date = specials[date]
#     datestr = f"{ordinals[int(week)]} Sun after {date}"
#     # datestr = f"{ordinals[week]} Sun on or after {date}"
#     day = int(day)
#     if day != 0:
#         datestr = f"{days[day]} after {datestr}"

#     lines = fn.open().readlines()
#     sections = parse_DO_sections(lines)
#     rank = "Feria"
#     try:
#         name, rank, rankno, source = [
#             *sections["Rank1960"][0].split(";;"),
#             None,
#             None,
#             None,
#             None,
#         ][:4]

#     except KeyError:
#         try:
#             name, rank, rankno, source = [
#                 *sections["Rank"][0].split(";;"),
#                 None,
#                 None,
#                 None,
#                 None,
#             ][:4]
#         except KeyError:
#             pass
#     try:
#         rank, octave = rank.split("cum")
#         privileged = True if "privilegiata" in octave else False
#         octave_rank = re.findall(r"Octava ([Pp]rivilegiata)* (.*)", octave)[0][1]
#         rank = Rank(
#             rank, octave=Octave(octave, privileged=privileged, rank=Rank(octave_rank))
#         )
#     except ValueError:
#         rank = Rank(rank)
#     celebration = None
#     commemorations = None

#     for section, content in sections.items():
#         if section == "Rule":
#             pass
#         # pass  # later implement handling here

#     return Feast(
#         rank,
#         Date(datestr),
#         calendar,
#         "de Tempore",
#         name,
#         celebration,
#         commemorations,
#         qualifiers,
#     )
