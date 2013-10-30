import logging
import xmltool
import json
from urllib2 import HTTPError
from pyramid.view import view_config
from pyramid.renderers import render
from .. import browser
from ..utils import unflatten_params
from base import BaseUserView

log = logging.getLogger(__name__)


def _get_tags(dtd_url):
    dic = xmltool.dtd_parser.parse(dtd_url=dtd_url)
    lis = []
    for k, v in dic.items():
        if issubclass(v, xmltool.elements.TextElement):
            continue
        lis += [k]
    lis.sort()
    return lis


class EditorView(BaseUserView):

    @view_config(route_name='edit', renderer='index.mak', permission='edit')
    @view_config(route_name='edit_json', renderer='json', permission='edit')
    def edit(self):
        filename = self.request.GET.get('filename') or ''
        if not filename:
            return {
                'error_msg': 'A filename should be provided',
            }
        root_path = self.root_path
        absfilename = browser.absolute_path(filename, root_path)
        try:
            obj = xmltool.load(absfilename)
            html = xmltool.generate_form_from_obj(
                obj,
                form_filename=filename,
                form_attrs={
                    'data-add-href': self.request.route_path('add_element_json'),
                    'data-comment-href': self.request.route_path('get_comment_modal_json'),
                    'data-href': self.request.route_path('update_json'),
                }
            )
            jstree_data = obj.to_jstree_dict([])
            if not self._is_json():
                jstree_data = json.dumps(jstree_data)
        except HTTPError, e:
            log.exception(e)
            return {
                'error_msg': 'The dtd of %s can\'t be loaded.' % filename
            }
        except Exception, e:
            log.exception(e)
            return {
                'error_msg': str(e)
            }
        breadcrumb = self._get_breadcrumb(filename)
        return {
            'content': html,
            'breadcrumb': breadcrumb,
            'jstree_data': jstree_data,
        }

    @view_config(route_name='get_tags_json', renderer='json', permission='edit')
    def get_tags(self):
        dtd_url = self.request.GET.get('dtd_url', None)

        if not dtd_url:
            return {}

        return {'tags': _get_tags(dtd_url)}

    @view_config(route_name='new_json', renderer='json', permission='edit')
    def new(self):
        dtd_url = self.request.GET.get('dtd_url') or None
        dtd_tag = self.request.GET.get('dtd_tag') or None

        if dtd_tag and dtd_url:
            html = xmltool.new(
                dtd_url,
                dtd_tag,
                form_attrs={
                    'data-add-href': self.request.route_path('add_element_json'),
                    'data-comment-href': self.request.route_path('get_comment_modal_json'),
                    'data-href': self.request.route_path('update_json'),
                })
            return {
                'content': html,
                'breadcrumb': self._get_breadcrumb(None, force_link=True),
            }

        content = render('blocks/new.mak',
                         {'dtd_urls': self.request.dtd_urls,
                          'tags': _get_tags(self.request.dtd_urls[0])},
                         self.request)
        return {'content': content}

    @view_config(route_name='update_json', renderer='json', permission='edit')
    def update(self):
        filename = self.request.POST.pop('_xml_filename', None)
        if not filename:
            return {'status': False, 'error_msg': 'No filename given'}

        root_path = self.root_path
        absfilename = browser.absolute_path(filename, root_path)
        try:
            xmltool.update(absfilename, self.request.POST)
        except Exception, e:
            log.exception(e)
            return {'status': False, 'error_msg': str(e)}

        return {
            'status': True,
            'breadcrumb': self._get_breadcrumb(filename)
        }

    @view_config(route_name='update_text_json', renderer='json', permission='edit')
    def update_text(self):
        filecontent = self.request.POST.get('filecontent')
        filename = self.request.POST.get('filename') or ''
        if not filecontent or not filename:
            return {'status': False, 'error_msg': 'Missing parameters!'}
        root_path = self.root_path
        absfilename = browser.absolute_path(filename, root_path)
        try:
            obj = xmltool.load_string(filecontent)
            obj.write(absfilename)
        except Exception, e:
            return {'status': False, 'error_msg': str(e)}

        content = 'File updated'
        if self.request.POST.get('commit'):
            content = render('blocks/commit_modal.mak',
                             {}, self.request)

        return {'status': True, 'content': content}

    @view_config(route_name='update_texts_json', renderer='json', permission='edit')
    def update_texts(self):
        params = unflatten_params(self.request.POST)

        if 'data' not in params or not params['data']:
            return {'status': False, 'error_msg': 'Missing parameters!'}

        root_path = self.root_path
        status = True
        error_msgs = []
        for dic in params['data']:
            filecontent = dic['filecontent']
            filename = dic['filename']
            absfilename = browser.absolute_path(filename, root_path)
            try:
                obj = xmltool.load_string(filecontent)
                obj.write(absfilename)
            except Exception, e:
                status = False
                error_msgs += ['%s: %s' % (filename, str(e))]

        if not status:
            return {'status': False, 'error_msg': '<br />'.join(error_msgs)}

        content = 'Files updated'
        if self.request.POST.get('commit'):
            content = render('blocks/commit_modal.mak',
                             {}, self.request)

        return {'status': True, 'content': content}

    @view_config(route_name='add_element_json', renderer='json',
                 permission='edit')
    def add_element_json(self):
        elt_id = self.request.GET.get('elt_id')
        dtd_url = self.request.GET.get('dtd_url')
        if not elt_id or not dtd_url:
            return {'status': False, 'error_msg': 'Bad parameter'}
        dic = xmltool.elements.get_jstree_json_from_str_id(elt_id,
                                                           dtd_url=dtd_url)
        dic['status'] = True
        return dic

    @view_config(route_name='get_comment_modal_json', renderer='json',
                 permission='edit')
    def get_comment_modal_json(self):
        comment = self.request.GET.get('comment') or ''
        content = render('blocks/comment_modal.mak',
                         {'comment': comment}, self.request)
        return {'content': content}


def includeme(config):
    config.add_route('edit', '/edit')
    config.add_route('edit_json', '/edit.json')
    config.add_route('get_tags_json', '/get-tags.json')
    config.add_route('new_json', '/new.json')
    config.add_route('update_json', '/update.json')
    config.add_route('update_text_json', '/update-text.json')
    config.add_route('update_texts_json', '/update-texts.json')
    config.add_route('add_element_json', '/add-element.json')
    config.add_route('get_comment_modal_json', '/get-comment-modal.json')
    config.scan(__name__)
