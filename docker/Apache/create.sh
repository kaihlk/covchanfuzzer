#!/bin/bash

docker pull httpd

docker run -d -p 8080:80 -v /path/to/my_website:/usr/local/apache2/htdocs httpd
