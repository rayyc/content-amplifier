# 🚀 Content Amplifier System

An AI-powered content marketing automation system that finds high-value content gaps, generates comprehensive articles using Claude AI, automatically injects affiliate links, and distributes content across multiple platforms.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-Private-red.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)

---

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Revenue Streams](#revenue-streams)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Security](#security)
- [Roadmap](#roadmap)
- [License](#license)

---

## ✨ Features

### 🔍 **Gap Detection**
- Scans Stack Overflow, Reddit, and Dev.to for high-engagement questions
- Identifies content gaps where existing answers are incomplete
- Scores opportunities based on views, engagement, and monetization potential
- Filters for topics with affiliate/consulting potential

### 📊 **Content Analysis**
- Analyzes gaps to identify missing elements (code, explanations, production guides)
- Generates comprehensive content briefs with outlines and SEO keywords
- Determines target audience level and optimal content type
- Assesses monetization potential for each opportunity

### ✍️ **AI Content Generation**
- Uses Claude Sonnet 4 to write 1,500-2,500 word articles
- Generates working code examples and troubleshooting guides
- Creates platform-specific versions (Dev.to, Medium, Twitter, LinkedIn)
- Produces 8-10 tweet threads from each article

### 💰 **Affiliate Automation**
- Automatically detects content context (tutorials, deployment guides, etc.)
- Intelligently injects relevant affiliate links (Udemy courses, hosting providers)
- Tracks revenue potential per article
- Supports multiple affiliate programs (Udemy, DigitalOcean, AWS, etc.)

### 📤 **Multi-Platform Distribution**
- **Dev.to**: Automated posting with proper frontmatter and tags
- **Twitter**: Thread generation and posting via API
- **Medium**: Draft creation with formatted content
- **LinkedIn**: Professional post generation
- **GitHub**: Automated repository creation with code examples

### 📈 **Revenue Tracking & Analytics**
- Tracks conversions from affiliate links
- Monitors revenue by platform and content type
- Generates weekly performance reports
- Provides ROI analysis and optimization recommendations

### 🎛️ **Dashboard**
- Streamlit web interface for system monitoring
- Real-time pipeline visualization
- Manual controls for each stage
- Demo mode for safe testing

---

## 🏗️ System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                   Content Amplifier System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │Gap Detector  │───▶│   Analyzer   │───▶│  Generator   │  │
│  │(Scan Platforms)│   │(Create Briefs)│   │  (AI Writer) │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                                         │          │
│         ▼                                         ▼          │
│  ┌──────────────┐                      ┌──────────────┐    │
│  │  Orchestrator │◀─────────────────────│ Distributor  │    │
│  │ (Coordinator) │                      │(Multi-Platform)│   │
│  └──────────────┘                      └──────────────┘    │
│         │                                         │          │
│         ▼                                         ▼          │
│  ┌──────────────┐                      ┌──────────────┐    │
│  │Revenue Tracker│                     │Affiliate Mgr │    │
│  │  (Analytics)  │                     │ (Link Inject)│    │
│  └──────────────┘                      └──────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 Revenue Streams

### 1. **Udemy Course Affiliates**
- **Commission**: 15% of sale price
- **Average Earnings**: $10-20 per course sale
- **Cookie Duration**: 7 days
- **Example**: Python course recommendation in tutorial articles

### 2. **DigitalOcean Referrals**
- **Commission**: $25 per referral when they spend $25
- **Recurring**: 25% of customer spend for 12 months
- **Best For**: Deployment guides, production tutorials

### 3. **Consulting Leads**
- Articles establish expertise in niche topics
- Include call-to-action for consulting services
- Average project value: $2,000-10,000

### 4. **Sponsored Content**
- Companies pay for featured articles
- Typical rate: $500-2,000 per article
- Requires established traffic/audience

### **Expected Revenue Timeline:**

| Timeline | Articles | Monthly Revenue | Notes |
|----------|----------|-----------------|-------|
| Month 1  | 8-12     | $50-100        | First conversions |
| Month 3  | 30-40    | $300-500       | System optimized |
| Month 6  | 70-80    | $1,000-2,000   | Authority built |
| Year 1   | 150+     | $2,000-5,000   | Passive income established |

---

## 🛠️ Tech Stack

### **Core Technologies**
- **Python 3.8+**: Main programming language
- **Anthropic Claude API**: AI content generation
- **Streamlit**: Web dashboard interface

### **Platform APIs**
- **PRAW**: Reddit scraping
- **StackAPI**: Stack Overflow data
- **Dev.to API**: Content posting
- **Tweepy**: Twitter integration
- **Medium API**: Article publishing
- **GitHub API**: Repository creation

### **Data & Storage**
- **JSON**: Configuration and data storage
- **python-dotenv**: Environment variable management

### **Key Libraries**
```
anthropic>=0.18.0
openai>=1.12.0
streamlit>=1.31.0
praw>=7.7.0
tweepy>=4.14.0
requests>=2.31.0
python-dotenv>=1.0.0
schedule>=1.2.0
```

---

## 📥 Installation

### **Prerequisites**
- Python 3.8 or higher
- Git
- API keys (see Configuration section)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/content-amplifier.git
cd content-amplifier
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Configure Environment**
```bash
# Copy example env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux

# Edit .env and add your API keys
notepad .env  # Windows
# or
nano .env     # macOS/Linux
```

---

## ⚙️ Configuration

### **1. Environment Variables (`.env`)**

**Required API Keys:**
```bash
# AI Content Generation (REQUIRED)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Platform Distribution
DEVTO_API_KEY=your_devto_key
TWITTER_BEARER_TOKEN=your_twitter_bearer
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret
MEDIUM_TOKEN=your_medium_token
GITHUB_TOKEN=ghp_your_github_token
```

**How to Get API Keys:**
- **Anthropic Claude**: https://console.anthropic.com/settings/keys
- **Dev.to**: https://dev.to/settings/extensions
- **Twitter**: https://developer.twitter.com/ (requires $100/month or use Buffer as alternative)
- **Medium**: https://medium.com/me/settings/security
- **GitHub**: https://github.com/settings/tokens

### **2. System Configuration (`config.json`)**
```json
{
  "detection": {
    "stackoverflow_tags": ["python", "javascript", "react"],
    "reddit_subreddits": ["webdev", "learnprogramming"],
    "scan_frequency_hours": 6
  },
  "content": {
    "batch_size": 3,
    "min_gap_score": 50,
    "review_required": true
  },
  "distribution": {
    "platforms": ["devto", "twitter"],
    "stagger_minutes": 30,
    "auto_publish": false
  }
}
```

### **3. Affiliate Configuration (`config/affiliates.json`)**
```json
{
  "udemy": {
    "enabled": true,
    "affiliate_url": "https://click.linksynergy.com/deeplink?id=YOUR_ID&mid=39197&murl="
  },
  "digitalocean": {
    "enabled": true,
    "referral_url": "https://m.do.co/c/YOUR_CODE"
  }
}
```

**Get Your Affiliate Links:**
- **Udemy**: Sign up at https://impact.com/ and search for Udemy
- **DigitalOcean**: https://cloud.digitalocean.com/account/referrals

---

## 🚀 Usage

### **Option 1: Web Dashboard (Recommended)**
```bash
streamlit run dashboard_combined.py
```

Then open your browser to `http://localhost:8501`

**Dashboard Features:**
- 🎮 **Demo Mode**: Test with simulated data (no API costs)
- ⚡ **Production Mode**: Run with real APIs
- 🎛️ **Control Panel**: Execute each stage manually
- 📊 **Visualizations**: Monitor gaps, briefs, articles, revenue
- ⚙️ **Configuration**: Edit settings in-app

### **Option 2: Command Line (Orchestrator)**
```bash
python src/orchestrator.py
```

**Menu Options:**
1. Run Full Pipeline (Manual) - Step-by-step with confirmations
2. Run Full Pipeline (Automated) - Fully automated
3. Gap Detection Only - Just scan for opportunities
4. Generate Weekly Report - Performance analytics
5. Schedule Automated Runs - Set it and forget it

### **Option 3: Individual Modules**
```bash
# Gap detection only
python src/gap_detector.py

# Content analysis only
python src/content_analyzer.py

# Content generation only
python src/content_generator.py
```

---

## 📁 Project Structure
```
content-amplifier/
├── src/
│   ├── gap_detector.py           # Scans platforms for opportunities
│   ├── content_analyzer.py       # Analyzes gaps, creates briefs
│   ├── content_generator.py      # AI content generation
│   ├── distribution_manager_v2.py # Multi-platform posting
│   ├── affiliate_manager.py      # Affiliate link injection
│   ├── revenue_tracker.py        # Conversion tracking
│   ├── orchestrator.py           # Master coordinator
│   └── utils.py                  # Helper functions
├── config/
│   └── affiliates.json           # Affiliate program configuration
├── data/                         # Generated data (gitignored)
│   ├── gaps/                     # Detected opportunities
│   ├── briefs/                   # Content briefs
│   └── analytics/                # Performance data
├── outputs/                      # Generated content (gitignored)
│   ├── articles/                 # Final articles
│   ├── reports/                  # Pipeline reports
│   └── threads/                  # Twitter threads
├── dashboard_combined.py         # Streamlit web interface
├── config.json                   # System configuration
├── .env                          # API keys (gitignored!)
├── .gitignore                    # Git exclusions
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🔄 How It Works

### **Complete Pipeline Flow:**

#### **Stage 1: Gap Detection** (5-10 minutes)
```
Stack Overflow + Reddit + Dev.to
           ↓
   Scan for high-engagement questions
           ↓
   Filter for incomplete answers
           ↓
   Calculate gap scores
           ↓
   Return top opportunities
```

#### **Stage 2: Content Analysis** (2-5 minutes)
```
Content Gaps
     ↓
Identify missing elements
     ↓
Assess monetization potential
     ↓
Generate content briefs
     ↓
Prioritize by revenue potential
```

#### **Stage 3: Content Generation** (3-5 minutes per article)
```
Content Brief
     ↓
Claude AI writes article
     ↓
Generate code examples
     ↓
Create platform-specific versions
     ↓
Generate Twitter thread
```

#### **Stage 4: Distribution** (1-2 minutes)
```
Content Package
     ↓
Inject affiliate links
     ↓
Post to Dev.to (draft)
     ↓
Post Twitter thread
     ↓
Create GitHub repo
     ↓
Track URLs & metrics
```

### **Example: Complete Run**
```bash
Input: Empty system
Output: 3 published articles with affiliate links

Timeline:
00:00 - Gap Detection starts
05:30 - Found 47 opportunities
05:35 - Analysis starts
10:20 - Generated 3 briefs
10:25 - Content generation starts (asks for approval)
15:30 - 3 articles generated (6,200 words total)
15:35 - Distribution starts (asks for approval)
18:00 - Posted to Dev.to and Twitter

Result:
- 3 articles published
- 2 affiliate links per article
- Estimated revenue potential: $142.50
```

---

## 🔐 Security

### **What's Protected:**
- ✅ `.env` file excluded from Git
- ✅ All data files excluded
- ✅ API keys loaded from environment variables
- ✅ Credentials never hardcoded

### **Best Practices:**
1. **Never commit `.env`** - Use `.env.example` as template
2. **Regenerate leaked keys immediately**
3. **Use private repository** for sensitive projects
4. **Rotate API keys periodically** (every 3-6 months)
5. **Review `.gitignore`** before first commit

### **If You Accidentally Commit Secrets:**
```bash
# Remove from Git history
git rm --cached .env
git commit -m "Remove .env from tracking"
git push --force

# CRITICAL: Regenerate ALL exposed API keys immediately!
```

---

## 🗺️ Roadmap

### **Phase 1: Core System** ✅
- [x] Gap detection across 3 platforms
- [x] AI content generation with Claude
- [x] Multi-platform distribution
- [x] Affiliate link automation
- [x] Revenue tracking

### **Phase 2: Enhancement** 🚧
- [ ] Image generation for articles
- [ ] Video script generation
- [ ] SEO optimization tools
- [ ] A/B testing for titles
- [ ] Email newsletter integration

### **Phase 3: Scale** 📅
- [ ] Multi-language support
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] Automated social media scheduling
- [ ] Integration with more platforms (Hashnode, Substack)

### **Phase 4: Monetization** 💰
- [ ] White-label offering
- [ ] SaaS version for clients
- [ ] Content marketplace
- [ ] Premium templates

---

## 📊 Performance Metrics

### **System Capabilities:**
- **Gap Detection**: ~500 opportunities/scan
- **Content Generation**: 3-5 articles/hour
- **Distribution**: 2-3 platforms simultaneously
- **Cost per Article**: ~$0.003 (Claude API)
- **Revenue per Article**: $15-50 average

### **Benchmarks:**
- Time to first article: ~15 minutes
- Articles per day: 10-20 (fully automated)
- Platforms supported: 5+
- Affiliate programs: 6+

---

## 📄 License

**Private License** - Not for redistribution

This project is private and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

Copyright © 2026 - All Rights Reserved

---

## 👤 Author

**Your Name**
- GitHub: [@rayyc](https://github.com/rayyc)
- Email: rayw68449@gmail.com
- Website: https://yourwebsite.com

---

## 🙏 Acknowledgments

- Anthropic for Claude AI
- OpenAI for GPT models
- Stack Overflow, Reddit, and Dev.to communities
- All open-source contributors

---

## 📞 Support

For questions or issues:
1. Check the documentation above
2. Review the [Issues](https://github.com/YOUR_USERNAME/content-amplifier/issues) page
3. Contact: your.email@example.com

---

## 🎯 Quick Start Summary
```bash
# 1. Clone and setup
git clone https://github.com/YOUR_USERNAME/content-amplifier.git
cd content-amplifier
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install and configure
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your API keys

# 3. Run dashboard
streamlit run dashboard_combined.py

# 4. Start earning!
# - Switch to Production Mode
# - Run Full Pipeline
# - Review and approve
# - Collect revenue 💰
```

---



*Last Updated: January 2026*