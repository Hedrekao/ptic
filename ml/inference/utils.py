from PIL import Image
import base64
import io
import requests
import os
from fastapi import HTTPException
from azure.storage.blob import BlobServiceClient


def base64_to_pil(base64_string: str) -> Image.Image:
    # We should use that later for supporting base64 encoded images
    """Convert base64 string to PIL Image."""
    try:
        # Remove data URL prefix if present
        if "base64," in base64_string:
            base64_string = base64_string.split("base64,")[1]

        # Decode base64 string
        image_data = base64.b64decode(base64_string)

        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))

        return image
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid image data: {str(e)}")


class StorageClient:
    def __init__(self):
        self.env = os.getenv('ENV', 'LOCAL')
        if self.env == 'AZURE':
            conn_str = os.getenv('BLOB_STORAGE_CONNECTION_STRING')
            self.blob_client = BlobServiceClient.from_connection_string(
                conn_str)
        else:
            self.server_url = os.getenv(
                'GO_SERVER_URL', 'http://localhost:4200')

    def get_image(self, file_path: str) -> Image.Image:
        if self.env == 'AZURE':
            container_name = "images"
            blob_client = self.blob_client.get_container_client(container_name)
            blob_data = blob_client.download_blob(file_path).readall()
            return Image.open(io.BytesIO(blob_data))
        else:
            response = requests.get(
                f"{self.go_server_url}/uploads/{file_path}", stream=True)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
