#import json
import time
import requests
import prometheus_client
from prometheus_client.core import REGISTRY, Gauge, GaugeMetricFamily


class TapisCollector(object):
    def __init__(self):
        pass

    def healthcheck(self, service):
        url = 'https://dev.develop.tapis.io/v3/%s/healthcheck' % service
        r = requests.get(url)
        status = r.status_code
        if (status == 200):
            return 1 # Healthy
        else:
            return 0 # Warning or Error

    def collect(self):

        # healthcheck
        healthcheck_metric = GaugeMetricFamily('tapis_service_health', 'Service Health', labels=['service'])
        for service in ['security','meta']:
            value = self.healthcheck(service)
            healthcheck_metric.add_metric([service], value)
        yield healthcheck_metric
    

if __name__ == "__main__":
    prometheus_client.start_http_server(8000)
    REGISTRY.register(TapisCollector())
    while True: time.sleep(1)
