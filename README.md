# 🌟 Flow System - Advanced AI-Powered Web Application

A sophisticated web-based system that takes natural language prompts, compiles intelligent plans, and executes multi-step operations using real APIs and enhanced search capabilities.

## ✨ Core Features

- **Natural Language Processing**: Understands complex English prompts and converts them to executable plans
- **Enhanced Search System V2**: Advanced search with relevance filtering, intelligent ranking, and source diversity
- **AI Automation Focus**: Specialized handling for AI automation workflows with summarization and email generation
- **Multi-API Integration**: Yelp, Google Custom Search, and web scraping capabilities
- **Plan Generation & Execution**: Automatically creates and executes step-by-step plans
- **Web Interface**: Modern Flask-based web application with real-time feedback
- **Configurable Search**: Tunable parameters for relevance, freshness, and authority scoring

## 🏗️ System Architecture

```
Flow System
├── Web Application (Flask)
├── Enhanced Search System V2
├── Plan Generation Engine
├── Multi-API Integration
└── Result Processing & Display
```

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- API keys for Yelp and Google Custom Search (optional)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd flow-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional):
   ```bash
   # Copy and edit config.env with your API keys
   cp config.env.example config.env
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open your browser** and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
Create a `config.env` file with your API keys:

```env
YELP_API_KEY=your_yelp_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CUSTOM_SEARCH_API_KEY=your_custom_search_key_here
GOOGLE_CUSTOM_SEARCH_CX=your_custom_search_cx_here
```

### Search Configuration
The system uses configurable parameters for search behavior:

```python
config = SearchConfig(
    min_relevance_score=0.2,      # Minimum relevance to include results
    max_domain_repeats=2,         # Maximum results from same domain
    max_results=15,               # Total results to return
    text_relevance_weight=0.4,    # Weight for text relevance
    freshness_weight=0.2,         # Weight for content freshness
    authority_weight=0.2,         # Weight for source authority
    engagement_weight=0.1,        # Weight for user engagement
    diversity_weight=0.1          # Weight for result diversity
)
```

## 🎯 How It Works

### 1. Natural Language Input
Users enter prompts like:
- "Find the best restaurants in San Francisco"
- "Research AI trends in 2024"
- "Compare Python vs JavaScript for web development"
- **"Compile the top 5 items about AI automation, summarize each in ~1 sentence, and prepare an email draft to founders@company.com"**

### 2. Intent Parsing
The system automatically:
- Extracts intent and parameters
- Identifies subject, location, count, and timeframe
- Routes queries to appropriate handlers

### 3. Plan Generation
Creates structured execution plans:
```
📋 Generated Plan:
Goal: Find the best restaurants in San Francisco
Steps: 4
  1. Parse search intent and parameters
  2. Execute multi-source search (Yelp + Google)
  3. Rank and filter results by relevance
  4. Present findings with source attribution
```

**AI Automation Workflow Example:**
```
📋 Generated Plan:
Goal: AI Automation Workflow: Compile the top 5 items about AI automation
Steps: 4
  1. Search for top 5 AI automation items
  2. Filter results to show only recent content (last 30 days)
  3. Summarize each result in ~1 sentence
  4. Create email draft with AI automation digest
```

### 4. Execution & Results
- Executes each step sequentially
- Provides real-time progress updates
- Displays formatted results with metadata
- Offers export and sharing options

## 🔍 Enhanced Search System V2

### Key Features
- **Relevance Filtering**: Query rewriting and hard gates for quality control
- **Intelligent Ranking**: Composite scoring with multiple weighted factors
- **Source Diversity**: Prevents domain repetition and ensures variety
- **Quality Control**: Authority scoring and freshness weighting
- **Uniform Schemas**: Consistent result presentation across all sources

## 🤖 AI Automation Workflow System

### Specialized Features
- **AI Automation Detection**: Automatically identifies AI automation related prompts
- **Focused Search**: Enhanced queries specifically for AI automation content
- **Content Summarization**: Condenses results to specified sentence count
- **Email Draft Generation**: Creates formatted email drafts for team communication
- **Daily Digest Workflows**: Complete automation from search to email preparation

### Interview Requirements Fulfillment
Your Flow System now fully supports the interview prompt:
> **"Build a tiny Flow-style system that takes a natural-language prompt, compiles a plan, and executes at least one step to produce a visible result."**

**Example Workflow**: "Every morning, compile the top 5 items about 'AI automation', summarize each in ~1 sentence, and prepare an email draft to founders@company.com"

✅ **Natural Language Processing**: Understands complex AI automation prompts
✅ **Plan Compilation**: Generates structured AI automation workflows  
✅ **Step Execution**: Executes search, filtering, summarization, and email creation
✅ **Visible Results**: Shows search results, summaries, and email drafts

### Search Sources
- **Yelp API**: Business listings and reviews
- **Google Custom Search**: Web content and news
- **Web Scraping**: Direct content extraction
- **Result Aggregation**: Intelligent merging and deduplication

## 🌐 Web Application Features

### User Interface
- Clean, modern design with responsive layout
- Real-time search and filtering
- Interactive result display
- Export functionality (JSON, CSV)

### Session Management
- Persistent user sessions
- Search history tracking
- Result caching and storage

### API Endpoints
- `GET /`: Main application interface
- `POST /search`: Execute search queries
- `POST /plan`: Generate execution plans
- `GET /results`: Retrieve stored results
- `POST /api/ai-automation/search`: AI automation focused search
- `POST /api/ai-automation/email-draft`: Create email drafts
- `POST /api/ai-automation/daily-digest`: Generate complete daily digest

## 📁 Project Structure

```
flow-system/
├── app.py                     # Main Flask application
├── enhanced_search_v2.py     # Enhanced search system V2
├── config.env                # Environment configuration
├── requirements.txt          # Python dependencies
├── templates/                # HTML templates
│   └── index.html           # Main application template
└── README.md                # This documentation
```

## 🧪 Testing & Development

### Running Tests
```bash
# Run the main application
python app.py

# Test search functionality
python -c "from enhanced_search_v2 import EnhancedSearchSystemV2; print('System ready')"
```

### Development Mode
```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## 🔌 API Integration

### Yelp Fusion API
- Business search and details
- Review aggregation
- Rating and price information

### Google Custom Search
- Web content discovery
- News and article search
- Custom search engine configuration

### Web Scraping
- Direct content extraction
- Metadata parsing
- Source validation

## 🚀 Performance & Scalability

### Optimization Features
- Intelligent caching of search results
- Configurable result limits
- Efficient API rate limiting
- Background task processing

### Monitoring
- Request/response logging
- Performance metrics
- Error tracking and reporting

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document complex functions
- Maintain consistent naming conventions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure your `config.env` file contains valid API keys
2. **Import Errors**: Verify all dependencies are installed with `pip install -r requirements.txt`
3. **Port Conflicts**: Change the port in `app.py` if 5000 is already in use

### Getting Help
- Check the application logs for detailed error messages
- Verify your API keys and permissions
- Ensure all required services are running

## 🔮 Future Enhancements

- **Machine Learning Integration**: Improved intent parsing and result ranking
- **Multi-language Support**: Internationalization and localization
- **Advanced Analytics**: User behavior tracking and insights
- **Mobile Application**: Native mobile app development
- **API Rate Limiting**: Intelligent request throttling
- **Result Caching**: Redis-based caching for improved performance
- **Scheduling System**: Daily automation and recurring tasks
- **Advanced Summarization**: AI-powered content condensation
- **Email Integration**: Direct email sending capabilities

---

**Built with ❤️ using Python, Flask, and modern web technologies**
