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
import urllib2
import imghdr
import os
import errno
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


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def pathdate(datetext):
    """return a path according to the date text
    datetext: Sunday, March 30, 2008 6:32:55 PM
    pathdate: /2008/03/30/"""
    datestruct = time.strptime(datetext, '%A, %B %d, %Y %I:%M:%S %p')
    return time.strftime("/%Y/%m/%d/", datestruct)


def getimages(blogpostdata, pathdate, archivepath):
    "given the blog post data structure, grab all local images"
    # Todo saving in a local directory
    for imguri in blogpostdata['imglist']:
        # take the last part of the path after "/"
        imagename = string.rsplit(imguri, "/", 1)[-1:][0]
        # take the last part of the string after "."
        extension = string.rsplit(imagename, ".", 1)[-1:][0]
        # where it should be saved
        filename = ("%s%s%s") % (archivepath, pathdate, imagename)
        # read image data
        imageresp = urllib2.urlopen(imguri)
        imagedata = imageresp.read()
        imageresp.close()
        # if the extension not in common format, what is it?
        if extension.lower() not in ["jpg", "png", "gif"]:
            imagetype = imghdr.what(None, imagedata[:32])
            if imagetype == "jpeg":
                extension = "jpg"
            # create a new filename for this image
            filename = ("%s.%s") % (filename, extension)
        # save the image
        with open(filename, 'wb') as imagefile:
            imagefile.write(imagedata)
            logging.info("created image at %s" % (filename))



def archiveit(blogpostdata, archivepath):
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
    archivepath = args.archivepath
    useruri = myopath % (username)
    # return the list of all blog posts URI
    everylinks = blogpostlist(useruri)
    # iterate over all blogposts
    everylinks = ["http://my.opera.com/karlcow/blog/2011/05/09/make-web-not-war-2011-vancouver",]
    for blogpostlink in everylinks:
        blogpost = getpostcontent(blogpostlink)
        print blogpost['title'][0]
        blogpostdatepath = pathdate(blogpost['date'][0])
        mkdir(("%s%s") % (archivepath, blogpostdatepath))
        # if the list of images is not empty, then grab the images
        if blogpost['imglist']:
            getimages(blogpost, blogpostdatepath, archivepath)
    # Encoding encoding
    # print foo[0].encode('utf-8')

if __name__ == "__main__":
    sys.exit(main())
