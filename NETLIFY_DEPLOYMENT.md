# Netlify Deployment Guide for Agent4Good

This guide explains how to deploy the Agent4Good application to Netlify using the prepared configuration files.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **Google Cloud Project** with:
   - BigQuery API enabled
   - Gemini API access
   - Service account with appropriate permissions
3. **GitHub Repository** with your code
4. **Environment Variables** configured

## 🚀 Deployment Steps

### Step 1: Prepare Your Repository

1. Create a new GitHub repository for the Netlify version
2. Copy these files from your current project:
   ```
   ├── netlify.toml
   ├── package.json
   ├── build.js
   ├── .env.netlify (rename to .env.example)
   ├── requirements.txt
   ├── static/
   │   ├── css/
   │   └── js/
   ├── templates/
   └── netlify/
       └── functions/
   ```

### Step 2: Set Up Netlify Site

1. **Connect to Git**:
   - Go to [Netlify Dashboard](https://app.netlify.com)
   - Click "New site from Git"
   - Choose GitHub and select your repository
   - Configure build settings:
     - **Build command**: `npm run build`
     - **Publish directory**: `dist`
     - **Functions directory**: `netlify/functions`

2. **Configure Environment Variables**:
   Go to Site Settings > Environment Variables and add:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   BIGQUERY_DATASET=air_quality_dataset
   BIGQUERY_TABLE=air_quality_data
   GEMINI_API_KEY=your-gemini-api-key
   SECRET_KEY=your-secret-key
   NODE_ENV=production
   ```

### Step 3: Set Up Google Cloud Service Account

1. **Create Service Account**:
   ```bash
   gcloud iam service-accounts create netlify-agent4good \
     --display-name "Netlify Agent4Good Service Account"
   ```

2. **Grant Permissions**:
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:netlify-agent4good@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/bigquery.dataViewer"
   
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:netlify-agent4good@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/bigquery.jobUser"
   ```

3. **Download Service Account Key**:
   ```bash
   gcloud iam service-accounts keys create service-account-key.json \
     --iam-account=netlify-agent4good@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

4. **Add Service Account to Netlify**:
   - Copy the contents of `service-account-key.json`
   - In Netlify, add environment variable: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - Paste the entire JSON content as the value

### Step 4: Deploy

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Add Netlify configuration"
   git push origin main
   ```

2. **Netlify will automatically**:
   - Detect the push
   - Run `npm run build`
   - Deploy to CDN
   - Set up serverless functions

### Step 5: Configure BigQuery Data

1. **Create Dataset and Table** (if not exists):
   ```sql
   CREATE SCHEMA IF NOT EXISTS air_quality_dataset;
   
   CREATE TABLE IF NOT EXISTS air_quality_dataset.air_quality_data (
     date DATE,
     state_name STRING,
     county_name STRING,
     aqi INT64,
     parameter_name STRING,
     site_name STRING
   );
   ```

2. **Load Sample Data**:
   ```bash
   bq load \
     --source_format=CSV \
     --skip_leading_rows=1 \
     air_quality_dataset.air_quality_data \
     daily_88101_2025.csv \
     date:DATE,state_name:STRING,county_name:STRING,aqi:INTEGER,parameter_name:STRING,site_name:STRING
   ```

## 🧪 Testing

After deployment, test these endpoints:

1. **Health Check**: `https://your-site.netlify.app/api/health`
2. **Air Quality Data**: `https://your-site.netlify.app/api/air-quality?days=7`
3. **AI Analysis**: `https://your-site.netlify.app/api/analyze` (POST)
4. **Health Recommendations**: `https://your-site.netlify.app/api/health-recommendations`

## 🔧 Local Development

To test locally with Netlify CLI:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Install dependencies
npm install

# Start local development
netlify dev
```

## 📊 Monitoring

- **Netlify Dashboard**: Monitor deployments and function logs
- **Google Cloud Console**: Monitor BigQuery usage and costs
- **Function Logs**: Check Netlify Functions tab for errors

## 🐛 Troubleshooting

### Common Issues:

1. **BigQuery Permission Errors**:
   - Verify service account has correct roles
   - Check environment variables are set

2. **Gemini API Errors**:
   - Verify API key is correct
   - Check API is enabled in Google Cloud

3. **Build Failures**:
   - Check build logs in Netlify Dashboard
   - Verify all dependencies are in package.json

4. **Function Timeout**:
   - Netlify Functions have 10-second timeout by default
   - Optimize BigQuery queries for speed

### Environment Variable Format:

For Google Service Account, use this format in Netlify:
```
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account","project_id":"your-project",...}
```

## 📞 Support

- **Netlify Docs**: [docs.netlify.com](https://docs.netlify.com)
- **Google Cloud BigQuery**: [cloud.google.com/bigquery/docs](https://cloud.google.com/bigquery/docs)
- **Gemini API**: [ai.google.dev](https://ai.google.dev)

---

**Built with ❤️ for Community Health & Wellness**

*Powered by Netlify, Google Cloud, BigQuery, and Gemini AI*