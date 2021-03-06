#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

"""

import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import os
import urllib2
import urllib
import re
import urlparse

YOUTUBE_PATTERN = re.compile(r"""(v[\/=]+)([^\/%&'"?]+)""")
YOUTUBE_PATTERN2 = re.compile(r"/embed/([^\/\?&=]+)[?$]*")
YOUTUBE_DIRECT_LINK_PATTERN = re.compile(r"&id=([^&?]+)")


Addon = xbmcaddon.Addon(id='plugin.video.marakana.tech.tv')

# load XML library
try:
    sys.path.append(os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
    from BeautifulSoup import BeautifulSoup
except:
    try:
        sys.path.insert(0, os.path.join(Addon.getAddonInfo('path'), r'resources', r'lib'))
        from BeautifulSoup import BeautifulSoup
    except:
        sys.path.append(os.path.join(os.getcwd(), r'resources', r'lib'))
        from BeautifulSoup import BeautifulSoup
        icon = xbmc.translatePath(os.path.join(os.getcwd().replace(';', ''), 'icon.png'))


# magic
thisPlugin = int(sys.argv[1])


def Get_MainCategories():
    url = "http://marakana.com/s/"
    f = open_url(url)
    if not f:
        return False

    html = f.read()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.ALL_ENTITIES)

    tags_block = soup.find("p", {"id": "tags"})
    tags = [tags_block.find("a", {"id": "tags-toggle"}).parent]
    tags.extend(tags_block.findAll(lambda tag: tag.name == 'span' and '-featured' in dict(tag.attrs).get('class', '')))
    tags.extend(tags_block.findAll(lambda tag: tag.name == 'span' and '-unfeatured' in dict(tag.attrs).get('class', '')))
    for item in tags:
        add_item(item.a.text, 'CATEGORY', urlparse.urljoin(url, item.a["href"]), isDirectory=True)

    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Episodes(params):
    base_url = "http://marakana.com"
    url = urllib.unquote_plus(params['url'])
    f = open_url(url)
    if not f:
        return False
    url = f.url
    html = f.read()
    soup = BeautifulSoup(html, convertEntities=BeautifulSoup.ALL_ENTITIES)

    for item in soup.findAll("div", {"class": "stream-post"}):
        try:
            img = item.find("img", {"class": "stream-post-thumbnail"})
            if img:
                img = img['src']
            post = item.find("div", {"class": "stream-post-title"})
            name = post.a.text.encode('utf-8')
            name = post.a.string.encode('utf-8')
            href = post.a["href"]
            author_tag = item.find("span", {"class": "stream-post-author"})
            author = ""
            if author_tag:
                author = author_tag.text

            time_tag = item.find("span", {"class": "stream-post-time"})
            time = ""
            if time_tag:
                time = time_tag.text

            name = "%s (%s %s )" % (name, author, time)
            add_item(name, 'EPISODE', urlparse.urljoin(base_url, href), thumbnailImage=urlparse.urljoin(base_url, img), isDirectory=False)
        except:
            continue

    pagination = soup.find("ul", {"class": "pagination-control"})
    if pagination:
        next_item = pagination.find("li", {"class": "next"})
        if next_item:
            add_item("Next Page >>", 'CATEGORY', urlparse.urljoin(url, next_item.a['href']), isDirectory=True)

    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Video(url):
    f = open_url(url)

    html = f.read()
    soup = BeautifulSoup(html)
    # check is youtube video
    source = soup.find("div", {"class": "body"}).find("iframe") or soup.find("iframe", {"class": "youtube-player"})

    if source is None:
        source = soup.find("object", {"class": "video"})['data']
        direct_url = urlparse.parse_qs(urlparse.urlparse(source)[4]).get('file', [''])[0]
    else:
        xbmc.log('source: ' + str(source['src']))
        v1 = YOUTUBE_PATTERN.search(source['src'])
        v2 = YOUTUBE_PATTERN2.search(source['src'])
        if v1:
            video_id = v1.groups()[1]
        elif v2:
            video_id = v2.groups()[0]
        else:
            video_id = None
        xbmc.log("youtube video_id: " + video_id)
        direct_url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + video_id
    xbmc.log("direct_url: " + direct_url)
    return direct_url


def PLAY(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    # img = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    try:
        video = Get_Video(url)
    except StandardError:
        # xbmcgui. ShowNotification("video not found")
        xbmcgui.Dialog().ok("Error", "Video not found")
        return
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


def add_item(name, mode, url, iconImage='', thumbnailImage='', isDirectory=True):
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
