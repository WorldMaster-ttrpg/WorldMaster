from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth import get_user_model
from worldmaster import models as worldmaster

User = get_user_model()

class RoleTarget(models.Model):
    '''A hierarchical role target.

    This allows hierarchical permissions checking without having to inspect
    other apps.

    All models that want to have roles applied and checked on them should
    reference this.
    '''

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        help_text="The parent of this RoleTarget, if it's not a root",
        blank=True,
        null=True,
        default=None,
    )

    def user_is_master(self, user: worldmaster.User) -> bool:
        # Superuser is always all roles
        if user.is_superuser:
            return True

        if user.is_authenticated:
            if Role.objects.filter(
                user=user,
                type=Role.Type.MASTER,
                target=self,
            ).exists():
                return True
        else:
            # We do not allow anonymous masters.  We should probably hard-
            # disallow anonymous editor or player as well.
            return False

        parent: RoleTarget | None = self.parent
        if parent is not None:
            return parent.user_is_master(user)

        return False

    def _user_is_role(self, user: worldmaster.User, type: Role.Type) -> bool:
        # Superuser is always all roles
        if user.is_superuser:
            return True

        if user.is_authenticated:
            query = models.Q(
                models.Q(user=None) | models.Q(user=user),
                type=type,
                target=self,
            )
        else:
            query = models.Q(
                user=None,
                type=type,
                target=self,
            )

        if Role.objects.filter(query).exists():
            return True

        # Master of this or any parent is also all roles
        return self.user_is_master(user)

    def user_can_edit(self, user: worldmaster.User):
        '''If the user has EDITOR or MASTER on the target or MASTER on any ancestor.
        '''
        return self._user_is_role(user, Role.Type.EDITOR)

    def user_can_view(self, user: worldmaster.User):
        '''If the user has VIEWER or MASTER on the target or MASTER on any ancestor.
        '''
        return self._user_is_role(user, Role.Type.VIEWER)

class Role(models.Model):
    '''A role, giving a user specific privileges on a specific target.
    '''

    class Type(models.TextChoices):
        # Admin permission on the item.  This is not called "owner", because
        # it doesn't just imply ownership, but full admin access, applied
        # transitively.  A MASTER on some object gets MASTER access on all sub-
        # objects as well.
        # The MASTER role needed to delete non-leaf objects, like Wiki articles,
        # because otherwise an EDITOR could delete sections they don't know
        # are there.
        MASTER = 'master', _('Master')

        # Allows editing and adding children to things.
        # On a Wiki: Allows adding sections.
        # On a Wiki section: Allows modifying or deleting the section.
        # On a Plane: Allows adding entities.
        # On a World: Allows adding Planes.
        EDITOR = 'editor', _('Editor')

        # Simply allows seeing some object.
        VIEWER = 'viewer', _('Viewer')

    # TODO: Use constraints to forbid anonymous EDITOR and MASTER roles
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='The user with this role.  If NULL, allows anonymous access to the role.',
        blank=True,
        null=True,
    )
    type = models.SlugField(
        max_length=16,
        help_text='The role type, like owner, editor, viewer, etc',
        choices=Type.choices,
        blank=False,
        null=False,
    )
    target = models.ForeignKey(
        RoleTarget,
        on_delete=models.CASCADE,
        help_text='The target for this role',
        blank=False,
        null=False,
    )

    def __str__(self) -> str:
        return f'<Role: {repr(self.user.username)} {repr(self.type)} {repr(self.target)}>'

    __repr__ = __str__

class RoleTargetBase(models.Model):
    '''An abstract base that gives a role_target field to a model.
    '''

    role_target = models.ForeignKey(
        RoleTarget,
        null=False,
        blank=False,
        on_delete=models.RESTRICT,
        related_name='+',
    )

    class Meta:
        abstract = True
