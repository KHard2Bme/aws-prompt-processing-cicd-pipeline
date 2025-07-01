import os
import json
from pathlib import Path
import boto3
from jinja2 import Template

BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def render_template(template_path, variables):
    with open(template_path) as f:
        template = Template(f.read())
    return template.render(**variables)

def call_bedrock(prompt, max_tokens=1024):
    client = boto3.client("bedrock-runtime")
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

    # Convert list of blocks to a string
    if isinstance(content, list):
        return "".join([block.get("text", "") for block in content])
    return content

def upload_to_s3(file_path, bucket_name, key):
    s3 = boto3.client("s3")
    s3.upload_file(str(file_path), bucket_name, key)
    print(f"Uploaded {file_path} to s3://{bucket_name}/{key}")

def main(env, bucket):
    prompts_dir = Path("prompts")
    templates_dir = Path("prompt_templates")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    for prompt_file in prompts_dir.glob("*.json"):
        with open(prompt_file) as f:
            config = json.load(f)

        template_file = templates_dir / prompt_file.name.replace(".json", ".txt")
        if not template_file.exists():
            print(f"Template not found for {prompt_file.name}, skipping...")
            continue

        rendered_prompt = render_template(template_file, config)
        bedrock_response = call_bedrock(rendered_prompt)

        output_ext = config.get("output_format", "html")  # default to html
        output_filename = prompt_file.stem + f".{output_ext}"
        output_path = outputs_dir / output_filename

        with open(output_path, "w") as out_f:
            out_f.write(bedrock_response)

        s3_key = f"{env}/outputs/{output_filename}"
        upload_to_s3(output_path, bucket, s3_key)

if __name__ == "__main__":
    env = os.environ.get("DEPLOY_ENV", "beta")
    bucket = os.environ.get("S3_BUCKET")
    if not bucket:
        raise ValueError("S3_BUCKET environment variable is not set.")
    main(env, bucket)

