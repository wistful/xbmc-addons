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


# magic
thisPlugin = int(sys.argv[1])


def Get_Categories():
    categories = (
        ('main', u'Подкаст Радио-Т', 'http://radio-t.com/', 'http://1.bp.blogspot.com/-e3vBuApYoLE/To9nSz0AscI/AAAAAAAAPYA/Nd8tAoh5eH8/s1600/rt-header-logo.png'),
        ('pirates', u'Пираты Радио-Т', 'http://pirates.radio-t.com', 'http://1.bp.blogspot.com/-e3vBuApYoLE/To9nSz0AscI/AAAAAAAAPYA/Nd8tAoh5eH8/s1600/rt-header-logo.png')
        )
    for tag, name, url, img in categories:
        xbmc.log("tuple: %s, %s, %s, %s" % (tag, name.encode('utf-8'), url, img))
        i = xbmcgui.ListItem(label=name.encode('utf-8'), iconImage=None, thumbnailImage=img)
        u = sys.argv[0] + '?mode=EPISODES'
        u += '&name=%s' % urllib.quote_plus(name.encode('utf-8'))
        u += '&url=%s' % urllib.quote_plus(url)
        u += '&tag=%s' % urllib.quote_plus(tag)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)

    xbmcplugin.endOfDirectory(thisPlugin)


def add_podcasts(html, tag):
    if tag == "main":
        link_compile = re.compile('rt_podcast\d+\.mp3')
    elif tag == "pirates":
        link_compile = re.compile('rt\d+post\.mp3')
    else:
        return

    soup = BeautifulSoup(html)
    for div in soup.findAll("div", {"class": "date-outer"}):
        podcast_link = div.find('a', href=link_compile)
        if podcast_link:
            href = podcast_link['href']
        else:
            continue

        str_date = div.find("h2", {"class": "date-header"}).span.text.encode('utf-8').replace('&#160;', ' ')
        name = div.find("h3").a.text.encode('utf-8')
        img = div.find('img')
        if img:
            img_src = img['src']
        else:
            img_src = None
        i = xbmcgui.ListItem("%s (%s)" % (name, str_date), iconImage=None, thumbnailImage=img_src)
        u = sys.argv[0] + '?mode=EPISODE'
        u += '&name=%s' % urllib.quote_plus(name)
        u += '&url=%s' % urllib.quote_plus(href)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, False)

    try:
        next_step = soup.find("div", {"id": "blog-pager"}).find("a", {"id": "Blog1_blog-pager-older-link"})["href"]
        i = xbmcgui.ListItem(u"Далее >>", iconImage=None, thumbnailImage=None)
        u = sys.argv[0] + '?mode=EPISODES'
        u += '&name=%s' % urllib.quote_plus('')
        u += '&url=%s' % urllib.quote_plus(next_step)
        u += '&tag=%s' % urllib.quote_plus(tag)
        xbmc.log("next step: %s" % next_step)
        xbmcplugin.addDirectoryItem(thisPlugin, u, i, True)
    except Exception, ex:
        xbmc.log('Exception: %s' % ex)


def Get_Episodes(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    xbmc.log("url : " + url)
    tag = urllib.unquote_plus(params['tag'])
    xbmc.log("tag: %s" % tag)

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
    add_podcasts(html, tag)
    xbmcplugin.endOfDirectory(thisPlugin)


def PLAY(params):
    # -- parameters
    url = urllib.unquote_plus(params['url'])
    name = urllib.unquote_plus(params['name'])
    img = None
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

if mode == 'EPISODES':
    Get_Episodes(params)
elif mode == 'EPISODE':
    PLAY(params)
else:
    # Get_Categories()
    pass
