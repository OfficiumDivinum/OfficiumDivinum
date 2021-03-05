# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.
import string
from pathlib import Path
from random import randint
from unittest.mock import Mock

from hypothesis import given
from hypothesis import strategies as st

import app.parsers.util
from app.parsers.util import Line


def make_linkstr(target, part, replacement, squash=True):
    if replacement:
        replacement = f"s/{replacement}//"
    if squash and replacement:
        replacement += "s"
    linkstr = f"@{target}:{part}:{replacement}"
    return linkstr


def make_both(target, part, replacement, squash=True):
    content = replacement
    if replacement:
        replacement = f"s/{replacement}//"
    if squash and replacement:
        replacement += "s"
    linkstr = f"@{target}:{part}:{replacement}"
    return linkstr, [[Line(0, content)]]


def sane_text(**kwargs):
    kwargs["alphabet"] = string.ascii_letters
    return st.text(**kwargs)


def file_filter(x):
    if "@" in x and not x.startswith("@"):
        return False
    if "[" in x and not x.startswith("[") and x.endswith("]"):
        return False
    return True


@st.composite
def mock_file(draw):
    lines = (draw(st.lists(st.text().filter(file_filter), min_size=20)),)
    print(lines)
    fn = Mock()
    o = Mock()
    o.readlines.return_value = lines
    fn.name = ""
    fn.open.return_value = o
    return fn


@st.composite
def make_linkstr_content(draw,):
    linkstr, content = draw(
        st.builds(make_both, sane_text(), sane_text(), sane_text(min_size=4))
    )
    return (linkstr, content)


@given(
    linkstr=st.builds(make_linkstr, sane_text(), sane_text(), sane_text()),
    originf=st.builds(Path),
)
def test_fuzz_deref(linkstr, originf):
    app.parsers.util.deref(linkstr=linkstr, originf=originf)


@given(fn=st.builds(Path))
def test_fuzz_guess_section_header(fn):
    app.parsers.util.guess_section_header(fn=fn)


@given(
    lines=st.lists(
        st.text().filter(lambda x: x.startswith("@") or "@" not in x), min_size=1
    ),
    section_header_regex=st.just("\\[(.*)\\]"),
)
def test_fuzz_parse_DO_sections(lines, section_header_regex):
    fn = Mock()
    o = Mock()
    o.readlines.return_value = lines
    fn.open.return_value = o
    print(fn.open().readlines())
    app.parsers.util.parse_DO_sections(fn=fn, section_header_regex=section_header_regex)


def version(v):
    versions = ["1960"]
    return versions[v]


def getf():
    files = list(Path("app/tests/parsers/test-DO-data/").glob("**/*.txt"))
    print(files)
    return files[randint(0, len(files))]


@given(
    fn=st.builds(getf),
    section_key=sane_text(),
    version=st.builds(version, st.integers(0, 0)),
    follow_links=st.booleans(),
    follow_only_interesting_links=st.booleans(),
    nasty_stuff=st.builds(list),
)
def test_fuzz_parse_file_as_dict(
    fn, section_key, version, follow_links, follow_only_interesting_links, nasty_stuff
):
    app.parsers.util.parse_file_as_dict(
        fn=fn,
        section_key=section_key,
        version=version,
        follow_links=follow_links,
        follow_only_interesting_links=follow_only_interesting_links,
        nasty_stuff=nasty_stuff,
    )


@given(params=make_linkstr_content())
def test_fuzz_substitute_linked_content(params):
    line, linked_content = params
    print(params)
    app.parsers.util.substitute_linked_content(linked_content=linked_content, line=line)


@given(data=sane_text(), cleanup=st.booleans())
def test_fuzz_unicode_to_ascii(data, cleanup):
    app.parsers.util.unicode_to_ascii(data=data, cleanup=cleanup)
