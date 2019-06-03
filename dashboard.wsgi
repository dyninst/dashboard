import os
import sys

local_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, local_dir)
os.chdir(local_dir)

import bottle
import dashboard
application = bottle.default_app()
