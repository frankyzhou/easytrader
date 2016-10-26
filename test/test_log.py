# from easytrader import log
#
# log.info("info")
# log.warn("warn")
# log.error("error")

from trade.util import *

logger = get_logger("test", "test")
logger.info("test")
