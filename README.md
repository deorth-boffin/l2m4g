# py-misc-exporter
prometheus exporter for some of my devices/services that I am using written in python.
# Installation
## Install global dependencies
`pip3 install -r requirement.txt`
## Optional dependency
See dependency section in each plugin section.
## clone repository
clone this repository:  
`git clone --recursive https://github.com/deorth-kku/py-misc-exporter.git`
## Run
```
cd py-misc-exporter
python3 main.py
```
# Configuration
As you can see from the command line help `python3 main.py --help`, there are only 4 command line option.  
Suggested way to use this is creating a systemd service by using the `--install` option, once executed, it will create three files:
* service file: /etc/systemd/system/py-misc-exporter.service
* environment file: /etc/default/py-misc-exporter
* config file: /etc/py-misc-exporter/pme.conf
And before you start the service, you need to run `systemctl daemon-reload` as the terminal log suggested.
## Environment file
Environment just the way to write command line option to a file instead of writing it to service file, therefore, three environment option is just the aliases of three command options
* PME_CONF: using specific json config file. If none specificed, use config.json from current directory.
* PME_LOG_FILE: using specific log file. If none specificed, use STDERR as output.
* PME_LOG_LEVEL: using specific log level. Default level is INFO
## Config file
### Global config
Global configuration are in the "export" setion, there are only 2 args:
* "port": http listening port, default: 8900
* "interval": metrics update interval (seconds), default: 10. Suggest to set the same as your prometheus job interval.
#### example
```
    "exporter":{
        "port":8901,
        "interval":5
    }
```
### Plugins config
Plugins configuration is written as `"plugin_name"` setion.  
Argument in each setion will be directly pass to plugin as it's keyword argments. See configuration section in each plugin section.  
Only plugin that its configuration existed in config file will be enabled. So even if the plugin does not need configuration at all, you will need to create its config setion as an empty dict, like this:
```
    "s_tui_sensors":{}
```
# Plugins
## tplink
Exporter for tplink router. China mainland model only. 
### Dependency
No extra dependency.
### Configuration options
Example:
```
"tplink":{
    "host":"192.168.1.1",
    "password":"qwerty"
}
```
* host: your router ip/hostname. Default: "tplogin.cn"
* password: your router admin password. This option is required.
### Garfana dashboard
See:
[Dashboard](dashboards/tplink.json)  
Showcase:  
![Showcase](https://user-images.githubusercontent.com/23164110/209465835-79c556f8-e537-409a-9a66-d4d6b2ed2dbc.jpg)
## viewpower
UPS statitics from viewpower WebUI
### Dependency
No extra dependency.
### Configuration options
* host: viewpower web host. Default: "127.0.0.1"
* port: viewpower web port. Default: 15178
* proto: "http" or "https". Default: "http"
* timeout: http request timeout. Default: 5.
### Garfana dashboard
See:
[Dashboard](dashboards/viewpower.json)  
Showcase:  
![Showcase](https://user-images.githubusercontent.com/23164110/209465880-cfb57d5c-40a3-44bc-b858-918de07bc561.jpg)
## s_tui_sensors
Export machine's sensors data from [s-tui](https://github.com/amanusk/s-tui).
### Install dependency
Follow the instruction from s-tui's [Simple installation](https://github.com/amanusk/s-tui#simple-installation).
### Configuration options
No need for configuration, leave it empty as the [Plugins config](#plugins-config) example did.
### Garfana dashboard
See:
[Dashboard](dashboards/s-tui.json)  
Showcase:  
![Showcase](https://user-images.githubusercontent.com/23164110/209465897-d6142827-aeb8-4fe5-a645-fde7f1960fd5.jpg)
## aria2
Export [aria2](https://github.com/aria2/aria2) download status data.
### Dependency
No extra dependency.
### Configuration options
Example:
```
"aria2":{
    "host":"aria2.server",
    "port":6801,
    "passwd":"qwerty"
}
```
* host: aria2 host. Default: "127.0.0.1"
* port: aria2 port. Default: 6800
* passwd: aria2 secert. Default: ""
* protocal: "http" or "https". Default: "http"
* api: "jsonrpc" or "xmlrpc". Default: "xmlrpc"
### Garfana dashboard
See:
[Dashboard](dashboards/aria2.json)  
Showcase:  
![Showcase](https://user-images.githubusercontent.com/23164110/209465906-930969f1-131e-4675-ab20-8b20e8ff0842.jpg)
## ryzenadj
AMD APU statistic from [RyzenAdj](https://github.com/FlyGoat/RyzenAdj)  
Python wrapper from [ryzen-ppd](https://github.com/xsmile/ryzen-ppd)
### Dependency
See ryzenppd's [Requirements](https://github.com/xsmile/ryzen-ppd#requirements)
### Configuration options
No need for configuration.
### Garfana dashboard
See:
[Dashboard](dashboards/amd-cpu-gpu-stats.json)  
Showcase:  
![Showcase](https://user-images.githubusercontent.com/23164110/209465985-603651d4-b4a1-4791-bed2-8998abdb3cf5.jpg)
## amdgpu
AMD GPU statistic from [pyamdgpuinfo](https://github.com/mark9064/pyamdgpuinfo)
### Dependency
`pip3 install pyamdgpuinfo`
### Configuration options
No need for configuration.
### Garfana dashboard
Shared with [ryzenadj](#ryzenadj)
# TODO
* [ ] aria2_task_download/uploadBytesTotal
