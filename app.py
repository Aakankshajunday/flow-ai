#!/usr/bin/env python3
"""
Flow System Web Application with Enhanced Search System
A web-based demonstration of the Flow-style system that takes natural language prompts,
compiles plans, and executes steps to produce visible results using real APIs.
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from enhanced_search_v2 import EnhancedSearchSystemV2, SearchConfig

# Load environment variables
load_dotenv('config.env')

app = Flask(__name__)
app.secret_key = 'flow-system-secret-key-2024'

@dataclass
class Step:
    """Represents a single step in a plan."""
    action: str
    description: str
    parameters: Dict[str, Any]
    expected_output: str
    status: str = "pending"
    result: str = ""

@dataclass
class Plan:
    """Represents a complete plan with multiple steps."""
    goal: str
    steps: List[Step]
    estimated_time: str
    status: str = "pending"
    created_at: str = ""

class FlowSystem:
    """Advanced Flow-style system that can handle ANY query using Enhanced Search System."""
    
    def __init__(self):
        # Initialize the enhanced search system V2 with custom configuration
        config = SearchConfig(
            min_relevance_score=0.2,
            max_domain_repeats=2,
            max_results=15,
            text_relevance_weight=0.4,
            freshness_weight=0.2,
            authority_weight=0.2,
            engagement_weight=0.1,
            diversity_weight=0.1
        )
        self.search_system = EnhancedSearchSystemV2(config)
        
        # Store current research results
        self._current_results = {}
        self._current_plan = None
        
        print("🚀 Advanced Flow System initialized with Enhanced Search System V2")
        
        # Set up available actions after all methods are defined
        self._setup_actions()
    
    def parse_prompt(self, prompt: str) -> Plan:
        """Parse any natural language prompt and create an execution plan."""
        print(f"🔍 Parsing prompt: {prompt}")
        
        # Check if this is an AI automation prompt
        if self._is_ai_automation_prompt(prompt):
            return self.parse_ai_automation_prompt(prompt)
        
        # Check if this is a restaurant search
        if self._is_restaurant_search(prompt):
            return self.parse_restaurant_search(prompt)
        
        # Extract intent and parameters
        intent = self._extract_intent(prompt)
        subject = self._extract_subject(prompt)
        location = self._extract_location(prompt)
        count = self._extract_count(prompt)
        timeframe = self._extract_timeframe(prompt)
        
        # Create dynamic plan based on query type
        steps = [
            Step(
                action='parse_intent',
                description=f"Parse prompt (intent = {intent}, subject = {subject}, location = {location}, count = {count})",
                parameters={'prompt': prompt},
                expected_output=f"Intent parsed: {prompt}",
                status='pending'
            ),
            Step(
                action='route_query',
                description=f"Route query to appropriate tool and fetch data for '{subject}'",
                parameters={'prompt': prompt},
                expected_output=f"Data fetched for {subject}",
                status='pending'
            ),
            Step(
                action='rank_results',
                description=f"Rank and score {count} results by relevance and quality",
                parameters={'prompt': prompt, 'count': count},
                expected_output=f"Ranked {count} results by relevance and quality",
                status='pending'
            ),
            Step(
                action='summarize_findings',
                description=f"Summarize findings and create comprehensive summary",
                parameters={'prompt': prompt, 'count': count},
                expected_output=f"Comprehensive summary of {count} research topics",
                status='pending'
            ),
            Step(
                action='display_results',
                description=f"Display results in formatted cards with source information",
                parameters={'prompt': prompt, 'format': 'cards'},
                expected_output=f"Results displayed in formatted cards",
                status='pending'
            )
        ]
        
        # Add optional steps based on intent
        if 'email' in prompt.lower() or 'draft' in prompt.lower():
            steps.append(Step(
                action='create_email_draft',
                description="Create email draft with findings",
                parameters={'recipient': 'founders@company.com'},
                expected_output="Email draft created and ready",
                status='pending'
            ))
        
        if 'save' in prompt.lower() or 'export' in prompt.lower():
            steps.append(Step(
                action='save_results',
                description="Save results to file or database",
                parameters={'format': 'json'},
                expected_output="Results saved successfully",
                status='pending'
            ))
        
        return Plan(
            goal=f"Research and analyze: {subject}",
            steps=steps,
            estimated_time="2-5 minutes",
            created_at=datetime.now().isoformat()
        )

    def parse_ai_automation_prompt(self, prompt: str) -> Plan:
        """Parse AI automation specific prompts with enhanced workflow."""
        print(f"🤖 Parsing AI automation prompt: {prompt}")
        
        # Extract components
        subject = self._extract_subject(prompt)
        count = self._extract_count(prompt)
        has_email = 'email' in prompt.lower() or 'draft' in prompt.lower()
        has_summarize = 'summarize' in prompt.lower() or 'sentence' in prompt.lower()
        
        # Create AI automation focused plan
        steps = [
            Step(
                action='ai_automation_search',
                description=f"Search for top {count} AI automation items about '{subject}'",
                parameters={'prompt': prompt, 'query': subject, 'count': count, 'focus': 'ai_automation'},
                expected_output=f"Found {count} AI automation focused results",
                status='pending'
            ),
            Step(
                action='filter_recent_content',
                description=f"Filter results to show only recent content (last 30 days)",
                parameters={'prompt': prompt, 'max_age_days': 30},
                expected_output="Results filtered for recent content",
                status='pending'
            ),
            Step(
                action='summarize_results',
                description=f"Summarize each result in ~1 sentence",
                parameters={'prompt': prompt, 'max_sentences': 1},
                expected_output=f"Each result summarized in one sentence",
                status='pending'
            )
        ]
        
        # Add email step if requested
        if has_email:
            steps.append(Step(
                action='create_email_draft',
                description="Create email draft with AI automation digest",
                parameters={'prompt': prompt, 'recipient': 'founders@company.com', 'subject': f'AI Automation Digest: {subject}'},
                expected_output="Email draft created and ready",
                status='pending'
            ))
        
        # Add display step to show results
        steps.append(Step(
            action='display_results',
            description="Display AI automation results and email draft",
            parameters={'prompt': prompt, 'format': 'cards'},
            expected_output="Results displayed in card format",
            status='pending'
        ))
        
        return Plan(
            goal=f"AI Automation Workflow: {subject}",
            steps=steps,
            estimated_time="3-7 minutes",
            created_at=datetime.now().isoformat()
        )

    def parse_restaurant_search(self, prompt: str) -> Plan:
        """Parse restaurant search prompts with location-based search."""
        print(f"🍽️ Parsing restaurant search prompt: {prompt}")
        
        # Extract components
        subject = self._extract_subject(prompt)
        location = self._extract_location(prompt)
        count = self._extract_count(prompt)
        
        # Create restaurant search plan
        steps = [
            Step(
                action='restaurant_search',
                description=f"Search for top {count} restaurants in {location or 'the specified area'}",
                parameters={'prompt': prompt, 'query': subject, 'location': location, 'count': count},
                expected_output=f"Found {count} restaurants in {location or 'the area'}",
                status='pending'
            ),
            Step(
                action='filter_by_rating',
                description=f"Filter restaurants by rating and reviews",
                parameters={'prompt': prompt, 'min_rating': 4.0},
                expected_output="Restaurants filtered by rating",
                status='pending'
            ),
            Step(
                action='display_results',
                description="Display restaurant results with ratings and details",
                parameters={'prompt': prompt, 'format': 'cards'},
                expected_output="Restaurant results displayed",
                status='pending'
            )
        ]
        
        return Plan(
            goal=f"Restaurant Search: {subject} in {location or 'specified area'}",
            steps=steps,
            estimated_time="2-4 minutes",
            created_at=datetime.now().isoformat()
        )

    def _is_ai_automation_prompt(self, prompt: str) -> bool:
        """Check if prompt is related to AI automation workflow."""
        prompt_lower = prompt.lower()
        
        # AI automation keywords
        ai_automation_keywords = [
            'ai automation', 'artificial intelligence automation', 'automation tools',
            'workflow automation', 'process automation', 'ai workflow', 'automation ai',
            'intelligent automation', 'ai tools', 'automation software', 'ai platform',
            'machine learning automation', 'robotic process automation', 'rpa',
            'business process automation', 'ai powered automation', 'smart automation'
        ]
        
        # Check for AI automation focus
        has_ai_focus = any(keyword in prompt_lower for keyword in ai_automation_keywords)
        
        # Check for workflow indicators (only if AI focus is present)
        workflow_indicators = [
            'compile', 'summarize', 'sentence', 'email draft',
            'founders@company.com', 'daily digest', 'morning', 'every morning'
        ]
        
        has_workflow = any(indicator in prompt_lower for indicator in workflow_indicators)
        
        # Must have BOTH AI focus AND workflow indicators to be considered AI automation
        return has_ai_focus and has_workflow

    def _is_restaurant_search(self, prompt: str) -> bool:
        """Check if prompt is related to restaurant search."""
        prompt_lower = prompt.lower()
        restaurant_keywords = [
            'restaurant', 'restaurants', 'food', 'dining', 'eat', 'lunch', 'dinner',
            'breakfast', 'brunch', 'cafe', 'bistro', 'grill', 'pizza', 'sushi',
            'italian', 'chinese', 'mexican', 'indian', 'thai', 'japanese', 'american'
        ]
        return any(keyword in prompt_lower for keyword in restaurant_keywords)

    def _restaurant_search(self, parameters: Dict[str, Any]) -> str:
        """Execute restaurant search using Google Places API."""
        prompt = parameters.get('prompt', '')
        location = parameters.get('location', '')
        count = parameters.get('count', 5)
        
        try:
            # Use Google Places API for restaurant search
            search_query = f"restaurants in {location}" if location else "restaurants"
            results = self.search_system.search_places(search_query, count, 'restaurant')
            
            # Store results for display
            self._current_results = results
            
            return f"Found {results.get('count', 0)} restaurants in {location or 'the area'}"
        except Exception as e:
            return f"Restaurant search failed: {str(e)}"

    def _filter_by_rating(self, parameters: Dict[str, Any]) -> str:
        """Filter restaurants by rating."""
        min_rating = parameters.get('min_rating', 4.0)
        
        if self._current_results and 'results' in self._current_results:
            # Filter results by rating
            rated_results = []
            for result in self._current_results['results']:
                rating = result.get('rating', 0)
                if rating >= min_rating:
                    rated_results.append(result)
            
            # Update stored results with filtered list
            self._current_results['results'] = rated_results
            self._current_results['count'] = len(rated_results)
            
            return f"Filtered to {len(rated_results)} restaurants with rating >= {min_rating}"
        
        return "No results to filter"

    def _ai_automation_search(self, parameters: Dict[str, Any]) -> str:
        """Execute AI automation focused search."""
        # Extract query from the prompt if not directly provided
        prompt = parameters.get('prompt', '')
        if not prompt:
            prompt = "AI automation"
        
        # Extract count from prompt or use default
        count = 5
        if 'top 5' in prompt.lower():
            count = 5
        elif 'top 10' in prompt.lower():
            count = 10
        
        try:
            results = self.search_system.get_ai_automation_focus_results(prompt, count)
            
            # Store results for display
            self._current_results = results
            
            return f"Found {results.get('count', 0)} AI automation focused results for '{prompt}'"
        except Exception as e:
            return f"AI automation search failed: {str(e)}"

    def _filter_recent_content(self, parameters: Dict[str, Any]) -> str:
        """Filter results to show only recent content."""
        # Extract max_age_days from parameters or use default
        max_age_days = parameters.get('max_age_days', 30)
        
        if self._current_results and 'results' in self._current_results:
            # Filter results for recent content
            recent_results = []
            for result in self._current_results['results']:
                # Check if result has recent date
                date_str = result.get('date', '')
                if date_str:
                    try:
                        from datetime import datetime
                        result_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        days_old = (datetime.now() - result_date).days
                        if days_old <= max_age_days:
                            recent_results.append(result)
                    except:
                        # If date parsing fails, include it
                        recent_results.append(result)
                else:
                    # If no date, include it
                    recent_results.append(result)
            
            # Update stored results with filtered list
            self._current_results['results'] = recent_results
            self._current_results['count'] = len(recent_results)
            self._current_results['filtered_for_recent'] = True
            
            return f"Content filtered to show only {len(recent_results)} items from the last {max_age_days} days"
        
        return f"Content filtered to show only items from the last {max_age_days} days"

    def _summarize_results(self, parameters: Dict[str, Any]) -> str:
        """Summarize results in specified number of sentences."""
        # Extract max_sentences from parameters or use default
        max_sentences = parameters.get('max_sentences', 1)
        
        if self._current_results and 'results' in self._current_results:
            # Summarize each result
            for result in self._current_results['results']:
                snippet = result.get('snippet', '')
                if snippet:
                    summary = self.search_system.summarize_content(snippet, max_sentences)
                    result['summarized_snippet'] = summary
            
            self._current_results['summarized'] = True
            return f"Results summarized in {max_sentences} sentence(s) each"
        
        return f"Results summarized in {max_sentences} sentence(s) each"

    def _create_email_draft(self, parameters: Dict[str, Any]) -> str:
        """Create email draft."""
        # Extract recipient and subject from parameters or use defaults
        recipient = parameters.get('recipient', 'founders@company.com')
        subject = parameters.get('subject', 'AI Automation Digest')
        
        if self._current_results and 'results' in self._current_results:
            # Create email draft with actual results
            results = self._current_results['results']
            
            # Create a simple email draft since the search system method might not work
            email_content = f"""
Subject: {subject}
To: {recipient}

AI Automation Digest

Here are the top AI automation findings:

"""
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No Title')
                snippet = result.get('snippet', result.get('summary', 'No summary available'))
                url = result.get('url', result.get('link', 'No URL'))
                
                email_content += f"""
{i}. {title}
   Summary: {snippet}
   Source: {url}

"""
            
            email_content += f"""
Total Results: {len(results)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Best regards,
AI Automation System
"""
            
            # Store email draft for display
            self._current_results['email_draft'] = email_content
            self._current_results['email_recipient'] = recipient
            self._current_results['email_subject'] = subject
            
            return f"Email draft created for {recipient} with {len(results)} results"
        
        return f"Email draft created for {recipient} with subject: {subject}"

    def _parse_intent(self, parameters: Dict[str, Any]) -> str:
        """Parse intent from parameters."""
        prompt = parameters.get('prompt', '')
        return self._extract_intent(prompt)

    def _route_query(self, parameters: Dict[str, Any]) -> str:
        """Route query to appropriate search method."""
        prompt = parameters.get('prompt', '')
        return f"Query routed for: {prompt}"

    def _rank_results(self, parameters: Dict[str, Any]) -> str:
        """Rank results by relevance."""
        count = parameters.get('count', 5)
        return f"Ranked {count} results by relevance"

    def _summarize_findings(self, parameters: Dict[str, Any]) -> str:
        """Summarize findings."""
        count = parameters.get('count', 5)
        return f"Summarized {count} findings"



    def _save_results(self, parameters: Dict[str, Any]) -> str:
        """Save results."""
        format_type = parameters.get('format', 'json')
        return f"Results saved in {format_type} format"
    
    def _setup_actions(self):
        """Set up available actions after all methods are defined."""
        self.available_actions = {
            'parse_intent': self._parse_intent,
            'route_query': self._route_query,
            'rank_results': self._rank_results,
            'summarize_findings': self._summarize_findings,
            'create_email_draft': self._create_email_draft,
            'save_results': self._save_results,
            'display_results': self._display_results,
            'ai_automation_search': self._ai_automation_search,
            'filter_recent_content': self._filter_recent_content,
            'summarize_results': self._summarize_results,
            'restaurant_search': self._restaurant_search,
            'filter_by_rating': self._filter_by_rating
        }
    
    def _display_results(self, parameters: Dict[str, Any]) -> str:
        """Display results."""
        format_type = parameters.get('format', 'cards')
        
        # Check if this is an AI automation workflow with stored results
        if hasattr(self, '_current_results') and self._current_results:
            # Check if we have email draft (indicates AI automation workflow)
            email_draft = self._current_results.get('email_draft', '')
            
            if email_draft:  # This is an AI automation workflow
                # Format the stored results for display
                results = self._current_results.get('results', [])
                
                if format_type == 'cards':
                    # Create HTML cards for the results
                    html_output = '<div class="results-container">'
                    
                    # Show search results
                    if results:
                        html_output += '<h3>🔍 AI Automation Search Results</h3>'
                        for i, result in enumerate(results, 1):
                            html_output += f'''
                            <div class="result-card">
                                <h4>{i}. {result.get('title', 'No Title')}</h4>
                                <div class="result-content">
                                    <p><strong>Summary:</strong> {result.get('summarized_snippet', result.get('snippet', 'No summary available'))}</p>
                                    <p><strong>Source:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('displayLink', 'Unknown Source')}</a></p>
                                    <p><strong>Score:</strong> {result.get('score', 'N/A')}</p>
                                </div>
                            </div>
                            '''
                    
                    # Show email draft
                    html_output += '<h3>📧 Email Draft</h3>'
                    html_output += f'<div class="email-draft" style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; white-space: pre-wrap; font-family: monospace;">{email_draft}</div>'
                    
                    html_output += '</div>'
                    return html_output
        
        # Fall back to default display method
        return f"Results displayed in {format_type} format"
    
    def execute_plan(self, plan: Plan) -> bool:
        """Execute a plan step by step."""
        print(f"🚀 Executing plan: {plan.goal}")
        
        success = True
        for i, step in enumerate(plan.steps):
            print(f"--- Step {i+1}/{len(plan.steps)} ---")
            print(f"🎯 Action: {step.action}")
            
            try:
                if step.action in self.available_actions:
                    # Pass the entire parameters dictionary, not just the prompt
                    result = self.available_actions[step.action](step.parameters)
                    step.result = result
                    step.status = "completed"
                    print(f"✅ Success: {result}")
                else:
                    step.result = f"Unknown action: {step.action}"
                    step.status = "failed"
                    success = False
                    print(f"❌ Failed: {step.result}")
            except Exception as e:
                step.result = f"Error: {str(e)}"
                step.status = "failed"
                success = False
                print(f"❌ Error: {step.result}")
        
        plan.status = "completed" if success else "completed_with_errors"
        return success
    
    def _extract_intent(self, prompt: str) -> str:
        """Extract the intent from the prompt."""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['research', 'analyze', 'study', 'investigate']):
            return 'research'
        elif any(word in prompt_lower for word in ['compare', 'rank', 'top', 'best']):
            return 'compare_rank'
        elif any(word in prompt_lower for word in ['summarize', 'summary', 'overview']):
            return 'summarize'
        elif any(word in prompt_lower for word in ['find', 'search', 'locate']):
            return 'search'
        else:
            return 'general'
    
    def _extract_subject(self, prompt: str) -> str:
        """Extract the main subject from the prompt."""
        # Preserve the full query context for better intent detection
        # Don't truncate - let the search system handle the full context
        return prompt.strip()
    
    def _extract_location(self, prompt: str) -> str:
        """Extract location from the prompt."""
        location_keywords = ['in', 'near', 'at', 'around']
        words = prompt.split()
        
        # Look for location patterns
        for i, word in enumerate(words):
            if word.lower() in location_keywords and i + 1 < len(words):
                # Take everything after the location keyword
                location = ' '.join(words[i+1:])
                # Clean up any trailing punctuation or extra words
                location = re.sub(r'[^\w\s,]', '', location).strip()
                return location
        
        # If no explicit location keyword, look for common city patterns
        city_patterns = [
            'new york', 'san francisco', 'los angeles', 'chicago', 'miami', 'boston',
            'seattle', 'denver', 'austin', 'dallas', 'houston', 'phoenix', 'atlanta',
            'bay area', 'silicon valley', 'manhattan', 'brooklyn', 'queens', 'bronx'
        ]
        
        prompt_lower = prompt.lower()
        for city in city_patterns:
            if city in prompt_lower:
                return city.title()
        
        return 'San Francisco, CA'  # Default location
    
    def _extract_count(self, prompt: str) -> int:
        """Extract count from the prompt."""
        import re
        numbers = re.findall(r'\d+', prompt)
        if numbers:
            return min(int(numbers[0]), 20)  # Cap at 20
        return 10  # Default count
    
    def _extract_timeframe(self, prompt: str) -> str:
        """Extract timeframe from the prompt."""
        timeframe_keywords = ['today', 'yesterday', 'this week', 'this month', 'this year', '2024', '2025']
        prompt_lower = prompt.lower()
        
        for keyword in timeframe_keywords:
            if keyword in prompt_lower:
                return keyword
        
        return 'recent'
    
    def _parse_intent(self, prompt: str) -> str:
        """Parse the intent from the prompt."""
        intent = self._extract_intent(prompt)
        subject = self._extract_subject(prompt)
        location = self._extract_location(prompt)
        count = self._extract_count(prompt)
        
        result = f"Intent parsed: {prompt} (intent={intent}, subject={subject}, location={location}, count={count})"
        print(f"✅ {result}")
        return result
    
    def _route_query(self, prompt: str) -> str:
        """Route the query to appropriate tools and fetch data."""
        try:
            # Extract query parameters
            intent = self._extract_intent(prompt)
            subject = self._extract_subject(prompt)
            location = self._extract_location(prompt)
            count = self._extract_count(prompt)
            
            print(f"🌐 Routing query: '{subject}' in {location}, count: {count}")
            
            # Use the enhanced search system to get real results
            results = self.search_system.unified_search(subject, location, count)
            
            # Store results for later use
            self._current_results = results
            
            return f"Data fetched from {results.get('source', 'unknown')}: {results.get('count', 0)} results"
            
        except Exception as e:
            print(f"❌ Query routing error: {e}")
            return f"Error routing query: {str(e)}"
    
    def _rank_results(self, prompt: str) -> str:
        """Rank and score the results by relevance and quality."""
        if not self._current_results:
            return "No results to rank"
        
        results = self._current_results.get('results', [])
        if not results:
            return "No results to rank"
        
        # Score and rank results
        scored_results = []
        for i, result in enumerate(results):
            score = self._calculate_result_score(result, i)
            result['score'] = score
            scored_results.append(result)
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Update current results
        self._current_results['results'] = scored_results
        self._current_results['ranked'] = True
        
        result = f"Ranked {len(scored_results)} results by relevance and quality"
        print(f"✅ {result}")
        return result
    
    def _calculate_result_score(self, result: Dict[str, Any], position: int) -> float:
        """Calculate a relevance score for a result."""
        score = 0.0
        
        # Base score from position (earlier results get higher scores)
        score += max(0, 10 - position)
        
        # Rating score (if available)
        if result.get('rating'):
            score += result['rating'] * 2
        
        # Review count score (if available)
        if result.get('review_count'):
            score += min(5, result['review_count'] / 100)
        
        # Source credibility score
        source = result.get('source', '')
        if 'yelp' in source or 'google' in source:
            score += 3
        elif 'news' in source:
            score += 2
        elif 'wikipedia' in source:
            score += 4
        
        # Content quality score
        if result.get('title'):
            score += 1
        if result.get('snippet'):
            score += 1
        
        return round(score, 2)
    
    def _summarize_findings(self, prompt: str) -> str:
        """Summarize the findings in a concise format."""
        if not self._current_results:
            return "No results to summarize"
        
        results = self._current_results.get('results', [])
        if not results:
            return "No results to summarize"
        
        # Create summary
        summary = f"Found {len(results)} results for '{self._current_results.get('query_used', 'query')}'\n\n"
        
        for i, result in enumerate(results[:5]):  # Top 5 results
            if 'name' in result:
                summary += f"{i+1}. {result['name']}"
            elif 'title' in result:
                summary += f"{i+1}. {result['title']}"
            else:
                summary += f"{i+1}. Result {i+1}"
            
            if 'rating' in result and result['rating']:
                summary += f" (⭐ {result['rating']})"
            
            if 'score' in result:
                summary += f" [Score: {result['score']}]"
            
            summary += "\n"
        
        result = f"Summary of {len(results)} findings"
        print(f"✅ {result}")
        return result
    

    
    def _save_results(self, parameters: Dict[str, Any]) -> str:
        """Save the results to a file."""
        if not self._current_results:
            return "No results to save"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self._current_results, f, indent=2)
            
            result = f"Results saved to {filename}"
            print(f"✅ {result}")
            return result
        except Exception as e:
            result = f"Error saving results: {str(e)}"
            print(f"❌ {result}")
            return result
    
    def _display_results(self, parameters: Dict[str, Any]) -> str:
        """Display the results with enhanced presentation and quality metrics."""
        if not self._current_results:
            return "No results to display"
        
        results = self._current_results.get('results', [])
        source = self._current_results.get('source', 'unknown')
        query = self._current_results.get('query_used', 'query')
        normalized_query = self._current_results.get('normalized_query', query)
        intent = self._current_results.get('intent', 'unknown')
        count = self._current_results.get('count', 0)
        timestamp = self._current_results.get('timestamp', 'unknown')
        quality_metrics = self._current_results.get('quality_metrics', {})
        config = self._current_results.get('config', {})
        
        print(f"🔍 Displaying {len(results)} results from {source}")
        print(f"🔍 Query: {query}")
        print(f"🔍 Intent: {intent}")
        
        # Enhanced header with quality information
        header = f"""
        <div class="results-header">
            <h2>🔍 Research Results</h2>
            <div class="query-info">
                <div class="info-item"><strong>Query:</strong> {query}</div>
                <div class="info-item"><strong>Intent:</strong> {intent}</div>
                <div class="info-item"><strong>Source:</strong> {source}</div>
                <div class="info-item"><strong>Results:</strong> {count}</div>
                <div class="info-item"><strong>Timestamp:</strong> {timestamp}</div>
            </div>
        """
        
        # Quality metrics section
        if quality_metrics:
            header += f"""
            <div class="quality-metrics">
                <h3>📊 Quality Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <span class="metric-label">Relevance Filtered:</span>
                        <span class="metric-value">{quality_metrics.get('relevance_filtered', 0)} results</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Duplicates Removed:</span>
                        <span class="metric-value">{quality_metrics.get('duplicates_removed', 0)} results</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Source Diversity:</span>
                        <span class="metric-value">{quality_metrics.get('source_diversity_applied', 0)} results</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Score Range:</span>
                        <span class="metric-value">{quality_metrics.get('final_score_range', 'N/A')}</span>
                    </div>
                </div>
            </div>
            """
        
        # Configuration summary
        if config:
            header += f"""
            <div class="search-config">
                <h3>⚙️ Search Configuration</h3>
                <div class="config-grid">
                    <div class="config-item">
                        <span class="config-label">Min Relevance Score:</span>
                        <span class="config-value">{config.get('min_relevance_score', 'N/A')}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Max Domain Repeats:</span>
                        <span class="config-value">{config.get('max_domain_repeats', 'N/A')}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Text Relevance Weight:</span>
                        <span class="config-value">{config.get('text_relevance_weight', 'N/A')}</span>
                    </div>
                    <div class="config-item">
                        <span class="config-label">Authority Weight:</span>
                        <span class="config-value">{config.get('authority_weight', 'N/A')}</span>
                    </div>
                </div>
            </div>
            """
        
        header += "</div>"
        
        # Format results based on source type
        if 'yelp' in source or 'google_places' in source:
            formatted_results = self._format_business_results_enhanced(results)
        else:
            formatted_results = self._format_web_results_enhanced(results)
        
        final_html = header + formatted_results
        print(f"🔍 Generated HTML length: {len(final_html)} characters")
        print(f"🔍 HTML preview: {final_html[:200]}...")
        
        result = f"Results displayed with enhanced presentation and quality metrics"
        print(f"✅ {result}")
        return final_html
    
    def _format_business_results_enhanced(self, results: List[Dict]) -> str:
        """Format business results with enhanced presentation."""
        formatted = "<div class='results-section'>\n"
        formatted += "<h3>🏪 Business Results</h3>\n"
        
        for i, result in enumerate(results):
            formatted += f"""
            <div class='result-card'>
                <h4>{i+1}. {result.get('title', result.get('name', 'Business'))}</h4>
                <div class='score-info'>
                    <span class='metric-label'>Score:</span> <span class='metric-value'>{result.get('score', 'N/A')}</span>
                </div>
                <div class='relevance-info'>
                    <span class='metric-label'>Relevance:</span> <span class='metric-value'>{result.get('relevance_reason', 'N/A')}</span>
                </div>
                <div class='rating-info'>
                    <span class='metric-label'>Rating:</span> <span class='metric-value'>{result.get('rating', 'N/A')}</span>
                </div>
                <div class='review-count-info'>
                    <span class='metric-label'>Reviews:</span> <span class='metric-value'>{result.get('review_count', 'N/A')}</span>
                </div>
                <div class='price-info'>
                    <span class='metric-label'>Price:</span> <span class='metric-value'>{result.get('price', 'N/A')}</span>
                </div>
                <div class='address-info'>
                    <span class='metric-label'>Address:</span> <span class='metric-value'>{result.get('address', 'N/A')}</span>
                </div>
                <div class='phone-info'>
                    <span class='metric-label'>Phone:</span> <span class='metric-value'>{result.get('phone', 'N/A')}</span>
                </div>
                <div class='categories-info'>
                    <span class='metric-label'>Categories:</span> <span class='metric-value'>{', '.join(result.get('categories', []))}</span>
                </div>
                <div class='tags-info'>
                    <span class='metric-label'>Tags:</span> <span class='metric-value'>{', '.join(result.get('tags', []))}</span>
                </div>
                <div class='url-info'>
                    <span class='metric-label'>Link:</span> <a href='{result.get('url', '#')}' target='_blank'>{result.get('url', 'N/A')}</a>
                </div>
                <div class='source-info'>
                    <span class='metric-label'>Source:</span> <span class='metric-value'>{result.get('source', 'unknown')}</span>
                </div>
                <div class='fetched-info'>
                    <span class='metric-label'>Fetched:</span> <span class='metric-value'>{result.get('fetched_at', 'unknown')}</span>
                </div>
            </div>
            """
        
        formatted += "</div>\n"
        return formatted
    
    def _format_web_results_enhanced(self, results: List[Dict]) -> str:
        """Format web search results with enhanced presentation."""
        formatted = "<div class='results-section'>\n"
        formatted += "<h3>🌐 Web Search Results</h3>\n"
        
        for i, result in enumerate(results):
            formatted += f"""
            <div class='result-card'>
                <h4>{i+1}. {result.get('title', 'Result')}</h4>
                <div class='score-info'>
                    <span class='metric-label'>Score:</span> <span class='metric-value'>{result.get('score', 'N/A')}</span>
                </div>
                <div class='relevance-info'>
                    <span class='metric-label'>Relevance:</span> <span class='metric-value'>{result.get('relevance_reason', 'N/A')}</span>
                </div>
                <div class='snippet-info'>
                    <span class='metric-label'>Summary:</span> <p>{result.get('snippet', 'No summary available')}</p>
                </div>
                <div class='url-info'>
                    <span class='metric-label'>Link:</span> <a href='{result.get('url', '#')}' target='_blank'>{result.get('url', 'N/A')}</a>
                </div>
                <div class='display-link-info'>
                    <span class='metric-label'>Source:</span> <a href='{result.get('display_link', '#')}' target='_blank'>{result.get('display_link', 'N/A')}</a>
                </div>
                <div class='tags-info'>
                    <span class='metric-label'>Tags:</span> <span class='metric-value'>{', '.join(result.get('tags', []))}</span>
                </div>
                <div class='fetched-info'>
                    <span class='metric-label'>Fetched:</span> <span class='metric-value'>{result.get('fetched_at', 'unknown')}</span>
                </div>
            </div>
            """
        
        formatted += "</div>\n"
        return formatted
    
    def _format_business_results(self, results: List[Dict]) -> str:
        """Format business results for display."""
        formatted = "# Research Results\n\n"
        
        for i, result in enumerate(results):
            formatted += f"## {i+1}. {result.get('name', 'Business')}\n"
            
            if 'rating' in result and result['rating']:
                formatted += f"⭐ **Rating:** {result['rating']}\n"
            
            if 'review_count' in result and result['review_count']:
                formatted += f"📊 **Reviews:** {result['review_count']}\n"
            
            if 'price' in result and result['price']:
                formatted += f"💰 **Price:** {result['price']}\n"
            
            if 'address' in result and result['address']:
                formatted += f"📍 **Address:** {result['address']}\n"
            
            if 'phone' in result and result['phone']:
                formatted += f"📞 **Phone:** {result['phone']}\n"
            
            if 'categories' in result and result['categories']:
                formatted += f"🏷️ **Categories:** {', '.join(result['categories'])}\n"
            
            if 'url' in result and result['url']:
                formatted += f"🔗 **Link:** {result['url']}\n"
            
            formatted += "\n---\n\n"
        
        return formatted
    
    def _format_web_results(self, results: List[Dict]) -> str:
        """Format web search results for display."""
        formatted = "# Research Results\n\n"
        
        for i, result in enumerate(results):
            formatted += f"## {i+1}. {result.get('title', 'Result')}\n"
            
            if 'snippet' in result and result['snippet']:
                formatted += f"📝 **Summary:** {result['snippet']}\n"
            
            if 'url' in result and result['url']:
                formatted += f"🔗 **Link:** {result['url']}\n"
            
            if 'display_link' in result and result['display_link']:
                formatted += f"🌐 **Source:** {result['display_link']}\n"
            
            if 'score' in result:
                formatted += f"📊 **Score:** {result['score']}\n"
            
            formatted += "\n---\n\n"
        
        return formatted
    
    def generate_dynamic_examples(self) -> List[Dict[str, str]]:
        """Generate dynamic examples based on available actions."""
        return [
            {
                "title": "Local Business Research",
                "prompt": "Find top 5 coffee shops in San Francisco with ratings and reviews",
                "description": "Local business search using real APIs with relevance filtering",
                "category": "local_business"
            },
            {
                "title": "Tutorial Search",
                "prompt": "Find React tutorial 2025 with step-by-step guides",
                "description": "Tutorial search with intent-aware filtering",
                "category": "tutorial_search"
            },
            {
                "title": "News Research",
                "prompt": "Research latest AI developments in 2025",
                "description": "News search with freshness and authority scoring",
                "category": "news_research"
            },
            {
                "title": "Competitive Analysis",
                "prompt": "Compare top 10 restaurants in New York City",
                "description": "Business comparison with source diversity",
                "category": "competitive_analysis"
            },
            {
                "title": "Technical Documentation",
                "prompt": "Find Python machine learning tutorials with code examples",
                "description": "Technical search with domain authority scoring",
                "category": "technical_search"
            }
        ]
    
    def generate_contextual_examples(self, user_input: str = "") -> List[Dict[str, str]]:
        """Generate contextual examples based on user input."""
        if not user_input:
            return self.generate_dynamic_examples()
        
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['restaurant', 'food', 'cafe', 'shop']):
            return [
                {
                    "title": "Restaurant Research",
                    "prompt": f"Find top 5 {user_input} in San Francisco with ratings",
                    "description": "Local restaurant search with real data",
                    "category": "restaurant_research"
                }
            ]
        elif any(word in user_lower for word in ['tech', 'startup', 'company']):
            return [
                {
                    "title": "Tech Company Research",
                    "prompt": f"Research {user_input} companies and their funding",
                    "description": "Technology company intelligence",
                    "category": "tech_research"
                }
            ]
        else:
            return [
                {
                    "title": "General Research",
                    "prompt": f"Research {user_input} and provide comprehensive analysis",
                    "description": "General information search",
                    "category": "general_research"
                }
            ]

# Initialize the Flow system
flow_system = FlowSystem()

@app.route('/')
def index():
    """Main page showing the Flow system interface."""
    # Add cache-busting parameter to force template reload
    return render_template('index.html', cache_buster=datetime.now().timestamp())

@app.route('/api/parse', methods=['POST'])
def parse_prompt():
    """Parse a natural language prompt into a plan."""
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Parse the prompt into a plan
    plan = flow_system.parse_prompt(prompt)
    
    # Convert to JSON-serializable format
    plan_dict = asdict(plan)
    plan_dict['steps'] = [asdict(step) for step in plan.steps]
    
    return jsonify({
        'plan': plan_dict,
        'message': 'Plan generated successfully'
    })

@app.route('/api/execute', methods=['POST'])
def execute_plan():
    """Execute a plan step by step."""
    data = request.get_json()
    plan_data = data.get('plan', {})
    
    if not plan_data:
        return jsonify({'error': 'No plan provided'}), 400
    
    # Reconstruct the plan object
    steps = [Step(**step_data) for step_data in plan_data['steps']]
    plan = Plan(
        goal=plan_data['goal'],
        steps=steps,
        estimated_time=plan_data['estimated_time'],
        created_at=plan_data['created_at']
    )
    
    # Execute the plan
    success = flow_system.execute_plan(plan)
    
    # Convert results to JSON-serializable format
    result_dict = asdict(plan)
    result_dict['steps'] = [asdict(step) for step in plan.steps]
    
    # Include the stored results if available
    response_data = {
        'result': result_dict,
        'success': success,
        'message': 'Plan executed successfully' if success else 'Plan execution completed with some failures'
    }
    
    # Add stored results for display
    if hasattr(flow_system, '_current_results') and flow_system._current_results:
        # Convert results to JSON-serializable format
        stored_results = flow_system._current_results.copy()
        
        # Clean up any non-serializable objects
        if 'results' in stored_results:
            for result in stored_results['results']:
                # Ensure all values are JSON-serializable
                for key, value in result.items():
                    if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                        result[key] = str(value)
        
        response_data['stored_results'] = stored_results
    
    return jsonify(response_data)

@app.route('/api/examples')
def get_examples():
    """Get dynamic example prompts based on available actions."""
    examples = [
        {
            "title": "AI Automation Daily Digest",
            "prompt": "Compile the top 5 items about AI automation, summarize each in ~1 sentence, and prepare an email draft to founders@company.com",
            "description": "Complete AI automation workflow with summarization and email generation",
            "category": "ai_automation"
        },
        {
            "title": "AI Automation Research",
            "prompt": "Find the latest AI automation tools and trends from the past month",
            "description": "Focused AI automation search with recent content filtering",
            "category": "ai_automation"
        },
        {
            "title": "Local Business Research",
            "prompt": "Find top 5 coffee shops in San Francisco with ratings and reviews",
            "description": "Local business search using real APIs",
            "category": "local_business"
        },
        {
            "title": "Web Information Search",
            "prompt": "Research artificial intelligence trends in 2025",
            "description": "General web search using Google Custom Search",
            "category": "web_search"
        },
        {
            "title": "Competitive Analysis",
            "prompt": "Compare top 10 restaurants in New York City",
            "description": "Business comparison and ranking",
            "category": "competitive_analysis"
        }
    ]
    
    # Add dynamic examples based on available actions
    dynamic_examples = flow_system.generate_dynamic_examples()
    examples.extend(dynamic_examples)
    
    return jsonify(examples)

@app.route('/api/examples/contextual', methods=['POST'])
def get_contextual_examples():
    """Get contextual examples based on user input."""
    data = request.get_json()
    user_input = data.get('input', '')
    
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    
    # Generate contextual examples
    contextual_examples = flow_system.generate_contextual_examples(user_input)
    
    return jsonify(contextual_examples)

@app.route('/api/config', methods=['GET'])
def get_search_config():
    """Get current search configuration."""
    config = flow_system.search_system.config
    return jsonify(asdict(config))

@app.route('/api/config', methods=['POST'])
def update_search_config():
    """Update search configuration."""
    data = request.get_json()
    
    try:
        # Update configuration
        config = flow_system.search_system.config
        
        # Update relevant fields
        if 'min_relevance_score' in data:
            config.min_relevance_score = float(data['min_relevance_score'])
        if 'max_domain_repeats' in data:
            config.max_domain_repeats = int(data['max_domain_repeats'])
        if 'max_results' in data:
            config.max_results = int(data['max_results'])
        if 'text_relevance_weight' in data:
            config.text_relevance_weight = float(data['text_relevance_weight'])
        if 'authority_weight' in data:
            config.authority_weight = float(data['authority_weight'])
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'config': asdict(config)
        })
    except Exception as e:
        return jsonify({'error': f'Failed to update configuration: {str(e)}'}), 400

@app.route('/api/ai-automation/search', methods=['POST'])
def ai_automation_search():
    """Search specifically for AI automation content."""
    data = request.get_json()
    query = data.get('query', '')
    count = data.get('count', 5)
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        # Use the new AI automation focused search
        results = flow_system.search_system.get_ai_automation_focus_results(query, count)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Found {results.get("count", 0)} AI automation focused results'
        })
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/ai-automation/email-draft', methods=['POST'])
def create_ai_automation_email():
    """Create an email draft for AI automation digest."""
    data = request.get_json()
    results = data.get('results', [])
    recipient = data.get('recipient', 'founders@company.com')
    subject = data.get('subject', 'AI Automation Digest')
    
    if not results:
        return jsonify({'error': 'No results provided'}), 400
    
    try:
        # Convert results to SearchResult objects if needed
        search_results = []
        for result in results:
            if isinstance(result, dict):
                # Create SearchResult from dict
                search_result = SearchResult(
                    title=result.get('title', ''),
                    url=result.get('url', ''),
                    source=result.get('source', 'unknown'),
                    fetched_at=datetime.now().isoformat(),
                    snippet=result.get('snippet', ''),
                    tags=result.get('tags', []),
                    rating=result.get('rating'),
                    address=result.get('address'),
                    author=result.get('author'),
                    date=result.get('date'),
                    score=result.get('score'),
                    relevance_reason=result.get('relevance_reason')
                )
                search_results.append(search_result)
            else:
                search_results.append(result)
        
        # Generate email draft
        email_content = flow_system.search_system.create_email_draft(
            search_results, recipient, subject
        )
        
        return jsonify({
            'success': True,
            'email_draft': email_content,
            'recipient': recipient,
            'subject': subject,
            'message': 'Email draft created successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to create email draft: {str(e)}'}), 500

@app.route('/api/ai-automation/daily-digest', methods=['POST'])
def generate_daily_digest():
    """Generate a complete daily AI automation digest."""
    data = request.get_json()
    query = data.get('query', 'AI automation trends')
    count = data.get('count', 5)
    recipient = data.get('recipient', 'founders@company.com')
    
    try:
        # Step 1: Search for AI automation content
        search_results = flow_system.search_system.get_ai_automation_focus_results(query, count)
        
        if not search_results or 'results' not in search_results:
            return jsonify({'error': 'No search results found'}), 404
        
        # Step 2: Create email draft
        results = search_results['results']
        search_result_objects = []
        
        for result in results:
            search_result = SearchResult(
                title=result.get('title', ''),
                url=result.get('url', ''),
                source=result.get('source', 'unknown'),
                fetched_at=datetime.now().isoformat(),
                snippet=result.get('snippet', ''),
                tags=result.get('tags', []),
                rating=result.get('rating'),
                address=result.get('address'),
                author=result.get('author'),
                date=result.get('date'),
                score=result.get('score'),
                relevance_reason=result.get('relevance_reason')
            )
            search_result_objects.append(search_result)
        
        email_draft = flow_system.search_system.create_email_draft(
            search_result_objects, recipient, f"Daily {query} Digest"
        )
        
        return jsonify({
            'success': True,
            'search_results': search_results,
            'email_draft': email_draft,
            'recipient': recipient,
            'message': f'Daily digest generated with {len(results)} items'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate daily digest: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
