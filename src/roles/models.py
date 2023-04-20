from __future__ import annotations

from typing import TypeVar

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.contrib.auth import get_user_model

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
        related_name='children',
    )

    users = models.ManyToManyField(
        User,
        related_name='role_targets',
        related_query_name='role_target',
        through='Role',
        through_fields=('target', 'user'),
    )

    def user_is_role(self, user: AbstractUser | AnonymousUser, type: Role.Type) -> bool:
        '''Return True if the user counts as this role.
        
        This is true if this user or the NULL user has the role on this target,
        or if the user is a superuser.
        '''
        # Superuser is always all roles
        if user.is_superuser:
            return True

        elif user.is_authenticated:
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

        return False

    def user_is_master(self, user: AbstractUser | AnonymousUser) -> bool:
        '''Returns True if the user has the MASTER role on this.
        '''
        return self.user_is_role(user, Role.Type.MASTER)

    def user_is_editor(self, user: AbstractUser | AnonymousUser):
        '''If the user has EDITOR on this.
        '''
        return self.user_is_role(user, Role.Type.EDITOR)

    def user_is_viewer(self, user: AbstractUser | AnonymousUser):
        '''If the user has VIEWER on this.
        '''
        return self.user_is_role(user, Role.Type.VIEWER)

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


    target = models.ForeignKey(
        RoleTarget,
        on_delete=models.CASCADE,
        help_text='The target for this role',
        blank=False,
        null=False,
        related_name='roles',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='The user with this role.  If NULL, allows anonymous access to the role.',
        blank=True,
        null=True,
        related_name='roles',
    )
    type = models.SlugField(
        max_length=16,
        help_text='The role type, like owner, editor, viewer, etc',
        choices=Type.choices,
        blank=False,
        null=False,
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['target', 'user', 'type'], name='unique_role_target_user_type'),
        ]

    def __str__(self) -> str:
        return f'<Role: {repr(self.user.username)} {repr(self.type)} {repr(self.target)}>'

    __repr__ = __str__


Subclass = TypeVar('Subclass', bound='RoleTargetBase')

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

    @classmethod
    def visible_to(cls: type[Subclass], user: AbstractUser | AnonymousUser) -> models.QuerySet[Subclass]:
        if user.is_superuser:
            return cls.objects.all()
        elif user.is_anonymous:
            return cls.objects.filter(
                role_target__roles__type=Role.Type.VIEWER,
                role_target__roles__user=None,
            )
        else:
            return cls.objects.filter(
                models.Q(role_target__roles__user=None) | models.Q(role_target__roles__user=user),
                role_target__roles__type=Role.Type.VIEWER,
            )
