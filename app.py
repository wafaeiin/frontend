from flask import Flask, request, render_template, redirect, url_for, jsonify
import boto3
from botocore.exceptions import NoCredentialsError

app = Flask(__name__)


AWS_ACCESS_KEY = "AKIA4MTWMPG2X5LYP2WW"
AWS_SECRET_KEY = "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"
S3_BUCKET = "my-documents-bucket-esi"  # bucket name
S3_REGION = "eu-north-1"       # bucket's region

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)
#ssh -i "docmanagesi.pem" Administrator@98.84.172.83
#5pzFvIImOCoyvF9LBrc$8Z9509?axTCm
# Upload a file
@app.route("/", methods=["GET"])
def home():
    try:
        # List files in S3 bucket
        objects = s3_client.list_objects_v2(Bucket=S3_BUCKET)
        files = [obj["Key"] for obj in objects.get("Contents", [])]
    except Exception as e:
        files = []
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return redirect(url_for("home"))

    file = request.files["file"]
    if file.filename == "":
        return redirect(url_for("home"))

    try:
        # Upload file to S3
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={"ACL": "public-read"}
        )
    except Exception as e:
        return f"Error uploading file: {str(e)}", 500

    return redirect(url_for("home"))

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        # Generate presigned URL for download
        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": filename},
            ExpiresIn=3600
        )
        return redirect(presigned_url)
    except Exception as e:
        return f"Error downloading file: {str(e)}", 500

@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    try:
        # Delete file from S3
        s3_client.delete_object(Bucket=S3_BUCKET, Key=filename)
    except Exception as e:
        return f"Error deleting file: {str(e)}", 500

    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
