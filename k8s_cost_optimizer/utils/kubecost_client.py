import httpx
import json
from .logger import logger

class KubecostClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.http_client = httpx.Client(timeout=20.0)
        logger.info("Kubecost client initialized", url=self.base_url)

    def get_total_monthly_cost(self) -> float:
        try:
            response = self.http_client.get(
                f"{self.base_url}/model/allocation",
                params={"window": "today", "aggregate": "cluster"}
            )
            response.raise_for_status()
            
            try:
                data = response.json()
            except json.JSONDecodeError:
                logger.warning("Kubecost returned a non-JSON response, likely still warming up. Using fallback cost.")
                return 1500.0
            
            if not data.get('data'):
                logger.warning("Kubecost data is empty, returning fallback cost.")
                return 1500.0

            # --- THE FIX IS HERE ---
            # We add "if item" to safely skip any None values in the list
            total_cost = sum(item.get('totalCost', 0) for item in data['data'] if item)

            if total_cost == 0:
                logger.warning("Kubecost returned zero total cost, likely still warming up. Using fallback cost.")
                return 1500.0
            return round(total_cost, 2)
        except (httpx.RequestError, httpx.HTTPStatusError, KeyError, IndexError) as e:
            logger.error("Failed to get or parse cost data from Kubecost", error=str(e))
            return 1500.0

    def get_savings_recommendations(self) -> list:
        try:
            response = self.http_client.get(f"{self.base_url}/model/savings")
            response.raise_for_status()
            data = response.json()
            recommendations = data.get('data', [])
            logger.info(f"Retrieved {len(recommendations)} savings recommendations from Kubecost.")
            return recommendations
        except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
            logger.error("Failed to retrieve savings recommendations from Kubecost", error=str(e))
            return []

