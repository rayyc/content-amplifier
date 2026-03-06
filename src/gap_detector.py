"""
Content Gap Detection Engine
Discovers high-value content opportunities across platforms
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict
import time

class GapDetector:
    def __init__(self, config: Dict):
        self.config = config
        self.gaps = []
        
    def search_stackoverflow(self, tags: List[str], min_views: int = 1000) -> List[Dict]:
        """Find high-view questions with low-quality answers"""
        base_url = "https://api.stackexchange.com/2.3/questions"
        
        gaps = []
        for tag in tags:
            params = {
                'order': 'desc',
                'sort': 'votes',
                'tagged': tag,
                'site': 'stackoverflow',
                'filter': 'withbody',
                'pagesize': 100
            }
            
            try:
                response = requests.get(base_url, params=params)
                data = response.json()
                
                for question in data.get('items', []):
                    # IMPROVED: Safe access to all question fields
                    view_count = question.get('view_count', 0)
                    
                    if view_count >= min_views:
                        # Check answer quality
                        answers = question.get('answers', [])
                        answer_score = max([a.get('score', 0) for a in answers], default=0)
                        
                        # Gap indicator: high views, low answer scores, or no accepted answer
                        if answer_score < 10 or not question.get('is_answered', False):
                            gaps.append({
                                'platform': 'stackoverflow',
                                'title': question.get('title', 'Untitled Question'),
                                'url': question.get('link', ''),
                                'views': view_count,
                                'tags': question.get('tags', []),
                                'answer_quality': answer_score,
                                'gap_score': self._calculate_gap_score(question),
                                'created': datetime.fromtimestamp(
                                    question.get('creation_date', 0)
                                ).isoformat() if question.get('creation_date') else datetime.now().isoformat(),
                                'body': question.get('body', '')  # Include body for analysis
                            })
                
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching Stack Overflow data for {tag}: {e}")
        
        return sorted(gaps, key=lambda x: x['gap_score'], reverse=True)
    
    def search_reddit(self, subreddits: List[str], timeframe: str = 'week') -> List[Dict]:
        """Find highly engaged posts with unanswered questions in comments"""
        gaps = []
        
        for subreddit in subreddits:
            url = f"https://www.reddit.com/r/{subreddit}/top.json"
            params = {'t': timeframe, 'limit': 50}
            headers = {'User-Agent': 'ContentGapBot/1.0'}
            
            try:
                response = requests.get(url, params=params, headers=headers)
                data = response.json()
                
                # IMPROVED: Safe access to Reddit response structure
                children = data.get('data', {}).get('children', [])
                
                for post in children:
                    post_data = post.get('data', {})
                    
                    # Look for question posts or high engagement
                    num_comments = post_data.get('num_comments', 0)
                    if num_comments > 20:
                        # IMPROVED: Safe access to all post_data fields
                        created_utc = post_data.get('created_utc', time.time())
                        
                        gaps.append({
                            'platform': 'reddit',
                            'subreddit': subreddit,
                            'title': post_data.get('title', 'Untitled Post'),
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'score': post_data.get('score', 0),
                            'comments': num_comments,
                            'gap_score': self._calculate_reddit_gap_score(post_data),
                            'created': datetime.fromtimestamp(created_utc).isoformat(),
                            'body': post_data.get('selftext', '')  # Include body for analysis
                        })
                
                time.sleep(2)  # Reddit rate limiting
                
            except Exception as e:
                print(f"Error fetching Reddit data for r/{subreddit}: {e}")
        
        return sorted(gaps, key=lambda x: x['gap_score'], reverse=True)
    
    def search_devto(self, tags: List[str]) -> List[Dict]:
        """Find Dev.to posts with high engagement but gaps in comments"""
        base_url = "https://dev.to/api/articles"
        gaps = []
        
        for tag in tags:
            params = {'tag': tag, 'per_page': 30, 'top': 7}
            
            try:
                response = requests.get(base_url, params=params)
                articles = response.json()
                
                for article in articles:
                    # IMPROVED: Safe access to article fields
                    comments_count = article.get('comments_count', 0)
                    reactions_count = article.get('public_reactions_count', 0)
                    
                    # High engagement indicator
                    if comments_count > 10 or reactions_count > 50:
                        gaps.append({
                            'platform': 'devto',
                            'title': article.get('title', 'Untitled Article'),
                            'url': article.get('url', ''),
                            'reactions': reactions_count,
                            'comments': comments_count,
                            'tags': article.get('tag_list', []),
                            'gap_score': self._calculate_devto_gap_score(article),
                            'created': article.get('published_at', datetime.now().isoformat()),
                            'body': article.get('body_markdown', '')  # Include body for analysis
                        })
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching Dev.to data for {tag}: {e}")
        
        return sorted(gaps, key=lambda x: x['gap_score'], reverse=True)
    
    def _calculate_gap_score(self, question: Dict) -> float:
        """Calculate opportunity score for Stack Overflow questions"""
        views = question.get('view_count', 0)
        answers = question.get('answers', [])
        answer_quality = max([a.get('score', 0) for a in answers], default=0)
        
        # Higher score = bigger gap
        # More views + worse answers = better opportunity
        base_score = (views / 100) * (1 / (answer_quality + 1))
        
        # Bonus for no accepted answer
        if not question.get('is_answered', False):
            base_score *= 1.5
        
        return base_score
    
    def _calculate_reddit_gap_score(self, post: Dict) -> float:
        """Calculate opportunity score for Reddit posts"""
        score = post.get('score', 0)
        comments = post.get('num_comments', 0)
        
        # High comment-to-score ratio = lots of discussion/questions
        if score > 0:
            engagement_ratio = comments / score
        else:
            engagement_ratio = comments
        
        return score * engagement_ratio
    
    def _calculate_devto_gap_score(self, article: Dict) -> float:
        """Calculate opportunity score for Dev.to articles"""
        reactions = article.get('public_reactions_count', 0)
        comments = article.get('comments_count', 0)
        
        # More comments relative to reactions = more questions/discussion
        return reactions + (comments * 3)
    
    def run_full_scan(self) -> Dict:
        """Execute full gap detection across all platforms"""
        print("🔍 Starting gap detection scan...")
        
        results = {
            'scan_time': datetime.now().isoformat(),
            'gaps': {
                'stackoverflow': [],
                'reddit': [],
                'devto': []
            },
            'top_opportunities': []
        }
        
        # Stack Overflow scan
        if self.config.get('stackoverflow_tags'):
            print("📊 Scanning Stack Overflow...")
            results['gaps']['stackoverflow'] = self.search_stackoverflow(
                self.config['stackoverflow_tags']
            )[:20]  # Top 20
        
        # Reddit scan
        if self.config.get('reddit_subreddits'):
            print("🔴 Scanning Reddit...")
            results['gaps']['reddit'] = self.search_reddit(
                self.config['reddit_subreddits']
            )[:20]
        
        # Dev.to scan
        if self.config.get('devto_tags'):
            print("📝 Scanning Dev.to...")
            results['gaps']['devto'] = self.search_devto(
                self.config['devto_tags']
            )[:20]
        
        # Combine and rank all opportunities
        all_gaps = (
            results['gaps']['stackoverflow'] +
            results['gaps']['reddit'] +
            results['gaps']['devto']
        )
        
        results['top_opportunities'] = sorted(
            all_gaps, 
            key=lambda x: x.get('gap_score', 0),  # IMPROVED: Safe access to gap_score
            reverse=True
        )[:10]
        
        print(f"✅ Scan complete! Found {len(all_gaps)} total gaps")
        print(f"🎯 Top 10 opportunities identified")
        
        return results
    
    def export_results(self, results: Dict, filename: str = 'gaps.json'):
        """Export gap analysis results"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"💾 Results exported to {filename}")
        except Exception as e:
            print(f"❌ Error exporting results: {e}")


# Example usage
if __name__ == "__main__":
    config = {
        'stackoverflow_tags': ['python', 'javascript', 'react', 'nextjs', 'typescript'],
        'reddit_subreddits': ['webdev', 'learnprogramming', 'reactjs', 'python'],
        'devto_tags': ['python', 'javascript', 'webdev', 'tutorial']
    }
    
    detector = GapDetector(config)
    results = detector.run_full_scan()
    detector.export_results(results)
    
    # Display top opportunities
    print("\n🏆 TOP 10 CONTENT OPPORTUNITIES:")
    print("=" * 80)
    for i, gap in enumerate(results.get('top_opportunities', []), 1):
        print(f"\n{i}. [{gap.get('platform', 'unknown').upper()}] {gap.get('title', 'Untitled')}")
        print(f"   Score: {gap.get('gap_score', 0):.2f}")
        print(f"   URL: {gap.get('url', 'N/A')}")