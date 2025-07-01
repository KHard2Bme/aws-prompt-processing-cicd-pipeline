import os
import json
import boto3
from pathlib import Path
from jinja2 import Template

# Constants
PROMPTS_DIR = "prompts"
TEMPLATES_DIR = "prompt_templates"
OUTPUTS_DIR = "outputs"
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Get environment variables
AWS_REGION = os.environ.get("AWS_REGION")
DEPLOY_ENV = os.environ.get("DEPLOY_ENV", "beta").lower()
S3_BUCKET = os.environ.get("S3_BUCKET_PROD") if DEPLOY_ENV == "prod" else os.environ.get("S3_BUCKET_BETA")

if not AWS_REGION:
    raise ValueError("AWS_REGION environment variable is not set.")
if not S3_BUCKET:
    raise ValueError("S3_BUCKET environment variable is not set (check S3_BUCKET_BETA or S3_BUCKET_PROD).")

def render_template(template_path, config):
    with open(template_path) as f:
        template = Template(f.read())
    return template.render(**config)

def call_bedrock(prompt, max_tokens=1024):
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {
                "role": "user",
                "content": f"Human: {prompt}"
            }
        ]
    }
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    response_body = json.loads(response["body"].read())
    content = response_body.get("content", [])

    if isinstance(content, list):
        return "".join([block.get("text", "") for block in content])
    return content

def upload_to_s3(file_path, bucket_name, key):
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.upload_file(str(file_path), bucket_name, key)
    print(f"Uploaded {file_path} to s3://{bucket_name}/{key}")

def copy_to_index(bucket_name, source_key):
    s3 = boto3.client("s3", region_name=AWS_REGION)
    s3.copy_object(
        Bucket=bucket_name,
        CopySource={'Bucket': bucket_name, 'Key': source_key},
        Key="index.html",
        ContentType='text/html',
        MetadataDirective='REPLACE'
    )
    print(f"Copied {source_key} to s3://{bucket_name}/index.html")

def main():
    print(f"Environment: {DEPLOY_ENV}")
    print(f"Using bucket: {S3_BUCKET}")

    Path(OUTPUTS_DIR).mkdir(exist_ok=True)

    for config_file in Path(PROMPTS_DIR).glob("*.json"):
        with open(config_file) as f:
            config = json.load(f)

        template_file = Path(TEMPLATES_DIR) / config["template"]
        rendered_prompt = render_template(template_file, config["variables"])
        bedrock_response = call_bedrock(rendered_prompt)

        output_filename = f"{config_file.stem}.html"
        output_path = Path(OUTPUTS_DIR) / output_filename

        with open(output_path, "w") as out_f:
            out_f.write(bedrock_response)

        s3_key = f"{DEPLOY_ENV}/outputs/{output_filename}"
        upload_to_s3(output_path, S3_BUCKET, s3_key)

        # Copy to root index.html
        copy_to_index(S3_BUCKET, s3_key)

if __name__ == "__main__":
    main()





  
