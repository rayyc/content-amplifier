"""
Affiliate Link Manager
Automatically injects affiliate links into content based on context
"""

import json
import os
import re
from typing import Dict, List, Optional
from datetime import datetime


class AffiliateManager:
    def __init__(self, config_file: str = 'config/affiliates.json'):
        """Initialize affiliate manager with configuration"""
        self.config_file = config_file
        self.affiliates = self._load_affiliates()
        self.injection_log = []
    
    def _load_affiliates(self) -> Dict:
        """Load affiliate configuration"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Error loading affiliates config: {e}")
                return self._get_default_config()
        else:
            print(f"⚠️  Affiliates config not found at {self.config_file}")
            print(f"💡 Creating default configuration...")
            config = self._get_default_config()
            self._save_config(config)
            return config
    
    def _get_default_config(self) -> Dict:
        """Get default affiliate configuration"""
        return {
            "udemy": {
                "name": "Udemy",
                "enabled": True,
                "affiliate_url": "https://click.linksynergy.com/deeplink?id=YOUR_AFFILIATE_ID&mid=39197&murl=",
                "keywords": ["udemy", "course", "courses", "online course", "learning platform", "tutorial course"],
                "products": {
                    "python": {
                        "name": "Complete Python Bootcamp",
                        "url": "https://www.udemy.com/course/complete-python-bootcamp/",
                        "description": "Learn Python from scratch"
                    },
                    "javascript": {
                        "name": "The Complete JavaScript Course",
                        "url": "https://www.udemy.com/course/the-complete-javascript-course/",
                        "description": "Master JavaScript with projects"
                    },
                    "react": {
                        "name": "React - The Complete Guide",
                        "url": "https://www.udemy.com/course/react-the-complete-guide/",
                        "description": "Learn React with hooks and Redux"
                    },
                    "nextjs": {
                        "name": "Next.js & React - Complete Guide",
                        "url": "https://www.udemy.com/course/nextjs-react-the-complete-guide/",
                        "description": "Build production-ready Next.js apps"
                    },
                    "nodejs": {
                        "name": "NodeJS - Complete Guide",
                        "url": "https://www.udemy.com/course/nodejs-the-complete-guide/",
                        "description": "Master Node.js and build APIs"
                    }
                }
            },
            "digitalocean": {
                "name": "DigitalOcean",
                "enabled": True,
                "referral_url": "https://m.do.co/c/YOUR_REFERRAL_CODE",
                "keywords": ["hosting", "vps", "server", "deploy", "deployment", "cloud hosting", "droplet", "digitalocean"],
                "description": "Get $200 credit for 60 days"
            },
            "aws": {
                "name": "AWS (Amazon Web Services)",
                "enabled": False,
                "affiliate_tag": "YOUR_AWS_TAG",
                "base_url": "https://aws.amazon.com",
                "keywords": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloud services"],
                "products": {
                    "general": "https://aws.amazon.com/?tag=YOUR_TAG"
                }
            },
            "vercel": {
                "name": "Vercel",
                "enabled": False,
                "referral_url": "YOUR_VERCEL_REFERRAL",
                "keywords": ["vercel", "nextjs hosting", "frontend hosting", "edge functions"]
            },
            "netlify": {
                "name": "Netlify",
                "enabled": False,
                "referral_url": "YOUR_NETLIFY_REFERRAL",
                "keywords": ["netlify", "jamstack", "static hosting", "serverless functions"]
            }
        }
    
    def _save_config(self, config: Dict):
        """Save affiliate configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Affiliate config saved to {self.config_file}")
    
    def update_affiliate_links(self, affiliate_updates: Dict):
        """Update affiliate links in configuration"""
        for program, data in affiliate_updates.items():
            if program in self.affiliates:
                self.affiliates[program].update(data)
        
        self._save_config(self.affiliates)
        print(f"✅ Updated affiliate links for: {', '.join(affiliate_updates.keys())}")
    
    def inject_affiliate_links(self, content: str, metadata: Dict = None) -> Dict:
        """
        Inject affiliate links into content based on context
        
        Returns:
            {
                'content': str,  # Modified content with affiliate links
                'injections': List[Dict],  # List of injections made
                'revenue_potential': float  # Estimated revenue potential
            }
        """
        modified_content = content
        injections = []
        
        # Detect context from metadata
        context = self._analyze_context(content, metadata)
        
        # Inject relevant affiliate links
        for program, config in self.affiliates.items():
            if not config.get('enabled', False):
                continue
            
            # Check if program is relevant to content
            if self._is_relevant(content, config.get('keywords', [])):
                injection = self._inject_program_links(
                    modified_content, 
                    program, 
                    config, 
                    context
                )
                
                if injection:
                    modified_content = injection['content']
                    injections.append(injection['info'])
        
        # Calculate revenue potential
        revenue_potential = self._calculate_revenue_potential(injections, context)
        
        # Log injection
        self._log_injection(metadata, injections, revenue_potential)
        
        return {
            'content': modified_content,
            'injections': injections,
            'revenue_potential': revenue_potential
        }
    
    def _analyze_context(self, content: str, metadata: Dict = None) -> Dict:
        """Analyze content context for smart affiliate injection"""
        content_lower = content.lower()
        
        context = {
            'topics': [],
            'intent': 'informational',  # informational, tutorial, comparison, tool_review
            'audience_level': 'intermediate',
            'includes_code': '```' in content or 'code' in content_lower,
            'mentions_deployment': any(word in content_lower for word in ['deploy', 'host', 'server', 'production']),
            'mentions_learning': any(word in content_lower for word in ['learn', 'tutorial', 'guide', 'course', 'beginner'])
        }
        
        # Detect topics
        topic_keywords = {
            'python': ['python', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'npm'],
            'react': ['react', 'jsx', 'hooks', 'components'],
            'nextjs': ['nextjs', 'next.js', 'next js'],
            'hosting': ['host', 'deploy', 'server', 'vps', 'cloud'],
            'frontend': ['frontend', 'ui', 'css', 'html'],
            'backend': ['backend', 'api', 'database', 'server']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                context['topics'].append(topic)
        
        # Detect intent
        if 'how to' in content_lower or 'tutorial' in content_lower:
            context['intent'] = 'tutorial'
        elif 'vs' in content_lower or 'comparison' in content_lower:
            context['intent'] = 'comparison'
        elif 'review' in content_lower or 'best' in content_lower:
            context['intent'] = 'tool_review'
        
        return context
    
    def _is_relevant(self, content: str, keywords: List[str]) -> bool:
        """Check if affiliate program is relevant to content"""
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in keywords)
    
    def _inject_program_links(self, content: str, program: str, config: Dict, context: Dict) -> Optional[Dict]:
        """Inject links for a specific affiliate program"""
        
        if program == 'udemy':
            return self._inject_udemy_links(content, config, context)
        elif program == 'digitalocean':
            return self._inject_digitalocean_links(content, config, context)
        elif program == 'aws':
            return self._inject_aws_links(content, config, context)
        else:
            return self._inject_generic_links(content, program, config, context)
    
    def _inject_udemy_links(self, content: str, config: Dict, context: Dict) -> Optional[Dict]:
        """Inject Udemy course links based on content topics"""
        
        # Find relevant courses
        relevant_courses = []
        products = config.get('products', {})
        
        for topic in context['topics']:
            if topic in products:
                relevant_courses.append((topic, products[topic]))
        
        if not relevant_courses:
            # Default to general course mention
            relevant_courses = [('general', list(products.values())[0])] if products else []
        
        if not relevant_courses:
            return None
        
        # Create affiliate link
        course_topic, course_data = relevant_courses[0]
        course_url = course_data.get('url', '')
        affiliate_base = config.get('affiliate_url', '')
        
        affiliate_link = f"{affiliate_base}{course_url}"
        
        # Create contextual call-to-action
        cta = self._create_course_cta(course_topic, course_data, context)
        
        # Inject at the end before conclusion
        modified_content = self._inject_before_conclusion(content, cta)
        
        return {
            'content': modified_content,
            'info': {
                'program': 'udemy',
                'type': 'course',
                'product': course_data.get('name'),
                'link': affiliate_link,
                'placement': 'before_conclusion'
            }
        }
    
    def _inject_digitalocean_links(self, content: str, config: Dict, context: Dict) -> Optional[Dict]:
        """Inject DigitalOcean referral links"""
        
        if not context['mentions_deployment']:
            return None
        
        referral_url = config.get('referral_url', '')
        description = config.get('description', 'Get started with cloud hosting')
        
        # Create contextual CTA
        cta = f"\n\n## 🚀 Ready to Deploy?\n\n"
        cta += f"Deploy your application on **[DigitalOcean]({referral_url})** "
        cta += f"and {description}. Perfect for production-ready applications.\n\n"
        
        # Inject before conclusion
        modified_content = self._inject_before_conclusion(content, cta)
        
        return {
            'content': modified_content,
            'info': {
                'program': 'digitalocean',
                'type': 'hosting',
                'link': referral_url,
                'placement': 'before_conclusion'
            }
        }
    
    def _inject_aws_links(self, content: str, config: Dict, context: Dict) -> Optional[Dict]:
        """Inject AWS affiliate links"""
        
        # Only if AWS is specifically mentioned or cloud services are discussed
        content_lower = content.lower()
        if 'aws' not in content_lower and 'amazon web services' not in content_lower:
            return None
        
        affiliate_tag = config.get('affiliate_tag', '')
        base_url = config.get('base_url', '')
        
        # Replace mentions of AWS with affiliate links
        # Pattern: AWS or Amazon Web Services
        pattern = r'\b(AWS|Amazon Web Services)\b'
        replacement = f'[\\1]({base_url}?tag={affiliate_tag})'
        
        modified_content = re.sub(pattern, replacement, content, count=1)
        
        if modified_content != content:
            return {
                'content': modified_content,
                'info': {
                    'program': 'aws',
                    'type': 'cloud_service',
                    'link': f"{base_url}?tag={affiliate_tag}",
                    'placement': 'inline'
                }
            }
        
        return None
    
    def _inject_generic_links(self, content: str, program: str, config: Dict, context: Dict) -> Optional[Dict]:
        """Inject generic affiliate links"""
        
        referral_url = config.get('referral_url', '')
        if not referral_url:
            return None
        
        # Create simple CTA
        program_name = config.get('name', program.capitalize())
        cta = f"\n\n💡 *Try [{program_name}]({referral_url}) for this project.*\n\n"
        
        modified_content = self._inject_before_conclusion(content, cta)
        
        return {
            'content': modified_content,
            'info': {
                'program': program,
                'type': 'generic',
                'link': referral_url,
                'placement': 'before_conclusion'
            }
        }
    
    def _create_course_cta(self, topic: str, course_data: Dict, context: Dict) -> str:
        """Create contextual CTA for course"""
        
        course_name = course_data.get('name', f'{topic.capitalize()} Course')
        course_desc = course_data.get('description', f'Master {topic}')
        
        if context['intent'] == 'tutorial' and context['audience_level'] == 'beginner':
            cta = f"\n\n## 📚 Want to Learn More?\n\n"
            cta += f"If you're just getting started with {topic}, I highly recommend "
            cta += f"**[{course_name}]({course_data.get('url', '#')})**. {course_desc} "
            cta += f"with hands-on projects and real-world examples.\n\n"
        else:
            cta = f"\n\n## 🎓 Deep Dive\n\n"
            cta += f"For a comprehensive guide to {topic}, check out "
            cta += f"**[{course_name}]({course_data.get('url', '#')})**. {course_desc}.\n\n"
        
        return cta
    
    def _inject_before_conclusion(self, content: str, injection: str) -> str:
        """Inject content before conclusion section"""
        
        # Find conclusion markers
        conclusion_markers = [
            '## Conclusion',
            '## Summary',
            '## Wrap Up',
            '## Final Thoughts',
            '## Next Steps'
        ]
        
        for marker in conclusion_markers:
            if marker in content:
                return content.replace(marker, injection + marker)
        
        # If no conclusion found, append before the end
        return content.rstrip() + '\n\n' + injection
    
    def _calculate_revenue_potential(self, injections: List[Dict], context: Dict) -> float:
        """Calculate estimated revenue potential"""
        
        # Base scores for different affiliate types
        scores = {
            'course': 15.0,  # Udemy courses typically $10-20 commission
            'hosting': 25.0,  # DigitalOcean gives $25 per referral
            'cloud_service': 5.0,  # AWS varies
            'generic': 10.0
        }
        
        total_potential = 0.0
        
        for injection in injections:
            affiliate_type = injection.get('type', 'generic')
            base_score = scores.get(affiliate_type, 10.0)
            
            # Adjust based on context
            if context['intent'] == 'tutorial':
                base_score *= 1.5  # Tutorials convert better
            elif context['intent'] == 'comparison':
                base_score *= 1.3
            
            if context['mentions_learning'] and affiliate_type == 'course':
                base_score *= 1.2
            
            total_potential += base_score
        
        return round(total_potential, 2)
    
    def _log_injection(self, metadata: Dict, injections: List[Dict], revenue_potential: float):
        """Log affiliate injection for tracking"""
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'content_id': metadata.get('gap_id') if metadata else 'unknown',
            'content_title': metadata.get('title') if metadata else 'unknown',
            'injections': injections,
            'revenue_potential': revenue_potential
        }
        
        self.injection_log.append(log_entry)
    
    def export_injection_log(self, filename: str = 'data/analytics/affiliate_injections.json'):
        """Export injection log"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.injection_log, f, indent=2)
        print(f"📊 Affiliate injection log exported to {filename}")
    
    def get_injection_stats(self) -> Dict:
        """Get statistics on affiliate injections"""
        
        total_injections = len(self.injection_log)
        total_potential = sum(log['revenue_potential'] for log in self.injection_log)
        
        # Count by program
        by_program = {}
        for log in self.injection_log:
            for injection in log['injections']:
                program = injection['program']
                by_program[program] = by_program.get(program, 0) + 1
        
        return {
            'total_injections': total_injections,
            'total_revenue_potential': total_potential,
            'by_program': by_program,
            'avg_potential_per_content': total_potential / total_injections if total_injections > 0 else 0
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize manager
    manager = AffiliateManager()
    
    # Example content
    sample_content = """
# Complete Guide to Next.js 15 Deployment

Next.js 15 brings exciting new features for production applications.

## Building Your App

First, build your Next.js application for production...

## Deployment Options

You have several options for deploying your Next.js app...

## Conclusion

Next.js 15 makes it easier than ever to build production-ready applications.
"""
    
    # Inject affiliate links
    result = manager.inject_affiliate_links(
        sample_content,
        metadata={'title': 'Next.js 15 Deployment Guide', 'gap_id': 'test_001'}
    )
    
    print("Modified Content:")
    print(result['content'])
    print("\n" + "="*80)
    print(f"\nInjections Made: {len(result['injections'])}")
    print(f"Revenue Potential: ${result['revenue_potential']}")
    print("\nInjection Details:")
    for inj in result['injections']:
        print(f"  - {inj['program']}: {inj['type']} ({inj['placement']})")
    
    # Show stats
    print("\n" + "="*80)
    print("Injection Statistics:")
    stats = manager.get_injection_stats()
    print(f"Total Injections: {stats['total_injections']}")
    print(f"Total Revenue Potential: ${stats['total_revenue_potential']}")
    print(f"By Program: {stats['by_program']}")