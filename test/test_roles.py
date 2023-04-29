from typing import cast, TYPE_CHECKING
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from roles.models import RoleTarget, Role
from django.contrib.auth import get_user_model
from worlds.models import World, Plane
from wiki.models import Article

if TYPE_CHECKING:
    from worldmaster import models as worldmaster

User = cast(type['worldmaster.User'], get_user_model())

class RoleTestCase(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='test')
        self.user.set_unusable_password()

        self.anonymous_user = AnonymousUser()

        self.other_user = User.objects.create(username='othertest')
        self.other_user.set_unusable_password()

        self.world = World.objects.create(
            slug='world',
            name='World',
        )
        self.plane = Plane.objects.create(
            world=self.world,
            slug='plane',
            name='Plane',
        )
        self.article: Article = self.plane.article

        self.world_target: RoleTarget = self.world.role_target
        self.plane_target: RoleTarget = self.plane.role_target
        self.article_target: RoleTarget = self.article.role_target

    def test_master_inherit(self):
        Role.objects.create(
            target=self.world_target,
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.user,
            )
        )
        self.assertFalse(
            self.article_target.user_is_master(
                user=self.other_user,
            )
        )

        self.assertFalse(
            self.article_target.user_is_master(
                user=self.anonymous_user,
            )
        )

        self.assertIn(self.world, World.mastered_by(self.user))
        self.assertNotIn(self.world, World.mastered_by(self.other_user))
        self.assertNotIn(self.world, World.mastered_by(self.anonymous_user))

        self.assertIn(self.plane, Plane.mastered_by(self.user))
        self.assertNotIn(self.plane, Plane.mastered_by(self.other_user))
        self.assertNotIn(self.plane, Plane.mastered_by(self.anonymous_user))

        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))

    def test_other_not_inherit(self):
        for type in Role.Type:
            if type is not Role.Type.MASTER:
                if not Role.objects.filter(
                    target=self.world_target,
                    user=self.user,
                    type=type,
                ).exists():
                    Role.objects.create(
                        target=self.world_target,
                        user=self.user,
                        type=type,
                    )

                self.assertFalse(
                    self.plane_target.user_is_role(
                        user=self.user,
                        type=type,
                    )
                )
                self.assertIn(self.world, World.with_role(self.user, type))
                self.assertNotIn(self.world, World.with_role(self.other_user, type))
                self.assertNotIn(self.world, World.with_role(self.anonymous_user, type))

                self.assertNotIn(self.plane, Plane.with_role(self.user, type))
                self.assertNotIn(self.plane, Plane.with_role(self.other_user, type))
                self.assertNotIn(self.plane, Plane.with_role(self.anonymous_user, type))

                self.assertNotIn(self.article, Article.with_role(self.user, type))
                self.assertNotIn(self.article, Article.with_role(self.other_user, type))
                self.assertNotIn(self.article, Article.with_role(self.anonymous_user, type))
        
    def test_master_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertNotIn(self.article, Article.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertNotIn(self.article, Article.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.visible_to(self.anonymous_user))

    def test_master_implied_inherited(self):
        Role.objects.create(
            target=self.world_target,
            user=self.user,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertNotIn(self.article, Article.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertNotIn(self.article, Article.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.visible_to(self.anonymous_user))

    def test_editor_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=self.user,
            type=Role.Type.EDITOR,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertNotIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertNotIn(self.article, Article.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertNotIn(self.article, Article.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.visible_to(self.anonymous_user))

    def test_viewer_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=self.user,
            type=Role.Type.VIEWER,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertNotIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertNotIn(self.article, Article.editable_by(self.user))
        self.assertNotIn(self.article, Article.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertNotIn(self.article, Article.visible_to(self.other_user))
        self.assertNotIn(self.article, Article.visible_to(self.anonymous_user))

    def test_anonymous_master_inherit(self):
        Role.objects.create(
            target=self.world_target,
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.user,
            )
        )
        self.assertTrue(
            self.article_target.user_is_master(
                user=self.other_user,
            )
        )

        self.assertTrue(
            self.article_target.user_is_master(
                user=self.anonymous_user,
            )
        )
        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertIn(self.article, Article.mastered_by(self.other_user))
        self.assertIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertIn(self.article, Article.editable_by(self.other_user))
        self.assertIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertIn(self.article, Article.visible_to(self.other_user))
        self.assertIn(self.article, Article.visible_to(self.anonymous_user))

    def test_anonymous_other_not_inherit(self):
        for type in Role.Type:
            if type is not Role.Type.MASTER:
                if not Role.objects.filter(
                    target=self.world_target,
                    user=None,
                    type=type,
                ).exists():
                    Role.objects.create(
                        target=self.world_target,
                        user=None,
                        type=type,
                    )

                self.assertFalse(
                    self.plane_target.user_is_role(
                        user=self.user,
                        type=type,
                    )
                )
                self.assertFalse(
                    self.article_target.user_is_role(
                        user=self.user,
                        type=type,
                    )
                )
                self.assertIn(self.world, World.with_role(self.user, type))
                self.assertIn(self.world, World.with_role(self.other_user, type))
                self.assertIn(self.world, World.with_role(self.anonymous_user, type))

                self.assertNotIn(self.plane, Plane.with_role(self.user, type))
                self.assertNotIn(self.plane, Plane.with_role(self.other_user, type))
                self.assertNotIn(self.plane, Plane.with_role(self.anonymous_user, type))

                self.assertNotIn(self.article, Article.with_role(self.user, type))
                self.assertNotIn(self.article, Article.with_role(self.other_user, type))
                self.assertNotIn(self.article, Article.with_role(self.anonymous_user, type))
        
    def test_anonymous_master_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertIn(self.article, Article.mastered_by(self.other_user))
        self.assertIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertIn(self.article, Article.editable_by(self.other_user))
        self.assertIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertIn(self.article, Article.visible_to(self.other_user))
        self.assertIn(self.article, Article.visible_to(self.anonymous_user))

    def test_anonymous_master_implied_inherited(self):
        Role.objects.create(
            target=self.world_target,
            user=None,
            type=Role.Type.MASTER,
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertIn(self.article, Article.mastered_by(self.user))
        self.assertIn(self.article, Article.mastered_by(self.other_user))
        self.assertIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertIn(self.article, Article.editable_by(self.other_user))
        self.assertIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertIn(self.article, Article.visible_to(self.other_user))
        self.assertIn(self.article, Article.visible_to(self.anonymous_user))

    def test_anonymous_editor_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=None,
            type=Role.Type.EDITOR,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertNotIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertIn(self.article, Article.editable_by(self.user))
        self.assertIn(self.article, Article.editable_by(self.other_user))
        self.assertIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertIn(self.article, Article.visible_to(self.other_user))
        self.assertIn(self.article, Article.visible_to(self.anonymous_user))

    def test_anonymous_viewer_implied(self):
        Role.objects.create(
            target=self.article_target,
            user=None,
            type=Role.Type.VIEWER,
        )

        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.other_user,
                type=Role.Type.VIEWER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.MASTER,
            )
        )
        self.assertFalse(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.EDITOR,
            )
        )
        self.assertTrue(
            self.article_target.user_is_role(
                user=self.anonymous_user,
                type=Role.Type.VIEWER,
            )
        )

        self.assertNotIn(self.article, Article.mastered_by(self.user))
        self.assertNotIn(self.article, Article.mastered_by(self.other_user))
        self.assertNotIn(self.article, Article.mastered_by(self.anonymous_user))
        self.assertNotIn(self.article, Article.editable_by(self.user))
        self.assertNotIn(self.article, Article.editable_by(self.other_user))
        self.assertNotIn(self.article, Article.editable_by(self.anonymous_user))
        self.assertIn(self.article, Article.visible_to(self.user))
        self.assertIn(self.article, Article.visible_to(self.other_user))
        self.assertIn(self.article, Article.visible_to(self.anonymous_user))

