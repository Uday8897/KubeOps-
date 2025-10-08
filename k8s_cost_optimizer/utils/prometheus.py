from prometheus_api_client import PrometheusConnect
from .logger import logger

class PrometheusClient:
    def __init__(self, url: str, timeout: int):
        self.client = None
        try:
            self.client = PrometheusConnect(url=url, disable_ssl=True)
            if self.client.check_prometheus_connection():
                logger.info("Prometheus client connected", url=url)
            else:
                self.client = None
                logger.warning("Prometheus connection check failed", url=url)
        except Exception as e:
            logger.error("Prometheus client initialization failed", error=str(e))
            self.client = None

    def query(self, query: str):
        if not self.client:
            return None
        try:
            return self.client.custom_query(query=query)
        except Exception as e:
            logger.error("Prometheus query failed", query=query, error=str(e))
            return None