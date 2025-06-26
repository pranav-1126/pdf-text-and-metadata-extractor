# 📄 PDF Metadata and Text Extractor using Google Cloud

This project automatically extracts **metadata** and **text** from PDF files uploaded to a Cloud Storage bucket, using Google Cloud services. The metadata and text preview are then published to a Pub/Sub topic for further processing or logging.

---

## 🚀 Services Used

| Service                         | Purpose                                                        |
|---------------------------------|----------------------------------------------------------------|
| **Google Cloud Storage (GCS)** | Stores uploaded PDF files                                      |
| **Google Cloud Functions**     | Executes code when a new file is uploaded                      |
| **Eventarc**                   | Automatically triggers the Cloud Function                      |
| **Pub/Sub**                    | Publishes extracted metadata + text to a messaging topic       |

---

## 🧱 Architecture

User Uploads PDF
↓
Google Cloud Storage (Bucket: pdf-upload-pranav)
↓
Eventarc (Triggers Function on File Upload)
↓
Cloud Function: extract_pdf_metadata
↓

Extracts:
• File name
• Title
• Author
• Number of pages
• Upload timestamp
• First 500 characters of PDF text
↓
Publishes result to Pub/Sub topic: pdf-metadata-topic

yaml
Copy
Edit

---

## 🧠 What the Function Does

- Listens to finalized (uploaded) PDFs in your Cloud Storage bucket
- Opens the PDF using `PyMuPDF`
- Extracts:
  - File name
  - Metadata (title, author)
  - Page count
  - Upload timestamp
  - Preview of full extracted text
- Publishes the info as JSON to a Pub/Sub topic

---

## 🧪 Sample Output

```json
{
  "file_name": "Cloud Metadata Extraction.pdf",
  "title": "Cloud Metadata Extraction",
  "author": "Pranav Naik",
  "num_pages": 1,
  "upload_time": "2025-06-26T09:30:30.634492",
  "extracted_text": "Title: Cloud Metadata Extraction \nAuthor: Pranav Naik \n\nThis is a sample PDF created by Pranav Naik for testing..."
}
⚙️ How to Deploy
1. Enable Required Services
bash
Copy
Edit
gcloud services enable \
  cloudfunctions.googleapis.com \
  pubsub.googleapis.com \
  storage.googleapis.com \
  eventarc.googleapis.com
2. Create Cloud Storage Bucket
bash
Copy
Edit
gsutil mb -l asia-south1 gs://pdf-upload-pranav/
3. Create Pub/Sub Topic and Subscription
bash
Copy
Edit
gcloud pubsub topics create pdf-metadata-topic
gcloud pubsub subscriptions create pdf-metadata-sub --topic=pdf-metadata-topic
4. Create These Files in Your Project Folder (pdf-function/)
✅ main.py
python
Copy
Edit
import fitz  # PyMuPDF
import functions_framework
from google.cloud import storage
from google.cloud import pubsub_v1
from datetime import datetime
import json

@functions_framework.cloud_event
def extract_pdf_metadata(cloud_event):
    bucket_name = cloud_event.data["bucket"]
    file_name = cloud_event.data["name"]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    temp_file = f"/tmp/{file_name}"
    blob.download_to_filename(temp_file)

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
✅ requirements.txt
pgsql
Copy
Edit
functions-framework==3.5.0
google-cloud-storage
PyMuPDF
google-cloud-pubsub
✅ .gitignore
markdown
Copy
Edit
__pycache__/
*.pyc
.env
*.zip
.DS_Store
.idea/
.vscode/
🚀 Deploy Cloud Function
bash
Copy
Edit
gcloud functions deploy extract_pdf_metadata \
  --gen2 \
  --region=asia-south1 \
  --runtime=python310 \
  --source=. \
  --entry-point=extract_pdf_metadata \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=pdf-upload-pranav"
🧪 How to Test
Upload a test PDF
bash
Copy
Edit
gsutil cp test.pdf gs://pdf-upload-pranav/
Check Function Logs
bash
Copy
Edit
gcloud functions logs read extract_pdf_metadata --region=asia-south1 --limit=10
Pull Pub/Sub Message
bash
Copy
Edit
gcloud pubsub subscriptions pull pdf-metadata-sub --limit=1 --auto-ack
📌 Summary
✅ 4 services used
✅ Code in GitHub
✅ Detailed README
✅ Deployment and testing steps included
✅ Everything is serverless and event-driven

👤 Author
Pranav Naik
Project ID: pdf-metadata-extractor-464017
Region: asia-south1