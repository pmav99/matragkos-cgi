## CGI example

### Prerequisites

You **need** to use python2!!!

You need to change the password for the emails!

### Instructions

1. Start the server: `python2 server.py`
2. Visit http://localhost:9999/ you will notice that the current directory is being served. The
   current directory is roughly equivalent to `http_public`. If you place an executable script
   in `./cgi-bin/` and visit it, it will be executed.
3. For example visit: http://localhost:9999/hello.py
4. Now visit http://localhost:9999/main_form.html
5. Fill in the form and click submit
6. Profit!
