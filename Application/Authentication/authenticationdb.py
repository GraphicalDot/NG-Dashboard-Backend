
import sys
from os.path import dirname, abspath
parentdir = dirname(dirname(abspath(__file__)))
print (parentdir)
sys.path.append(parentdir)
from custom_logging import logger
import coloredlogs

logger.debug("Hey now")


