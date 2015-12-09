# -*- coding: utf-8 -*-
# © 2015 Elico corp (www.elico-corp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from urllib import urlencode
import urllib2

from openerp import models


class Slide(models.Model):
    _inherit = 'slide.slide'

    def _get_embed_code(self):
        super(Slide, self)._get_embed_code()

        for record in self:
            if record.slide_type == 'video':
                if record.document_id and record.mime_type == "qq":
                    record.embed_code = """
                        <iframe frameborder="0" width="640" height="498"
                            src="http://v.qq.com/iframe/player.html?vid=%s&tiny=0&auto=0"
                            allowfullscreen></iframe>
                    """ % (record.document_id)

    # for qq vedio
    def _fetch_qq_data(self, base_url, data, content_type=False):
        result = {'values': dict()}
        try:
            if content_type == 'json':
                if data:
                    base_url = base_url + '%s&otype=json' % urlencode(data)
                req = urllib2.Request(base_url)
                content = urllib2.urlopen(
                    req).read().split("=")[1].split(';')[0]
                result['values'] = eval(content)

                if result['values'].get('msg'):
                    result['error'] = result['values'].get('msg')
            elif content_type == 'image':
                req = urllib2.Request(base_url)
                content = urllib2.urlopen(req).read()
                result['values'] = content.encode('base64')
            else:
                result['values'] = ""
        except urllib2.HTTPError as e:
            result['error'] = e.read()
            e.close()
        except urllib2.URLError as e:
            result['error'] = e.reason
        return result

    def _find_document_data_from_url(self, url):
        # QQ video
        expr = re.compile(r'.*(v.qq.com).*(vid=?)([^#\&\?]*).*')
        arg = expr.match(url)
        document_id = arg and arg.group(3) or False
        if document_id:
            return ('qq', document_id)

        return super(Slide, self)._find_document_data_from_url()

    def _parse_qq_video_title(self, res):
        title = ""

        try:
            title = res['values']['vl']['vi'][0]['ti']
        except:
            title = ""

        return title

    def _parse_qq_video_thumbnails(self, res, document_id):
        img_url = ""

        try:
            head = "http://vpic.video.qq.com/"
            link = res['values']['vl']['vi'][0]['ul']['ui'][3]['url'].split(
                "http://video.dispatch.tc.qq.com/")[1]
            jpg = document_id + "_160_90_3.jpg"
            img_url = head + link + jpg
        except:
            img_url = ""

        return img_url

    def _parse_qq_document(self, document_id, only_preview_fields):
        fetch_res = self._fetch_qq_data(
            'http://vv.video.qq.com/getinfo?', {'vid': document_id}, 'json'
        )

        if fetch_res.get('error'):
            return fetch_res

        title = self._parse_qq_video_title(fetch_res)
        img_url = self._parse_qq_video_thumbnails(fetch_res, document_id)

        values = {'slide_type': 'video', 'document_id': document_id}

        if only_preview_fields:
            values.update({
                'url_src': img_url,
                'title': title,
            })

            return values

        values.update({
            'name': title,
            'image': self._fetch_qq_data(img_url, {}, 'image')['values'],
            'mime_type': "qq"
        })
        return {'values': values}
