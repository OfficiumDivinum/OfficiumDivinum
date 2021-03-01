# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.bible import Verse  # noqa
from app.models.calendar import *  # noqa
from app.models.hymn import *  # noqa
from app.models.item import Item  # noqa
from app.models.martyrology import *  # noqa
from app.models.user import User  # noqa
