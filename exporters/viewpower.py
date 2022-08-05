#!/bin/python3
import requests
import logging
from prometheus_client import Gauge, Info
from utils import ExceptionLogger

def get_monitor_data(host="127.0.0.1", port=15178, proto="http"):
    monitor_url = "%s://%s:%s/ViewPower/workstatus/reqMonitorData" % (
        proto,host,port)
    req = requests.get(url=monitor_url)
    return req.json()

def init():
    global viewpower_metrics
    global viewpower_info
    viewpower_info=Info("viewpower_workInfo","viewpower workInfo none-numeric args")
    viewpower_metrics={}

@ExceptionLogger()
def main(**config):
    data=get_monitor_data(host=config.get("host","127.0.0.1"),port=config.get("port",15178),proto=config.get("proto","http"))["workInfo"]
    info={}
    for arg in data:
        try:
            value=float(data[arg])
        except ValueError:
            if type(data[arg])==str and data[arg]!="":
                info.update({arg:data[arg]})
            continue
        except TypeError:
            continue
        
        metric_name="viewpower_"+arg
        if metric_name not in viewpower_metrics:
            logging.debug("add metric %s"%metric_name)
            metric_obj=Gauge(metric_name,documentation="")
            viewpower_metrics.update({metric_name:metric_obj})
        else:
            metric_obj=viewpower_metrics[metric_name]

        metric_obj.set(value)
    viewpower_info.clear()
    viewpower_info.info(info)
    

if __name__ == "__main__":
    main()
