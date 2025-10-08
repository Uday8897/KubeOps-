from kubernetes import client, config
from kubernetes.client.rest import ApiException
from .logger import logger

class KubernetesClient:
    def __init__(self):
        try:
            config.load_incluster_config()
            self.in_cluster = True
        except config.ConfigException:
            config.load_kube_config()
            self.in_cluster = False
        
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.autoscaling_v2 = client.AutoscalingV2Api()
        logger.info("Kubernetes client initialized", mode="in-cluster" if self.in_cluster else "kube-config")

    def get_nodes(self) -> list:
        try:
            return self.core_v1.list_node().items
        except ApiException as e:
            logger.error("Failed to get nodes", error=str(e))
            return []

    def get_all_pods(self) -> list:
        try:
            return self.core_v1.list_pod_for_all_namespaces().items
        except ApiException as e:
            logger.error("Failed to get pods", error=str(e))
            return []

    def get_unbound_pvcs(self) -> list:
        try:
            pvcs = self.core_v1.list_persistent_volume_claim_for_all_namespaces().items
            mounted_claims = set()
            all_pods = self.get_all_pods()

            for pod in all_pods:
                if pod.spec.volumes:
                    for volume in pod.spec.volumes:
                        if volume.persistent_volume_claim:
                            mounted_claims.add(f"{pod.metadata.namespace}/{volume.persistent_volume_claim.claim_name}")
            
            unbound_pvcs = [
                pvc for pvc in pvcs
                if pvc.status.phase != "Bound" or f"{pvc.metadata.namespace}/{pvc.metadata.name}" not in mounted_claims
            ]
            return unbound_pvcs
        except ApiException as e:
            logger.error("Failed to get unbound PVCs", error=str(e))
            return []

    def list_hpas(self) -> list:
        try:
            return self.autoscaling_v2.list_horizontal_pod_autoscaler_for_all_namespaces().items
        except ApiException as e:
            logger.error("Failed to list HPAs", error=str(e))
            return []

    def delete_pod(self, name: str, namespace: str) -> bool:
        try:
            self.core_v1.delete_namespaced_pod(name=name, namespace=namespace)
            logger.info("Successfully deleted pod", pod_name=name, namespace=namespace)
            return True
        except ApiException as e:
            logger.error("Failed to delete pod", pod_name=name, namespace=namespace, error=str(e))
            return False

    def delete_pvc(self, name: str, namespace: str) -> bool:
        try:
            self.core_v1.delete_namespaced_persistent_volume_claim(name=name, namespace=namespace)
            logger.info("Successfully deleted PVC", pvc_name=name, namespace=namespace)
            return True
        except ApiException as e:
            logger.error("Failed to delete PVC", pvc_name=name, namespace=namespace, error=str(e))
            return False
            
    def cordon_node(self, node_name: str) -> bool:
        try:
            body = {"spec": {"unschedulable": True}}
            self.core_v1.patch_node(name=node_name, body=body)
            logger.info("Successfully cordoned node", node_name=node_name)
            return True
        except ApiException as e:
            logger.error("Failed to cordon node", node_name=node_name, error=str(e))
            return False

    def drain_node(self, node_name: str) -> bool:
        log = logger.bind(node_name=node_name)
        try:
            pods = self.core_v1.list_pod_for_all_namespaces(field_selector=f'spec.nodeName={node_name}').items
            for pod in pods:
                if pod.metadata.namespace in ["kube-system", "opencost"]:
                    log.info("Skipping eviction for system pod", pod_name=pod.metadata.name, namespace=pod.metadata.namespace)
                    continue
                
                eviction_body = client.V1Eviction(
                    metadata=client.V1ObjectMeta(name=pod.metadata.name, namespace=pod.metadata.namespace),
                    delete_options=client.V1DeleteOptions(grace_period_seconds=30)
                )
                self.core_v1.create_namespaced_pod_eviction(name=pod.metadata.name, namespace=pod.metadata.namespace, body=eviction_body)
                log.info("Evicted pod", pod_name=pod.metadata.name, namespace=pod.metadata.namespace)
            
            log.info("Successfully drained pods from node")
            return True
        except ApiException as e:
            log.error("Failed to drain node", error=str(e))
            return False