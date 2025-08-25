#!/usr/bin/env python3
"""
Flow System Web Application with Enhanced Search System
A web-based demonstration of the Flow-style system that takes natural language prompts,
compiles plans, and executes steps to produce visible results using real APIs.
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
from urllib.parse import urlparse
from enhanced_search_v2 import EnhancedSearchSystemV2, SearchConfig, SearchResult

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
    """Advanced Flow System with intelligent workflow generation and execution."""
    
    def __init__(self):
        """Initialize the Flow System with enhanced search capabilities."""
        self.search_system = EnhancedSearchSystemV2()
        self._current_results = {}
        self._current_plan = None
        self._execution_history = []
        
        # Initialize available actions after all methods are defined
        self._setup_actions()
    
    def parse_prompt(self, prompt: str) -> Plan:
        """Intelligently route prompts to appropriate workflows."""
        subject = self._extract_subject(prompt)
        count = self._extract_count(prompt)
        location = self._extract_location(prompt)
        intent = self._analyze_intent(prompt)
        
        print(f"🧠 Analyzing prompt: {prompt}")
        print(f"📊 Extracted: Subject='{subject}', Count={count}, Location='{location}', Intent='{intent}'")
        
        # Route based on intent
        if intent == "ai_automation":
            return self._create_ai_automation_workflow(prompt, subject, count)
        elif intent == "business_analysis":
            return self._create_business_analysis_workflow(prompt, subject, location, count)
        else:
            # Default to AI automation workflow for other intents
            return self._create_ai_automation_workflow(prompt, subject, count)
    
    def _analyze_intent(self, prompt: str) -> str:
        """Intelligently analyze prompt intent using context and keywords."""
        prompt_lower = prompt.lower()
        
        # AI automation patterns - HIGHEST PRIORITY - MORE SPECIFIC CHECKS
        if 'ai automation' in prompt_lower:
            print(f"🔍 AI Automation detected: '{prompt}'")
            return 'ai_automation'
        
        if 'artificial intelligence' in prompt_lower:
            print(f"🔍 AI Automation detected: '{prompt}'")
            return 'ai_automation'
        
        # Check for AI automation workflow patterns
        ai_keywords = ['ai', 'artificial intelligence', 'automation', 'workflow', 'machine learning', 'ml', 'robotic', 'process', 'rpa', 'intelligent', 'smart']
        workflow_keywords = ['compile', 'summarize', 'prepare', 'create', 'generate', 'draft', 'email', 'digest', 'report', 'research', 'find', 'top']
        
        has_ai_keywords = any(ai_keyword in prompt_lower for ai_keyword in ai_keywords)
        has_workflow_keywords = any(workflow_keyword in prompt_lower for workflow_keyword in workflow_keywords)
        
        # Special check for the specific AI automation pattern
        if has_ai_keywords and has_workflow_keywords:
            print(f"🔍 AI Automation detected: '{prompt}'")
            return 'ai_automation'
        
        # Business analysis patterns - HIGHER PRIORITY for location-based queries
        business_keywords = ['business', 'restaurant', 'shop', 'cafe', 'coffee', 'pizza', 'food', 'service', 'company', 'startup', 'competitor', 'market', 'rating', 'review', 'compare', 'analysis']
        if any(keyword in prompt_lower for keyword in business_keywords):
            # If it has a location, definitely business analysis
            if self._extract_location(prompt):
                print(f"🔍 Business Analysis detected: '{prompt}'")
                return 'business_analysis'
            # If it has business-specific keywords, likely business analysis
            elif any(k in prompt_lower for k in ['coffee', 'restaurant', 'shop', 'cafe', 'rating', 'compare', 'market']):
                print(f"🔍 Business Analysis detected: '{prompt}'")
                return 'business_analysis'
        
        # Default to business analysis for location-based queries
        if self._extract_location(prompt):
            print(f"🔍 Business Analysis detected (location-based): '{prompt}'")
            return 'business_analysis'
        
        # Default to AI automation for other queries
        print(f"🔍 AI Automation detected (default): '{prompt}'")
        return 'ai_automation'
    
    def _extract_subject(self, prompt: str) -> str:
        """Extract the main subject from the prompt."""
        # Special handling for AI automation prompts
        if 'ai automation' in prompt.lower() or 'artificial intelligence' in prompt.lower():
            # Extract the specific topic after "about" or "in"
            if 'about' in prompt.lower():
                about_index = prompt.lower().find('about')
                topic_part = prompt[about_index + 6:].strip()
                # Clean up the topic - remove quotes and take first part
                topic_part = topic_part.replace("'", "").replace('"', '').split(',')[0].split('.')[0].strip()
                if topic_part and len(topic_part) > 2:
                    return topic_part
            elif 'in' in prompt.lower():
                in_index = prompt.lower().find('in')
                topic_part = prompt[in_index + 3:].strip()
                # Clean up the topic
                topic_part = topic_part.replace("'", "").replace('"', '').split(',')[0].split('.')[0].strip()
                if topic_part and len(topic_part) > 2:
                    return topic_part

            # If no specific topic found, return "AI automation"
            return "AI automation"

        # Special handling for business prompts - extract complete business type
        business_keywords = ['coffee shops', 'coffee shop', 'restaurants', 'restaurant', 'shops', 'shop', 'cafes', 'cafe', 'businesses', 'business']
        prompt_lower = prompt.lower()
        
        for business_type in business_keywords:
            if business_type in prompt_lower:
                return business_type
        
        # If no business type found, extract meaningful subject
        # Remove common words and extract meaningful subject
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'top', 'best', 'latest', 'new', 'find', 'search', 'research', 'analyze', 'compare', 'summarize', 'create', 'prepare', 'draft', 'email', 'digest', 'report', 'compile', 'items', 'each', 'sentence', 'prepare', 'draft', '5', '10', '15', '20', '25', '30', '35', '40', '45', '50']

        words = prompt.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        subject = ' '.join(filtered_words).strip()
        
        # Clean up the subject
        if subject:
            # Remove location references
            location_words = ['san francisco', 'new york', 'los angeles', 'chicago', 'miami', 'seattle', 'boston', 'austin', 'denver', 'portland']
            for loc in location_words:
                subject = subject.replace(loc, '').strip()
            
            # Remove count references
            import re
            subject = re.sub(r'\d+', '', subject).strip()
            
            # Clean up extra spaces and punctuation
            subject = re.sub(r'\s+', ' ', subject).strip()
            subject = subject.strip('.,!?')
            
            if len(subject) > 2:
                return subject
        
        return prompt.split(',')[0].strip()
    
    def _extract_count(self, prompt: str) -> int:
        """Extract the count/number from the prompt."""
        import re
        
        # Look for patterns like "top 5", "top 10", "5 items", "10 tools"
        patterns = [
            r'top\s+(\d+)',
            r'(\d+)\s+items?',
            r'(\d+)\s+tools?',
            r'(\d+)\s+papers?',
            r'(\d+)\s+results?',
            r'(\d+)\s+developments?',
            r'(\d+)\s+trends?',
            r'(\d+)\s+coffee\s+shops?',
            r'(\d+)\s+restaurants?',
            r'(\d+)\s+businesses?',
            r'(\d+)\s+shops?',
            r'(\d+)\s+cafes?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                try:
                    count = int(match.group(1))
                    if 1 <= count <= 50:  # Reasonable range
                        return count
                except ValueError:
                    continue
        
        # Look for standalone numbers that are likely counts
        standalone_numbers = re.findall(r'\b(\d+)\b', prompt)
        for num_str in standalone_numbers:
            try:
                count = int(num_str)
                if 1 <= count <= 50:  # Reasonable range
                    return count
            except ValueError:
                continue
        
        # Default count
        return 5
    
    def _extract_location(self, prompt: str) -> str:
        """Extract location from prompt using intelligent parsing."""
        import re
        
        # Look for location patterns
        location_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in San Francisco"
            r'near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "near New York"
            r'around\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "around Los Angeles"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*[A-Z]{2}',  # "San Francisco, CA"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, prompt)
            if match:
                location = match.group(1).strip()
                if len(location) > 2:  # Valid location
                    return location
        
        # Look for common city names
        common_cities = [
            'San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Miami',
            'Seattle', 'Boston', 'Austin', 'Denver', 'Portland', 'Atlanta',
            'Dallas', 'Houston', 'Phoenix', 'Philadelphia', 'San Diego'
        ]
        
        for city in common_cities:
            if city.lower() in prompt.lower():
                return city
        
        # If no location found, return None
        return None
    
    def _extract_timeframe(self, prompt: str) -> str:
        """Extract timeframe from prompt."""
        prompt_lower = prompt.lower()
        
        if 'today' in prompt_lower or 'morning' in prompt_lower:
            return 'today'
        elif 'week' in prompt_lower or 'weekly' in prompt_lower:
            return 'this week'
        elif 'month' in prompt_lower or 'monthly' in prompt_lower:
            return 'this month'
        elif 'year' in prompt_lower or '2025' in prompt_lower:
            return 'this year'
        else:
            return 'recent'
    
    def _wants_email(self, prompt: str) -> bool:
        """Detect if the user explicitly wants an email draft."""
        p = prompt.lower()
        # common ways users ask for email/digest
        triggers = [
            "email", "draft", "digest", "newsletter",
            "send to ", "compose", "mail", "outreach"
        ]
        # any explicit email address counts
        has_address = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", p) is not None
        return has_address or any(t in p for t in triggers)
    
    def _create_business_analysis_workflow(self, prompt: str, subject: str, location: str, count: int) -> Plan:
        """Create a business analysis workflow using local business APIs."""
        steps = [
            Step(
                action='business_search',
                description=f"Search for {count} {subject} businesses in {location or 'the area'}",
                parameters={'prompt': prompt, 'subject': subject, 'location': location, 'count': count},
                expected_output=f"Found {count} {subject} businesses in {location or 'the area'}",
                status='pending'
            ),
            Step(
                action='business_analysis',
                description="Analyze business ratings, reviews, and market positioning",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Business analysis completed with ratings and market insights",
                status='pending'
            ),
            Step(
                action='business_comparison',
                description="Compare businesses and identify market gaps",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Business comparison analysis completed",
                status='pending'
            ),
            Step(
                action='display_results',
                description="Display business analysis results",
                parameters={'prompt': prompt, 'format': 'business_cards'},
                expected_output="Business analysis results displayed",
                status='pending'
            )
        ]
        
        return Plan(
            goal=f"Business Analysis: {prompt}",
            steps=steps,
            estimated_time="3-4 minutes",
            created_at=datetime.now().isoformat()
        )
    
    def _create_location_analysis_workflow(self, prompt: str, subject: str, location: str, count: int) -> Plan:
        """Create a location-based analysis workflow."""
        steps = [
            Step(
                action='location_based_search',
                description=f"Search for {count} {subject} in {location}",
                parameters={'prompt': prompt, 'query': subject, 'location': location, 'count': count},
                expected_output=f"Found {count} {subject} in {location}",
                status='pending'
            ),
            Step(
                action='geographic_filter',
                description="Filter results by geographic relevance",
                parameters={'prompt': prompt, 'location': location},
                expected_output="Results filtered by geographic relevance",
                status='pending'
            ),
            Step(
                action='display_results',
                description="Display location-based results",
                parameters={'prompt': prompt, 'format': 'location_cards'},
                expected_output="Location-based results displayed",
                status='pending'
            )
        ]
        
        return Plan(
            goal=f"Location Analysis: {prompt}",
            steps=steps,
            estimated_time="2-3 minutes",
            created_at=datetime.now().isoformat()
        )
    
    def _create_ai_automation_workflow(self, prompt: str, subject: str, count: int) -> Plan:
        """Create an AI automation workflow."""
        steps = [
            Step(
                action='ai_automation_search',
                description=f"Intelligently search for {count} relevant items about '{subject}'",
                parameters={'prompt': prompt, 'query': subject, 'count': count, 'intent': 'ai_automation'},
                expected_output=f"Found {count} relevant results for {subject}",
                status='pending'
            ),
            Step(
                action='contextual_filter',
                description="Filter results based on prompt context and relevance",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Results filtered for relevance and context",
                status='pending'
            ),
            Step(
                action='filter_recent_content',
                description="Filter content to show only recent items",
                parameters={'prompt': prompt},
                expected_output="Content filtered to show only recent items",
                status='pending'
            ),
            Step(
                action='summarize_results',
                description="Summarize results in 1 sentence(s) each",
                parameters={'prompt': prompt, 'sentence_count': 1},
                expected_output="Results summarized in 1 sentence(s) each",
                status='pending'
            ),
        ]

        # ✅ add email only if the user asked
        if self._wants_email(prompt):
            steps.append(
                Step(
                action='create_email_draft',
                    description="Create email draft",
                    parameters={'recipient': 'founders@company.com', 'subject': f"AI Automation Digest: {subject}"},
                    expected_output="Email draft created",
                status='pending'
                )
            )

        steps.append(
            Step(
                action='display_results',
                description="Display research results with contextual summaries" + (" and email draft" if self._wants_email(prompt) else ""),
                parameters={'prompt': prompt, 'format': 'research_cards'},
                expected_output="Research results displayed",
                status='pending'
            )
        )
        
        return Plan(
            goal=f"AI Automation Research Workflow: {prompt}",
            steps=steps,
            estimated_time="3-5 minutes",
            created_at=datetime.now().isoformat()
        )
    
    def _create_research_workflow(self, prompt: str, subject: str, count: int) -> Plan:
        """Create a general research workflow."""
        steps = [
            Step(
                action='intelligent_search',
                description=f"Intelligently search for {count} relevant items about '{subject}'",
                parameters={'prompt': prompt, 'query': subject, 'count': count},
                expected_output=f"Found {count} relevant results for {subject}",
                status='pending'
            ),
            Step(
                action='contextual_filter',
                description="Filter results based on prompt context",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Results filtered for context relevance",
                status='pending'
            ),
            Step(
                action='adaptive_summarize',
                description="Adaptively summarize results based on prompt requirements",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Results summarized adaptively",
                status='pending'
            ),
            Step(
                action='display_results',
                description="Display research results",
                parameters={'prompt': prompt, 'format': 'research_cards'},
                expected_output="Research results displayed",
                status='pending'
            )
        ]
        
        return Plan(
            goal=f"Research Workflow: {prompt}",
            steps=steps,
            estimated_time="2-4 minutes",
            created_at=datetime.now().isoformat()
        )
    
    def _create_intelligent_workflow(self, prompt: str, subject: str, count: int, intent: str) -> Plan:
        """Create an intelligent workflow that adapts to any prompt."""
        steps = [
            Step(
                action='intelligent_search',
                description=f"Intelligently search for {count} relevant items about '{subject}'",
                parameters={'prompt': prompt, 'query': subject, 'count': count, 'intent': intent},
                expected_output=f"Found {count} relevant results for {subject}",
                status='pending'
            ),
            Step(
                action='contextual_filter',
                description="Filter results based on prompt context",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Results filtered for context relevance",
                status='pending'
            ),
            Step(
                action='adaptive_summarize',
                description="Adaptively summarize results",
                parameters={'prompt': prompt, 'context': subject},
                expected_output="Results summarized adaptively",
                status='pending'
            ),
            Step(
                action='display_results',
                description="Display intelligent results",
                parameters={'prompt': prompt, 'format': 'intelligent_cards'},
                expected_output="Intelligent results displayed",
                status='pending'
            )
        ]
        
        return Plan(
            goal=f"Intelligent Workflow: {prompt}",
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
        # AND must NOT be a restaurant search (restaurant search takes priority)
        if self._is_restaurant_search(prompt):
            return False
            
        return has_ai_focus and has_workflow

    def _is_restaurant_search(self, prompt: str) -> bool:
        """Check if prompt is related to restaurant search."""
        prompt_lower = prompt.lower()
        
        # Primary restaurant keywords
        restaurant_keywords = [
            'restaurant', 'restaurants', 'food', 'dining', 'eat', 'lunch', 'dinner',
            'breakfast', 'brunch', 'cafe', 'bistro', 'grill', 'pizza', 'sushi',
            'italian', 'chinese', 'mexican', 'indian', 'thai', 'japanese', 'american'
        ]
        
        # Check for restaurant keywords
        has_restaurant_keywords = any(keyword in prompt_lower for keyword in restaurant_keywords)
        
        # Check for location indicators (city, state, area)
        location_indicators = ['in ', 'near ', 'around ', 'at ', 'ca', 'california', 'ny', 'new york', 'tx', 'texas']
        has_location = any(indicator in prompt_lower for indicator in location_indicators)
        
        # Check for count indicators
        count_indicators = ['top ', 'best ', 'top 5', 'top 10', 'top 3']
        has_count = any(indicator in prompt_lower for indicator in count_indicators)
        
        # Consider it a restaurant search if it has restaurant keywords AND either location or count
        return has_restaurant_keywords and (has_location or has_count)


    
    def _ai_automation_search(self, parameters: Dict[str, Any]) -> str:
        """Search for AI automation focused results."""
        prompt = parameters.get('prompt', '')
        query = parameters.get('query', '')
        count = parameters.get('count', 5)
        
        print(f"🤖 AI Automation Search: {query} (count: {count})")
        
        # Use the enhanced search system for AI automation queries
        results = self.search_system.ai_automation_search(query, count)
        
        if results:
            self._current_results['results'] = results
            self._current_results['source'] = 'ai_automation_search'
            return f"Found {len(results)} AI automation focused results for '{query}'"
        else:
            return f"No AI automation results found for '{query}'"
    
    def _filter_recent_content(self, parameters: Dict[str, Any]) -> str:
        """Filter content to show only recent items."""
        prompt = parameters.get('prompt', '')
        
        if 'results' not in self._current_results:
            return "No results to filter"
        
        results = self._current_results['results']
        if not results:
            return "No results to filter"
        
        # Filter for recent content (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=30)
        
        recent_results = []
        for result in results:
            # Check if result has a date field
            if 'date' in result:
                try:
                    result_date = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
                    if result_date >= cutoff_date:
                        recent_results.append(result)
                except:
                    # If date parsing fails, include the result
                    recent_results.append(result)
                else:
                    # If no date field, include the result
                    recent_results.append(result)
        
        self._current_results['results'] = recent_results
        return f"Content filtered to show only {len(recent_results)} items from the last 30 days"
    
    def _summarize_results(self, parameters: Dict[str, Any]) -> str:
        """Summarize results in specified number of sentences."""
        prompt = parameters.get('prompt', '')
        sentence_count = parameters.get('sentence_count', 1)
        
        if 'results' not in self._current_results:
            return "No results to summarize"
        
        results = self._current_results['results']
        if not results:
            return "No results to summarize"
        
        # Summarize each result
        for result in results:
            snippet = result.get('snippet', result.get('description', ''))
            if snippet:
                # Simple sentence extraction (split by periods and take first sentence)
                sentences = snippet.split('.')
                if sentences:
                    summary = sentences[0].strip()
                    if summary:
                        result['summarized_snippet'] = summary
        
        self._current_results['summarized'] = True
        return f"Results summarized in {sentence_count} sentence(s) each"
    
    def _create_email_draft(self, parameters: Dict[str, Any]) -> str:
        """Create email draft based on parameters."""
        recipient = parameters.get('recipient', 'founders@company.com')
        subject = parameters.get('subject', 'AI Automation Digest')
        
        if 'results' not in self._current_results:
            return "No results to create email from"
        
        results = self._current_results['results']
        if not results:
            return "No results to create email from"
        
        # Create email content
        email_content = f"""
Subject: {subject}
To: {recipient}

Dear Team,

Here's your AI automation digest:

"""
        
        for i, result in enumerate(results, 1):
            title = result.get('title', result.get('name', f'Item {i}'))
            summary = result.get('summarized_snippet', result.get('snippet', 'No summary available'))
            url = result.get('url', '#')
            
            email_content += f"{i}. {title}\n"
            email_content += f"   {summary}\n"
            email_content += f"   Source: {url}\n\n"
        
        email_content += """
Best regards,
AI Automation System
"""
        
        # Store email draft and mark it as created in this execution
        self._current_results['email_draft'] = email_content
        self._current_results['email_created_in_execution'] = True
        return f"Email draft created for {recipient} with subject: {subject}"
    
    def _intelligent_search(self, parameters: Dict[str, Any]) -> str:
        """Perform intelligent search using the enhanced search system."""
        prompt = parameters.get('prompt', '')
        query = parameters.get('query', '')
        count = parameters.get('count', 5)
        
        print(f"🧠 Intelligent Search: {query} (count: {count})")
        
        # Use the unified search for intelligent results
        results = self.search_system.unified_search(query, location=None, count=count)
        
        if results:
            self._current_results['results'] = results
            self._current_results['source'] = 'intelligent_search'
            return f"Found {len(results)} intelligent results for '{query}'"
        else:
            return f"No intelligent results found for '{query}'"
    
    def _contextual_filter(self, parameters: Dict[str, Any]) -> str:
        """Filter results based on prompt context."""
        prompt = parameters.get('prompt', '')
        context = parameters.get('context', '')
        
        if 'results' not in self._current_results:
            return "No results to filter"
        
        results = self._current_results['results']
        if not results:
            return "No results to filter"
        
        # Simple contextual filtering based on keyword presence
        filtered_results = []
        context_words = context.lower().split()
        
        for result in results:
            title = result.get('title', result.get('name', '')).lower()
            snippet = result.get('snippet', result.get('description', '')).lower()
            
            # Check if context words appear in title or snippet
            relevance_score = 0
            for word in context_words:
                if word in title:
                    relevance_score += 2  # Title matches are more important
                if word in snippet:
                    relevance_score += 1
            
            if relevance_score > 0:
                result['contextual_score'] = relevance_score
                filtered_results.append(result)
        
        self._current_results['results'] = filtered_results
        return f"Results filtered for context relevance: {len(filtered_results)} items"
    
    def _adaptive_summarize(self, parameters: Dict[str, Any]) -> str:
        """Adaptively summarize results based on prompt requirements."""
        prompt = parameters.get('prompt', '')
        context = parameters.get('context', '')
        
        if 'results' not in self._current_results:
            return "No results to summarize"
        
        results = self._current_results['results']
        if not results:
            return "No results to summarize"
        
        # Adaptive summarization based on prompt context
        if 'brief' in prompt.lower() or 'quick' in prompt.lower():
            max_length = 50
        elif 'detailed' in prompt.lower() or 'comprehensive' in prompt.lower():
            max_length = 200
        else:
            max_length = 100
        
        for result in results:
            snippet = result.get('snippet', result.get('description', ''))
            if snippet:
                # Truncate to max_length
                if len(snippet) > max_length:
                    summary = snippet[:max_length].rsplit(' ', 1)[0] + '...'
                else:
                    summary = snippet
                result['adaptive_summary'] = summary
        
        self._current_results['adaptive_summarized'] = True
        return f"Results summarized adaptively (max length: {max_length} chars)"
    
    def _create_contextual_email(self, parameters: Dict[str, Any]) -> str:
        """Create contextual email draft based on prompt."""
        prompt = parameters.get('prompt', '')
        context = parameters.get('context', '')
        
        if 'results' not in self._current_results:
            return "No results to create email from"
        
        results = self._current_results['results']
        if not results:
            return "No results to create email from"
        
        # Create contextual email
        email_content = f"""
Subject: Research Summary: {context}
To: team@company.com

Hi Team,

Based on your request: "{prompt}"

Here are the key findings:

"""
        
        for i, result in enumerate(results, 1):
            title = result.get('title', result.get('name', f'Finding {i}'))
            summary = result.get('adaptive_summary', result.get('summarized_snippet', result.get('snippet', 'No summary available')))
            url = result.get('url', '#')
            
            email_content += f"{i}. {title}\n"
            email_content += f"   {summary}\n"
            email_content += f"   Source: {url}\n\n"
        
        email_content += """
Best regards,
AI Research System
"""
        
        self._current_results['contextual_email'] = email_content
        return f"Contextual email draft created for research on '{context}'"
    
    def _location_based_search(self, parameters: Dict[str, Any]) -> str:
        """Perform location-based search."""
        prompt = parameters.get('prompt', '')
        query = parameters.get('query', '')
        location = parameters.get('location', '')
        count = parameters.get('count', 5)
        
        print(f"📍 Location-based Search: {query} in {location} (count: {count})")
        
                # Use the enhanced search system for location-based queries
        results = self.search_system.unified_search(f"{query} {location}", location=location, count=count)
        
        if results:
            self._current_results['results'] = results
            self._current_results['source'] = 'location_based_search'
            self._current_results['location'] = location
            return f"Found {len(results)} location-based results for '{query}' in {location}"
        else:
            return f"No location-based results found for '{query}' in {location}"
    
    def _geographic_filter(self, parameters: Dict[str, Any]) -> str:
        """Filter results by geographic relevance."""
        prompt = parameters.get('prompt', '')
        location = parameters.get('location', '')
        
        if 'results' not in self._current_results:
            return "No results to filter geographically"
        
        results = self._current_results['results']
        if not results:
            return "No results to filter geographically"
        
        # Simple geographic filtering (in a real system, you'd use geocoding)
        filtered_results = []
        location_words = location.lower().split()
        
        for result in results:
            title = result.get('title', result.get('name', '')).lower()
            snippet = result.get('snippet', result.get('description', '')).lower()
            
            # Check if location appears in the result
            if any(loc_word in title or loc_word in snippet for loc_word in location_words):
                filtered_results.append(result)
        
        self._current_results['results'] = filtered_results
        return f"Results filtered by geographic relevance: {len(filtered_results)} items"
    
    def _business_search(self, parameters: Dict[str, Any]) -> str:
        """Search for businesses using Yelp API with fallback to Google Places."""
        prompt = parameters.get('prompt', '')
        subject = parameters.get('subject', '')
        count = parameters.get('count', 5)
        location = parameters.get('location', 'San Francisco')
        
        # DEBUG: Log exactly what we received
        print(f"🔍 DEBUG: Received parameters:")
        print(f"   prompt: '{prompt}'")
        print(f"   subject: '{subject}'")
        print(f"   count: '{count}'")
        print(f"   location: '{location}'")
        print(f"   All parameters: {parameters}")
        
        # Construct proper search query using extracted parameters
        if subject and location:
            search_query = f"{subject} in {location}"
        elif subject:
            search_query = subject
        else:
            # Fallback: extract business type from prompt
            business_types = ['coffee shops', 'coffee shop', 'restaurants', 'restaurant', 'shops', 'shop', 'cafes', 'cafe']
            for business_type in business_types:
                if business_type in prompt.lower():
                    search_query = f"{business_type} in {location}"
                    break
            else:
                search_query = prompt
        
        print(f"🏢 Business Search: {search_query} (count: {count})")
        
                # Try Yelp API first
        try:
            print(f"🌐 Trying Yelp API: {search_query}")
            payload = self.search_system._search_yelp_businesses(search_query, location, count)
            
            if payload and payload.get('results'):
                biz_list = payload['results']
                print(f"✅ Yelp API found {len(biz_list)} results")
            # Store results for later use
                self._current_results = {
                    'results': biz_list,            # <-- list of businesses
                    'query': search_query,
                    'intent': 'business_search',
                    'count': len(biz_list),
                    'source': 'yelp'
                }
                print(f"🔍 DEBUG: Stored {type(biz_list)} with {len(biz_list)} businesses")
                return f"Found {len(biz_list)} {subject} businesses in {location} via Yelp"
            else:
                print(f"⚠️ Yelp API returned no results, trying Google Places...")
                
        except Exception as e:
            print(f"❌ Yelp API error: {str(e)}, trying Google Places...")
        
        # Fallback to Google Places API
        try:
            print(f"🌐 Trying Google Places API: {search_query}")
            payload = self.search_system._search_google_places(search_query, location, count)
            
            if payload and payload.get('results'):
                biz_list = payload['results']
                print(f"✅ Google Places API found {len(biz_list)} results")
                # Store results for later use
                self._current_results = {
                    'results': biz_list,            # <-- list of businesses
                    'query': search_query,
                    'intent': 'business_search',
                    'count': len(biz_list),
                    'source': 'google_places'
                }
                print(f"🔍 DEBUG: Stored {type(biz_list)} with {len(biz_list)} businesses")
                return f"Found {len(biz_list)} {subject} businesses in {location} via Google Places"
            else:
                print(f"⚠️ Google Places API also returned no results")
            
        except Exception as e:
            print(f"❌ Google Places API error: {str(e)}")
        
        # If both APIs fail, return error
        self._current_results = {
            'results': [],
            'query': search_query,
            'intent': 'business_search',
            'count': 0,
            'source': 'none'
        }
        return f"Error: Could not find {subject} businesses in {location} via any API"
    
    def _business_analysis(self, parameters: Dict[str, Any]) -> str:
        """Analyze business results for market positioning."""
        prompt = parameters.get('prompt', '')
        context = parameters.get('context', '')
        
        if 'results' not in self._current_results:
            return "No business results to analyze"
        
        results = self._current_results['results']
        if not results:
            return "No business results to analyze"
        
        # Ensure results is a list
        if isinstance(results, str):
            return f"Cannot analyze string results: {results}"
        
        # Analyze each business
        for result in results:
            if isinstance(result, dict):
                rating = result.get('rating', 0)
                review_count = result.get('review_count', 0)
                
                # Calculate market score (rating * log(review_count + 1))
                import math
                market_score = rating * math.log(review_count + 1) if review_count > 0 else rating
                result['market_score'] = round(market_score, 2)
                
                # Add market positioning category
                if result['market_score'] >= 4.0:
                    result['positioning'] = 'Premium'
                elif result['market_score'] >= 3.0:
                    result['positioning'] = 'Premium'
                else:
                    result['positioning'] = 'Emerging'
        
        self._current_results['analyzed'] = True
        return f"Business analysis completed for {len(results)} businesses"
    
    def _business_comparison(self, parameters: Dict[str, Any]) -> str:
        """Compare businesses and identify market gaps."""
        prompt = parameters.get('prompt', '')
        context = parameters.get('context', '')
        
        if not self._current_results or 'results' not in self._current_results:
            return "No business results to compare"
        
        results = self._current_results['results']
        if not results:
            return "No business results to compare"
        
        # Ensure results is a list
        if isinstance(results, str):
            return f"Cannot compare string results: {results}"
        
        if len(results) < 2:
            return "Need at least 2 businesses for comparison"
        
        # Sort by market score for ranking
        sorted_results = sorted(results, key=lambda x: x.get('market_score', 0) if isinstance(x, dict) else 0, reverse=True)
        
        # Identify market gaps
        gaps = []
        for i in range(len(sorted_results) - 1):
            current = sorted_results[i]
            next_business = sorted_results[i + 1]
            
            if isinstance(current, dict) and isinstance(next_business, dict):
                score_diff = current.get('market_score', 0) - next_business.get('market_score', 0)
                if score_diff > 0.5:  # Significant gap
                    gaps.append(f"Gap between {current.get('name', 'Business')} and {next_business.get('name', 'Business')}: {score_diff:.2f} points")
        
        # Store comparison results
        self._current_results['comparison'] = {
            'ranked_results': sorted_results,
            'market_gaps': gaps,
            'total_businesses': len(results)
        }
        
        return f"Business comparison completed. Found {len(gaps)} significant market gaps"
    
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
    
    def _restaurant_search(self, parameters: Dict[str, Any]) -> str:
        """Search for restaurants using Google Places API."""
        prompt = parameters.get('prompt', '')
        query = parameters.get('query', '')
        location = parameters.get('location', '')
        count = parameters.get('count', 5)
        
        print(f"🍽️ Restaurant Search: {query} in {location} (count: {count})")
        
        # Use Google Places API for restaurant search
        results = self.search_system._search_google_places(query, location, count)
        
        if results:
            self._current_results['results'] = results
            self._current_results['source'] = 'google_places'
            return f"Found {len(results)} restaurants in {location or 'the area'}"
            else:
            return f"No restaurants found in {location or 'the area'}"
    
    def _filter_by_rating(self, parameters: Dict[str, Any]) -> str:
        """Filter results by rating."""
        prompt = parameters.get('prompt', '')
        min_rating = parameters.get('min_rating', 4.0)
        
        if 'results' not in self._current_results:
            return "No results to filter by rating"
        
        results = self._current_results['results']
        if not results:
            return "No results to filter by rating"
        
        # Filter by rating
        filtered_results = []
        for result in results:
            rating = result.get('rating', 0)
            if rating >= min_rating:
                filtered_results.append(result)
        
        self._current_results['results'] = filtered_results
        return f"Results filtered by rating (min: {min_rating}): {len(filtered_results)} items"
    
    def _parse_intent(self, parameters: Dict[str, Any]) -> str:
        """Parse intent from parameters."""
        prompt = parameters.get('prompt', '')
        return self._analyze_intent(prompt)
    
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
        """Register all available workflow actions."""
        self.available_actions = {
            # AI Automation actions
            'ai_automation_search': self._ai_automation_search,
            'contextual_filter': self._contextual_filter,
            'filter_recent_content': self._filter_recent_content,
            'summarize_results': self._summarize_results,
            'create_email_draft': self._create_email_draft,
            'display_results': self._display_results,
            
            # Business Analysis actions
            'business_search': self._business_search,
            'business_analysis': self._business_analysis,
            'business_comparison': self._business_comparison,
            
            # Restaurant Search actions
            'restaurant_search': self._restaurant_search,
        }
    
    def _display_results(self, parameters: Dict[str, Any]) -> str:
        """Display results."""
        format_type = parameters.get('format', 'cards')
        
        # Debug logging
        print(f"🔍 DEBUG: _display_results called with format_type: {format_type}")
        print(f"🔍 DEBUG: _current_results keys: {list(self._current_results.keys()) if self._current_results else 'None'}")
        print(f"🔍 DEBUG: _current_results content: {self._current_results}")
        
        results = self._current_results.get('results', [])
        
        # If this came from AI-automation search OR we already have an email draft, show AI cards.
        if self._current_results.get('source') == 'ai_automation_search' or self._current_results.get('email_draft'):
            html_output = '<div class="results-container">'
            if results and isinstance(results, list):
                html_output += '<h3>🤖 AI Automation Results</h3>'
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        title = result.get('title', 'Untitled')
                        url = result.get('url', '#')
                        summary = result.get('summarized_snippet', result.get('snippet', 'No summary available'))
                        score = result.get('score', 'N/A')
                        display_link = (
                            result.get('displayLink')
                            or (urlparse(url).netloc if url else '')
                            or result.get('source', 'Unknown Source')
                        )
                        html_output += f"""
                        <div class="result-card">
                            <h4>{i}. {title}</h4>
                            <div class="result-content">
                                <p><strong>Summary:</strong> {summary}</p>
                                <p><strong>Source:</strong> <a href="{url}" target="_blank">{display_link}</a></p>
                                <p><strong>Score:</strong> {score}</p>
                            </div>
                        </div>
                        """
                # Show email draft if it exists and was created in this execution
                if self._current_results.get('email_draft') and self._current_results.get('email_created_in_execution'):
                    html_output += '<h3>📧 Email Draft</h3>'
                    html_output += f'<div class="email-draft" style="background:#f8f9fa;padding:20px;border-radius:10px;margin:20px 0;white-space:pre-wrap;font-family:monospace;">{self._current_results["email_draft"]}</div>'
                html_output += '</div>'
                return html_output
            else:
                # No results but we have an email draft
                if self._current_results.get('email_draft'):
                    html_output += '<h3>📧 Email Draft</h3>'
                    html_output += f'<div class="email-draft" style="background:#f8f9fa;padding:20px;border-radius:10px;margin:20px 0;white-space:pre-wrap;font-family:monospace;">{self._current_results["email_draft"]}</div>'
                    html_output += '</div>'
                    return html_output
                html_output += '</div>'
                return html_output
        
        # Check if this is a business analysis workflow
        elif self._current_results.get('analyzed') and self._current_results.get('comparison'):
            # Format business analysis results
            results = self._current_results.get('results', [])
            comparison = self._current_results.get('comparison', {})
            
            if format_type == 'business_cards' and isinstance(results, list):
                html_output = '<div class="results-container">'
                html_output += '<h3>🏢 Business Analysis Results</h3>'
                
                # Show market gaps
                if comparison.get('market_gaps'):
                    html_output += '<h4>📊 Market Gaps Identified</h4>'
                    html_output += '<div class="market-gaps">'
                    for gap in comparison['market_gaps']:
                        html_output += f'<p class="gap-item">🔍 {gap}</p>'
                    html_output += '</div>'
                
                # Show ranked businesses
                html_output += '<h4>🏆 Ranked Businesses</h4>'
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        html_output += f'''
                        <div class="result-card business-card">
                            <h4>{i}. {result.get('name', result.get('title', 'No Name'))}</h4>
                            <div class="result-content">
                                <p><strong>Rating:</strong> {result.get('rating', 'N/A')} ⭐ ({result.get('review_count', 0)} reviews)</p>
                                <p><strong>Market Score:</strong> {result.get('market_score', 'N/A')}</p>
                                <p><strong>Positioning:</strong> {result.get('positioning', 'N/A')}</p>
                                <p><strong>Address:</strong> {result.get('address', 'Address not available')}</p>
                                <p><strong>Phone:</strong> {result.get('phone', 'Phone not available')}</p>
                                <p><strong>Source:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('displayLink', 'Unknown Source')}</a></p>
                    </div>
                    </div>
                        '''
                
                html_output += '</div>'
                return html_output
        
        # Check if this is a business search workflow (even without analysis)
        elif self._current_results.get('intent') == 'business_search' and self._current_results.get('results'):
        results = self._current_results.get('results', [])
            
            if format_type == 'business_cards' and isinstance(results, list):
                html_output = '<div class="results-container">'
                html_output += '<h3>🏢 Business Search Results</h3>'
                
                # Show businesses found
                html_output += '<h4>📍 Businesses Found</h4>'
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        html_output += f'''
                        <div class="result-card business-card">
                            <h4>{i}. {result.get('name', result.get('title', 'No Name'))}</h4>
                            <div class="result-content">
                                <p><strong>Rating:</strong> {result.get('rating', 'N/A')} ⭐ ({result.get('review_count', 0)} reviews)</p>
                                <p><strong>Address:</strong> {result.get('address', 'Address not available')}</p>
                                <p><strong>Phone:</strong> {result.get('phone', 'Phone not available')}</p>
                                <p><strong>Categories:</strong> {', '.join(result.get('categories', [])) if result.get('categories') else 'N/A'}</p>
                                <p><strong>Price:</strong> {result.get('price', 'N/A')}</p>
                                <p><strong>Source:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('displayLink', 'Yelp')}</a></p>
            </div>
                    </div>
                        '''
                
                html_output += '</div>'
                return html_output
        
        # Check if this is a restaurant search workflow
        elif self._current_results.get('results') and isinstance(self._current_results.get('results'), list):
            results = self._current_results.get('results', [])
            # Check if any result contains restaurant-related content
            has_restaurant_content = any(
                isinstance(result, dict) and (
                    'restaurant' in str(result).lower() or 
                    'food' in str(result).lower() or
                    'rating' in str(result).lower()
                ) for result in results
            )
            
            if has_restaurant_content and format_type == 'cards':
                # Format restaurant search results
                html_output = '<div class="results-container">'
                html_output += '<h3>🍽️ Restaurant Search Results</h3>'
                
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        html_output += f'''
                        <div class="result-card">
                            <h4>{i}. {result.get('title', 'No Title')}</h4>
                            <div class="result-content">
                                <p><strong>Address:</strong> {result.get('address', 'Address not available')}</p>
                                <p><strong>Rating:</strong> {result.get('rating', 'N/A')} ⭐</p>
                                <p><strong>Type:</strong> {result.get('type', 'Restaurant')}</p>
                                <p><strong>Source:</strong> <a href="{result.get('url', '#')}" target="_blank">{result.get('displayLink', 'Unknown Source')}</a></p>
                    </div>
                    </div>
                        '''
                
                html_output += '</div>'
                return html_output
        
        # Check if this is an intelligent workflow with stored results
        if hasattr(self, '_current_results') and self._current_results and self._current_results.get('results'):
            results = self._current_results.get('results', [])
            
            if format_type in ['adaptive', 'intelligent', 'research_cards', 'location_cards'] and isinstance(results, list):
                html_output = '<div class="results-container">'
                
                # Determine the appropriate header based on context
                if self._current_results.get('context_filtered'):
                    html_output += '<h3>🔍 Intelligent Research Results</h3>'
                elif self._current_results.get('geographically_filtered'):
                    html_output += '<h3>📍 Location-Based Results</h3>'
                elif self._current_results.get('adaptively_summarized'):
                    html_output += '<h3>📝 Contextual Summary Results</h3>'
                else:
                    html_output += '<h3>🔍 Search Results</h3>'
                
                # Display results with intelligent formatting
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        title = result.get('title', 'No Title')
                        summary = result.get('adaptive_summary', result.get('summarized_snippet', result.get('snippet', 'No summary available')))
                        url = result.get('url', '#')
                        display_link = result.get('displayLink', 'Unknown Source')
                        score = result.get('score', 'N/A')
                        
                        html_output += f'''
                        <div class="result-card">
                            <h4>{i}. {title}</h4>
                            <div class="result-content">
                                <p><strong>Summary:</strong> {summary}</p>
                                <p><strong>Source:</strong> <a href="{url}" target="_blank">{display_link}</a></p>
                                <p><strong>Score:</strong> {score}</p>
                    </div>
                    </div>
                        '''
                
                # Show email draft if available
                if self._current_results.get('email_draft'):
                    html_output += '<h3>📧 Email Draft</h3>'
                    html_output += f'<div class="email-draft" style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; white-space: pre-wrap; font-family: monospace;">{self._current_results["email_draft"]}</div>'
                
                html_output += '</div>'
                return html_output
        
        # Fall back to default display method
        return f"Results displayed in {format_type} format"
    

    
    def execute_plan(self, plan: Plan) -> Dict[str, Any]:
        """Execute a plan step by step."""
        print(f"🚀 Executing plan: {plan.goal}")
        
        # Clear previous results for new execution
        self._current_results = {}
        
        results = {}
        
        for i, step in enumerate(plan.steps, 1):
            print(f"--- Step {i}/{len(plan.steps)} ---")
            print(f"🎯 Action: {step.action}")
            
            if step.action in self.available_actions:
                try:
                    # Execute the action with parameters
                    result = self.available_actions[step.action](step.parameters)
                    
                    # Handle both string and dictionary results
                    if isinstance(result, str):
                        # If result is a string (success/error message), store it
                        results[step.action] = result
                        print(f"✅ Success: {result}")
                    elif isinstance(result, dict):
                        # If result is a dictionary, process it normally
                        for key, value in result.items():
                            results[key] = value
                        print(f"✅ Success: {step.action} completed")
        else:
                        # For any other type, convert to string
                        results[step.action] = str(result)
                        print(f"✅ Success: {step.action} completed")
                        
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    results[step.action] = error_msg
                    print(f"❌ Error: {error_msg}")
            else:
                error_msg = f"Unknown action: {step.action}"
                results[step.action] = error_msg
                print(f"❌ Error: {error_msg}")
        
        return results
    

    
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
    try:
    data = request.get_json()
        print(f"🔍 DEBUG /api/parse raw data: {data}")
        
        if data is None:
            print("❌ ERROR: request.get_json() returned None - check Content-Type header")
            return jsonify({'error': 'Invalid JSON data received'}), 400
        
    prompt = data.get('prompt', '')
        print(f"🔍 DEBUG prompt: '{prompt}'")
    
    if not prompt:
            print("❌ ERROR: No prompt provided in request")
        return jsonify({'error': 'No prompt provided'}), 400
    
    # Parse the prompt into a plan
        print(f"🚀 Attempting to parse prompt: '{prompt}'")
    plan = flow_system.parse_prompt(prompt)
        print(f"✅ Plan generated successfully: {plan.goal}")
    
    # Convert to JSON-serializable format
    plan_dict = asdict(plan)
    plan_dict['steps'] = [asdict(step) for step in plan.steps]
    
    return jsonify({
        'plan': plan_dict,
        'message': 'Plan generated successfully'
    })
        
    except Exception as e:
        print(f"❌ CRASH in parse_prompt: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': f'Parse failed: {type(e).__name__}: {str(e)}',
            'details': 'Check server logs for full traceback'
        }), 500

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
    execution_results = flow_system.execute_plan(plan)
    
    # Check if execution was successful (no error messages)
    success = True
    for action, result in execution_results.items():
        if isinstance(result, str) and result.startswith('Error:'):
            success = False
            break
    
    # Convert results to JSON-serializable format
    result_dict = asdict(plan)
    result_dict['steps'] = [asdict(step) for step in plan.steps]
    
    # Include the stored results if available
    response_data = {
        'result': result_dict,
        'execution_results': execution_results,
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
                if isinstance(result, dict):
                    for key, value in result.items():
                        if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                            result[key] = str(value)
                elif isinstance(result, str):
                    # Convert string results to dict format
                    stored_results['results'] = [{'content': result}]
                else:
                    # Convert other types to string
                    stored_results['results'] = [{'content': str(result)}]
        
        response_data['stored_results'] = stored_results
    
    return jsonify(response_data)

@app.route('/api/examples')
def get_examples():
    """Get example prompts for AI automation use cases only."""
    examples = [
        {
            "title": "AI Automation Daily Digest",
            "prompt": "Compile the top 5 items about AI automation, summarize each in ~1 sentence, and prepare an email draft to founders@company.com",
            "description": "Complete AI automation workflow with summarization and email generation",
            "category": "ai_automation"
        },
        {
            "title": "AI Automation Research",
            "prompt": "Research the latest AI automation tools and trends for 2025",
            "description": "Focused AI automation search with recent content filtering (no email)",
            "category": "ai_automation"
        }
    ]
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

# Set up available actions after all methods are defined
flow_system._setup_actions()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
