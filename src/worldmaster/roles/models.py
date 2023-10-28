from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Generic, Self, TypeVar

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser, AnonymousUser
    from django.db.models.manager import RelatedManager
    from worldmaster.worldmaster.models import User
else:
    User = get_user_model()

class RoleTarget(models.Model):
    """A hierarchical role target.

    This allows hierarchical permissions checking without having to inspect
    other apps.

    All models that want to have roles applied and checked on them should
    reference this.
    """

    id: int

    parent: models.ForeignKey[RoleTarget | None, RoleTarget | None] = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        help_text="The parent of this RoleTarget, if it's not a root",
        blank=True,
        null=True,
        default=None,
        related_name="children",
    )

    children: RelatedManager[RoleTarget]

    users: models.ManyToManyField[User, User] = models.ManyToManyField(
        User,
        related_name="role_targets",
        related_query_name="role_target",
        through="Role",
        through_fields=("target", "user"),
    )

    roles: RelatedManager[Role]

    def user_is_role(self, user: AbstractUser | AnonymousUser, type: Role.Type) -> bool:
        """Return True if the user counts as this role.

        This is true if this user or the NULL user has the role on this target,
        or if the user is a superuser.
        """
        # Superuser is always all roles
        if user.is_superuser:
            return True

        user_check = models.Q(user=None)

        if user.is_authenticated:
            user_check |= models.Q(user=user)

        return self.roles.filter(
            user_check,
            type=type,
        ).exists()

    def user_is_master(self, user: AbstractUser | AnonymousUser) -> bool:
        """Return True if the user has the MASTER role on this or any ancestor."""
        return self.user_is_role(user, Role.Type.MASTER)

    def user_is_editor(self, user: AbstractUser | AnonymousUser):
        """If the user has EDITOR on this."""
        return self.user_is_role(user, Role.Type.EDITOR)

    def user_is_viewer(self, user: AbstractUser | AnonymousUser):
        """If the user has VIEWER on this."""
        return self.user_is_role(user, Role.Type.VIEWER)

    def _delete_implicit_roles(self, recursive: bool = True):
        """Delete the implicit roles for this role target and optionally its
        children.
        """
        self.roles.filter(explicit=False).delete()

        if recursive:
            for child in self.children.all():
                child._delete_implicit_roles()

    def _setup_implicit_roles(self, recursive: bool = True):
        """Set up implicit roles for a role target.
        """
        parent = self.parent

        user_id: int
        type: Role.Type

        # Inherited roles first.
        if parent is not None:
            for user_id, type in self.roles.filter(
                type__in=Role._INHERITED,
            ).values_list("user_id", "type"):
                self.roles.get_or_create(
                    type=type,
                    user_id=user_id,
                    defaults={
                        "explicit": False,
                    },
                )

        # Then sub-roles.
        for user_id, type in self.roles.filter(
            type__in=Role._SUB.keys(),
        ).values_list(
            "user_id",
            "type",
        ):
            for sub in Role._SUB[type]:
                self.roles.get_or_create(
                    type=sub,
                    user_id=user_id,
                    defaults={
                        "explicit": False,
                    },
                )

        if recursive:
            for child in self.children.all():
                child._setup_implicit_roles()

class Role(models.Model):
    """A role, giving a user specific privileges on a specific target."""

    class Type(models.IntegerChoices):
        # Admin permission on the item.  This is not called "owner", because
        # it doesn't just imply ownership, but full admin access, applied
        # transitively.  A MASTER on some object gets MASTER access on all sub-
        # objects as well.
        # The MASTER role needed to delete non-leaf objects, like Wiki articles,
        # because otherwise an EDITOR could delete sections they don't know
        # are there.
        MASTER = 1, _("Master")

        # Allows editing and adding children to things.
        # On a Wiki: Allows adding sections.
        # On a Wiki section: Allows modifying or deleting the section.
        # On a Plane: Allows adding entities.
        # On a World: Allows adding Planes.
        EDITOR = 2, _("Editor")

        # Simply allows seeing some object.
        VIEWER = 3, _("Viewer")

    # A map from a Role type to all the Role types that it implicitly-grants.
    # Role.Types don't include themselves.
    # A signal automatically grants the sub-roles.
    _SUB: Mapping[Type, frozenset[Type]] = {
        Type.MASTER: frozenset((Type.EDITOR, Type.VIEWER)),
        Type.EDITOR: frozenset((Type.VIEWER,)),
        Type.VIEWER: frozenset(),
    }

    # Roles that are inherited from parent roletargets.
    _INHERITED: frozenset[Type] = frozenset((
        Type.MASTER,
    ))

    id: int

    target: models.ForeignKey[RoleTarget, RoleTarget] = models.ForeignKey(
        RoleTarget,
        on_delete=models.CASCADE,
        help_text="The target for this role",
        blank=False,
        null=False,
        related_name="roles",
        related_query_name="role",
    )
    user: models.ForeignKey[User, User] = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user with this role.  If NULL, allows anonymous access to the role.",
        blank=True,
        null=True,
        related_name="roles",
        related_query_name="role",
    )

    type: models.PositiveSmallIntegerField[Type, Type] = models.PositiveSmallIntegerField(
        help_text="The role type, like owner, editor, viewer, etc",
        choices=Type.choices,
        blank=False,
        null=False,
    )

    explicit: models.BooleanField[bool, bool] = models.BooleanField(
        blank=False,
        null=False,
        help_text="Whether this is a manually-applied role.  If this is False, then the role is inherited or implied.",
        default=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["target", "user", "type"], name="unique_role_target_user_type"),
        ]

    def __str__(self) -> str:
        return f"<Role: {self.user.username!r} {self.type!r} {self.target!r}>"

    @classmethod
    def rebuild(cls: type[Self]) -> None:
        """Rebuild all implicit roles.
        """
        cls.objects.filter(explicit=False).delete()
        # This is a naive implementation.  We could probably do better by
        # Sharing some implementation between the signals and this.
        for role in cls.objects.all():
            role.save()

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

        user_check = models.Q(role_target__role__user=None)

        if user.is_authenticated:
            user_check |= models.Q(role_target__role__user=user)

        return self.filter(
            user_check,
            role_target__role__type=type,
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
