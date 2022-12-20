#!/bin/python3
import sys
import requests
import time
import logging
from func_timeout import func_set_timeout
from utils import ExceptionLogger
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
class CustomCollector(object):
    def collect(self):
        yield GaugeMetricFamily('my_gauge', 'Help text', value=7)
        c = CounterMetricFamily('my_counter_total', 'Help text', labels=['foo'])
        time.sleep(5)
        c.add_metric(['bar'], 1.7)
        c.add_metric(['baz'], 3.8)
        yield c

class CustomCollector2(object):
    def collect(self):
        yield GaugeMetricFamily('my_gauge1', 'Help text', value=7)
        c = CounterMetricFamily('my_counter_total1', 'Help text', labels=['foo'])
        time.sleep(5)
        c.add_metric(['bar'], 1.7)
        c.add_metric(['baz'], 3.8)
        yield c


if __name__ == "__main__":
    start_http_server(port=11122)
    REGISTRY.register(CustomCollector())
    REGISTRY.register(CustomCollector2())
    time.sleep(10000)