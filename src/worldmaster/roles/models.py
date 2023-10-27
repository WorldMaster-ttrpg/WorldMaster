from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from django.contrib.auth import get_user_model
from django.db import connection, models
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _
from worldmaster.jinja import get_template

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser, AnonymousUser

User = get_user_model()


class RoleTarget(models.Model):
    """A hierarchical role target.

    This allows hierarchical permissions checking without having to inspect
    other apps.

    All models that want to have roles applied and checked on them should
    reference this.
    """

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        help_text="The parent of this RoleTarget, if it's not a root",
        blank=True,
        null=True,
        default=None,
        related_name="children",
    )

    users = models.ManyToManyField(
        User,
        related_name="role_targets",
        related_query_name="role_target",
        through="Role",
        through_fields=("target", "user"),
    )

    def user_roles(self, user: AbstractUser | AnonymousUser) -> frozenset[Role.Type]:
        if user.is_superuser:
            # Superuser automatically has all roles on everything.
            return frozenset((
                Role.Type.MASTER,
                Role.Type.EDITOR,
                Role.Type.VIEWER,
            ))

        template = get_template("roles/user_roles.sql")
        vars = []
        sql = template.render(
            roletarget=self,
            user=user,
            vars=vars,
        )
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            return frozenset(row[0] for row in cursor.fetchall())


    def user_is_role(self, user: AbstractUser | AnonymousUser, type: Role.Type) -> bool:
        """Return True if the user counts as this role.

        This is true if this user or the NULL user has the role on this target,
        or if the user is a superuser.
        """
        return type in self.user_roles(user)

    def user_is_master(self, user: AbstractUser | AnonymousUser) -> bool:
        """Return True if the user has the MASTER role on this or any ancestor."""
        return self.user_is_role(user, Role.Type.MASTER)

    def user_is_editor(self, user: AbstractUser | AnonymousUser):
        """If the user has EDITOR on this."""
        return self.user_is_role(user, Role.Type.EDITOR)

    def user_is_viewer(self, user: AbstractUser | AnonymousUser):
        """If the user has VIEWER on this."""
        return self.user_is_role(user, Role.Type.VIEWER)

class Role(models.Model):
    """A role, giving a user specific privileges on a specific target."""

    class Type(models.TextChoices):
        # Admin permission on the item.  This is not called "owner", because
        # it doesn't just imply ownership, but full admin access, applied
        # transitively.  A MASTER on some object gets MASTER access on all sub-
        # objects as well.
        # The MASTER role needed to delete non-leaf objects, like Wiki articles,
        # because otherwise an EDITOR could delete sections they don't know
        # are there.
        MASTER = "master", _("Master")

        # Allows editing and adding children to things.
        # On a Wiki: Allows adding sections.
        # On a Wiki section: Allows modifying or deleting the section.
        # On a Plane: Allows adding entities.
        # On a World: Allows adding Planes.
        EDITOR = "editor", _("Editor")

        # Simply allows seeing some object.
        VIEWER = "viewer", _("Viewer")


    target = models.ForeignKey(
        RoleTarget,
        on_delete=models.CASCADE,
        help_text="The target for this role",
        blank=False,
        null=False,
        related_name="roles",
        related_query_name="role",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user with this role.  If NULL, allows anonymous access to the role.",
        blank=True,
        null=True,
        related_name="roles",
        related_query_name="role",
    )
    type = models.SlugField(
        max_length=16,
        help_text="The role type, like owner, editor, viewer, etc",
        choices=Type.choices,
        blank=False,
        null=False,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["target", "user", "type"], name="unique_role_target_user_type"),
        ]

    def __str__(self) -> str:
        return f"<Role: {self.user.username!r} {self.type!r} {self.target!r}>"

    __repr__ = __str__


Model = TypeVar("Model", bound="RoleTargetBase")

class RoleTargetManager(models.Manager, Generic[Model]):
    def with_role(
        self: RoleTargetManager[Model],
        user: AbstractUser | AnonymousUser,
        type: Role.Type,
    ) -> models.QuerySet[Model]:
        if user.is_superuser:
            return self.all()

        template = get_template("roles/with_role.sql")
        vars = []
        sql = template.render(
            user=user,
            role_type=type.value,
            table=self.model._meta.db_table,
            vars=vars,
        )

        return self.filter(
            role_target__id__in=RawSQL(sql, vars),
        )

    def mastered_by(self: RoleTargetManager[Model], user: AbstractUser | AnonymousUser) -> models.QuerySet[Model]:
        return self.with_role(user, Role.Type.MASTER)

    def editable_by(self: RoleTargetManager[Model], user: AbstractUser | AnonymousUser) -> models.QuerySet[Model]:
        return self.with_role(user, Role.Type.EDITOR)

    def visible_to(self: RoleTargetManager[Model], user: AbstractUser | AnonymousUser) -> models.QuerySet[Model]:
        return self.with_role(user, Role.Type.VIEWER)

class RoleTargetBase(models.Model):
    """An abstract base that gives a role_target field to a model."""

    # ForeignKey instead of OneToOneField because World models and their wiki
    # articles share role targets
    role_target = models.ForeignKey(
        RoleTarget,
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
        related_name="+",
    )

    class Meta:
        abstract = True
