#!/usr/bin/env python3
"""
Enhanced Search System V2 with System-Level Improvements
- Relevance filtering with query rewriting and hard gates
- Intelligent ranking with composite scoring
- Consistent presentation with uniform schemas
- Source diversity and quality control
- Configurable parameters for tuning
"""

import os
import requests
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs, urlunparse
import json

# Load environment variables
load_dotenv('config.env')

@dataclass
class SearchResult:
    """Uniform item schema for consistent presentation."""
    title: str
    url: str
    source: str
    fetched_at: str
    snippet: str
    tags: List[str]
    rating: Optional[float] = None
    address: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    score: Optional[float] = None
    relevance_reason: Optional[str] = None

@dataclass
class SearchConfig:
    """Configurable parameters for tuning search behavior."""
    # Relevance thresholds
    min_relevance_score: float = 0.2      # Minimum score to include result
    min_keyword_matches: int = 1
    max_domain_repeats: int = 2
    
    # Time constraints
    max_age_days: int = 365
    freshness_weight: float = 0.3
    
    # Ranking weights
    text_relevance_weight: float = 0.4
    freshness_weight: float = 0.2
    authority_weight: float = 0.2
    engagement_weight: float = 0.1
    diversity_weight: float = 0.1
    
    # Display settings
    max_title_length: int = 80
    max_snippet_length: int = 160
    max_results: int = 10

class EnhancedSearchSystemV2:
    """Enhanced search system with system-level improvements."""

    def __init__(self, config: SearchConfig = None):
        self.config = config or SearchConfig()
        
        # API keys
        self.yelp_api_key = os.getenv('YELP_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_custom_search_key = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
        self.google_custom_search_cx = os.getenv('GOOGLE_CUSTOM_SEARCH_CX')
        
        # Stop words for query cleaning
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more',
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get',
            'come', 'made', 'may', 'part'
        }
        
        # Domain authority scores
        self.domain_authority = {
            'stackoverflow.com': 0.9,
            'github.com': 0.9,
            'docs.microsoft.com': 0.8,
            'developer.mozilla.org': 0.8,
            'python.org': 0.8,
            'reactjs.org': 0.8,
            'vuejs.org': 0.8,
            'angular.io': 0.8,
            'medium.com': 0.6,
            'dev.to': 0.6,
            'hashnode.dev': 0.6,
            'blog.logrocket.com': 0.7,
            'css-tricks.com': 0.7,
            'smashingmagazine.com': 0.7,
            'alistapart.com': 0.7
        }
        
        print("🚀 Enhanced Search System V2 initialized")
        self._print_api_status()

    def _print_api_status(self):
        """Print the status of available APIs."""
        print("\n📡 API Status:")
        print(f"✅ Yelp API: {'Configured' if self.yelp_api_key and self.yelp_api_key != 'your_yelp_api_key_here' else 'Not configured'}")
        print(f"✅ Google Places API: {'Configured' if self.google_api_key and self.google_api_key != 'your_google_api_key_here' else 'Not configured'}")
        print(f"✅ Google Custom Search: {'Configured' if self.google_custom_search_key and self.google_custom_search_cx and self.google_custom_search_cx != 'your_custom_search_engine_id_here' else 'Not configured'}")

    def unified_search(self, query: str, location: str = None, count: int = None) -> Dict[str, Any]:
        """Unified search with enhanced relevance filtering and ranking."""
        if count is None:
            count = self.config.max_results
            
        # Step 1: Query rewriting and normalization
        normalized_query = self._rewrite_query(query)
        print(f"🔍 Original query: {query}")
        print(f"🔍 Normalized query: {normalized_query}")
        
        # Step 2: Intent detection and routing
        intent = self._detect_intent(normalized_query)
        print(f"🎯 Detected intent: {intent}")
        
        # Step 3: Fetch results from appropriate sources
        if intent == 'local_business':
            results = self._search_local_businesses(normalized_query, location, count)
        else:
            results = self._search_general_information(normalized_query, count)
        
        if not results or not results.get('results'):
            return self._create_no_results_response(query, intent)
        
        # Step 4: Apply relevance filtering
        filtered_results = self._apply_relevance_filtering(results['results'], normalized_query, intent)
        
        # Step 5: Remove duplicates
        deduped_results = self._remove_duplicates(filtered_results)
        print(f"🔍 Deduplication: {len(filtered_results)} → {len(deduped_results)} results")
        
        # Step 6: Apply source diversity constraints
        diverse_results = self._apply_source_diversity(deduped_results)
        print(f"🔍 Source diversity: {len(deduped_results)} → {len(diverse_results)} results")
        
        # Step 7: Score and rank results
        scored_results = self._score_and_rank_results(diverse_results, normalized_query, intent)
        
        # Step 7.5: Apply minimum score threshold
        final_results = [r for r in scored_results if r.get('score', 0) >= self.config.min_relevance_score]
        print(f"🔍 Score filtering: {len(scored_results)} → {len(final_results)} results (min score: {self.config.min_relevance_score})")
        
        # Step 8: Format results consistently
        formatted_results = self._format_results_consistently(final_results)
        
        return {
            'source': results.get('source', 'enhanced_search'),
            'query_used': query,
            'normalized_query': normalized_query,
            'intent': intent,
            'location': location,
            'count': len(formatted_results),
            'results': formatted_results,
            'timestamp': datetime.now().isoformat(),
            'config': asdict(self.config),
            'quality_metrics': {
                'relevance_filtered': len(filtered_results),
                'duplicates_removed': len(filtered_results) - len(deduped_results),
                'source_diversity_applied': len(deduped_results) - len(diverse_results),
                'final_score_range': f"{min(r.get('score', 0) for r in scored_results):.2f} - {max(r.get('score', 0) for r in scored_results):.2f}"
            }
        }

    def _rewrite_query(self, query: str) -> str:
        """Rewrite and normalize the query for better search results."""
        # Convert to lowercase
        query = query.lower()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Remove stop words (but keep important ones)
        important_stop_words = {'how', 'what', 'when', 'where', 'why', 'which', 'who'}
        words = query.split()
        filtered_words = [word for word in words if word not in self.stop_words or word in important_stop_words]
        
        # Add synonyms and expand abbreviations
        synonyms = {
            'tutorial': 'guide how-to learn',
            'guide': 'tutorial how-to learn',
            'how-to': 'tutorial guide learn',
            'learn': 'tutorial guide how-to',
            'best': 'top excellent great',
            'top': 'best excellent great',
            'compare': 'vs versus comparison',
            'vs': 'compare versus comparison',
            'versus': 'compare vs comparison',
            'review': 'rating feedback opinion',
            'rating': 'review feedback opinion'
        }
        
        expanded_query = ' '.join(filtered_words)
        for original, expansion in synonyms.items():
            if original in expanded_query:
                expanded_query += ' ' + expansion
        
        return expanded_query

    def _detect_intent(self, query: str) -> str:
        """Detect the intent of the query for appropriate routing."""
        query_lower = query.lower()
        
        # Priority 1: AI Automation queries (highest priority for tech focus)
        ai_automation_keywords = [
            'ai automation', 'artificial intelligence automation', 'automation tools',
            'workflow automation', 'process automation', 'ai workflow', 'automation ai',
            'intelligent automation', 'ai tools', 'automation software', 'ai platform',
            'machine learning automation', 'robotic process automation', 'rpa',
            'business process automation', 'ai powered automation', 'smart automation'
        ]
        
        # Check for AI automation intent first
        if any(keyword in query_lower for keyword in ai_automation_keywords):
            return 'ai_automation'
        
        # Priority 2: Learning/Educational/Information queries
        learning_keywords = [
            'youtube', 'channel', 'learn', 'learning', 'tutorial', 'course', 'education',
            'how to', 'guide', 'tips', 'advice', 'best practices', 'examples', 'research',
            'video', 'podcast', 'blog', 'article', 'resource', 'study', 'training',
            'what is', 'explain', 'understand', 'knowledge', 'information', 'find out',
            'discover', 'explore', 'investigate', 'analyze', 'compare', 'review'
        ]
        
        # Check for learning intent first - if ANY learning keyword is present, it's general
        if any(keyword in query_lower for keyword in learning_keywords):
            return 'general'  # Use web search for learning resources
        
        # Priority 2: Local business queries (only if NO learning keywords AND has business indicators)
        local_business_keywords = [
            'restaurant', 'food', 'cafe', 'bar', 'shop', 'store', 'business', 'service',
            'near me', 'local', 'address', 'phone', 'rating', 'review', 'hours', 'open',
            'delivery', 'takeout', 'reservation', 'booking', 'appointment', 'salon',
            'spa', 'gym', 'dentist', 'doctor', 'lawyer', 'plumber', 'electrician',
            'mechanic', 'car wash', 'gas station', 'bank', 'pharmacy', 'hospital',
            'coffee shop', 'pizza', 'burger', 'sushi', 'steak', 'italian', 'chinese'
        ]
        
        # Location indicators that suggest local business intent
        location_indicators = [
            'in ', 'near ', 'around ', 'at ', 'by ', 'close to ', 'within ',
            'new york', 'san francisco', 'los angeles', 'chicago', 'miami', 'boston',
            'seattle', 'denver', 'austin', 'dallas', 'houston', 'phoenix', 'atlanta',
            'bay area', 'silicon valley', 'manhattan', 'brooklyn', 'queens', 'bronx'
        ]
        
        # Only classify as local business if:
        # 1. Has business keywords AND
        # 2. Has location indicators AND  
        # 3. NO learning keywords (already checked above)
        has_business_keywords = any(keyword in query_lower for keyword in local_business_keywords)
        has_location_indicators = any(indicator in query_lower for indicator in location_indicators)
        
        if has_business_keywords and has_location_indicators:
            return 'local_business'
        
        # Priority 3: News/Current events
        news_keywords = [
            'news', 'latest', 'recent', 'update', 'announcement', 'release',
            'trend', 'trending', 'breaking', 'today', 'this week', 'this month',
            'current', 'happening now', 'latest news', 'breaking news'
        ]
        
        if any(keyword in query_lower for keyword in news_keywords):
            return 'general'
        
        # Priority 4: Comparison/Ranking (but not if it's about learning)
        comparison_keywords = [
            'compare', 'versus', 'vs', 'top', 'best', 'worst', 'ranking', 'rank',
            'compare top', 'top 10', 'top 5', 'best 10', 'best 5', 'better than'
        ]
        
        if any(keyword in query_lower for keyword in comparison_keywords):
            # If it's about learning/YouTube, it's general, not comparison
            if any(keyword in query_lower for keyword in learning_keywords):
                return 'general'
            # If it's about local businesses with location, it's local_business
            if has_business_keywords and has_location_indicators:
                return 'local_business'
            return 'compare_rank'
        
        # Default: General intent for anything else
        return 'general'

    def _route_query(self, query: str, intent: str, location: str = None, count: int = 10) -> Dict[str, Any]:
        """Route query to appropriate search method based on intent."""
        print(f"🌐 Routing query: '{query}' in {location}, count: {count}")
        
        # Normalize query for better search results
        normalized_query = self._normalize_query(query)
        print(f"🔍 Original query: {query}")
        print(f"🔍 Normalized query: {normalized_query}")
        print(f"🎯 Detected intent: {intent}")
        
        try:
            if intent == 'local_business':
                print(f"🏪 Searching for local businesses: {normalized_query}")
                return self._search_local_businesses(normalized_query, location, count)
            
            elif intent == 'general':
                print(f"🌐 Searching web for general information: {normalized_query}")
                return self._search_web(normalized_query, count)
            
            elif intent == 'compare_rank':
                # For comparison queries, try local business first if it seems location-specific
                if location and any(word in query.lower() for word in ['restaurant', 'food', 'shop', 'business', 'service']):
                    print(f"🏪 Comparing local businesses: {normalized_query}")
                    return self._search_local_businesses(normalized_query, location, count)
                else:
                    print(f"🌐 Comparing web results: {normalized_query}")
                    return self._search_web(normalized_query, count)
            
            else:
                # Default to web search for any unrecognized intent
                print(f"🌐 Defaulting to web search: {normalized_query}")
                return self._search_web(normalized_query, count)
                
        except Exception as e:
            print(f"❌ Query routing error: {str(e)}")
            # Fallback to web search if anything fails
            try:
                print(f"🔄 Fallback to web search: {normalized_query}")
                return self._search_web(normalized_query, count)
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {str(fallback_error)}")
                return {"error": f"Search failed: {str(e)}", "results": []}

    def _search_local_businesses(self, query: str, location: str = None, count: int = 10) -> Dict[str, Any]:
        """Search for local businesses using Yelp and Google Places APIs."""
        print(f"🏪 Searching for local businesses: {query}")
        
        # Try Yelp first
        yelp_results = self._search_yelp_businesses(query, location, count)
        if yelp_results and yelp_results.get('results'):
            print("✅ Yelp results found")
            return yelp_results
        
        # Fallback to Google Places
        google_results = self._search_google_places(query, location, count)
        if google_results and google_results.get('results'):
            print("✅ Google Places results found")
            return google_results
        
        # If both fail, use fallback
        print("🔄 Both APIs failed, using fallback")
        return self._fallback_business_search(query, location, count)

    def _search_general_information(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Search for general information using Google Custom Search API."""
        print(f"🌐 Searching for general information: {query}")
        
        # Try Google Custom Search first
        google_custom_results = self._search_google_custom_search(query, count)
        if google_custom_results and google_custom_results.get('results'):
            print("✅ Google Custom Search results found")
            return google_custom_results
        
        # Fallback to simulated results
        print("🔄 Google Custom Search failed, using fallback")
        return self._simulate_web_search(query, count)

    def _search_yelp_businesses(self, query: str, location: str = None, count: int = 10) -> Dict[str, Any]:
        """Search Yelp for businesses."""
        try:
            if not self.yelp_api_key or self.yelp_api_key == 'your_yelp_api_key_here':
                print("⚠️  Yelp API key not configured")
                return None
            
            headers = {'Authorization': f'Bearer {self.yelp_api_key}'}
            params = {
                'term': query,
                'location': location or 'San Francisco, CA',
                'limit': count,
                'sort_by': 'rating'
            }
            
            print(f"🌐 Making Yelp API call: {query}")
            response = requests.get('https://api.yelp.com/v3/businesses/search',
                                 headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                businesses = data.get('businesses', [])
                print(f"✅ Yelp API call successful. Found {len(businesses)} businesses.")
                
                return {
                    'source': 'yelp',
                    'query_used': query,
                    'location': location,
                    'count': len(businesses),
                    'results': self._format_yelp_results(businesses),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"❌ Yelp API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Yelp search error: {e}")
            return None

    def _search_google_places(self, query: str, location: str = None, count: int = 10) -> Dict[str, Any]:
        """Search Google Places for locations."""
        try:
            if not self.google_api_key or self.google_api_key == 'your_google_api_key_here':
                print("⚠️  Google Places API key not configured")
                return None
            
            params = {
                'query': f"{query} in {location or 'San Francisco, CA'}",
                'key': self.google_api_key,
                'type': 'establishment'
            }
            
            print(f"🌐 Making Google Places API call: {query}")
            response = requests.get('https://maps.googleapis.com/maps/api/place/textsearch/json',
                                 params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    places = data.get('results', [])[:count]
                    print(f"✅ Google Places API call successful. Found {len(places)} places.")
                    
                    return {
                        'source': 'google_places',
                        'query_used': query,
                        'location': location,
                        'count': len(places),
                        'results': self._format_google_places_results(places),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print(f"❌ Google Places API error: {data.get('status')}")
                    return None
            else:
                print(f"❌ Google Places HTTP error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Google Places search error: {e}")
            return None

    def _search_google_custom_search(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Search using Google Custom Search JSON API."""
        try:
            if not self.google_custom_search_key or not self.google_custom_search_cx:
                print("⚠️  Google Custom Search not configured")
                return None
            
            if self.google_custom_search_cx == 'your_custom_search_engine_id_here':
                print("⚠️  Google Custom Search Engine ID not configured")
                return None
            
            # Google Custom Search API endpoint
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_custom_search_key,
                'cx': self.google_custom_search_cx,
                'q': query,
                'num': min(count, 10),  # Google CSE max is 10 per request
                'safe': 'active'
            }
            
            print(f"🌐 Making Google Custom Search API call: {query}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                results = []
                for item in items:
                    result = {
                        'title': item.get('title', ''),
                        'snippet': item.get('snippet', ''),
                        'url': item.get('link', ''),
                        'source': 'google_custom_search',
                        'display_link': item.get('displayLink', ''),
                        'image': item.get('pagemap', {}).get('cse_image', [{}])[0].get('src', '') if item.get('pagemap', {}).get('cse_image') else '',
                        'rich_snippet': item.get('pagemap', {}).get('metatags', [{}])[0].get('og:description', '') if item.get('pagemap', {}).get('metatags') else ''
                    }
                    results.append(result)
                
                print(f"✅ Google Custom Search successful. Found {len(results)} results.")
                
                return {
                    'source': 'google_custom_search',
                    'query_used': query,
                    'count': len(results),
                    'results': results,
                    'timestamp': datetime.now().isoformat(),
                    'total_results': data.get('searchInformation', {}).get('totalResults', '0'),
                    'search_time': data.get('searchInformation', {}).get('searchTime', 0)
                }
            else:
                print(f"❌ Google Custom Search API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Google Custom Search error: {e}")
            return None

    def _apply_relevance_filtering(self, results: List[Dict], query: str, intent: str) -> List[Dict]:
        """Apply relevance filtering with hard gates."""
        filtered_results = []
        query_lower = query.lower()
        
        # Extract key phrases from query
        key_phrases = self._extract_key_phrases(query)
        print(f"🔍 Key phrases: {key_phrases}")
        
        for result in results:
            # Get title and snippet for relevance checking
            title = result.get('title', '').lower()
            snippet = result.get('snippet', '').lower()
            content = f"{title} {snippet}"
            
            # For general intent queries (learning, YouTube, etc.), be much more lenient
            if intent == 'general':
                # Just check basic quality - don't require specific keyword matches
                if len(title) >= 3 and len(snippet) >= 5:
                    filtered_results.append(result)
                    continue
            
            # For local business queries, apply stricter filtering
            elif intent == 'local_business':
                # Hard relevance gate 1: Must contain at least TWO key phrases for high confidence
                phrase_matches = sum(1 for phrase in key_phrases if phrase in content)
                if phrase_matches >= 2:
                    filtered_results.append(result)
                    continue
                
                # Hard relevance gate 2: Must contain at least ONE key phrase + business signal
                business_signals = ['restaurant', 'food', 'cafe', 'shop', 'business', 'service', 'coffee']
                has_business_signal = any(signal in content for signal in business_signals)
                if phrase_matches >= 1 and has_business_signal:
                    filtered_results.append(result)
                    continue
            
            # For other intents, apply moderate filtering
            else:
                # Must contain at least ONE key phrase
                phrase_matches = sum(1 for phrase in key_phrases if phrase in content)
                if phrase_matches >= 1:
                    filtered_results.append(result)
                    continue
        
        print(f"🔍 Relevance filtering: {len(results)} → {len(filtered_results)} results")
        return filtered_results

    def _is_obviously_irrelevant(self, result: Dict, query_lower: str) -> bool:
        """Check if a local business result is obviously irrelevant."""
        title = result.get('title', '').lower()
        
        # If title is empty or very short, it's probably not a real business
        if not title or len(title) < 2:
            return True
        
        # Check for obvious spam or irrelevant content
        spam_indicators = ['click here', 'buy now', 'free money', 'make money fast', 'work from home']
        if any(indicator in title for indicator in spam_indicators):
            return True
        
        # For restaurant queries, make sure it's actually a business name
        if 'restaurant' in query_lower or 'food' in query_lower or 'cafe' in query_lower:
            # Business names should be reasonable length and not look like URLs
            if len(title) > 100 or title.startswith('http'):
                return True
        
        return False

    def _extract_key_phrases(self, query: str) -> List[str]:
        """Extract key phrases from the query."""
        # Remove common words and keep meaningful phrases
        words = query.split()
        key_phrases = []
        
        # Priority 1: Multi-word business/location phrases (highest priority)
        business_location_phrases = [
            'coffee shop', 'restaurant', 'cafe', 'business', 'service',
            'san francisco', 'new york', 'los angeles', 'chicago', 'miami',
            'bay area', 'silicon valley', 'manhattan', 'brooklyn',
            'new york city', 'nyc', 'manhattan', 'brooklyn', 'queens'
        ]
        
        for phrase in business_location_phrases:
            if phrase in query.lower():
                key_phrases.append(phrase)
        
        # Priority 2: Single important words (medium priority)
        important_words = ['coffee', 'shop', 'cafe', 'restaurant', 'food', 'business', 'service', 'rating', 'price']
        for word in words:
            if word.lower() in important_words and word.lower() not in [p.split()[0] for p in key_phrases]:
                key_phrases.append(word.lower())
        
        # Priority 3: Location words (medium priority)
        location_words = ['san', 'francisco', 'york', 'angeles', 'chicago', 'miami', 'boston', 'seattle', 'city']
        for word in words:
            if word.lower() in location_words and word.lower() not in [p.split()[0] for p in key_phrases]:
                key_phrases.append(word.lower())
        
        # Priority 4: Action words (lower priority)
        action_words = ['find', 'top', 'best', 'compare', 'search', 'locate']
        for word in words:
            if word.lower() in action_words and word.lower() not in [p.split()[0] for p in key_phrases]:
                key_phrases.append(word.lower())
        
        # Remove duplicates and return
        return list(set(key_phrases))

    def _passes_task_aware_filter(self, result: Dict, intent: str) -> bool:
        """Check if result passes task-aware filtering."""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        content = f"{title} {snippet}"
        
        if intent == 'tutorial':
            # Must contain instructional signals
            tutorial_signals = ['tutorial', 'guide', 'how to', 'step by step', 'learn', 'walkthrough']
            return any(signal in content for signal in tutorial_signals)
        
        elif intent == 'news':
            # Must contain freshness signals
            freshness_signals = ['2024', '2025', 'latest', 'new', 'recent', 'update', 'announcement']
            return any(signal in content for signal in freshness_signals)
        
        elif intent == 'local_business':
            # For local businesses, be more lenient - they often have location info in separate fields
            # Just check that it's not obviously irrelevant
            business_signals = ['coffee', 'shop', 'cafe', 'restaurant', 'food', 'business', 'service']
            return any(signal in content for signal in business_signals)
        
        return True

    def _passes_content_quality_check(self, result: Dict) -> bool:
        """Check if result passes content quality requirements."""
        title = result.get('title', result.get('name', ''))
        snippet = result.get('snippet', result.get('description', result.get('summary', '')))
        url = result.get('url', result.get('link', ''))
        
        # Must have title
        if not title:
            return False
        
        # Title should be reasonable length
        if len(title) < 3 or len(title) > 200:
            return False
        
        # Snippet/description is optional but if present should be reasonable length
        if snippet and (len(snippet) < 5 or len(snippet) > 1000):
            return False
        
        # URL should be valid (but allow for missing URLs in some cases)
        if url and not url.startswith('http'):
            return False
        
        return True

    def _passes_intent_specific_check(self, result: Dict, intent: str, query_lower: str) -> bool:
        """Check if result passes an intent-specific relevance check."""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        content = f"{title} {snippet}"
        
        if intent == 'tutorial':
            # Must contain instructional signals
            tutorial_signals = ['tutorial', 'guide', 'how to', 'step by step', 'learn', 'walkthrough']
            return any(signal in content for signal in tutorial_signals)
        
        elif intent == 'news':
            # Must contain freshness signals
            freshness_signals = ['2024', '2025', 'latest', 'new', 'recent', 'update', 'announcement']
            return any(signal in content for signal in freshness_signals)
        
        elif intent == 'local_business':
            # For local businesses, be more lenient - they often have location info in separate fields
            # Just check that it's not obviously irrelevant
            business_signals = ['coffee', 'shop', 'cafe', 'restaurant', 'food', 'business', 'service']
            return any(signal in content for signal in business_signals)
        
        return True

    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """Remove duplicate results using multiple strategies."""
        seen_urls = set()
        seen_titles = set()
        deduped_results = []
        
        for result in results:
            url = result.get('url', '')
            title = result.get('title', '')
            
            # Normalize URL (remove tracking parameters)
            normalized_url = self._normalize_url(url)
            
            # Check for exact URL match
            if normalized_url in seen_urls:
                continue
            
            # Check for similar titles (fuzzy matching)
            if self._is_similar_title(title, seen_titles):
                continue
            
            seen_urls.add(normalized_url)
            seen_titles.add(title)
            deduped_results.append(result)
        
        return deduped_results

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing tracking parameters and fragments."""
        try:
            parsed = urlparse(url)
            # Remove tracking parameters
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v for k, v in query_params.items() 
                             if not any(tracker in k.lower() for tracker in 
                                      ['utm_', 'fbclid', 'gclid', 'ref', 'source'])}
            
            # Rebuild URL without tracking params
            clean_query = '&'.join(f"{k}={v[0]}" for k, v in filtered_params.items())
            clean_url = urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, clean_query, ''  # Remove fragment
            ))
            return clean_url
        except:
            return url

    def _is_similar_title(self, title: str, seen_titles: set, threshold: float = 0.8) -> bool:
        """Check if title is similar to any seen titles using Jaccard similarity."""
        title_tokens = set(title.lower().split())
        
        for seen_title in seen_titles:
            seen_tokens = set(seen_title.lower().split())
            
            # Calculate Jaccard similarity
            intersection = len(title_tokens & seen_tokens)
            union = len(title_tokens | seen_tokens)
            
            if union > 0 and intersection / union >= threshold:
                return True
        
        return False

    def _apply_source_diversity(self, results: List[Dict]) -> List[Dict]:
        """Apply source diversity constraints."""
        domain_counts = {}
        diverse_results = []
        
        for result in results:
            url = result.get('url', '')
            domain = urlparse(url).netloc if url else 'unknown'
            
            # Count domain occurrences
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            
            # For local business searches, be much more lenient with business directories
            # Allow more results from legitimate business sources like Yelp, Google Places
            if 'yelp.com' in domain or 'google.com' in domain or 'maps.google.com' in domain:
                # Allow up to max_results from primary local business sources
                if domain_counts[domain] <= self.config.max_results:
                    diverse_results.append(result)
            elif domain_counts[domain] <= self.config.max_domain_repeats:
                diverse_results.append(result)
        
        return diverse_results

    def _score_and_rank_results(self, results: List[Dict], query: str, intent: str) -> List[Dict]:
        """Score and rank results using composite scoring."""
        scored_results = []
        
        for result in results:
            score = self._calculate_composite_score(result, query, intent)
            result['score'] = score
            scored_results.append(result)
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_results

    def _calculate_composite_score(self, result: Dict, query: str, intent: str) -> float:
        """Calculate composite score for ranking."""
        score = 0.0
        
        # Text relevance score (40% weight)
        text_relevance = self._calculate_text_relevance(result, query)
        score += self.config.text_relevance_weight * text_relevance
        
        # Freshness score (20% weight)
        freshness = self._calculate_freshness_score(result)
        score += self.config.freshness_weight * freshness
        
        # Authority score (20% weight)
        authority = self._calculate_authority_score(result)
        score += self.config.authority_weight * authority
        
        # Engagement score (10% weight)
        engagement = self._calculate_engagement_score(result)
        score += self.config.engagement_weight * engagement
        
        # Diversity penalty (10% weight)
        if result.get('diversity_penalty'):
            score *= 0.7
        
        # Bonus for local business intent (more lenient scoring)
        if intent == 'local_business':
            score += 0.3  # Add significant bonus to help local business results pass filtering
        
        # Bonus for verified sources like Yelp
        source = result.get('source', '')
        if 'yelp' in source or 'google' in source:
            score += 0.2  # Bonus for legitimate business directories
        
        return round(score, 3)

    def _calculate_text_relevance(self, result: Dict, query: str) -> float:
        """Calculate text relevance score."""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        content = f"{title} {snippet}"
        query_lower = query.lower()
        
        # Extract key phrases for more accurate scoring
        key_phrases = self._extract_key_phrases(query)
        
        # Score based on key phrase matches (higher weight for longer phrases)
        phrase_score = 0.0
        for phrase in key_phrases:
            if phrase in content:
                # Longer phrases get higher scores
                phrase_score += len(phrase.split()) * 0.2
        
        # Score based on individual word matches
        query_words = query_lower.split()
        word_matches = sum(1 for word in query_words if word in content and len(word) > 3)
        word_score = min(1.0, word_matches / max(1, len(query_words))) * 0.3
        
        # Combined score
        total_score = phrase_score + word_score
        
        # For local business searches, be much more generous
        if any(word in query_lower for word in ['coffee', 'shop', 'cafe', 'restaurant', 'food', 'business']):
            # Local business results often have minimal text - don't penalize them
            if total_score < 0.2:  # Very low threshold for local business
                total_score = 0.2  # Give minimum score instead of 0
            
            # Bonus for having a business name (title)
            if title and len(title) > 2:
                total_score += 0.1
            
            # Bonus for having any content
            if content.strip():
                total_score += 0.1
        
        return min(1.0, total_score)

    def _calculate_freshness_score(self, result: Dict) -> float:
        """Calculate freshness score based on date."""
        # Try to extract date from various fields
        date_str = (result.get('date') or result.get('published_at') or 
                   result.get('created_at') or result.get('updated_at'))
        
        if not date_str:
            return 0.5  # Default score for unknown dates
        
        try:
            # Parse date (simplified)
            if isinstance(date_str, str):
                # Look for year patterns
                year_match = re.search(r'20\d{2}', date_str)
                if year_match:
                    year = int(year_match.group())
                    current_year = datetime.now().year
                    age_years = current_year - year
                    # Exponential decay: newer = higher score
                    return max(0.1, 1.0 / (1 + age_years * 0.5))
        except:
            pass
        
        return 0.5

    def _calculate_authority_score(self, result: Dict) -> float:
        """Calculate authority score based on source domain."""
        url = result.get('url', '')
        domain = urlparse(url).netloc if url else 'unknown'
        
        # Check domain authority scores
        if domain in self.domain_authority:
            return self.domain_authority[domain]
        
        # Default authority based on TLD
        if domain.endswith('.org') or domain.endswith('.edu'):
            return 0.7
        elif domain.endswith('.gov'):
            return 0.8
        elif domain.endswith('.com'):
            return 0.6
        else:
            return 0.5

    def _calculate_engagement_score(self, result: Dict) -> float:
        """Calculate engagement score based on available metrics."""
        score = 0.5  # Default score
        
        # Rating score
        rating = result.get('rating')
        if rating:
            score += min(0.3, rating / 10)
        
        # Review count score
        review_count = result.get('review_count', 0)
        if review_count:
            score += min(0.2, review_count / 1000)
        
        return min(1.0, score)

    def _format_results_consistently(self, results: List[Dict]) -> List[Dict]:
        """Format results using uniform schema."""
        formatted_results = []
        
        for result in results:
            # Extract and clean data
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            url = result.get('url', '')
            
            # Truncate title and snippet
            title = self._truncate_text(title, self.config.max_title_length)
            snippet = self._truncate_text(snippet, self.config.max_snippet_length)
            
            # Create uniform result
            formatted_result = SearchResult(
                title=title,
                url=url,
                source=result.get('source', 'unknown'),
                fetched_at=datetime.now().isoformat(),
                snippet=snippet,
                tags=self._extract_tags(result),
                rating=result.get('rating'),
                address=result.get('address'),
                author=result.get('author'),
                date=result.get('date'),
                score=result.get('score'),
                relevance_reason=self._generate_relevance_reason(result)
            )
            
            formatted_results.append(asdict(formatted_result))
        
        return formatted_results

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text smartly at word boundaries."""
        if len(text) <= max_length:
            return text
        
        # Truncate at word boundary
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'

    def _extract_tags(self, result: Dict) -> List[str]:
        """Extract relevant tags from result."""
        tags = []
        
        # Source-based tags
        source = result.get('source', '')
        if 'yelp' in source:
            tags.extend(['business', 'local', 'reviews'])
        elif 'google' in source:
            tags.extend(['web', 'search'])
        
        # Content-based tags
        title = result.get('title', '').lower()
        if any(word in title for word in ['tutorial', 'guide', 'how-to']):
            tags.append('tutorial')
        if any(word in title for word in ['news', 'latest', 'update']):
            tags.append('news')
        
        return list(set(tags))  # Remove duplicates

    def _generate_relevance_reason(self, result: Dict) -> str:
        """Generate explanation for why result is relevant."""
        reasons = []
        
        score = result.get('score', 0)
        if score > 0.8:
            reasons.append('high relevance')
        elif score > 0.6:
            reasons.append('good relevance')
        else:
            reasons.append('moderate relevance')
        
        # Add source quality info
        source = result.get('source', '')
        if 'yelp' in source or 'google' in source:
            reasons.append('verified source')
        
        # Add freshness info
        if result.get('date'):
            reasons.append('recent content')
        
        return ' • '.join(reasons)

    def _create_no_results_response(self, query: str, intent: str) -> Dict[str, Any]:
        """Create a response when no results are found."""
        return {
            'source': 'no_results',
            'query_used': query,
            'intent': intent,
            'count': 0,
            'results': [],
            'timestamp': datetime.now().isoformat(),
            'message': f"No relevant results found for '{query}'. Try adjusting your search terms or broadening your query.",
            'suggestions': [
                'Use more specific keywords',
                'Try different phrasing',
                'Check spelling',
                'Broaden your search scope'
            ]
        }

    def _format_yelp_results(self, businesses: List[Dict]) -> List[Dict]:
        """Format Yelp API results."""
        formatted = []
        for business in businesses:
            formatted.append({
                'id': business.get('id'),
                'title': business.get('name'),
                'snippet': f"{business.get('categories', [{}])[0].get('title', 'Business')} in {business.get('location', {}).get('city', 'Unknown')}",
                'url': business.get('url'),
                'source': 'yelp',
                'rating': business.get('rating'),
                'review_count': business.get('review_count'),
                'price': business.get('price'),
                'address': business.get('location', {}).get('address1', ''),
                'phone': business.get('phone'),
                'categories': [cat.get('title') for cat in business.get('categories', [])]
            })
        return formatted

    def _format_google_places_results(self, places: List[Dict]) -> List[Dict]:
        """Format Google Places API results."""
        formatted = []
        for place in places:
            formatted.append({
                'id': place.get('place_id'),
                'title': place.get('name'),
                'snippet': f"Place in {place.get('formatted_address', 'Unknown location')}",
                'url': place.get('website', ''),
                'source': 'google_places',
                'rating': place.get('rating'),
                'review_count': place.get('user_ratings_total'),
                'price': '$' * place.get('price_level', 0) if place.get('price_level') else 'N/A',
                'address': place.get('formatted_address', ''),
                'phone': place.get('formatted_phone_number', ''),
                'categories': place.get('types', [])
            })
        return formatted

    def _fallback_business_search(self, query: str, location: str = None, count: int = 10) -> Dict[str, Any]:
        """Fallback business search with simulated data."""
        print(f"🎭 Using fallback business search for: {query}")
        
        businesses = []
        for i in range(min(count, 10)):
            business = {
                'id': f"fallback_{i+1}",
                'title': f"{query.title()} Business {i+1}",
                'snippet': f"Local {query} business in {location or 'San Francisco, CA'}",
                'url': f"https://example.com/business-{i+1}",
                'source': 'fallback',
                'rating': round(3.5 + (i * 0.3), 1),
                'review_count': 50 + (i * 25),
                'price': '$' * (1 + (i % 3)),
                'address': f"{i+100} Main St, {location or 'San Francisco, CA'}",
                'phone': f"+1-555-{1000+i:04d}",
                'categories': [query.title()]
            }
            businesses.append(business)
        
        return {
            'source': 'fallback_business',
            'query_used': query,
            'location': location,
            'count': len(businesses),
            'results': businesses,
            'timestamp': datetime.now().isoformat(),
            'note': 'Fallback data - API keys may be missing or invalid'
        }

    def _simulate_web_search(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Simulate web search results."""
        print(f"🎭 Simulating web search for: {query}")
        
        results = []
        for i in range(min(count, 10)):
            result = {
                'title': f"Result {i+1}: {query.title()} Information",
                'snippet': f"This is a simulated search result about {query}. It contains relevant information that would normally be found through web search.",
                'url': f"https://example.com/result-{i+1}",
                'source': 'simulated_web_search'
            }
            results.append(result)
        
        return {
            'source': 'simulated_web_search',
            'query_used': query,
            'count': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'note': 'Simulated results - Google Custom Search API may not be configured'
        }

    def summarize_content(self, content: str, max_sentences: int = 1) -> str:
        """Summarize content to specified number of sentences."""
        if not content or len(content.strip()) < 50:
            return content
        
        # Split into sentences (basic approach)
        sentences = re.split(r'[.!?]+', content.strip())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return content
        
        # Take first sentence and clean it up
        first_sentence = sentences[0]
        
        # Ensure it ends with proper punctuation
        if not first_sentence.endswith(('.', '!', '?')):
            first_sentence += '.'
        
        # Add ellipsis if we're truncating
        if len(sentences) > 1:
            first_sentence += '...'
        
        return first_sentence

    def create_email_draft(self, results: List[SearchResult], recipient: str = "founders@company.com", 
                          subject: str = "AI Automation Digest") -> str:
        """Create an email draft with search results."""
        if not results:
            return "No results to include in email."
        
        email_content = f"""Subject: {subject}

Dear Team,

Here's your daily AI automation digest with the top {len(results)} items:

"""
        
        for i, result in enumerate(results[:5], 1):
            summary = self.summarize_content(result.snippet, max_sentences=1)
            email_content += f"{i}. {result.title}\n"
            email_content += f"   {summary}\n"
            email_content += f"   Source: {result.url}\n\n"
        
        email_content += """Best regards,
Flow System AI

---
Generated automatically by Flow System - AI Automation Workflow
"""
        
        return email_content

    def get_ai_automation_focus_results(self, query: str, count: int = 5) -> Dict[str, Any]:
        """Get results specifically focused on AI automation topics."""
        # Enhance query with AI automation focus
        enhanced_query = f"{query} AI automation artificial intelligence workflow tools"
        
        # Search with enhanced query
        results = self.unified_search(enhanced_query, count=count)
        
        if results and 'results' in results:
            # Filter for recent content (last 30 days)
            recent_results = []
            for result in results['results']:
                # Check if result has recent date
                date_str = result.get('date', '')
                if date_str:
                    try:
                        result_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        days_old = (datetime.now() - result_date).days
                        if days_old <= 30:
                            recent_results.append(result)
                    except:
                        # If date parsing fails, include it
                        recent_results.append(result)
                else:
                    # If no date, include it
                    recent_results.append(result)
            
            # Update results with filtered list
            results['results'] = recent_results[:count]
            results['count'] = len(results['results'])
            results['focus'] = 'ai_automation'
            results['note'] = 'Filtered for AI automation focus and recent content'
        
        return results

# Example usage
if __name__ == "__main__":
    # Create custom configuration
    config = SearchConfig(
        min_relevance_score=0.5,
        max_domain_repeats=3,
        max_results=15
    )
    
    search_system = EnhancedSearchSystemV2(config)
    
    # Test local business search
    print("\n🧪 Testing local business search...")
    business_results = search_system.unified_search("Indian restaurants in San Francisco", "San Francisco, CA", 5)
    if business_results:
        print(f"Found {business_results['count']} results from {business_results['source']}")
        print(f"Quality metrics: {business_results['quality_metrics']}")
    
    # Test general information search
    print("\n🧪 Testing general information search...")
    info_results = search_system.unified_search("React tutorial 2025", count=5)
    if info_results:
        print(f"Found {info_results['count']} results from {info_results['source']}")
        print(f"Quality metrics: {info_results['quality_metrics']}")
