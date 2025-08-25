# 🚀 Flow System - AI Automation Platform

> **Interview Demo**: A working prototype of a Flow-style system that takes natural language prompts, compiles plans, and executes workflows to produce visible results.

## 🎯 **What This Demo Shows**

This is a **fully functional prototype** that demonstrates:
- **Natural Language Processing**: Converts prompts like "find top 5 AI automation trends" into structured plans
- **Intelligent Workflow Generation**: Automatically creates multi-step execution plans
- **API Integration**: Real-time data from Yelp, Google Places, and Google Custom Search
- **AI Automation**: Content filtering, summarization, and email draft generation
- **Business Analysis**: Local business search, competitor analysis, market research

## 🚀 **Quick Start (5 minutes)**

### **Prerequisites**
- Python 3.8+
- pip package manager

### **Installation**
```bash
# Clone the repository
git clone https://github.com/Aakankshajunday/flow-ai.git
cd flow-ai

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### **Access the App**
Open your browser and navigate to: `http://localhost:5000`

## 🎯 **Demo Examples to Try**

### **1. AI Automation Workflow**
**Prompt**: "Compile the top 5 items about AI automation, summarize each in ~1 sentence, and prepare an email draft to founders@company.com"

**What it does**: 
- Searches for AI automation content
- Filters for relevance
- Summarizes results
- Generates email draft

### **2. Business Analysis**
**Prompt**: "Find top 5 coffee shops in San Francisco with ratings and reviews"

**What it does**:
- Searches Yelp API for local businesses
- Analyzes ratings and market positioning
- Compares businesses for market gaps
- Displays results with real data

### **3. Market Research**
**Prompt**: "Research the latest AI automation tools and trends for 2025"

**What it does**:
- Performs intelligent web search
- Filters for recent content
- Provides contextual summaries
- Ranks by relevance

## 🏗️ **Architecture Overview**

```
User Prompt → Intent Analysis → Workflow Generation → Plan Execution → Results Display
     ↓              ↓                ↓                ↓              ↓
Natural Language → AI Routing → Multi-step Plan → API Calls → Rich UI
```

### **Core Components**
- **FlowSystem**: Main orchestrator for workflow management
- **EnhancedSearchSystemV2**: Multi-API search engine
- **Plan/Step**: Structured workflow representation
- **Flask Web Interface**: Modern, responsive UI

## 🔧 **Technical Features**

- **Multi-API Integration**: Yelp, Google Places, Google Custom Search
- **Intelligent Routing**: Automatically detects intent and routes to appropriate workflows
- **Real-time Data**: Live results from external APIs
- **Error Handling**: Robust error handling and fallback mechanisms
- **Responsive UI**: Modern interface with glassmorphism design

## 📊 **API Integration**

### **Yelp Fusion API**
- Business search and analysis
- Ratings, reviews, and market data
- Location-based filtering

### **Google Places API**
- Geographic business search
- Fallback for Yelp results
- Location intelligence

### **Google Custom Search**
- Web content discovery
- Relevance scoring
- Content filtering

## 🎨 **User Interface**

- **Modern Design**: Glassmorphism with gradient backgrounds
- **Responsive Layout**: Works on desktop and mobile
- **Real-time Updates**: Dynamic result display
- **Interactive Elements**: Clickable examples and results

## 🚀 **Deployment**

### **Local Development**
```bash
python app.py
```

### **Production Deployment**
```bash
# Railway (recommended)
git push origin main

# Render
git push origin main
```

## 📝 **Configuration**

Create a `config.env` file with your API keys:
```env
YELP_API_KEY=your_yelp_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CUSTOM_SEARCH_API_KEY=your_search_api_key
GOOGLE_CUSTOM_SEARCH_CX=your_search_engine_id
```

## 🔍 **Troubleshooting**

### **Common Issues**
1. **API Keys**: Ensure all API keys are properly configured
2. **Dependencies**: Run `pip install -r requirements.txt`
3. **Port Conflicts**: Change port in `app.py` if 5000 is busy

### **Getting Help**
- Check the terminal output for detailed error messages
- Verify API key configuration
- Ensure all dependencies are installed

## 🎯 **Interview Talking Points**

### **Technical Achievements**
- **Natural Language Processing**: Converts human language to structured workflows
- **API Orchestration**: Manages multiple external APIs seamlessly
- **Workflow Automation**: Creates and executes multi-step plans
- **Real-time Data**: Provides live results from external sources

### **Business Value**
- **Automation**: Reduces manual research time
- **Intelligence**: Provides context-aware results
- **Scalability**: Can handle various types of queries
- **User Experience**: Simple interface for complex operations

### **Future Enhancements**
- Machine learning for better intent detection
- Additional API integrations
- Advanced workflow templates
- Mobile app development

## 📚 **Code Quality**

- **Clean Architecture**: Separation of concerns
- **Error Handling**: Comprehensive error management
- **Documentation**: Well-documented code and APIs
- **Testing**: Ready for unit and integration tests

## 🌟 **Why This is Impressive**

1. **Real Working System**: Not just a concept, but a functional prototype
2. **API Integration**: Connects to multiple real-world services
3. **Natural Language**: Understands human intent and converts to actions
4. **Production Ready**: Clean code that could be deployed to production
5. **Scalable Design**: Architecture that can grow with requirements

---

**Built with ❤️ for demonstrating real-world AI automation capabilities**
