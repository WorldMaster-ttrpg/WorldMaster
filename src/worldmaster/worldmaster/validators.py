"""Worldmaster-global validators."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_not_reserved(value: str):
    """Ensure that the value does not begin with wm-."""
    if value.startswith("wm-"):
        raise ValidationError(_("wm- is a reserved prefix"))
