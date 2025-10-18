# Agent4Good - Netlify Deployment

Community Health & Wellness Advisor - Air Quality Monitoring Platform optimized for Netlify deployment.

![Platform Overview](https://img.shields.io/badge/Platform-Netlify-00C7B7?style=for-the-badge&logo=netlify)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6-F7DF1E?style=for-the-badge&logo=javascript)
![BigQuery](https://img.shields.io/badge/BigQuery-Enabled-669DF6?style=for-the-badge&logo=google-cloud)

## 🌟 Features

- **Serverless Architecture**: Powered by Netlify Functions
- **Multi-Agent AI System**: Google Agent SDK integration
- **Real-time Air Quality Data**: BigQuery integration with intelligent agents
- **AI-Powered Insights**: Gemini AI analysis and agent-driven responses
- **Static Site Generation**: Fast CDN delivery
- **Responsive Design**: Modern, mobile-first UI
- **Interactive Visualizations**: Chart.js and D3.js

## 🚀 Quick Deploy

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/coder-chick/agent4good-netlify)

## 📋 Prerequisites

- **Netlify Account**: [Sign up free](https://netlify.com)
- **Google Cloud Project** with:
  - BigQuery API enabled
  - Gemini API access
  - Service account key
- **Environment Variables** configured

## 🛠️ Local Development

1. **Clone and Install**:
   ```bash
   git clone https://github.com/coder-chick/agent4good-netlify.git
   cd agent4good-netlify
   npm install
   ```

2. **Set Up Environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run Locally**:
   ```bash
   # Install Netlify CLI
   npm install -g netlify-cli
   
   # Start development server
   netlify dev
   ```

## ⚙️ Environment Variables

Configure these in Netlify Dashboard > Site Settings > Environment Variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Your GCP project ID | ✅ |
| `BIGQUERY_DATASET` | BigQuery dataset name | ✅ |
| `BIGQUERY_TABLE` | BigQuery table name | ✅ |
| `GEMINI_API_KEY` | Gemini AI API key | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | Service account JSON | ✅ |
| `SECRET_KEY` | Flask session secret | ✅ |

## 🏗️ Architecture

```
┌─────────────────┐
│   Netlify CDN   │ ← Static Files (HTML/CSS/JS)
│  (Global Edge)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Netlify Functions│ ← Serverless API Endpoints
│   (AWS Lambda)   │
└─────────┬───────┘
          │
          ├──────────────┬──────────────┐
          ▼              ▼              ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  BigQuery   │  │  Gemini AI   │  │ Multi-Agent  │
│  Database   │  │   (SDK)      │  │    System    │
└─────────────┘  └──────────────┘  └──────────────┘
                                          │
                                          ▼
                                  ┌──────────────┐
                                  │ Google Agent │
                                  │     SDK      │
                                  └──────────────┘
```

## 🤖 Intelligent Agent System

The platform includes two sophisticated AI agents built with Google Agent SDK:

### **BigQuery Agent** (`multi_tool_agent_bquery_tools`)
- **Purpose**: Real-time data analysis and querying
- **Capabilities**: 
  - Direct BigQuery integration
  - Complex air quality data analysis
  - Location-aware queries with county-to-state mapping
  - Real-time data insights

### **Multi-Tool Agent** (`multi_tool_agent`)
- **Purpose**: General-purpose AI assistant
- **Capabilities**:
  - Natural language processing
  - Health recommendations
  - Multi-domain knowledge
  - Fallback support when BigQuery agent is unavailable

### **Agent Features**:
- **Smart Location Detection**: Automatic county-to-state mapping
- **Contextual Responses**: Understanding of air quality and health relationships
- **Fallback Mechanisms**: Graceful degradation when services are unavailable
- **Async Processing**: Non-blocking query processing

## 📊 API Endpoints

- **`/api/air-quality`** - Get air quality data
- **`/api/analyze`** - AI analysis of air quality
- **`/api/agent-query`** - Multi-agent intelligent query system
- **`/api/health-recommendations`** - Health recommendations
- **`/api/health`** - Health check

## 🎨 Frontend Features

- **Modern UI**: Tailwind CSS with custom components
- **Interactive Charts**: Real-time data visualization
- **Responsive Design**: Mobile-first approach
- **Smooth Animations**: Anime.js powered transitions
- **3D Background**: Three.js atmospheric effects

## 📱 Demo

Visit the live demo: [https://agent4good-netlify.netlify.app](https://agent4good-netlify.netlify.app) *(URL will be available after deployment)*

## 📖 Documentation

- **[Deployment Guide](NETLIFY_DEPLOYMENT.md)** - Complete setup instructions
- **[File Structure](FILES_TO_COPY.md)** - Repository organization
- **[API Documentation](#)** - Endpoint specifications

## 🐛 Troubleshooting

### Common Issues:

1. **Build Failures**: Check Node.js version (18.x required)
2. **Function Timeouts**: Optimize BigQuery queries
3. **CORS Errors**: Environment variables not set
4. **Authentication**: Service account permissions

### Get Help:

- 📧 [Open an Issue](https://github.com/coder-chick/agent4good-netlify/issues)
- 📚 [Netlify Docs](https://docs.netlify.com)
- 🌐 [Google Cloud BigQuery](https://cloud.google.com/bigquery/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

**Agents for Impact** - Community Health & Wellness Initiative

## 🙏 Acknowledgments

- **Netlify** for serverless hosting
- **Google Cloud Platform** for data infrastructure
- **Gemini AI** for intelligent insights
- **Open Source Community** for amazing tools

---

**Built with ❤️ for Community Health & Wellness**

*Powered by Netlify, Google Cloud, BigQuery, and Gemini AI*

## 🚀 Deploy Now

Ready to deploy? Click the button above or follow the [deployment guide](NETLIFY_DEPLOYMENT.md)!