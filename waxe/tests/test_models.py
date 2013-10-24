from ..testing import WaxeTestCase, DBSession
from ..models import (
    get_editors,
    get_contributors,
    User,
    Role,
    UserConfig,
    ROLE_EDITOR,
    ROLE_CONTRIBUTOR,
    VersioningPath,
    VERSIONING_PATH_STATUS_ALLOWED,
    VERSIONING_PATH_STATUS_FORBIDDEN
)
from mock import patch


class TestFunctions(WaxeTestCase):

    def test_get_editors(self):
        result = get_editors()
        self.assertEqual(result, [])

        user = User(login='user1', password='pass1')
        user.roles = [Role.query.filter_by(name=ROLE_EDITOR).one()]
        DBSession.add(user)
        result = get_editors()
        self.assertEqual(result, [])

        user.config = UserConfig(root_path='/path')
        DBSession.add(user)
        result = get_editors()
        self.assertEqual(result, [user])

    def test_get_contributor(self):
        result = get_contributors()
        self.assertEqual(result, [])

        user = User(login='user1', password='pass1')
        user.roles = [Role.query.filter_by(name=ROLE_CONTRIBUTOR).one()]
        DBSession.add(user)
        result = get_contributors()
        self.assertEqual(result, [])

        user.config = UserConfig(root_path='/path')
        DBSession.add(user)
        result = get_contributors()
        self.assertEqual(result, [user])


class TestGeneral(WaxeTestCase):

    def test_get_tws_view_html(self):
        DBSession.add(self.user_fred)
        self.assertTrue(self.user_fred.config.get_tws_view_html())

    def test___unicode__(self):
        DBSession.add(self.user_fred)
        role = Role.query.filter_by(name=ROLE_CONTRIBUTOR).one()
        self.assertTrue(unicode(role))
        self.assertTrue(unicode(self.user_fred))
        vp = VersioningPath(
            status=VERSIONING_PATH_STATUS_ALLOWED,
            path='/home/test/')
        self.assertTrue(unicode(vp))


class TestUser(WaxeTestCase):

    def test_has_role(self):
        DBSession.add(self.user_bob)
        self.assertTrue(self.user_bob.has_role('admin'))
        self.assertFalse(self.user_bob.has_role('unexisting'))

    def test_is_admin(self):
        DBSession.add(self.user_bob)
        DBSession.add(self.user_fred)
        self.assertTrue(self.user_bob.is_admin())
        self.assertFalse(self.user_fred.is_admin())

