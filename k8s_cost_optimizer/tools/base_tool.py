from abc import ABC, abstractmethod
from typing import List
from k8s_cost_optimizer.models.schemas import OptimizationAction
from k8s_cost_optimizer.utils.k8s_client import KubernetesClient
from k8s_cost_optimizer.utils.prometheus import PrometheusClient

class BaseOptimizationTool(ABC):
    def __init__(
        self,
        k8s_client: KubernetesClient,
        prometheus_client: PrometheusClient,
    ):
        self.k8s_client = k8s_client
        self.prometheus_client = prometheus_client

    @abstractmethod
    def analyze(self) -> List[OptimizationAction]:
        pass