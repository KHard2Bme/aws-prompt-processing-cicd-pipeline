import os, json, boto3
from jinja2 import Template
from pathlib import Path

BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def render_template(template_path, variables):
    with open(template_path) as f:
        template = Template(f.read())
    return template.render(variables)

def call_bedrock(prompt, max_tokens=1024):
    client = boto3.client("bedrock-runtime")
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": [
            {"role": "user", "content": f"Human: {prompt}"}
        ]
    }
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=json.dumps(body)
    )
    return json.loads(response["body"].read())["content"]

def upload_to_s3(file_path, bucket, prefix):
    s3 = boto3.client("s3")
    key = f"{prefix}/outputs/{os.path.basename(file_path)}"
    s3.upload_file(file_path, bucket, key)
    print(f"Uploaded to s3://{bucket}/{key}")

def main(env_prefix, bucket_name):
    prompts_dir = Path("prompts")
    templates_dir = Path("prompt_templates")
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    for prompt_file in prompts_dir.glob("*.json"):
        with open(prompt_file) as f:
            config = json.load(f)

        template_file = templates_dir / prompt_file.name.replace(".json", ".txt")
        rendered_prompt = render_template(template_file, config)
        bedrock_response = call_bedrock(rendered_prompt)

        output_filename = prompt_file.stem + ".html"
        output_path = outputs_dir / output_filename
        with open(output_path, "w") as out_f:
            out_f.write(bedrock_response)

        upload_to_s3(str(output_path), bucket_name, env_prefix)

if __name__ == "__main__":
    env = os.environ.get("DEPLOY_ENV", "beta")
    bucket = os.environ.get("S3_BUCKET_BETA" if env == "beta" else "S3_BUCKET_PROD")
    main(env, bucket)
