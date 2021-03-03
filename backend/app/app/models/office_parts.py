from sqlalchemy import Column, Integer, String


class BlockMixin:
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    rubrics = Column(String, index=True)


class LineMixin:
    id = Column(Integer, primary_key=True, index=True)
    rubrics = Column(String, index=True)
    prefix = Column(String, index=True)
    suffix = Column(String, index=True)
    content = Column(String, index=True)


class FromDOMixin:
    sourcefile = Column(String, index=True)
    at = Column(String, index=True)
