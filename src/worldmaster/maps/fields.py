from django.contrib.gis.db.models.fields import GeometryField, MultiPolygonField
from django.utils.translation import gettext_lazy as _


class PolyhedralSurfaceField(GeometryField):
    geom_type = "POLYHEDRALSURFACE"
    geom_class = MultiPolygonField.geom_class
    form_class = MultiPolygonField.form_class
    description = _("Polyhedral Surface")

    def __init__(self, *args, dim=3, **kwargs) -> None:
        super().__init__(*args, dim=dim, **kwargs)

