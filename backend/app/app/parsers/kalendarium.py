import re
from typing import Dict, Optional, Union

from devtools import debug


def num(s: str) -> Union[int, str]:
    try:
        return int(s)
    except ValueError:
        return float(s)


def extract_line(line: str) -> Optional[Dict]:
    """Extract feast info from line."""

    line = line.strip()
    if line.startswith("*"):
        return None

    parts = line.split("=")
    date, alternative_date = parts[:2]
    data = {"date": date, "alternative_date": alternative_date, "feasts": []}
    line = "=".join(parts[2:])
    for match in re.findall(r"((.*?)=([0-9]+\.?[0-9]*)=*)", line):
        data["feasts"].append({"name": match[1], "rank": num(match[2])})
    return data
