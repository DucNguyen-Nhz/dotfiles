import os
import requests
from elasticsearch import Elasticsearch, RequestsHttpConnection
import logging
import platform

logger = logging.getLogger('info_logger')

class ELKService:
    
    def __init__(self):
        
        self.proxy_enabled = os.getenv("ES_PROXY_ENABLE", "false") == "false"
        self.host = os.getenv("MC_ES_HOST")
        self.user = os.getenv("MC_ES_USER")
        self.password = os.getenv("MC_ES_PASS")
        self.http_proxy = os.getenv("HTTP_PROXY", "http://10.36.232.10:8080")
        self.https_proxy = os.getenv("HTTPS_PROXY", "https://10.36.232.10:8080")

    @property
    def client(self): 
        try:
            if platform.system() == "Windows":
                session = requests.Session()
                session.proxies = {
                    "http": self.http_proxy,
                    "https": self.https_proxy
                }
            
                return Elasticsearch(
                    hosts=[self.host],
                    connection_class=RequestsHttpConnection,
                    http_auth=(self.user, self.password),
                    verify_certs=False,
                    session = session 
                )

            return Elasticsearch(
                hosts=[self.host],
                http_auth=(self.user, self.password),
                verify_certs=False
            )
        
        except Exception as e:
            raise e
    

    def _query(self, query: dict, index_name: str):
        
        scroll_id = None
        try:
            response = self.client.search(index=index_name, scroll="2m", size=10000, body=query)
            scroll_id = response.get("_scroll_id")
            hits = response["hits"]["hits"]

            yield hits
            page = 2

            while len(hits) > 0:
                page += 1
                response = self.client.scroll(scroll_id=scroll_id, scroll='2m')
                hits = response["hits"]["hits"]
                yield hits

        except Exception as e:
            raise e

        finally:

            if scroll_id:
                try:
                    self.client.clear_scroll(scroll_id=scroll_id)
                except Exception as e:
                    logger.warning(f"Failed to clear scroll: {e}")

    
    def query(self, query: dict, index_name: str = "callcenter-calllog-*"):
        response = []
        for result in self._query(query, index_name):
            response += result
        
        return [item["_source"] for item in response]
        

