# acms
minimal content management system (cms)

# testing
## serving locally
I recommend thttpd (tiny/turbo/throttling HTTP server). It's not on apt-get but it configure/make/install's easy. Here's the invocation I use:
```
$ thttpd -D -c *.cgi -p 8080
```
You can stick it in serve.sh for convenience.

## command line invocation
Remember how simple CGI is. The server just invokes your script with environment variables set up and standard input. Here are the three cases:

* PATH_INFO gets set to any path in the url after the script
* QUERY_STRING gets set for GET requests
* stdin is written for POST requests

Thus you set up an input file, and invoke `./control.cgi < input` to simulate the post requests.

Another method is just to supply more than one argument for the script to see that it's running locally. Separate all core functions from their web callers.
