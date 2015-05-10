import urlparse
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPFound
import pyramid.httpexceptions as exc
from pyramid.renderers import render
from ..models import User
from .. import browser
from .. import models
from base import (
    BaseView,
    BaseUserView,
)


class IndexView(BaseView):

    @view_config(route_name='profile', permission='authenticated')
    def profile(self):
        """Get the profile of the user
        """
        return self.logged_user_profile()


class IndexUserView(BaseUserView):

    @view_config(route_name='account_profile', permission='edit')
    def account_profile(self):
        """Get the profile of the user
        """
        config = self.current_user.config
        if not config:
            return {}
        templates_path = None
        if config.root_template_path:
            templates_path = browser.relative_path(config.root_template_path,
                                                   self.root_path)
        dic = {
            'login': self.current_user.login,
            'has_template_files': bool(config.root_template_path),
            'templates_path': templates_path,
            'has_versioning': self.has_versioning(),
            'has_search': ('whoosh.path' in self.request.registry.settings),
            'has_xml_renderer': ('waxe.renderers' in
                                 self.request.registry.settings),
            'dtd_urls': self.request.registry.settings['dtd_urls'].split(),
        }
        res = {'account_profile': dic}
        if self.req_get.get('full'):
            res['user_profile'] = self.logged_user_profile()
        return res


def includeme(config):
    config.add_route('profile', '/profile.json')
    # TODO: remove hardcoding path
    config.add_route('account_profile',
                     '/account/{login}/account-profile.json')
    config.scan(__name__)
