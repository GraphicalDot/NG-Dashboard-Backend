#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
parentdir = dirname(dirname(abspath(__file__)))
sys.path.append(parentdir)
from custom_logging import logger
print (logger)
#import coloredlogs

import logging
def testing():
	#logger.debug("Hey now")
	logging.info("Hey now")
	print ("Hey now")
	return 

