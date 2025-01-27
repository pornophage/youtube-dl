# encoding: utf-8
import re

from .common import InfoExtractor
from ..utils import (
    compat_urllib_parse,
    determine_ext,
)


class DaumIE(InfoExtractor):
    _VALID_URL = r'https?://tvpot\.daum\.net/.*?clipid=(?P<id>\d+)'
    IE_NAME = u'daum.net'

    _TEST = {
        u'url': u'http://tvpot.daum.net/clip/ClipView.do?clipid=52554690',
        u'file': u'52554690.mp4',
        u'info_dict': {
            u'title': u'DOTA 2GETHER 시즌2 6회 - 2부',
            u'description': u'DOTA 2GETHER 시즌2 6회 - 2부',
            u'upload_date': u'20130831',
            u'duration': 3868,
        },
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group(1)
        canonical_url = 'http://tvpot.daum.net/v/%s' % video_id
        webpage = self._download_webpage(canonical_url, video_id)
        full_id = self._search_regex(
            r'<iframe src="http://videofarm.daum.net/controller/video/viewer/Video.html\?.*?vid=(.+?)[&"]',
            webpage, u'full id')
        query = compat_urllib_parse.urlencode({'vid': full_id})
        info = self._download_xml(
            'http://tvpot.daum.net/clip/ClipInfoXml.do?' + query, video_id,
            u'Downloading video info')
        urls = self._download_xml(
            'http://videofarm.daum.net/controller/api/open/v1_2/MovieData.apixml?' + query,
            video_id, u'Downloading video formats info')

        self.to_screen(u'%s: Getting video urls' % video_id)
        formats = []
        for format_el in urls.findall('result/output_list/output_list'):
            profile = format_el.attrib['profile']
            format_query = compat_urllib_parse.urlencode({
                'vid': full_id,
                'profile': profile,
            })
            url_doc = self._download_xml(
                'http://videofarm.daum.net/controller/api/open/v1_2/MovieLocation.apixml?' + format_query,
                video_id, note=False)
            format_url = url_doc.find('result/url').text
            formats.append({
                'url': format_url,
                'ext': determine_ext(format_url),
                'format_id': profile,
            })

        return {
            'id': video_id,
            'title': info.find('TITLE').text,
            'formats': formats,
            'thumbnail': self._og_search_thumbnail(webpage),
            'description': info.find('CONTENTS').text,
            'duration': int(info.find('DURATION').text),
            'upload_date': info.find('REGDTTM').text[:8],
        }
