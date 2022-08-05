#!/bin/python3
import requests
import re
import logging
from prometheus_client import Info
from utils import ExceptionLogger

def init(**_):
    global tieba_userinfo_line
    tieba_userinfo_line = Info("tieba_userinfo_line",
                           "some userinfo from baidu tieba")

def get_userinfo(id: str) -> dict:
    url = "https://tieba.baidu.com/home/main?id=%s" % id
    text = requests.get(url).text
    regexes = {
        "username": '<span class="userinfo_username ">(.*?)</span>',
        "location": "<span>IP属地:(.*?)</span>"
    }
    out = {'id': id}
    for arg in regexes:
        try:
            value = re.findall(regexes[arg], text)[0]
        except IndexError:
            value = "Failed"
            logging.warning("getting id %s %s failed" % (id, arg))
        out.update({arg: value})
    return out


@ExceptionLogger()
def main(**config) -> None:
    for id in config["ids"]:
        info = get_userinfo(id)
        tieba_userinfo_line.info(info)



if __name__ == "__main__":
    pass
