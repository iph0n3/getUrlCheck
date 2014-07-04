#!/usr/bin/env python
# by piaca
# 2012.7.7

import os
import re
import sys
import time
import pycurl 
import hashlib
import urlparse
import StringIO
import subprocess
from math import floor
from urllib import *
import urllib2
import urllib
import cookielib
import socket

class HTTP():
    
    @staticmethod
    def getPage(**kwargs):
        url = kwargs.get('url')
        referer = kwargs.get('referer')
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener.addheaders = [('Cookie', 'googlecookie=1'), ('User-agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36'), ('Referer', referer), ('AlexaToolbar-ALX_NS_PH','AlexaToolbar/alxg-3.3')]
        urllib2.install_opener(opener)
        req = urllib2.Request(url=url)
        r = opener.open(req)
 
        
        return (r.read(),'')
      

def getGoogle(keyword, page):
    googleMobile = "http://203.116.165.138/search?filter=0&newwindow=1&num=100&q=%s&start=%d" %(keyword, page)
    googleResponse, googleHeaders = HTTP.getPage(url=googleMobile, referer="http://www.google.com")
    #print googleResponse
    if not isinstance(page, pycurl.error):
        #print googleResponse
        googleUrls = re.findall("href=\"([\w\W]{1,99}\.swf)\"", googleResponse)
        print len(googleUrls)
        if len(googleUrls) != 0:
            return googleUrls
        else:
            return None
    else:
        return None

def searchGoogle(keyword, page):
    flashUrls = []
    flashHashs = []
    for i in range(int(page)):
        time.sleep(5)
        start = i * 100
        urls = getGoogle(quote(keyword), start)
      
        if urls != None:
            for url in urls:
                _url = unquote(url)
                __url = urlparse.urlparse(_url)
                flashUrl = "%s://%s%s" % (__url[0],__url[1],__url[2])
                flashHash = hashlib.md5(flashUrl).hexdigest()
                if flashHash not in flashHashs:
                    flashHashs.append(flashHash)
                    flashUrls.append(flashUrl.encode("ascii"))
        else:
            break
    return flashUrls

def scanSWF(swfdpath, flashUrl):

    p = subprocess.Popen("%s %s" % (swfdpath, flashUrl), stdout=subprocess.PIPE)
    buff = p.stdout.read()
    buff = buff.split("-->")
    if len(buff) > 0:
        if buff[-1].strip()[-3:] == ".as":
            asfile = buff[-1].strip()
            asfp = file(asfile, "r")
            ascontent = asfp.read()
            # alertinofs = [ 
            #     "ExternalInterface.call",
            #     "getURL",
            #     "navigateToURL",
            #     "getUrlBlankVar",
            #     "getUrlParentVar",
            #     "getUrlJSParam",
            #     "loadMovieNumVar",
            #     "htmlVar",
            #     "externallnterfaceVar",
            #     "loadMovieVar",
            #     "loadVariables",
            #     "loadMovie",
            #     "loadmovieNum",
            #     "xml.load",
            #     "xmldoc.load",
            #     "loadvars.load",
            #     "sound.loadsound",
            #     "netstream.play"
            # ]
            resultpath = os.getcwd() + '\\result\\'
            alertinfo = re.compile('[\W\w]*geturl[\s]*\\([\s]*[\w]+', re.I)
            print 'debug'
            #for alertinfo in alertinofs:
            if alertinfo.match(ascontent) != None:
                print flashUrl
                fo = open(resultpath + '%s.as'%(flashUrl.replace(':','_').replace(r'/','_')), 'w+')
                fo.write(ascontent)
                return flashUrl
                # if alertinfo in ascontent and ".parameters" in ascontent:
                #     print flashUrl
                #     print "%s is vul (as3), function found: %s" % (asfile, alertinfo)
                #     return flashUrl + '   function found: %s' % (alertinfo)
                # elif alertinfo in ascontent and "_root." in ascontent:
                #     print flashUrl
                #     print "%s is vul (as2), function found: %s" % (asfile, alertinfo)
                #     return flashUrl + '   function found: %s' % (alertinfo)

def xargs():
        print "xargs: %s [mode] [option]" % sys.argv[0]
        print " mode:"
        print "  -s    search"
        print "  -t    test"
        print "  -p    pentest"
        print " option:"
        print "  -u    url"
        print "  -c    cmd with pentest"
        print "  -k    keyword with search"
        print "  -page page with search"
        print "  -h    help"

if __name__ == "__main__":

    if len(sys.argv) <= 1:
        xargs()
        sys.exit(1)

    count = 0
    mode = ""
    url = ""
    cmd = ""
    keyword = ""
    page = ""
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    swfddir = "%s\\%s" % (scriptpath, "swfd\\") 
    swfdpath = "%s\\%s" % (scriptpath, "swfd\\swfd.exe") 
    vulurl = []

    for arg in sys.argv:
        if arg == "-h":
            xargs()
            sys.exit(1)
        elif arg == "-s":
            mode = arg
        elif arg == "-k":
            keyword = sys.argv[count+1]
        elif arg == "-page":
            page = sys.argv[count+1]
        count += 1

    if mode == "-s":
        if keyword == "" or page == "":
            xargs()
            sys.exit(1)
        else:
            flashUrls = []

            flashUrls = searchGoogle(keyword, page)
           
            if len(flashUrls) != 0:
                for flashUrl in flashUrls:
                    #print flashUrl
                    vurl = scanSWF(swfdpath, flashUrl)
                    if vurl!= None:
                        vulurl.append(vurl)
    vulurl = [vurl + '\n' for vurl in vulurl]
    fo = open('result.txt', 'w+')
    for vurl in vulurl:
        fo.write(vurl)
    print vulurl
    fo.close()