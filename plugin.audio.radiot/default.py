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


def get_url(url):
    return "http:" + urllib.quote(url.replace('http:', ''))


Addon = xbmcaddon.Addon(id='plugin.audio.radiot')

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

BeautifulSoup.NESTABLE_BLOCK_TAGS = ('blockquote', 'div', 'fieldset', 'ins', 'del', 'article', 'header', 'p')
BeautifulSoup.NESTABLE_TAGS.update({'header': [], 'article': [], 'p': []})

# magic
thisPlugin = int(sys.argv[1])


def Get_Categories():
    categories = (
        ('main', u'Подкаст Радио-Т', 'http://radio-t.com/', 'http://www.radio-t.com/images/rt-header-logo.png'),
        ('pirates', u'Пираты Радио-Т', 'http://pirates.radio-t.com', 'http://pirates.radio-t.com/images/pirates-logo.png')
        )
    for tag, name, url, img in categories:
        xbmc.log("tuple: %s, %s, %s, %s" % (tag, name.encode('utf-8'), url, img))
        i = xbmcgui.ListItem(label=name.encode('utf-8'), iconImage=None, thumbnailImage=img)
        u = sys.argv[0] + '?mode=category'
        u += '&name=%s' % urllib.quote_plus(name.encode('utf-8'))
        u += '&url=%s' % urllib.quote_plus(url)
        u += '&tag=%s' % urllib.quote_plus(tag)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)

    xbmcplugin.endOfDirectory(thisPlugin)


def Get_Subcategories(params):
    tag = urllib.unquote_plus(params['tag'])
    if tag == 'pirates':
        subcategories = (
            ('pirates-recent', u'Последние выпуски', 'http://pirates.radio-t.com/'),
            ('pirates-archive', u'Архив выпусков', 'http://pirates.radio-t.com/archives/')
        )
    else:
        subcategories = (
            ('main-online', 'On air', 'http://stream.radio-t.com:8181/stream.m3u'),
            ('main-recent', u'Последние выпуски', 'http://radio-t.com/'),
            ('main-archive', u'Архив выпусков', 'http://www.radio-t.com/archives/')
        )

    for tag, name, url in subcategories:
        # xbmc.log("tuple: %s, %s, %s" % (tag, name.encode('utf-8'), url))
        i = xbmcgui.ListItem(label=name.encode('utf-8'), iconImage=None, thumbnailImage=None)
        u = sys.argv[0] + '?mode=subcategory'
        if tag == 'main-online':
            u = sys.argv[0] + '?mode=episode'
        u += '&name=%s' % urllib.quote_plus(name.encode('utf-8'))
        u += '&url=%s' % urllib.quote_plus(url)
        u += '&tag=%s' % urllib.quote_plus(tag)
        if tag == 'main-online':
            xbmcplugin.addDirectoryItem(thisPlugin, u, i, False)
        else:
            xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)

    xbmcplugin.endOfDirectory(thisPlugin)


def main_episodes(html):
    soup = BeautifulSoup(html)
    episodes = []
    for article in soup.findAll('article'):
        print str(article)
        try:
            title_el = article.find('h1')
            if title_el.find('a'):
                title = title_el.find('a').text.encode('utf-8')
            else:
                title = title_el.text.encode('utf-8')
            img_el = article.find('div', attrs={'class': re.compile(r'\bentry-content\b')}).find('img')
            img = ''
            if img_el:
                img = img_el['src']
                if 'http:' not in img:
                    img = 'http://www.radio-t.com/' + img
            podcast_link = article.find('audio')
            if podcast_link:
                episodes.append((title, podcast_link['src'], img.replace(r'com//', r'com/')))
        except Exception:
            raise
    return episodes


def create_request(url, post=None):
    request = urllib2.Request(url, post)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
    request.add_header('Accept', '*/*')
    request.add_header('Accept-Language', 'ru-RU')

    try:
        f = urllib2.urlopen(request)
        return f.read()
    except IOError, e:
        if hasattr(e, 'reason'):
            xbmc.log('We failed to reach a server. Reason: ' + e.reason)
        elif hasattr(e, 'code'):
            xbmc.log('The server couldn\'t fulfill the request. Error code: ' + e.code)
    return ""


def get_episodes(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    xbmc.log("url : " + url)
    tag = urllib.unquote_plus(params['tag'])
    xbmc.log("tag: %s" % tag)
    html = create_request(url, None)

    episodes = []
    if tag in  ('main-recent', 'pirates-recent'):
        episodes = main_episodes(html)
    elif tag == 'main-archive':
        episodes = filter(lambda item: 'podcast-' in item[1], [(article.find('h1').find('a').text.encode('utf-8'), 'http://www.radio-t.com' + article.find('h1').find('a')['href'], '') for article in BeautifulSoup(html).find('div', attrs={'id': 'blog-archives'}).findAll('article')])
    elif tag == 'pirates-archive':
        episodes = filter(lambda item: 'podcast-' in item[1], [(article.find('h1').find('a').text.encode('utf-8'), 'http://pirates.radio-t.com' + article.find('h1').find('a')['href'], '') for article in BeautifulSoup(html).find('div', attrs={'id': 'blog-archives'}).findAll('article')])
    else:
        return

    for name, url, img in episodes:
        print tag, name, url, img
        i = xbmcgui.ListItem(label=name, iconImage=None, thumbnailImage=img)
        u = sys.argv[0] + '?mode=episode'
        u += '&name=%s' % urllib.quote_plus(name)
        u += '&url=%s' % urllib.quote_plus(url)
        u += '&tag=%s' % urllib.quote_plus('episode')
        u += '&img=%s' % urllib.quote_plus(img)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, False)
    xbmcplugin.endOfDirectory(thisPlugin)


def PLAY(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    img = urllib.unquote_plus(params['img'])
    if not url.endswith('mp3'):
        html = create_request(url, None)
        name, url, img = main_episodes(html)[0]
        print name, url, img
    if img:
        i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(url), thumbnailImage=img)
    else:
        i = xbmcgui.ListItem(label=name, path=urllib.unquote_plus(url))
    i.setInfo('video', {'Title': name})
    i.setProperty('IsPlayable', 'true')
    playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playList.clear()
    playList.add(urllib.unquote_plus(url), i)
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
    xbmc.log("params: " + str(param))
    return param

params = get_params(sys.argv[2])

mode = None

try:
    mode = urllib.unquote_plus(params['mode'])
except:
    Get_Categories()

if mode == 'category':
    Get_Subcategories(params)
elif mode == 'subcategory':
    get_episodes(params)
elif mode == 'episode':
    PLAY(params)
else:
    pass
