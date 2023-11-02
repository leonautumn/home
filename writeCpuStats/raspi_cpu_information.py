import sys, time, psutil
import logging as log
from gpiozero import CPUTemperature
from influxdb import InfluxDBClient

BYTES_TO_GB = 1 / 1024.0 / 1024.0 / 1024.0

def getCPUInformation():
    # CPU temperature
    cpuTemperature = round(CPUTemperature().temperature, 2)
    cpuInformation = {"cpuTemperature": cpuTemperature}

    # CPU load
    cpuLoad = round(psutil.cpu_percent(), 2)
    cpuInformation.update({"cpuLoad": cpuLoad})

    # Disk total
    disk = psutil.disk_usage('/')
    diskTotal = round(disk.total * BYTES_TO_GB, 2)
    cpuInformation.update({"diskTotal": diskTotal})

    # Disk free
    diskFree = round(disk.free * BYTES_TO_GB, 2)
    cpuInformation.update({"diskFree": diskFree})

    # Disk usage
    diskUsage = round((diskTotal - diskFree) / diskTotal * 100.0, 2)
    cpuInformation.update({"diskUsage": diskUsage})

    log.info(cpuInformation)

    return cpuInformation
