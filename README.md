# acms
minimal content management system (cms)
* written in python
* one dependency: python lib PIL (import Image)
* for apache

# setup
* install PIL on your server.
* copy control.py to some random filename (your knowledge of this secret URL is the super secure auth method)
* create a settings.py (see settings_example.py)
* 

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

