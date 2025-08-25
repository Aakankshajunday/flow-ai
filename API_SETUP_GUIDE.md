# 🔑 API Setup Guide - Get Real Data in 10 Minutes

> **For Interviewers**: This guide will get you running with real API data from Yelp, Google Places, and Google Custom Search.

## 🚀 **Quick Start (10 minutes total)**

### **Step 1: Yelp Fusion API (2 minutes)**
1. Go to [Yelp Developers](https://www.yelp.com/developers)
2. Click **"Get Started"** → **"Create App"**
3. Fill in basic info (any app name works)
4. **Copy your API Key** (starts with `Bearer...`)
5. **Free tier**: 500 requests/day

### **Step 2: Google Places API (3 minutes)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. **Create new project** or select existing
3. Enable **"Places API"** in Library
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. **Copy your API Key** (starts with `AIza...`)
6. **Free tier**: $200/month credit (plenty for demo)

### **Step 3: Google Custom Search (3 minutes)**
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **"Create a search engine"**
3. Enter any website (e.g., `example.com`)
4. **Copy your Search Engine ID** (looks like `123456789:abcdefgh`)
5. Go to [Google Cloud Console](https://console.cloud.google.com)
6. Enable **"Custom Search API"**
7. **Copy your API Key** (starts with `AIza...`)
8. **Free tier**: 100 searches/day

### **Step 4: Configure Your App (2 minutes)**
1. Create `config.env` file in your project root:
```env
YELP_API_KEY=Bearer_your_yelp_key_here
GOOGLE_API_KEY=AIza_your_google_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=AIza_your_search_key_here
GOOGLE_CUSTOM_SEARCH_CX=123456789:abcdefgh
```

2. Restart your app: `python app.py`

## 🎯 **What You'll Get**

### **With Yelp API**
- Real business listings with ratings
- Actual addresses and phone numbers
- Real review counts and prices
- Live data from Yelp's database

### **With Google Places API**
- Geographic business search
- Location-based results
- Business details and contact info
- Fallback when Yelp doesn't have data

### **With Google Custom Search**
- Web content discovery
- News and article search
- Relevance scoring
- Source diversity

## 🔍 **Test Your Setup**

### **Test 1: Business Search**
**Prompt**: "Find top 5 coffee shops in San Francisco"
**Expected**: Real Yelp results with ratings, addresses, phone numbers

### **Test 2: AI Automation**
**Prompt**: "Research the latest AI automation tools and trends for 2025"
**Expected**: Web search results from Google Custom Search

### **Test 3: Location Analysis**
**Prompt**: "Find restaurants near Times Square in New York"
**Expected**: Google Places results with location data

## ⚠️ **Common Issues & Solutions**

### **"API key not valid" Error**
- Check that you copied the **entire** API key
- Ensure you enabled the correct API in Google Cloud Console
- Verify your API key has the right permissions

### **"No results found"**
- Check your API quotas (free tiers have limits)
- Verify your search terms are specific enough
- Ensure your location is a real city/area

### **"Rate limit exceeded"**
- Free tiers have daily/monthly limits
- Wait a few minutes and try again
- Consider upgrading to paid tiers for production

## 💰 **Cost Breakdown**

| API | Free Tier | Paid Tier |
|-----|-----------|-----------|
| **Yelp** | 500 requests/day | $0.01/request |
| **Google Places** | $200/month credit | $0.017/request |
| **Google Custom Search** | 100 searches/day | $5/1000 searches |

**Total cost for demo**: $0 (all free tiers)

## 🚀 **Production Considerations**

### **For Real Deployment**
- Upgrade to paid API tiers
- Implement rate limiting
- Add caching mechanisms
- Monitor API usage

### **Security Best Practices**
- Never commit API keys to git
- Use environment variables
- Implement API key rotation
- Monitor for unauthorized usage



### **Yelp API Issues**
- [Yelp Developer Documentation](https://docs.developer.yelp.com/)
- [Yelp Developer Support](https://www.yelp.com/developers/support)

### **Google API Issues**
- [Google Cloud Documentation](https://cloud.google.com/docs)
- [Google Cloud Support](https://cloud.google.com/support)

### **App Issues**
- Check the terminal output for error messages
- Verify your `config.env` file format
- Ensure all dependencies are installed

---

**🎯 Pro Tip**: Set up the APIs before your interview demo to show real, live data instead of mock results!
