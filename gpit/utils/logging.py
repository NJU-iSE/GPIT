import logging

COL_LOG = logging.getLogger("COLLECTING")
ClE_LOG = logging.getLogger("CLEANING")
COU_LOG = logging.getLogger("COUNTING")

COL_LOG.setLevel(logging.INFO)
COL_LOG.addHandler(logging.StreamHandler())

