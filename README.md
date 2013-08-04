# MyOBackup

## Introduction

A Python script to export the blog posts of a [My Opera](http://my.opera.com/) user.

## Dependencies

- Er, Python.
- The [Requests module](http://kennethreitz.org/exposures/requests). Install with `sudo pip install requests` (you may need to install Pip first).
- The My Opera username of the blog you wish to export.

## Usage

To run it, just do:

    python myoperabkp.py -u <username> -o "<localpath>" -f markdown

## Output

Blog posts are exported in two formats:

- Simple HTML format: An individual file is created for each post.
- Markdown compatible with [Pelican](http://docs.getpelican.com/en/3.2/)
- Basic WXR (WordPress eXtended Rss) format: An `output.xml` file is created to import all posts into a WordPress blog.

At present, the content and tags of posts are exported but not their comments.

## License

Released under the MIT License (see [LICENSE.md](LICENSE.md)).