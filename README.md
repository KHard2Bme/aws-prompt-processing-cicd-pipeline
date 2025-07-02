# Prompt Processing Pipeline with Amazon Bedrock + GitHub Actions

## 🚀 Overview
This repo processes prompt templates with config files and uses Amazon Bedrock for inference. The output is uploaded to an S3 bucket configured as a static website.

## 📦 Setup

### 1. AWS Resources
- **Create S3 buckets** for beta and prod
- Enable **Static Website Hosting**
- Ensure proper IAM role permissions for S3 and Bedrock access

### 2. GitHub Secrets
Configure:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_BETA`
- `S3_BUCKET_PROD`

### 3. Templates & Prompts
- Add prompt JSON files to `prompts/`
- Add matching Jinja2-style templates to `prompt_templates/`

### 4. Running the Workflows
- **Pull Request →** triggers beta deployment
- **Merge to `main` →** triggers prod deployment

### 5. Viewing Outputs
- Visit:
 - 'http://aws-prompt-processing-001-s3.s3-website-us-east-1.amazonaws.com' [BETA]
 - 'http://aws-prompt-processing-002-s3.s3-website-us-east-1.amazonaws.com' [PROD]
  

## 🔒 Notes
- No credentials are hardcoded
- Bedrock model used: `anthropic.claude-3-sonnet-20240229-v1:0`
- Uses real-time Bedrock inference only
