#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Google Code University video lectures
"""

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import os
import urllib2
import urllib
import httplib
import re
import urlparse

YOUTUBE_PATTERN = re.compile(r"""(v[\/=]+)([^\/%&'"?]+)""")
YOUTUBE_PATTERN2 = re.compile(r"/embed/([^\/\?&=]+)[?$]*")
YOUTUBE_DIRECT_LINK_PATTERN = re.compile(r"&id=([^&?]+)")
GVIDEO_PATTERN = re.compile(r"docId=([^&?]+)", re.I)
GVIDEO_DIRECT_PATTERN = re.compile('videoUrl([^"])+"')


Addon = xbmcaddon.Addon(id='plugin.video.marakana.tech.tv')

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup  import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup  import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''),'icon.png'))


# magic
thisPlugin = int(sys.argv[1])


def Get_MainCategories():
    categories = {'Programming Languages': 'http://code.google.com/intl/en/edu/languages/index.html',
                    'Web Programming': 'http://code.google.com/intl/en/edu/ajax/index.html',
                    'Web Security': 'http://code.google.com/intl/en/edu/security/index.html',
                    'Algorithms': 'http://code.google.com/intl/en/edu/algorithms/index.html',
                    'Android': 'http://code.google.com/intl/en/edu/android/index.html',
                    'Distributed Systems': 'http://code.google.com/intl/en/edu/parallel/index.html'
                }

    for course in categories:
        add_item(course, 'CATEGORY', categories[course], isDirectory=True)

    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Episodes(params):
    url = urllib.unquote_plus(params['url'])
    f = open_url(url)
    if not f:
        return False
    url = f.url
    html = f.read()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.ALL_ENTITIES)

    for item in soup.findAll("embed"):
        try:
            name = item.findAllPrevious('h3', limit=1)[0].text
            href = item["src"]
            add_item(name, 'EPISODE', href, thumbnailImage=None, isDirectory=False)
        except:
            continue

    xbmcplugin.endOfDirectory(thisPlugin)


def GetYoutubeVideoInfo(videoID, eurl=None):
    '''
    Return direct URL to video and dictionary containing additional info
    >> url,info = GetYoutubeVideoInfo("tmFbteHdiSw")
    >>
    '''
    if not eurl:
        params = urllib.urlencode({'video_id': videoID})
    else:
        params = urllib.urlencode({'video_id': videoID, 'eurl': eurl})
    conn = httplib.HTTPConnection("www.youtube.com")
    conn.request("GET", "/get_video_info?&%s" % params)
    response = conn.getresponse()
    data = response.read()
    video_info = dict((k, urllib.unquote_plus(v)) for k, v in
                               (nvp.split('=') for nvp in data.split('&')))
    conn.request('GET', '/get_video?video_id=%s&t=%s' %
                         (video_info['video_id'], video_info['token']))
    response = conn.getresponse()
    direct_url = response.getheader('location')
    return direct_url, video_info


def GetGoogleVideoDirectUrl(videoId):
    url = "http://video.google.com/videofeed?fgvns=1&fai=1&docid=%s&hl=en" % videoId
    html = urllib2.urlopen(url).read()
    direct_url = urllib2.unquote(GVIDEO_DIRECT_PATTERN.search(html).group(0)[9:-1]).replace('&amp;', '&')
    direct_url = direct_url[:direct_url.index('&thumbnailUrl')]
    return direct_url


def Get_Video(url):
    v1 = YOUTUBE_PATTERN.search(url)
    v2 = YOUTUBE_PATTERN2.search(url)
    if v1:
        video_id = v1.groups()[1]
    elif v2:
        video_id = v2.groups()[0]
    else:
        return

    direct_url, video_info = GetYoutubeVideoInfo(video_id)
    info_link = urllib.unquote_plus(video_info['url_encoded_fmt_stream_map'])
    if not direct_url:
        direct_url = info_link[4:YOUTUBE_DIRECT_LINK_PATTERN.search(info_link).end()]
    return direct_url


def PLAY(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    if 'video.google.com' in url:
        video = GetGoogleVideoDirectUrl(GVIDEO_PATTERN.search(url).groups(0)[0])
    else:
        video = Get_Video(url)
    xbmc.log("url: " + video)
    i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(video))
    i.setInfo('video', {'Title': name})
    i.setProperty('IsPlayable', 'true')
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    playList.add(urllib.unquote_plus(video), i)
    player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    player.play(playList)


def get_url(url):
    return "http:" + urllib.quote(url.replace('http:', ''))


def open_url(url):
    post = None
    request = urllib2.Request(url, post)

    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')

    try:
        f = urllib2.urlopen(request)
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: ' + e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: ' + e.code)
        return None
    return f


def add_item(name, mode, url, iconImage=None, thumbnailImage=None, isDirectory=True):
    # xbmc.log("add item - name: %s , mode: %s , url: %s" % (name, mode, url))
    i = xbmcgui.ListItem(label=name.encode('utf-8'), iconImage=iconImage, thumbnailImage=thumbnailImage)
    u = "%s?mode=%s&name=%s&url=%s" % (sys.argv[0], mode, urllib.quote_plus(name.encode('utf-8')), urllib.quote_plus(url))
    xbmcplugin.addDirectoryItem(thisPlugin, u, i, isDirectory)


def get_params(paramstring):
    return dict([(key, value[0]) for key, value in urlparse.parse_qs(paramstring[1:]).items()])

params = get_params(sys.argv[2])

mode = None
isException = False

try:
    mode = urllib.unquote_plus(params['mode']).upper()
except Exception, ex:
    isException = True
    Get_MainCategories()

if mode == 'CATEGORY':
    Get_Episodes(params)
elif mode == 'EPISODE':
    PLAY(params)
else:
    isException and Get_MainCategories()
