from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from worlds import models as worlds
from wiki import models as wiki

class User(AbstractUser):
    '''The concrete user model.

    This currently doesn't do anything over the regular django user model.  This
    just makes it easier to add fields later.
    '''
