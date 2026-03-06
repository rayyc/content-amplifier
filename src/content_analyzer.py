"""
Content Analysis Pipeline
Analyzes gaps and generates content briefs using AI
"""

import json
import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ContentAnalyzer:
    def __init__(self, api_key: str = None):
        """
        Initialize with optional API key for Claude/OpenAI
        
        Note: Currently uses rule-based analysis. 
        API key will be used for AI-powered analysis in future updates.
        """
        # Load from .env if not provided
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
        
        self.api_key = api_key
        # Note: Not using AI yet, but keeping for future enhancement
        
    def analyze_gap(self, gap: Dict) -> Dict:
        """Deep analysis of a content gap"""
        analysis = {
            'gap_id': f"{gap['platform']}_{hash(gap['url'])}",
            'platform': gap['platform'],
            'original_title': gap['title'],
            'url': gap['url'],
            'analysis': {}
        }
        
        # Fetch content if needed
        content = self._fetch_content(gap)
        
        if content:
            analysis['analysis'] = {
                'main_question': self._extract_main_question(gap['title']),
                'missing_elements': self._identify_missing_elements(content),
                'audience_level': self._determine_audience_level(content),
                'content_type': self._suggest_content_type(gap),
                'keywords': self._extract_keywords(gap, content),
                'monetization_potential': self._assess_monetization(gap, content)
            }
        
        return analysis
    
    def _fetch_content(self, gap: Dict) -> str:
        """Fetch content from URL if available"""
        try:
            # For Stack Overflow, we already have the body
            # For Reddit/Dev.to, we'd need to fetch
            # This is a simplified version
            return gap.get('body', '')
        except:
            return ""
    
    def _extract_main_question(self, title: str) -> str:
        """Extract or reformulate the core question"""
        # Simple extraction - in production, use AI
        if '?' in title:
            return title
        else:
            return f"How to {title.lower()}?"
    
    def _identify_missing_elements(self, content: str) -> List[str]:
        """Identify what's missing from existing content"""
        missing = []
        
        # Check for common missing elements
        checks = {
            'working_code': ['example', 'code', 'snippet'],
            'explanation': ['because', 'reason', 'why'],
            'debugging': ['error', 'debug', 'fix'],
            'production_ready': ['production', 'deploy', 'scale'],
            'best_practices': ['best practice', 'recommended', 'should'],
            'comparison': ['vs', 'versus', 'compare', 'difference'],
            'step_by_step': ['step', 'tutorial', 'guide'],
        }
        
        content_lower = content.lower()
        for element, keywords in checks.items():
            if not any(kw in content_lower for kw in keywords):
                missing.append(element)
        
        return missing
    
    def _determine_audience_level(self, content: str) -> str:
        """Determine target audience skill level"""
        # Simple heuristic - in production, use AI
        beginner_indicators = ['beginner', 'introduction', 'getting started', 'basics']
        advanced_indicators = ['advanced', 'optimization', 'architecture', 'scale']
        
        content_lower = content.lower()
        
        if any(ind in content_lower for ind in advanced_indicators):
            return 'advanced'
        elif any(ind in content_lower for ind in beginner_indicators):
            return 'beginner'
        else:
            return 'intermediate'
    
    def _suggest_content_type(self, gap: Dict) -> str:
        """Suggest best content format for this gap"""
        title = gap['title'].lower()
        
        if 'how' in title or 'tutorial' in title:
            return 'step_by_step_guide'
        elif 'vs' in title or 'compare' in title:
            return 'comparison_article'
        elif 'error' in title or 'fix' in title:
            return 'troubleshooting_guide'
        elif 'best' in title or 'top' in title:
            return 'curated_list'
        else:
            return 'comprehensive_guide'
    
    def _extract_keywords(self, gap: Dict, content: str) -> List[str]:
        """Extract relevant keywords"""
        # Simple extraction from tags/title
        keywords = []
        
        if 'tags' in gap:
            keywords.extend(gap['tags'])
        
        # Add title words (simplified)
        title_words = gap['title'].lower().split()
        keywords.extend([w for w in title_words if len(w) > 4])
        
        return list(set(keywords))[:10]
    
    def _assess_monetization(self, gap: Dict, content: str) -> Dict:
        """Assess monetization potential"""
        score = 0
        methods = []
        
        # Check for commercial intent
        commercial_keywords = ['tool', 'service', 'course', 'hosting', 'platform']
        title_lower = gap['title'].lower()
        
        for kw in commercial_keywords:
            if kw in title_lower:
                score += 2
                
        # Platform-based scoring
        if gap['platform'] == 'stackoverflow' and gap.get('views', 0) > 5000:
            score += 3
        
        # Suggest monetization methods
        if 'tool' in title_lower or 'service' in title_lower:
            methods.append('affiliate_links')
        if gap.get('views', 0) > 10000 or gap.get('score', 0) > 100:
            methods.append('sponsored_content')
        if score > 5:
            methods.append('consulting_leads')
        
        return {
            'score': min(score, 10),
            'methods': methods,
            'priority': 'high' if score >= 7 else 'medium' if score >= 4 else 'low'
        }
    
    def generate_content_brief(self, gap: Dict, analysis: Dict) -> Dict:
        """Generate a complete content brief"""
        brief = {
            'title_suggestions': self._generate_titles(gap, analysis),
            'outline': self._generate_outline(gap, analysis),
            'key_points': self._generate_key_points(analysis),
            'cta_suggestions': self._generate_ctas(analysis),
            'seo_keywords': analysis['analysis'].get('keywords', []),
            'estimated_word_count': self._estimate_word_count(analysis),
            'target_platforms': self._suggest_platforms(gap, analysis)
        }
        
        return brief
    
    def _generate_titles(self, gap: Dict, analysis: Dict) -> List[str]:
        """Generate multiple title options"""
        # FIXED: Safe access to main_question with fallback to gap query
        main_q = analysis.get('analysis', {}).get('main_question', gap.get('title', 'this topic'))
        
        titles = [
            gap['title'],  # Original
            f"The Complete Guide to {main_q}",
            f"{main_q} - What the Docs Don't Tell You",
            f"I Spent 10 Hours on {main_q} - Here's What Works",
            f"{main_q} (With Working Code Examples)"
        ]
        return titles
    
    def _generate_outline(self, gap: Dict, analysis: Dict) -> List[str]:
        """Generate content outline"""
        # FIXED: Safe access to missing_elements
        missing = analysis.get('analysis', {}).get('missing_elements', [])
        
        outline = [
            "Introduction - The Problem",
            "Why This Matters",
            "The Solution (Overview)"
        ]
        
        if 'working_code' in missing:
            outline.append("Complete Code Example")
        if 'explanation' in missing:
            outline.append("How It Works (Deep Dive)")
        if 'debugging' in missing:
            outline.append("Common Errors and Fixes")
        if 'production_ready' in missing:
            outline.append("Production Considerations")
        if 'best_practices' in missing:
            outline.append("Best Practices")
        
        outline.extend([
            "Conclusion",
            "Next Steps / Resources"
        ])
        
        return outline
    
    def _generate_key_points(self, analysis: Dict) -> List[str]:
        """Generate key points to cover"""
        # FIXED: Safe access to missing_elements
        missing = analysis.get('analysis', {}).get('missing_elements', [])
        return [f"Address missing: {m.replace('_', ' ')}" for m in missing]
    
    def _generate_ctas(self, analysis: Dict) -> List[str]:
        """Generate call-to-action suggestions"""
        # FIXED: Safe access to monetization_potential
        monetization = analysis.get('analysis', {}).get('monetization_potential', {})
        methods = monetization.get('methods', [])
        
        ctas = []
        if 'affiliate_links' in methods:
            ctas.append("Check out [Tool Name] (affiliate link)")
        if 'consulting_leads' in methods:
            ctas.append("Need help implementing this? Let's talk")
        if 'sponsored_content' in methods:
            ctas.append("Download my free [Resource] for more")
        
        ctas.append("Subscribe for more [niche] tutorials")
        
        return ctas
    
    def _estimate_word_count(self, analysis: Dict) -> int:
        """Estimate ideal word count"""
        # FIXED: Safe access to content_type
        content_type = analysis.get('analysis', {}).get('content_type', 'comprehensive_guide')
        
        counts = {
            'step_by_step_guide': 1500,
            'comparison_article': 2000,
            'troubleshooting_guide': 1200,
            'curated_list': 1000,
            'comprehensive_guide': 2500
        }
        
        return counts.get(content_type, 1500)
    
    def _suggest_platforms(self, gap: Dict, analysis: Dict) -> List[str]:
        """Suggest best platforms for distribution"""
        platforms = ['devto']  # Always good for dev content
        
        # FIXED: Safe access to audience_level
        audience = analysis.get('analysis', {}).get('audience_level', 'intermediate')
        
        if audience == 'beginner':
            platforms.extend(['medium', 'hashnode'])
        if gap.get('views', 0) > 5000:
            platforms.append('personal_blog')
        
        platforms.extend(['twitter_thread', 'linkedin'])
        
        return platforms
    
    def analyze_batch(self, gaps: List[Dict], top_n: int = 5) -> List[Dict]:
        """Analyze multiple gaps and return prioritized briefs"""
        print(f"📊 Analyzing {len(gaps)} gaps...")
        
        results = []
        for gap in gaps[:top_n]:
            analysis = self.analyze_gap(gap)
            brief = self.generate_content_brief(gap, analysis)
            
            # FIXED: Safe access to monetization_potential priority
            priority = analysis.get('analysis', {}).get('monetization_potential', {}).get('priority', 'low')
            
            results.append({
                'gap': gap,
                'analysis': analysis,
                'brief': brief,
                'priority': priority
            })
        
        # Sort by priority
        results.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        print(f"✅ Analysis complete! {sum(1 for r in results if r['priority'] == 'high')} high-priority opportunities")
        
        return results


# Example usage
if __name__ == "__main__":
    # Check if API key is available (for future AI features)
    analyzer = ContentAnalyzer()
    if analyzer.api_key:
        print("✅ Content Analyzer initialized (API key found for future AI features)")
    else:
        print("✅ Content Analyzer initialized (using rule-based analysis)")
        print("   💡 Add ANTHROPIC_API_KEY to .env for AI-powered analysis (coming soon)")
    
    # Load gaps from previous scan
    try:
        with open('data/gaps/gaps.json', 'r') as f:
            scan_results = json.load(f)
    except FileNotFoundError:
        print("\n❌ No gaps.json found!")
        print("Run gap_detector.py first to generate gaps.")
        print("\nExpected location: data/gaps/gaps.json")
        exit(1)
    
    # Analyze top opportunities
    briefs = analyzer.analyze_batch(scan_results.get('top_opportunities', []), top_n=5)
    
    if not briefs:
        print("\n⚠️  No opportunities found to analyze")
        exit(1)
    
    # Export briefs
    import os
    os.makedirs('data/briefs', exist_ok=True)
    with open('data/briefs/content_briefs.json', 'w') as f:
        json.dump(briefs, f, indent=2)
    
    print("\n🎯 TOP 3 CONTENT BRIEFS:")
    print("=" * 80)
    for i, brief in enumerate(briefs[:3], 1):
        print(f"\n{i}. {brief['gap']['title']}")
        print(f"   Priority: {brief['priority'].upper()}")
        print(f"   Suggested Title: {brief['brief']['title_suggestions'][1]}")
        print(f"   Word Count: {brief['brief']['estimated_word_count']}")
        print(f"   Platforms: {', '.join(brief['brief']['target_platforms'])}")
    
    print(f"\n💾 Briefs saved to: data/briefs/content_briefs.json")