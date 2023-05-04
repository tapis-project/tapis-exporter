from json import loads
import os
import sys
import time
import re
import requests
import prometheus_client
from prometheus_client.core import REGISTRY, CounterMetricFamily, Gauge, GaugeMetricFamily
import pymongo

streams_regex = re.compile('^Streams(.*)DB$')

class TapisCollector(object):
    def __init__(self,tapis_url, meta_mongo_uri, tapis_services=[]):
        self.tapis_url = tapis_url
        
        # Use default serivces list if None has been specified
        if tapis_services is []:
            self.services = ['security','meta','streams']
        else:
            self.services = tapis_services

        self.mongo_client = pymongo.MongoClient(
                            meta_mongo_uri,
                            authSource='admin',
                            username=os.environ['META_USER'],
                            password=os.environ['META_PASSWORD'])

    def healthcheck(self, service):
        url = '%s/v3/%s/healthcheck' % (self.tapis_url, service)
        r = requests.get(url, verify=False)
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
          healthcheck_metric.add_metric([service], value )
        yield healthcheck_metric
        
        # streams
        streams_transfers_total = CounterMetricFamily('tapis_streams_transfers_total', 'Number of streams data transfers', labels=['type','tenant'])
        streams_transfers_bytes = CounterMetricFamily('tapis_streams_transfers_bytes', 'Amount of streams data collected', labels=['type','tenant'], unit='bytes')

        mongo_dbs = self.mongo_client.list_database_names()
        streams_dbs_names = filter(streams_regex.match, mongo_dbs)

        for db_name in streams_dbs_names:
          tenant = streams_regex.match(db_name).group(1)

          streams_db = self.mongo_client[db_name]
          streams_metrics = streams_db['streams_metrics']
          streams_xfer_agg = streams_metrics.aggregate(
            [
              {
                "$group": {
                  "_id": "$type",
                  "bytes": {"$sum": {"$toInt" : "$size"}},
                  "count": {"$sum": 1}
                }
              }
            ]
          )
          streams_xfer_summary = list(streams_xfer_agg)
  
          for entry in streams_xfer_summary:
            streams_transfers_total.add_metric([entry['_id'],tenant], entry['count'])
            streams_transfers_bytes.add_metric([entry['_id'],tenant], entry['bytes'])
  
        yield streams_transfers_total
        yield streams_transfers_bytes

if __name__ == "__main__":
    # Check that the environment variables have been specified, fail if they have not.
    tapis_url = os.environ["TAPIS_URL"]
        
    # Try to load serivces list from environment variable TAPIS_SERVICES
    service_env = os.getenv('TAPIS_SERVICES', "")
    if not service_env:
        tapis_services = []
    else:
        tapis_services = loads(service_env)

    meta_mongo_uri = os.getenv('META_DB_URL','mongodb://restheart-mongo:27017/')
    
    print("Detected Inputs")
    print("TAPIS_URL : {}".format(tapis_url))
    print("TAPIS_SERVICES : {}".format(tapis_services))
    print("META_DB_URL : {}".format(meta_mongo_uri))
    print("META_USER : {}".format(os.environ['META_USER']))
    sys.stdout.flush()

    prometheus_client.start_http_server(8000)
    REGISTRY.register(TapisCollector(tapis_url, meta_mongo_uri, tapis_services))
    while True: time.sleep(1)
