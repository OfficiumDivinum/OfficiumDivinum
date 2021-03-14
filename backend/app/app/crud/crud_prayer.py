from app import models, schemas

from .base import CRUDWithOwnerBase


class CRUDPrayerPrayer(
    CRUDWithOwnerBase[
        models.prayer.Prayer, schemas.prayer.PrayerCreate, schemas.prayer.PrayerUpdate
    ]
):
    pass


prayer = CRUDPrayerPrayer(models.prayer.Prayer)
