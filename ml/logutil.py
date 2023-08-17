# -*- coding: utf-8 -*-
# @Author: libin
# @Date: 2023-04-21 09:54:53
# @email: 1499237580@qq.com
# @Software: Sublime Text
import logging
import logging.handlers
from config import Config

# 日志系统， 既要把日志输出到控制台， 还要写入日志文件
g_loggerInited = False


def getLogger():
    config = Config()
    global g_loggerInited
    if g_loggerInited:
        return logging.getLogger(config.name)
    else:
        logger = logging.getLogger(config.name)
        logger.setLevel(config.log_level)

        # 创建一个handler，用于写入日志文件
        # fh = logging.FileHandler(logfile)
        # filename = sys.path[0]+ config.log_path
        filename = config.log_path
        fh = logging.handlers.TimedRotatingFileHandler(
            filename=filename, when="D", interval=1, backupCount=30, encoding="utf-8")
        fh.setLevel(config.log_level)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(config.log_level)

        # 定义handler的输出格式
        formatter = logging.Formatter(config.log_format)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        g_loggerInited = True
        # logger.info("logger inited....")
        return logger
