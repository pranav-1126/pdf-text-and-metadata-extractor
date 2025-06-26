import fitz  # PyMuPDF
import functions_framework
from google.cloud import storage, pubsub_v1
from datetime import datetime
import json

@functions_framework.cloud_event
def extract_pdf_metadata(cloud_event):
    bucket_name = cloud_event.data["bucket"]
    file_name = cloud_event.data["name"]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Download the PDF to a temp file
    temp_file = f"/tmp/{file_name}"
    blob.download_to_filename(temp_file)

    # Read PDF
    doc = fitz.open(temp_file)

    metadata = doc.metadata or {}
    title = metadata.get("title", "Unknown")
    author = metadata.get("author", "Unknown")
    num_pages = doc.page_count
    upload_time = datetime.utcnow().isoformat()

    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    result = {
        "file_name": file_name,
        "title": title,
        "author": author,
        "num_pages": num_pages,
        "upload_time": upload_time,
        "extracted_text": full_text[:500] + "..." if len(full_text) > 500 else full_text
    }

    print("Extracted PDF info:", json.dumps(result, indent=2))

    # Publish to Pub/Sub
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path("pdf-metadata-extractor-464017", "pdf-metadata-topic")
    publisher.publish(topic_path, json.dumps(result).encode("utf-8"))
