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


def get_url(url):
    return "http:" + urllib.quote(url.replace('http:', ''))


Addon = xbmcaddon.Addon(id='plugin.video.tut.by.tv')

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
    categories = (
        ('projects', u'Проекты и Программы', 'http://news.tut.by/projects/?utm_source=main.tut.by&utm_medium=tv-block&utm_campaign=mainpage-tv-block'),
        ('recent', u'Последние выпуски', 'http://news.tut.by/tv'),
        ('live', u'Сейчас в эфире', 'http://www.tut.by/')
        )

    for tag, name, url in categories:
        xbmc.log("tuple: %s, %s, %s" % (tag, name.encode('utf-8'), url))
        i = xbmcgui.ListItem(label=name.encode('utf-8'), iconImage=None, thumbnailImage=None)
        u = sys.argv[0] + '?mode=CATEGORIES'
        u += '&name=%s' % urllib.quote_plus(name.encode('utf-8'))
        u += '&url=%s' % urllib.quote_plus(url)
        u += '&tag=%s' % urllib.quote_plus(tag)
        if tag == 'live':
            xbmcplugin.addDirectoryItem(thisPlugin, u, i, False)
        else:
            xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)

    xbmcplugin.endOfDirectory(thisPlugin)


def fetch_categories(url):
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

    html = f.read()

    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    for h2 in soup.findAll("h2"):
        tag = h2.a['href']
        name = h2.a['title'].encode('utf-8')
        img = h2.parent.find('img', {'class': 'opImg'})['src']
        # descr = h2.parent.find('span', {'class': 'opText'}).text.encode('utf-8')
        i = xbmcgui.ListItem(label=name, iconImage=None, thumbnailImage=img)
        u = sys.argv[0] + '?mode=SUBCATEGORIES'
        u += '&name=%s' % urllib.quote_plus(name)
        u += '&url=%s' % urllib.quote_plus(tag)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)


def fetch_subcategories(url):
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

    html = f.read()

    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    count = 0
    for div in soup.find("ul", {"id": "newsBlock1"}).findAll("li"):
        str_date = div.span.text.encode('utf-8')
        name = div.a.text.encode('utf-8')
        href = div.a['href']
        is_video = div.find(lambda tag: tag.name == "img" and u"Видео" in dict(tag.attrs).get('title', ''))
        # is_audio = div.find(lambda tag: tag.name == "img" and u"Аудио" in dict(tag.attrs).get('title', ''))
        if not is_video:
            continue
        i = xbmcgui.ListItem("%s (%s)" % (name, str_date), iconImage=None, thumbnailImage=None)
        u = sys.argv[0] + '?mode=EPISODE'
        u += '&name=%s' % urllib.quote_plus(name)
        u += '&url=%s' % urllib.quote_plus(href)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, False)
        count += 1

    next_step = None
    try:
        next_step = soup.find("div", {"class": "otherInfo"}).find("ul", {"class": "pagination"}).findAll("li")[-1].find("a", {"class": "step"})['href']
        i = xbmcgui.ListItem(u"Далее >>", iconImage=None, thumbnailImage=None)
        u = sys.argv[0] + '?mode=SUBCATEGORIES'
        u += '&name=%s' % urllib.quote_plus('')
        u += '&url=%s' % urllib.quote_plus(next_step)
        xbmc.log("next step: " + next_step)
        if count < 15:
            fetch_subcategories(next_step)
        else:
            xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)
    except Exception, ex:
        xbmc.log('Exception: ' + str(ex))


def fetch_live(url):
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

    html = f.read()

    soup = BeautifulSoup(html)

    live_tag = soup.find("input", {"id": "airVideoFile"})
    if live_tag:
        return live_tag['value']
    return None


def Get_Categories(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    tag = urllib.unquote_plus(params['tag'])
    name = urllib.unquote_plus(params['name'])
    xbmc.log("categories - tag: %s , name: %s, url: %s" % (tag, name, url))

    if tag == 'projects':
        fetch_categories(url)
    elif tag == "recent":
        fetch_subcategories(url)
    elif tag == "live":
        ON_LIVE(url)

    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Subcategories(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    url2 = get_url(url)
    xbmc.log("url: " + url2)
    # category_name = urllib.unquote_plus(params['name'])
    fetch_subcategories(url2)
    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Video(url):
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

    html = f.read()
    soup = BeautifulSoup(html, fromEncoding="windows-1251")
    img = soup.find("div", {'id': 'article_body'}).find(lambda tag: tag.name == 'img' and not tag['src'].endswith('gif')) or {}
    for a in soup.find("div", {'id': 'article_body'}).findAll('a'):
        if a['href'].endswith('mp4') or a['href'].endswith('flv'):
            xbmc.log('return link: %s , img: %s' % (a['href'], img.get('src', None)))
            return a['href'], img.get('src', None)


def ON_LIVE(url):
    name = "TUT.BY LIVE"

    live_link = fetch_live(url).replace(r'///', r'/')
    # live_link = "rtmp://video.tut.by/live/live1"
    i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(live_link))
    i.setInfo('video', {'Title': name})
    i.setProperty('IsPlayable', 'true')
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    playList.add(urllib.unquote_plus(live_link), i)
    player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    player.play(playList)


def PLAY(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    # img = urllib.unquote_plus(params['img'])
    name = urllib.unquote_plus(params['name'])

    video, img = Get_Video(url)

    if img:
        i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(video), thumbnailImage=img)
    else:
        i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(video))
    i.setInfo('video', {'Title': name})
    i.setProperty('IsPlayable', 'true')
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    playList.add(urllib.unquote_plus(video), i)
    player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    player.play(playList)


def get_params(paramstring):
    param = []
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param

params = get_params(sys.argv[2])

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    Get_MainCategories()

if mode == 'CATEGORIES':
    Get_Categories(params)
elif mode == 'SUBCATEGORIES':
    Get_Subcategories(params)
elif mode == 'EPISODE':
    PLAY(params)
else:
    Get_MainCategories()
