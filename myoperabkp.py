#!/usr/bin/env python2.7
# encoding: utf-8
"""
myoperabkp.py

Created by Karl Dubost on 2013-01-24.
Copyright (c) 2013 Grange. All rights reserved.
see LICENSE.TXT
"""

import argparse
import sys
import requests
import logging
from lxml import etree
from urlparse import urljoin
import time
import string
# import os
# import locale

# variables
myopath = "http://my.opera.com/%s/archive/"


def getcontent(uri):
    """Given a uri, parse an html document"""
    headers = {'User-Agent': "MyOpera-Backup/1.0"}
    r = requests.get(uri, headers=headers)
    responsetext = r.text
    logging.info("parsed %s" % (uri))
    return responsetext


def getpostcontent(uri):
    "return the elements of a blog post: content, title, date"
    myparser = etree.HTMLParser(encoding="utf-8")
    posthtml = getcontent(uri)
    tree = etree.HTML(posthtml, parser=myparser)
    # grab the title of the blog post
    title = tree.xpath('//div[@id="firstpost"]//h2[@class="title"]/text()')
    postdate = tree.xpath('//div[@id="firstpost"]//p[@class="postdate"]/text()')
    content = tree.xpath('//div[@id="firstpost"]//div[@class="content"]')
    imageslist = tree.xpath('//div[@id="firstpost"]//div[@class="content"]//img/@src')
    return dict([
        ("uri", uri),
        ("title", title),
        ("date", postdate),
        ("html", etree.tostring(content[0])),
        ("imglist", imageslist)])


def pathdate(datetext):
    """return a path according to the date text
    datetext: Sunday, March 30, 2008 6:32:55 PM
    pathdate: /2008/03/30/"""
    datestruct = time.strptime(datetext, '%A, %B %d, %Y %I:%M:%S %p')
    return time.strftime("/%Y/%m/%d/", datestruct)


def getimages(blogpostdata, pathdate):
    "given the blog post data structure, grab all local images"
    # Todo saving in a local directory
    for imguri in blogpostdata['imglist']:
        imagename = string.rsplit(imguri, "/", 1)[-1:][0]
        filename = ("%s%s") % (pathdate, imagename)
        print filename
        # imgout = open(filename, "wb")
        # imgout.write(imagebit)
        # imgout.close()


def archiveit(blogpostdata, arcpath):
    "given the blogpostdata, archive them locally in arcpath"
    # todo creating a directory structure
    pass


def blogpostlist(useruri):
    "return a list of blog posts URI for a given username"
    postlist = []
    myparser = etree.HTMLParser(encoding="utf-8")
    archivehtml = getcontent(useruri)
    tree = etree.HTML(archivehtml, parser=myparser)
    navlinks = tree.xpath('//p[@class="pagenav"]//a/@href')
    # Insert the first page of the archive at the beginning
    navlinks.insert(0, useruri)
    # Remove the last item of the list which is the next link
    navlinks.pop()
    # we go through all the list
    for navlink in navlinks:
        archtml = getcontent(urljoin(useruri, navlink))
        tree = etree.HTML(archtml, parser=myparser)
        links = tree.xpath('//div[@id="arc"]//li//a/@href')
        for link in links:
            postlist.append(urljoin(useruri, link))
    return postlist


def main():
    logging.basicConfig(filename='log-myopera.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    # Parsing the cli
    parser = argparse.ArgumentParser(
        description="Export html content from my.opera")
    parser.add_argument(
        '-u',
        action='store',
        dest="username",
        help='username we want to backup')
    parser.add_argument(
        '-o',
        action='store',
        dest="archivepath",
        help='local path where the backup will be kept')

    args = parser.parse_args()
    username = args.username
    useruri = myopath % (username)
    # return the list of all blog posts URI
    everylinks = blogpostlist(useruri)
    # iterate over all blogposts
    for blogpostlink in everylinks:
        blogpost = getpostcontent(blogpostlink)
        print blogpost['title'][0]
        blogpostdatepath = pathdate(blogpost['date'][0])
        # if the list of images is not empty, then grab the images
        if blogpost['imglist']:
            getimages(blogpost, blogpostdatepath)
    # Encoding encoding
    # print foo[0].encode('utf-8')

if __name__ == "__main__":
    sys.exit(main())
