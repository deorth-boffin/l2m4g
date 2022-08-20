#!/bin/python3
import logging
from prometheus_client import start_http_server
import click
from utils import JsonConfig, MyLogSettings, ExceptionLogger, my_log_settings
import exporters
import os
import sys
import time
from threading import Thread
from func_timeout import func_set_timeout
from typing import Callable
from functools import wraps



def install_systemd_service(ctx, _, value):
    if not value or ctx.resilient_parsing:
        return
    args = {p.name: p.default for p in ctx.command.params}
    args.update(ctx.params)
    my_log_settings(args.get("log"), args.get("log_level"))

    service_filename = "/etc/systemd/system/py-misc-exporter.service"
    env_filename = "/etc/default/py-misc-exporter"
    config_filename = "/etc/py-misc-exporter/pme.conf"

    python_path = sys.executable
    script_path = os.path.abspath(__file__)
    service_file_text = """[Unit]
Description=prometheus exporter for some of my devices written in python
Documentation=https://github.com/deorth-kku/py-misc-exporter
After=network.target nss-lookup.target
[Service]
EnvironmentFile=%s
User=root
ExecStart=%s %s
Restart=on-failure
[Install]
WantedBy=multi-user.target
""" % (env_filename, python_path, script_path)

    env_file_text = '''#configure command line args for systemd service here, run %s %s --help for more information
    PME_CONF="%s"
    PME_LOG_FILE="/var/log/pme.log"
    PME_LOG_LEVEL="INFO"
''' % (python_path, script_path, config_filename)

    if os.path.exists(service_filename):
        logging.error(
            "not overwriting exist service file %s, remove it first if you have to" % service_filename)
    else:
        with open(service_filename, "w") as f:
            f.write(service_file_text)
        logging.info("created service file %s" % service_filename)
        logging.warning(
            "you need to run \"systemctl daemon-reload\" manually (for now)")

    if os.path.exists(env_filename):
        logging.error(
            "not overwriting exist env file %s, remove it first if you have to" % env_filename)
    else:
        with open(env_filename, "w") as f:
            f.write(env_file_text)
        logging.info("created env file %s" % env_filename)

    if os.path.exists(config_filename):
        logging.error(
            "not overwriting exist env file %s, remove it first if you have to" % config_filename)
    else:
        os.makedirs(os.path.dirname(config_filename), exist_ok=True)
        f = JsonConfig(config_filename)
        f.dumpconfig({
            "exporter": {}
        })
        logging.info("created config file %s" % config_filename)

    ctx.exit()


class FuncJitInfRun(object):
    @staticmethod
    def wait_until_next(interval: int, jitter: float = 0) -> None:
        jitter = abs(jitter)
        if jitter < interval/2:
            time.sleep(jitter)
        now = time.time()
        wait = max(interval-(now % interval) - jitter, 0)
        time.sleep(wait)

    def __init__(self, interval) -> None:
        self.interval = interval


    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapped_function(*args, **kwargs):
            jitter = self.interval*0.48
            while True:
                self.__class__.wait_until_next(self.interval, jitter)
                logging.debug("started running function %s"%func.__name__)
                start_time = time.time()
                func(*args, **kwargs)
                used_time=time.time()-start_time
                logging.debug("finished running function %s, used time %.3fs"%(func.__name__,used_time))
                jitter = (used_time+jitter)*0.55+0.02
        return wrapped_function
                


@click.command(context_settings=dict(auto_envvar_prefix="PME"))
@click.option('--install', is_flag=True, callback=install_systemd_service,
              expose_value=False, is_eager=True, help='install systemd service file to system')
@click.option('-c', "--conf", type=click.Path(exists=True), help='using specific json config file', default="config.json", show_envvar=True, show_default=True)
@MyLogSettings(show_envvar=True, show_default=True)
@ExceptionLogger()
def main(conf):
    conf = JsonConfig(conf)
    start_http_server(conf.get("exporter", {}).get("port", 8900))
    inited_module = []
    for module_name in conf:
        if module_name == "exporter":
            continue
        try:
            module_init = eval("exporters.%s.init" % module_name)
        except AttributeError:
            logging.warning(
                "cannot run init() in module %s, please check if module is correctly written" % module_name)
            continue
        try:
            module_init(**conf[module_name])
        except Exception as e:
            logging.error(
                "init() in module %s failed with exception, see logs below")
            logging.exception(e)
            continue
        inited_module.append(module_name)
    interval = conf.get("exporter", {}).get("interval", 10)
    for module_name in inited_module:
        try:
            module_main = eval("exporters.%s.main" % module_name)
        except AttributeError:
            logging.warning(
                "cannot run main() in module %s, please check if module is correctly written" % module_name)
            continue
        module_main.__name__ = module_name+"_main"
        module_main = func_set_timeout(interval)(module_main)
        module_main = FuncJitInfRun(interval)(module_main)
        module_main = ExceptionLogger()(module_main)
        t = Thread(target=module_main, kwargs=conf[module_name])
        t.start()


        


if __name__ == "__main__":
    sys.exit(main())
