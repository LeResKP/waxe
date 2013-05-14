import unittest
from pyramid import testing
from ..testing import WaxeTestCase, login_user
from mock import patch
from ..models import DBSession, User, UserConfig, Role, ROLE_EDITOR
from ..views.index import (
    Views,
    HTTPBadRequest,
    JSONHTTPBadRequest,
    bad_request
)

class TestViews(WaxeTestCase):

    def setUp(self):
        super(TestViews, self).setUp()
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()
        super(TestViews, self).tearDown()

    def test_class_init(self):
        request = testing.DummyRequest(root_path=None)
        class C(object): pass
        request.matched_route = C()
        request.matched_route.name = 'route'
        try:
            Views(request)
            assert 0
        except HTTPBadRequest, e:
            self.assertEqual(str(e), 'root path not given')

        request.matched_route.name = 'route_json'
        try:
            Views(request)
            assert 0
        except JSONHTTPBadRequest, e:
            self.assertEqual(str(e), 'root path not given')

        request.matched_route.name = 'login_selection'
        o = Views(request)
        self.assertEqual(o.request, request)

    def test_home(self):
        request = testing.DummyRequest(root_path='/path')
        res = Views(request).home()
        self.assertEqual(res,
                         {'content': 'home content<br/>Root path: /path'})

    def test_login_selection(self):
        DBSession.add(self.user_bob)
        request = testing.DummyRequest(root_path='/path', user=self.user_bob)
        try:
            res = Views(request).login_selection()
            assert 0
        except HTTPBadRequest, e:
            self.assertEqual(str(e), 'Invalid login')

        request = testing.DummyRequest(root_path='/path', user=self.user_bob,
                                       params={'login': 'editor'})
        try:
            res = Views(request).login_selection()
            assert 0
        except HTTPBadRequest, e:
            self.assertEqual(str(e), 'Invalid login')

        editor = User(login='editor', password='pass1')
        editor.roles = [Role.query.filter_by(name=ROLE_EDITOR).one()]
        editor.config = UserConfig(root_path='/path')
        DBSession.add(editor)

        res = Views(request).login_selection()
        self.assertEqual(res.status, "302 Found")
        self.assertEqual(res.location, '/')

    def test_bad_request(self):
        DBSession.add(self.user_bob)
        request = testing.DummyRequest(user=self.user_bob)
        dic = bad_request(request)
        self.assertEqual(len(dic), 1)
        self.assertTrue('There is a problem with your configuration' in
                        dic['content'])

        editor = User(login='editor', password='pass1')
        editor.roles = [Role.query.filter_by(name=ROLE_EDITOR).one()]
        editor.config = UserConfig(root_path='/path')
        DBSession.add(editor)

        # TODO: try to find why there is TopLevelLookupException
        # dic = bad_request(request)


class FunctionalTestViews(WaxeTestCase):

    def test_home_forbidden(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(
            res.location,
            'http://localhost/login?next=http%3A%2F%2Flocalhost%2F')
        res = res.follow()
        self.assertEqual(res.status, "200 OK")
        self.assertTrue('<form' in res.body)
        self.assertTrue('Login' in res.body)

    @login_user('Fred')
    def test_home_bad_login(self):
        res = self.testapp.get('/', status=302)
        self.assertEqual(res.location,
                         'http://localhost/forbidden')

    @login_user('Bob')
    def test_home(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(
            'There is a problem with your configuration' in res.body)
        self.assertTrue(('Content-Type', 'text/html; charset=UTF-8') in
                        res._headerlist)

        DBSession.remove()
        DBSession.add(self.user_bob)
        self.user_bob.config = UserConfig(root_path='/path')
        res = self.testapp.get('/', status=200)
        self.assertTrue('home content' in res.body)
        self.assertTrue(('Content-Type', 'text/html; charset=UTF-8') in
                        res._headerlist)

    @login_user('Bob')
    def test_home_json(self):
        res = self.testapp.get('/home.json', status=200)
        self.assertTrue(
            'There is a problem with your configuration' in res.body)
        self.assertTrue(('Content-Type', 'application/json; charset=UTF-8') in
                        res._headerlist)

        DBSession.remove()
        DBSession.add(self.user_bob)
        self.user_bob.config = UserConfig(root_path='/path')
        res = self.testapp.get('/home.json', status=200)
        self.assertTrue('home content' in res.body)
        self.assertTrue(('Content-Type', 'application/json; charset=UTF-8') in
                        res._headerlist)

    def test_login_selection_forbidden(self):
        res = self.testapp.get('/login-selection', status=302)
        self.assertEqual(
            res.location,
            'http://localhost/login?next=http%3A%2F%2Flocalhost%2Flogin-selection')
        res = res.follow()
        self.assertEqual(res.status, "200 OK")
        self.assertTrue('<form' in res.body)
        self.assertTrue('Login' in res.body)

    @login_user('Bob')
    def test_login_selection(self):
        res = self.testapp.get('/login-selection', status=200)
        self.assertTrue('There is a problem with your configuration' in
                        res.body)
