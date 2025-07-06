# Prompt Processing Pipeline with Amazon Bedrock + GitHub Actions

## 🚀 Overview
This repo processes prompt templates with config files and uses Amazon Bedrock for inference. The output is uploaded to an S3 bucket configured as a static website.

## 📦 Setup

### 1. AWS Resources
- **Create S3 buckets** for beta and prod environments
- **Unblock public access** and create a **bucket policy** for both buckets
- Enable **Static Website Hosting**
- Create IAM role for GitHub account with full access permissions to S3 and Bedrock

### 2. GitHub Secrets
Configure:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `S3_BUCKET_BETA`
- `S3_BUCKET_PROD`

### 3. Templates & Prompts
- Add prompt JSON file to `prompts/`
- Add matching Jinja2-style template to `prompt_templates/`

### 4. Running the Workflows

 **Pull Request →** triggers beta deployment

- Select "Commit changes" to save changes
- Create a commit message and add a description (optional)
- Select "Create a new branch for this commit and start a pull request": a branch name will be auto-generated.
- Select "Propose changes"
- Select "Create pull request"; you will soon see the message "Prompt Preview(PR-Beta) process-prompts (pull request) started now - This check has started, then finally Successful.

**Merge to `main` →** triggers prod deployment

- Select "Merge pull request" 
- Create a commit message and add a description (optional)
- Select "Confirm merge"
- You should see the message "Pull request successfully merged and closed".
- Select "Delete branch" and you will next see the message "You're all set - the branch has been merged".



### 5. Viewing Outputs

### For the beta s3 bucket: 'http://aws-prompt-processing-beta-s3.s3-website-us-east-1.amazonaws.com' 
### For the prod s3 bucket: 'http://aws-prompt-processing-prod-s3.s3-website-us-east-1.amazonaws.com' 

- Go to your S3 bucket via AWS Console
- Check `beta/outputs` or `prod/outputs` folder for needed .html file, which will also be copied to default index.html file in root folder
- go to properties tab in bucket, copy and past the bucket website endpoint URL into a web browser to view generated response




## 🔒 Notes
- No credentials are hardcoded
- Bedrock model used: `anthropic.claude-3-sonnet-20240229-v1:0`
- Uses real-time Bedrock inference only

