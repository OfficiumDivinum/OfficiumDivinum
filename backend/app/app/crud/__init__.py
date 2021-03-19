from .crud_bible import bible  # noqa
from .crud_calendar import commemoration, feast  # noqa
from .crud_hymn import hymn, hymn_verse  # noqa
from .crud_item import item  # noqa
from .crud_martyrology import martyrology, old_date_template, ordinals  # noqa
from .crud_user import user  # noqa
from .office_parts import *  # noqa

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
