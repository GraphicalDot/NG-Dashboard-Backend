#!/usr/bin/env python3

import sys
from os.path import dirname, abspath
parentdir = dirname(dirname(abspath(__file__)))
sys.path.append(parentdir)
from custom_logging import logger
from settings import 