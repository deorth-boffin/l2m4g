#!/bin/python3
import sys
import requests
import time
import logging
from func_timeout import func_set_timeout
from utils import ExceptionLogger

@func_set_timeout(5)
@ExceptionLogger(exceptions=Exception, handler_func=(logging.exception,))
def test():
    requests.get("http://baidu.com:12800",timeout=5,proxies={"http":"http://127.0.0.1:8888"})


if __name__ == "__main__":
    test()
