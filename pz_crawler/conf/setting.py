# -*- coding: utf-8 -*-

__author__ = 'commissar'

import logging
import logging.config
import os

log_conf_file = os.path.abspath(os.path.join( os.path.dirname(__file__),"log.conf"))


logging.config.fileConfig(log_conf_file)

log = logging.getLogger("pz_crawler.package")
