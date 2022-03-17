#!/usr/bin/env python3

import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/usr/local/etc/recommendit') #'/home/ubuntu/recommendit') #'/var/www/html') #'/home/username/ExampleFlask/ExampleFlask')
from app import app as application
application.secret_key = 'anything you wish'

