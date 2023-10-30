from __future__ import annotations

from typing import TYPE_CHECKING, cast

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from django.test import TestCase
from worldmaster.roles.models import Role, RoleTarget
from worldmaster.wiki.models import Article
from worldmaster.worlds.models import Plane, World

if TYPE_CHECKING:
    from worldmaster.worldmaster import models as worldmaster

User = cast(type["worldmaster.User"], get_user_model())

class RoleTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username="test")
        self.user.set_unusable_password()

        self.anonymous_user = AnonymousUser()

        self.other_user = User.objects.create(username="othertest")
        self.other_user.set_unusable_password()

        self.world = World.objects.create(
            slug="world",
            name="World",
        )
        self.plane = self.world.plane_set.create(
            slug="plane",
            name="Plane",
        )
        self.article: Article = self.plane.article

        self.world_target: RoleTarget = self.world.role_target
        self.plane_target: RoleTarget = self.plane.role_target
        self.article_target: RoleTarget = self.article.role_target

    def test_master_inherit(self):
        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.user,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_master(
                user=self.other_user,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_master(
                user=self.anonymous_user,
            ),
        )

        self.assertIn(self.world, World.objects.mastered_by(self.user))
        self.assertNotIn(self.world, World.objects.mastered_by(self.other_user))
        self.assertNotIn(self.world, World.objects.mastered_by(self.anonymous_user))

        self.assertIn(self.plane, Plane.objects.mastered_by(self.user))
        self.assertNotIn(self.plane, Plane.objects.mastered_by(self.other_user))
        self.assertNotIn(self.plane, Plane.objects.mastered_by(self.anonymous_user))

        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))

    def test_other_not_inherit(self):
        for type in Role.Type:
            if type is not Role.Type.MASTER:
                if not self.world_target.roles.filter(
                    user=self.user,
                    type=type,
                ).exists():
                    self.world_target.roles.create(
                        user=self.user,
                        type=type,
                    )

                self.assertFalse(
                    self.plane_target.user_is_role(
                        user=self.user,
                        type=type,
                    ),
                )
                self.assertIn(self.world, World.objects.with_role(self.user, type))
                self.assertNotIn(self.world, World.objects.with_role(self.other_user, type))
                self.assertNotIn(self.world, World.objects.with_role(self.anonymous_user, type))

                self.assertNotIn(self.plane, Plane.objects.with_role(self.user, type))
                self.assertNotIn(self.plane, Plane.objects.with_role(self.other_user, type))
                self.assertNotIn(self.plane, Plane.objects.with_role(self.anonymous_user, type))

                self.assertNotIn(self.article, Article.objects.with_role(self.user, type))
                self.assertNotIn(self.article, Article.objects.with_role(self.other_user, type))
                self.assertNotIn(self.article, Article.objects.with_role(self.anonymous_user, type))

    def test_master_implied(self):
        self.article_target.roles.create(
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_master_implied_inherited(self):
        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_editor_implied(self):
        self.article_target.roles.create(
            user=self.user,
            type=Role.Type.EDITOR,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertNotIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_viewer_implied(self):
        self.article_target.roles.create(
            user=self.user,
            type=Role.Type.VIEWER,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertNotIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_anonymous_master_inherit(self):
        self.world_target.roles.create(
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.user,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_master(
                user=self.other_user,
            ),
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.anonymous_user,
            ),
        )
        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_anonymous_other_not_inherit(self):
        for type in Role.Type:
            if type not in Role._INHERITED:
                self.world_target.roles.get_or_create(
                    user=None,
                    type=type,
                )

                self.assertFalse(
                    self.plane_target.user_is_role(
                        user=self.user,
                        type=type,
                    ),
                )
                self.assertFalse(
                    self.article_target.user_is_role(
                        user=self.user,
                        type=type,
                    ),
                )
                self.assertIn(self.world, World.objects.with_role(self.user, type))
                self.assertIn(self.world, World.objects.with_role(self.other_user, type))
                self.assertIn(self.world, World.objects.with_role(self.anonymous_user, type))

                self.assertNotIn(self.plane, Plane.objects.with_role(self.user, type))
                self.assertNotIn(self.plane, Plane.objects.with_role(self.other_user, type))
                self.assertNotIn(self.plane, Plane.objects.with_role(self.anonymous_user, type))

                self.assertNotIn(self.article, Article.objects.with_role(self.user, type))
                self.assertNotIn(self.article, Article.objects.with_role(self.other_user, type))
                self.assertNotIn(self.article, Article.objects.with_role(self.anonymous_user, type))

    def test_anonymous_master_implied(self):
        self.article_target.roles.create(
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_anonymous_master_implied_inherited(self):
        self.world_target.roles.create(
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertIn(self.article, Article.objects.mastered_by(self.user))
        self.assertIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_anonymous_editor_implied(self):
        self.article_target.roles.create(
            user=None,
            type=Role.Type.EDITOR,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertNotIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.editable_by(self.user))
        self.assertIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertIn(self.article, Article.objects.visible_to(self.anonymous_user))

    def test_anonymous_viewer_implied(self):
        self.article_target.roles.create(
            user=None,
            type=Role.Type.VIEWER,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            ),
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            ),
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            ),
        )

        self.assertNotIn(self.article, Article.objects.mastered_by(self.user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.mastered_by(self.anonymous_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.objects.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.objects.visible_to(self.user))
        self.assertIn(self.article, Article.objects.visible_to(self.other_user))
        self.assertIn(self.article, Article.objects.visible_to(self.anonymous_user))


    def test_no_duplicates(self):
        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.plane_target.roles.get_or_create(
            user=self.user,
            type=Role.Type.EDITOR,
        )

        self.assertEqual(
            Plane.objects.visible_to(self.user).count(),
            1,
        )

    def test_role_delete(self):
        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.VIEWER,
        )
        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertFalse(self.world_target.user_is_editor(self.user))
        self.assertTrue(self.world_target.user_is_viewer(self.user))
        self.assertFalse(self.plane_target.user_is_master(self.user))
        self.assertFalse(self.plane_target.user_is_editor(self.user))
        self.assertFalse(self.plane_target.user_is_viewer(self.user))

        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.EDITOR,
        )
        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertTrue(self.world_target.user_is_editor(self.user))
        self.assertTrue(self.world_target.user_is_viewer(self.user))
        self.assertFalse(self.plane_target.user_is_master(self.user))
        self.assertFalse(self.plane_target.user_is_editor(self.user))
        self.assertFalse(self.plane_target.user_is_viewer(self.user))

        self.world_target.roles.get(
            user=self.user,
            type=Role.Type.VIEWER,
        ).delete()
        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertTrue(self.world_target.user_is_editor(self.user))
        self.assertTrue(self.world_target.user_is_viewer(self.user))
        self.assertFalse(self.plane_target.user_is_master(self.user))
        self.assertFalse(self.plane_target.user_is_editor(self.user))
        self.assertFalse(self.plane_target.user_is_viewer(self.user))

        self.world_target.roles.get(
            user=self.user,
            type=Role.Type.EDITOR,
        ).delete()

        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertFalse(self.world_target.user_is_editor(self.user))
        self.assertFalse(self.world_target.user_is_viewer(self.user))
        self.assertFalse(self.plane_target.user_is_master(self.user))
        self.assertFalse(self.plane_target.user_is_editor(self.user))
        self.assertFalse(self.plane_target.user_is_viewer(self.user))

        self.world_target.roles.create(
            user=self.user,
            type=Role.Type.MASTER,
        )
        self.assertTrue(self.world_target.user_is_master(self.user))
        self.assertTrue(self.world_target.user_is_editor(self.user))
        self.assertTrue(self.world_target.user_is_viewer(self.user))
        self.assertTrue(self.plane_target.user_is_master(self.user))
        self.assertTrue(self.plane_target.user_is_editor(self.user))
        self.assertTrue(self.plane_target.user_is_viewer(self.user))

        self.plane_target.roles.update_or_create(
            user=self.user,
            type=Role.Type.EDITOR,
            defaults={
                "explicit": True,
            },
        )
        self.world_target.roles.get(
            user=self.user,
            type=Role.Type.MASTER,
        ).delete()

        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertFalse(self.world_target.user_is_editor(self.user))
        self.assertFalse(self.world_target.user_is_viewer(self.user))
        self.assertFalse(self.plane_target.user_is_master(self.user))
        self.assertTrue(self.plane_target.user_is_editor(self.user))
        self.assertTrue(self.plane_target.user_is_viewer(self.user))

        self.plane.delete()

        self.assertFalse(self.world_target.user_is_master(self.user))
        self.assertFalse(self.world_target.user_is_editor(self.user))
        self.assertFalse(self.world_target.user_is_viewer(self.user))

    def test_save_implicit_fails(self):
        self.plane_target.roles.create(
            user=self.user,
            type=Role.Type.EDITOR,
        )

        with self.assertRaises(ValidationError):
            # We should never try to save an implicit role.
            self.plane_target.roles.get(
                user=self.user,
                type=Role.Type.VIEWER,
            ).full_clean()

        # We can, however, make an explicit role implicit
        role = self.plane_target.roles.get(
            user=self.user,
            type=Role.Type.VIEWER,
        )
        role.explicit = True
        role.full_clean()
        role.save()


