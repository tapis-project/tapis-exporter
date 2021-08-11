from json import loads
import os
import sys
import time
import requests
import prometheus_client
from prometheus_client.core import REGISTRY, Gauge, GaugeMetricFamily


class TapisCollector(object):
    def __init__(self,tapis_url, tapis_services=[]):
        self.tapis_url = tapis_url
        
        # Use default serivces list if None has been specified
        if tapis_services is []:
            self.services = ['security','meta','streams']
        else:
            self.services = tapis_services

    def healthcheck(self, service):
        url = '%s/v3/%s/healthcheck' % (self.tapis_url, service)
        r = requests.get(url)
        status = r.status_code
        if (status == 200):
            return 1 # Healthy
        else:
            return 0 # Warning or Error

    def collect(self):

        # healthcheck
        healthcheck_metric = GaugeMetricFamily('tapis_service_health', 'Service Health', labels=['service'])
        for service in self.services:
            value = self.healthcheck(service)
            healthcheck_metric.add_metric([service], value)
        yield healthcheck_metric
    

if __name__ == "__main__":
    # Check that the environment variable TAPIS_URL has been specified, fail if it has not.
    try:
      tapis_url = os.environ['TAPIS_URL']
    except:
      sys.exit("[ERROR] Environment variable not set: TAPIS_URL")
    
    # Try to load serivces list from environment variable TAPIS_SERVICES
    tapis_serivces = loads(os.environ.get('TAPIS_SERVICES'),[])
                           
    prometheus_client.start_http_server(8000)
    REGISTRY.register(TapisCollector(tapis_url, tapis_services))
    while True: time.sleep(1)
