from __future__ import annotations

from django.contrib.auth.models import AbstractUser, UserManager


class User(AbstractUser):
    """The concrete user model.

    This currently doesn't do anything over the regular django user model.  This
    just makes it easier to add fields later.
    """

    objects = UserManager()
