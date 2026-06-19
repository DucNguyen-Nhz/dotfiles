import os
import logging
import httpx
from django.conf import settings

logger = logging.getLogger('info_logger')

class CallCenter:
    _instance = None

    host = settings.CALL_CENTER_HOST
    auth_token = settings.CALL_CENTER_AUTH_TOKEN

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> httpx.Client:
        return httpx.Client(
            base_url=self.host,
            headers={
                "Authorization": f"Basic {self.auth_token}",
            },
        )

    def import_leads_by_excel(self, campaign: str, filepath: str):
        try:
            with open(filepath, "rb") as f:
                files = {
                    "file": (os.path.basename(filepath), f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                }
                resp = self.client.post(
                    f'api/campaigns/{campaign}/import-customers/',
                    files=files,
                    data={ "campaign_id": campaign },
                    timeout=60
                )
                resp.raise_for_status()
                resp_json = resp.json()
                return resp_json.get("file_upload_id", "")

        except httpx.HTTPStatusError as err:
            logger.error(
                f"Push leads to excel failed: {err.response.status_code}",
                exc_info=err
            )
            logger.info(err.response.text)

            raise err

    def import_job_status(self, campaign: str, job_id: str):

        try:
            response = self.client.get(f'api/campaigns/{campaign}/import-customers/{job_id}/')
            response.raise_for_status()
            response_json = response.json()
            if "status" not in response_json:
                raise ValueError("Error: {}".format(response.text))

            if response_json["status"] == 0:
                return 0

            return response_json

        except Exception as e:
            logger.error("get_job_import_status - Error: {}".format(e))
            raise e

