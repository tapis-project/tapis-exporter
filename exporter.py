from json import loads
import os
import sys
from tapipy.tapis import Tapis
import time
import requests
import prometheus_client
from prometheus_client.core import REGISTRY, CounterMetricFamily, Gauge, GaugeMetricFamily
import pymongo


class TapisCollector(object):
    def __init__(self,tapis_url, tapis_services=[], streams_db):
        self.tapis_url = tapis_url
        
        # Use default serivces list if None has been specified
        if tapis_services is []:
            self.services = ['security','meta','streams']
        else:
            self.services = tapis_services

        self.service_token = Tapis(base_url=tapis_url,
                              username=os.environ['STREAMS_USER'],
                              account_type='service',
                              service_password=os.environ['STREAMS_SERVICE_PASSWORD'],
                              tenant_id='master')

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
        
        # streams
        yield CounterMetricFamily('tapis_streams_uploads_total_bytes', 'Amount of streaming data collected', labels=['report','streams'],
                                  value=self.service_token.meta.getCollection('streams_metrics').aggregate($group:{type:'upload', total:{$sum:"$size"}))
        yield CounterMetricFamily('tapis_streams_uploads_total', 'Number of data streams transferred', labels=['report','streams'],
                                  value=self.service_token.meta.getCollection('streams_metrics').find({type:'upload'}).count())
        yield CounterMetricFamily('tapis_streams_uploads_total', 'Number of stream archive policies registered', labels=['report','streams'],
                                  value=self.service_token.meta.getCollection('streams_metrics').find({type:'archive'}).count())
    

if __name__ == "__main__":
    # Check that the environment variables have been specified, fail if they have not.
    tapis_url = os.environ["TAPIS_URL"]
    streams_db = os.environ['STREAMS_USER']
        
    # Try to load serivces list from environment variable TAPIS_SERVICES
    service_env = os.getenv('TAPIS_SERVICES', "")
    if not service_env:
        tapis_services = []
    else:
        tapis_services = loads(service_env)
    
    print("Detected Inputs")
    print("TAPIS_URL : {}".format(tapis_url))
    print("TAPIS_SERVICES : {}".format(tapis_services))
    print("STREAMS_DB : {}".format(streams_db))

    prometheus_client.start_http_server(8000)
    REGISTRY.register(TapisCollector(tapis_url, tapis_services, streams_db))
    while True: time.sleep(1)
