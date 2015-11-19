# ACMS
my minimal take on a content management system (cms)
* written in python
* one dependency: python lib PIL (import Image)
* for apache

# how it works
The only visual thing ACMS does is inserts into a region of index.html marked by comments. Since you control EVERYTHING else about that html file (html itself, what js is included, what stylesheet is used), your blog can look like literally anything.

Additionally, ACMS will create directories and accept uploads to hold your stuff that's associated with a post.

# philosophy
goals of ACMS:
* post stuff quickly, before the thought of the work involved changes my mind
* hold crap away from my HDD
* post stuff accessible to friends only (currently using simple htpasswd method)

If you need additional control (editing a post, adding files, etc.) then you can fall back to manual editing (via scp, sftp, ssh, whatever). That functionality is not included in order to keep ACMS simple and less buggy.

# setup
* install PIL on your server.
* copy control.py to some random filename (your knowledge of this secret URL is the super secure auth method)
* create a settings.py, example:
```
author = 'JoeShmoe'
debug = False
thumbSize = (128,128)
cmsPath = '/home/jshmoe/web/blog'
htaccess = 'AuthUserFile /home/jshmoe/web/blog/.htpasswd\nAuthType Basic\nAuthName "Private Files, Bro!"\nRequire valid-user'
htpasswd = 'JaneDoe:$apZe1$N1uQd4vCy$.U99zVWlnvBW4ASqagv8z9'
```
* create an index.html with the marks
```
<html>
 <head>
  <link href="stylesheet.css" rel="stylesheet" type="text/css">
 </head>
 <title>
  Blog Title
 </title>

 <body>

<!-- ACMS-start -->

<!-- ACMS-end -->

 </body>
</html>
```

# devel/debug
I recommend thttpd (tiny/turbo/throttling HTTP server). It's not on apt-get but it configure/make/install's easy. Here's the invocation I use:
```
$ thttpd -D -c "*.py" -p 8080
```
Then navigate your browser to http://localhost:8080.

Without early syntax errors, `cgitb.enable()` does a fine job of echoing problems to your browser for debugging.

## CGI notes
Remember how simple CGI is. The server just invokes your script with environment variables set up and standard input. Here are the three cases:

* PATH_INFO gets set to any path in the url after the script
* for GET requests, QUERY_STRING is set
* for POST requests, CONTENT_LENGTH set to length of data which is written to stdin

