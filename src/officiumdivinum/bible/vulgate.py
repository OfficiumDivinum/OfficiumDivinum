from pathlib import Path
from re import search

from dotmap import DotMap

from ..objects import Verse
from .bible import Bible


class Vulgate(Bible):
    def from_file(self, fn: Path):

        current_book_name = "Gn"
        book = DotMap()

        with fn.open() as f:
            for line in f.readlines():
                results = search(
                    r"([0-9]* *.+?) ([0-9]+) ([0-9]+) (.*)", line.strip()
                ).groups()

                book_name, chapter, verseno, verse = results
                book_name = book_name.replace(" ", "")
                chapter = int(chapter)
                verseno = int(verseno)
                if book_name != current_book_name:
                    self.content[current_book_name] = book
                    book = DotMap()
                    current_book_name = book_name
                try:
                    book[chapter][verseno] = Verse(
                        verseno, chapter, book_name, verse, self.version
                    )
                except KeyError:
                    book[chapter] = DotMap()
                    book[chapter][verseno] = Verse(
                        verseno, chapter, book_name, verse, self.version
                    )
        self.content[book_name] = book

    def load(self, app):
        """
        Load content.

        We can get this from a database later.
        """
        import os

        print(os.getcwd())
        fn = Path(app.root_path) / "../bible/vulgate.txt"
        self.from_file(fn)
