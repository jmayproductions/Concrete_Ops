# modules/data_hub/cloud_exporter.py

"""
ConcreteOps: Cloud Exporter
Uploads validated and cleaned data from ConcreteOps to cloud storage platforms like GCP, AWS S3, or Azure Blob.
Supports structured export with automatic bucket path formatting by project and module type.
"""

import os
import datetime
from shared.utils import log_event


class CloudExporter:
    def __init__(self, project_id, backend='gcp'):
        self.project_id = project_id
        self.backend = backend.lower()
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    def export(self, df, module_name, export_path=None):
        filename = f"{self.project_id}_{module_name}_{self.timestamp}.csv"
        local_path = os.path.join("/tmp", filename)
        df.to_csv(local_path, index=False)

        if self.backend == 'gcp':
            return self._upload_to_gcp(local_path, module_name)
        elif self.backend == 'aws':
            return self._upload_to_s3(local_path, module_name)
        elif self.backend == 'azure':
            return self._upload_to_azure(local_path, module_name)
        else:
            raise NotImplementedError(f"Cloud backend '{self.backend}' not supported.")

    def _upload_to_gcp(self, path, module_name):
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket("concreteops-bucket")
        blob = bucket.blob(f"{self.project_id}/{module_name}/{os.path.basename(path)}")
        blob.upload_from_filename(path)
        log_event(f"[{self.project_id}] Exported to GCP: {blob.public_url}")
        return blob.public_url

    def _upload_to_s3(self, path, module_name):
        import boto3
        s3 = boto3.client('s3')
        key = f"{self.project_id}/{module_name}/{os.path.basename(path)}"
        s3.upload_file(path, "concreteops-bucket", key)
        url = f"https://s3.amazonaws.com/concreteops-bucket/{key}"
        log_event(f"[{self.project_id}] Exported to S3: {url}")
        return url

    def _upload_to_azure(self, path, module_name):
        from azure.storage.blob import BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_CONN_STRING"))
        blob_client = blob_service_client.get_blob_client(container="concreteops", blob=f"{self.project_id}/{module_name}/{os.path.basename(path)}")
        with open(path, "rb") as data:
            blob_client.upload_blob(data)
        url = blob_client.url
        log_event(f"[{self.project_id}] Exported to Azure: {url}")
        return url
