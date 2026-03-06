"""
AI Content Generation System
Creates content based on briefs using Claude/GPT
Requires: pip install anthropic openai python-dotenv
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ContentGenerator:
    def __init__(self, api_key: str = None, provider: str = 'anthropic'):
        """
        Initialize content generator
        provider: 'anthropic' (Claude) or 'openai' (GPT)
        api_key: If not provided, loads from .env file
        """
        # Load from .env if not provided
        if api_key is None:
            if provider == 'anthropic':
                api_key = os.getenv('ANTHROPIC_API_KEY')
            elif provider == 'openai':
                api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                raise ValueError(f"No API key found for {provider}. Set {provider.upper()}_API_KEY in .env file")
        
        self.api_key = api_key
        self.provider = provider
        
        if provider == 'anthropic':
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = "claude-sonnet-4-20250514"
        elif provider == 'openai':
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
    
    def generate_article(self, brief: Dict, custom_instructions: str = "") -> Dict:
        """Generate full article from brief"""
        print(f"✍️  Generating content for: {brief['gap']['title']}")
        
        prompt = self._build_article_prompt(brief, custom_instructions)
        
        # Generate content
        content = self._call_ai(prompt, max_tokens=4000)
        
        # Generate code examples if needed
        # FIXED: Safe access to missing_elements
        code_examples = []
        missing_elements = brief.get('analysis', {}).get('analysis', {}).get('missing_elements', [])
        if 'working_code' in missing_elements:
            code_examples = self._generate_code_examples(brief)
        
        # FIXED: Safe access to title_suggestions
        title_suggestions = brief.get('brief', {}).get('title_suggestions', [brief['gap'].get('title', 'Untitled')])
        suggested_title = title_suggestions[1] if len(title_suggestions) > 1 else title_suggestions[0]
        
        article = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'gap_id': brief.get('analysis', {}).get('gap_id', 'unknown'),
                'title': suggested_title,
                'word_count': len(content.split()),
                'target_platforms': brief.get('brief', {}).get('target_platforms', ['devto'])
            },
            'content': {
                'markdown': content,
                'code_examples': code_examples,
                'seo_keywords': brief.get('brief', {}).get('seo_keywords', [])
            },
            'distribution': {
                'ready_for': [],
                'requires_review': True
            }
        }
        
        return article
    
    def _build_article_prompt(self, brief: Dict, custom_instructions: str) -> str:
        """Build comprehensive prompt for article generation"""
        gap = brief.get('gap', {})
        # FIXED: Safe access to nested analysis dictionary
        analysis = brief.get('analysis', {}).get('analysis', {})
        content_brief = brief.get('brief', {})
        
        # FIXED: Provide safe defaults for all analysis fields
        audience_level = analysis.get('audience_level', 'intermediate')
        content_type = analysis.get('content_type', 'comprehensive_guide')
        missing_elements = analysis.get('missing_elements', [])
        outline = content_brief.get('outline', ['Introduction', 'Main Content', 'Conclusion'])
        seo_keywords = content_brief.get('seo_keywords', [])
        cta_suggestions = content_brief.get('cta_suggestions', ['Subscribe for more tutorials'])
        estimated_word_count = content_brief.get('estimated_word_count', 1500)
        
        prompt = f"""You are a technical content writer creating a comprehensive guide for developers.

ORIGINAL QUESTION/GAP:
{gap.get('title', 'Untitled')}
Source: {gap.get('platform', 'unknown')} - {gap.get('url', 'N/A')}

CONTENT REQUIREMENTS:
- Target Audience: {audience_level} developers
- Content Type: {content_type.replace('_', ' ')}
- Word Count: ~{estimated_word_count} words
- Missing Elements to Address: {', '.join(missing_elements) if missing_elements else 'comprehensive coverage'}

OUTLINE TO FOLLOW:
{chr(10).join(f'{i}. {section}' for i, section in enumerate(outline, 1))}

KEY REQUIREMENTS:
1. Write in a conversational, developer-to-developer tone
2. Be specific and actionable - no fluff
3. Include technical details that other sources miss
4. Explain WHY things work, not just HOW
5. Add practical examples and gotchas
6. Write in Markdown format with proper headings
7. Include code placeholders like [CODE_EXAMPLE_1] where code should go

SEO KEYWORDS TO NATURALLY INCLUDE:
{', '.join(seo_keywords[:5]) if seo_keywords else 'relevant technical terms'}

CALLS TO ACTION:
{chr(10).join(f'- {cta}' for cta in cta_suggestions)}

{custom_instructions}

Now write the complete article in Markdown format. Make it valuable enough that someone would bookmark it."""
        
        return prompt
    
    def _generate_code_examples(self, brief: Dict) -> List[Dict]:
        """Generate working code examples"""
        print("💻 Generating code examples...")
        
        gap = brief.get('gap', {})
        # FIXED: Safe access to seo_keywords
        keywords = brief.get('brief', {}).get('seo_keywords', [])
        
        prompt = f"""Generate 2-3 complete, working code examples for this tutorial:

Topic: {gap.get('title', 'Programming tutorial')}
Keywords: {', '.join(keywords[:3]) if keywords else 'programming concepts'}

For each example, provide:
1. A clear description of what it does
2. Complete, runnable code
3. Expected output or behavior
4. Common errors and how to fix them

Focus on practical, production-ready examples that developers can copy and use.
Format as JSON array with objects containing: description, code, language, notes"""
        
        response = self._call_ai(prompt, max_tokens=2000)
        
        # Parse response (simplified - in production, handle better)
        try:
            examples = json.loads(response)
            return examples
        except:
            # Fallback if JSON parsing fails
            return [
                {
                    'description': 'Code example (to be added manually)',
                    'code': '# Add working code here',
                    'language': 'python',
                    'notes': 'Review and add actual implementation'
                }
            ]
    
    def generate_twitter_thread(self, brief: Dict) -> List[str]:
        """Generate Twitter thread from brief"""
        print("🐦 Generating Twitter thread...")
        
        # FIXED: Safe access to gap title
        title = brief.get('gap', {}).get('title', 'Technical topic')
        
        prompt = f"""Create an engaging Twitter thread (8-10 tweets) about:

{title}

Requirements:
- Tweet 1: Hook that makes people stop scrolling
- Tweets 2-7: Key insights, code snippets, gotchas
- Tweet 8: CTA to full article
- Each tweet should be standalone valuable
- Use code snippets where relevant (in backticks)
- Keep technical but accessible
- End with engaging question or CTA

Format as JSON array of tweet strings."""
        
        response = self._call_ai(prompt, max_tokens=1000)
        
        try:
            tweets = json.loads(response)
            return tweets
        except:
            return [
                "🧵 Thread about " + title,
                "Learn more: [link]"
            ]
    
    def generate_devto_post(self, article: Dict) -> str:
        """Format article for Dev.to with proper frontmatter"""
        metadata = article.get('metadata', {})
        content = article.get('content', {})
        
        # FIXED: Safe access with defaults
        title = metadata.get('title', 'Untitled')
        seo_keywords = content.get('seo_keywords', [])
        markdown = content.get('markdown', '')
        code_examples = content.get('code_examples', [])
        
        # Dev.to frontmatter
        frontmatter = f"""---
title: {title}
published: false
description: 
tags: {', '.join(seo_keywords[:4])}
canonical_url: 
---

"""
        
        # Insert code examples into placeholders
        for i, example in enumerate(code_examples, 1):
            code_block = f"""
```{example.get('language', 'python')}
{example.get('code', '# Code here')}
```

*{example.get('notes', '')}*
"""
            placeholder = f"[CODE_EXAMPLE_{i}]"
            markdown = markdown.replace(placeholder, code_block)
        
        return frontmatter + markdown
    
    def generate_linkedin_post(self, brief: Dict) -> str:
        """Generate LinkedIn post"""
        print("💼 Generating LinkedIn post...")
        
        # FIXED: Safe access to gap title
        title = brief.get('gap', {}).get('title', 'Technical topic')
        
        prompt = f"""Create a LinkedIn post about:

{title}

Requirements:
- Professional but approachable tone
- Hook in first 2 lines
- Share a key insight or lesson learned
- Include a mini code snippet if relevant
- End with question for engagement
- 200-300 words max

Format as plain text ready to post."""
        
        return self._call_ai(prompt, max_tokens=500)
    
    def _call_ai(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call AI API based on provider"""
        try:
            if self.provider == 'anthropic':
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            
            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"❌ Error calling AI API: {e}")
            return f"Error generating content: {e}"
    
    def generate_full_content_package(self, brief: Dict) -> Dict:
        """Generate complete content package for all platforms"""
        print(f"\n🎨 Creating full content package...")
        print("=" * 80)
        
        # FIXED: Safe access to gap_id
        gap_id = brief.get('analysis', {}).get('gap_id', 'unknown')
        
        package = {
            'brief_id': gap_id,
            'created_at': datetime.now().isoformat(),
            'assets': {}
        }
        
        # Main article
        article = self.generate_article(brief)
        package['assets']['article'] = article
        
        # Platform-specific versions
        package['assets']['devto'] = self.generate_devto_post(article)
        package['assets']['twitter'] = self.generate_twitter_thread(brief)
        package['assets']['linkedin'] = self.generate_linkedin_post(brief)
        
        # Medium version (similar to Dev.to but different formatting)
        package['assets']['medium'] = article.get('content', {}).get('markdown', '')
        
        print("\n✅ Content package complete!")
        print(f"   - Article: {article.get('metadata', {}).get('word_count', 0)} words")
        print(f"   - Twitter thread: {len(package['assets']['twitter'])} tweets")
        print(f"   - Dev.to post: Ready")
        print(f"   - LinkedIn post: Ready")
        
        return package


# Example usage
if __name__ == "__main__":
    # Load briefs
    try:
        with open('content_briefs.json', 'r') as f:
            briefs = json.load(f)
    except FileNotFoundError:
        print("❌ content_briefs.json not found!")
        print("Run content_analyzer.py first to generate briefs.")
        briefs = []
    
    # Initialize generator - now loads from .env automatically!
    try:
        generator = ContentGenerator(provider='anthropic')
        print("✅ Content Generator initialized with API key from .env")
    except ValueError as e:
        print(f"❌ {e}")
        print("\nMake sure your .env file contains:")
        print("ANTHROPIC_API_KEY=sk-ant-your-key-here")
        generator = None
    
    # Show what would be generated
    if briefs and generator:
        # FIXED: Safe access to brief data
        first_brief = briefs[0]
        title_suggestions = first_brief.get('brief', {}).get('title_suggestions', ['Untitled'])
        platforms = first_brief.get('brief', {}).get('target_platforms', ['devto'])
        
        print(f"\nTop priority brief:")
        print(f"Title: {title_suggestions[1] if len(title_suggestions) > 1 else title_suggestions[0]}")
        print(f"Platforms: {', '.join(platforms)}")
        
        print("\nTo generate content package:")
        print("package = generator.generate_full_content_package(briefs[0])")
    elif not briefs:
        print("\n⚠️  No briefs available. Run content_analyzer.py first.")
    else:
        print("\n⚠️  Generator not initialized. Check your .env file.")