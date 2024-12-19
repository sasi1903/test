from fastapi import FastAPI, File, UploadFile
from azure.storage.blob import BlobServiceClient
from mangum import Mangum
import os

app = FastAPI()

# Azure Blob Storage configuration
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "largefiles"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Create a BlobClient for the file
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=file.filename)

        # Upload file in chunks
        chunk_size = 4 * 1024 * 1024  # 4MB chunk size
        with file.file as file_stream:
            while chunk := file_stream.read(chunk_size):
                blob_client.upload_blob(chunk, blob_type="BlockBlob", overwrite=True)

        return {"filename": file.filename, "status": "uploaded successfully"}
    except Exception as e:
        return {"error": str(e)}

# Azure Functions adapter
handler = Mangum(app)
