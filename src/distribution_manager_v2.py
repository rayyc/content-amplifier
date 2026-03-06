"""
Enhanced Distribution Manager V2
Full automation with affiliate link injection and multi-platform support
"""

import json
import os
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import affiliate manager
try:
    from affiliate_manager import AffiliateManager
    AFFILIATE_MANAGER_AVAILABLE = True
except ImportError:
    AFFILIATE_MANAGER_AVAILABLE = False
    print("⚠️  Affiliate Manager not available")


class DistributionManagerV2:
    def __init__(self, credentials: Dict = None):
        """
        Initialize enhanced distribution manager
        Credentials can be passed or loaded from environment
        """
        self.credentials = credentials or self._load_credentials_from_env()
        self.distribution_log = []
        
        # Initialize affiliate manager
        if AFFILIATE_MANAGER_AVAILABLE:
            self.affiliate_manager = AffiliateManager()
            print("✅ Affiliate Manager initialized")
        else:
            self.affiliate_manager = None
            print("⚠️  Affiliate Manager unavailable - links won't be injected")
    
    def _load_credentials_from_env(self) -> Dict:
        """Load credentials from environment variables"""
        return {
            'devto': {
                'api_key': os.getenv('DEVTO_API_KEY')
            },
            'twitter': {
                'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
                'api_key': os.getenv('TWITTER_API_KEY'),
                'api_secret': os.getenv('TWITTER_API_SECRET'),
                'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
                'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            },
            'medium': {
                'integration_token': os.getenv('MEDIUM_TOKEN')
            },
            'github': {
                'token': os.getenv('GITHUB_TOKEN')
            },
            'linkedin': {
                'access_token': os.getenv('LINKEDIN_ACCESS_TOKEN')
            }
        }
    
    def distribute_content_package(self, 
                                   package: Dict, 
                                   platforms: List[str] = None,
                                   auto_inject_affiliates: bool = True,
                                   publish_immediately: bool = False) -> Dict:
        """
        Distribute complete content package with affiliate injection
        
        Args:
            package: Content package from generator
            platforms: List of platforms to distribute to
            auto_inject_affiliates: Whether to inject affiliate links
            publish_immediately: If False, creates drafts for review
        
        Returns:
            Distribution results with URLs and status
        """
        print(f"\n📤 Starting enhanced distribution...")
        print("=" * 80)
        
        if platforms is None:
            platforms = ['devto', 'twitter', 'medium']
        
        article = package['assets']['article']
        metadata = article['metadata']
        
        # Inject affiliate links if enabled
        if auto_inject_affiliates and self.affiliate_manager:
            print("💰 Injecting affiliate links...")
            for asset_type in ['devto', 'medium', 'markdown']:
                if asset_type in package['assets']:
                    result = self.affiliate_manager.inject_affiliate_links(
                        package['assets'][asset_type],
                        metadata
                    )
                    package['assets'][asset_type] = result['content']
                    
                    if result['injections']:
                        print(f"   ✅ Injected {len(result['injections'])} affiliate links")
                        print(f"   💵 Revenue potential: ${result['revenue_potential']}")
        
        results = {
            'package_id': package['brief_id'],
            'distributed_at': datetime.now().isoformat(),
            'platforms': {},
            'success_count': 0,
            'failed_count': 0,
            'affiliate_injections': []
        }
        
        # Dev.to
        if 'devto' in platforms:
            print("\n📝 Posting to Dev.to...")
            devto_result = self.post_to_devto(
                package['assets'].get('devto', ''),
                metadata,
                publish=publish_immediately
            )
            results['platforms']['devto'] = devto_result
            if devto_result['success']:
                results['success_count'] += 1
                print(f"   ✅ Posted: {devto_result.get('url', 'N/A')}")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {devto_result.get('error', 'Unknown error')}")
        
        # Twitter
        if 'twitter' in platforms:
            print("\n🐦 Posting to Twitter...")
            twitter_result = self.post_twitter_thread(
                package['assets'].get('twitter', [])
            )
            results['platforms']['twitter'] = twitter_result
            if twitter_result['success']:
                results['success_count'] += 1
                print(f"   ✅ Posted: {twitter_result.get('url', 'N/A')}")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {twitter_result.get('error', 'Unknown error')}")
        
        # Medium
        if 'medium' in platforms:
            print("\n📰 Posting to Medium...")
            medium_result = self.post_to_medium(
                package['assets'].get('medium', ''),
                metadata,
                publish=publish_immediately
            )
            results['platforms']['medium'] = medium_result
            if medium_result['success']:
                results['success_count'] += 1
                print(f"   ✅ Posted: {medium_result.get('url', 'N/A')}")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {medium_result.get('error', 'Unknown error')}")
        
        # LinkedIn
        if 'linkedin' in platforms:
            print("\n💼 Posting to LinkedIn...")
            linkedin_result = self.post_to_linkedin(
                package['assets'].get('linkedin', ''),
                metadata
            )
            results['platforms']['linkedin'] = linkedin_result
            if linkedin_result['success']:
                results['success_count'] += 1
                print(f"   ✅ Posted")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {linkedin_result.get('error', 'Unknown error')}")
        
        # GitHub
        if 'github' in platforms and article['content'].get('code_examples'):
            print("\n💻 Creating GitHub repo...")
            github_result = self.create_github_repo(
                article['content']['code_examples'],
                metadata
            )
            results['platforms']['github'] = github_result
            if github_result['success']:
                results['success_count'] += 1
                print(f"   ✅ Created: {github_result.get('url', 'N/A')}")
            else:
                results['failed_count'] += 1
                print(f"   ❌ Failed: {github_result.get('error', 'Unknown error')}")
        
        print(f"\n✅ Distribution complete!")
        print(f"   Success: {results['success_count']}")
        print(f"   Failed: {results['failed_count']}")
        
        self.distribution_log.append(results)
        return results
    
    def post_to_devto(self, content: str, metadata: Dict, publish: bool = False) -> Dict:
        """Post article to Dev.to"""
        api_key = self.credentials.get('devto', {}).get('api_key')
        
        if not api_key:
            return {'success': False, 'error': 'No Dev.to API key configured'}
        
        url = "https://dev.to/api/articles"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Extract title from content or metadata
        title = metadata.get('title', 'Untitled')
        
        # Parse tags from keywords
        tags = metadata.get('seo_keywords', [])[:4]  # Dev.to allows max 4 tags
        
        article_data = {
            'article': {
                'title': title,
                'published': publish,  # False = draft, True = published
                'body_markdown': content,
                'tags': tags,
                'series': metadata.get('series'),
                'canonical_url': metadata.get('canonical_url')
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=article_data)
            result = response.json()
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'url': result.get('url'),
                    'id': result.get('id'),
                    'platform': 'devto',
                    'status': 'published' if publish else 'draft'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def post_to_medium(self, content: str, metadata: Dict, publish: bool = False) -> Dict:
        """Post article to Medium"""
        token = self.credentials.get('medium', {}).get('integration_token')
        
        if not token:
            return {'success': False, 'error': 'No Medium token configured'}
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            # Get user ID
            user_response = requests.get('https://api.medium.com/v1/me', headers=headers)
            
            if user_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Failed to get user info: {user_response.status_code}',
                    'details': user_response.text
                }
            
            user_data = user_response.json()
            user_id = user_data['data']['id']
            
            # Create post
            post_url = f"https://api.medium.com/v1/users/{user_id}/posts"
            
            post_data = {
                'title': metadata.get('title', 'Untitled'),
                'contentFormat': 'markdown',
                'content': content,
                'tags': metadata.get('seo_keywords', [])[:5],
                'publishStatus': 'public' if publish else 'draft',
                'license': 'all-rights-reserved',
                'notifyFollowers': publish
            }
            
            response = requests.post(post_url, headers=headers, json=post_data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    'success': True,
                    'url': result['data']['url'],
                    'id': result['data']['id'],
                    'platform': 'medium',
                    'status': 'published' if publish else 'draft'
                }
            else:
                return {
                    'success': False,
                    'error': f'Post failed: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def post_twitter_thread(self, tweets: List[str]) -> Dict:
        """Post Twitter thread"""
        twitter_creds = self.credentials.get('twitter', {})
        
        # Check for required credentials
        required = ['bearer_token', 'api_key', 'api_secret', 'access_token', 'access_token_secret']
        missing = [key for key in required if not twitter_creds.get(key)]
        
        if missing:
            return {
                'success': False,
                'error': f'Missing Twitter credentials: {", ".join(missing)}'
            }
        
        try:
            import tweepy
            
            # Initialize Tweepy client
            client = tweepy.Client(
                bearer_token=twitter_creds['bearer_token'],
                consumer_key=twitter_creds['api_key'],
                consumer_secret=twitter_creds['api_secret'],
                access_token=twitter_creds['access_token'],
                access_token_secret=twitter_creds['access_token_secret']
            )
            
            tweet_ids = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweets, 1):
                # Add thread numbering for threads > 1 tweet
                if len(tweets) > 1:
                    numbered_tweet = f"{i}/{len(tweets)} {tweet_text}"
                else:
                    numbered_tweet = tweet_text
                
                # Ensure tweet is within character limit
                if len(numbered_tweet) > 280:
                    numbered_tweet = numbered_tweet[:277] + "..."
                
                # Post tweet
                try:
                    if previous_tweet_id:
                        response = client.create_tweet(
                            text=numbered_tweet,
                            in_reply_to_tweet_id=previous_tweet_id
                        )
                    else:
                        response = client.create_tweet(text=numbered_tweet)
                    
                    tweet_ids.append(response.data['id'])
                    previous_tweet_id = response.data['id']
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"   ⚠️  Error posting tweet {i}: {e}")
                    continue
            
            if tweet_ids:
                thread_url = f"https://twitter.com/i/web/status/{tweet_ids[0]}"
                return {
                    'success': True,
                    'url': thread_url,
                    'tweet_ids': tweet_ids,
                    'platform': 'twitter',
                    'tweet_count': len(tweet_ids)
                }
            else:
                return {'success': False, 'error': 'Failed to post any tweets'}
            
        except ImportError:
            return {
                'success': False,
                'error': 'tweepy not installed. Run: pip install tweepy'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def post_to_linkedin(self, content: str, metadata: Dict) -> Dict:
        """Post to LinkedIn (simplified version)"""
        token = self.credentials.get('linkedin', {}).get('access_token')
        
        if not token:
            return {'success': False, 'error': 'No LinkedIn token configured'}
        
        # Note: LinkedIn API is complex and requires OAuth setup
        # This is a placeholder for the full implementation
        
        return {
            'success': False,
            'error': 'LinkedIn API requires OAuth setup. Please configure manually.',
            'note': 'Consider using LinkedIn manual posting or third-party tools like Buffer'
        }
    
    def create_github_repo(self, code_examples: List[Dict], metadata: Dict) -> Dict:
        """Create GitHub repo with code examples"""
        token = self.credentials.get('github', {}).get('token')
        
        if not token:
            return {'success': False, 'error': 'No GitHub token configured'}
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Sanitize repo name
        repo_name = metadata['title'].lower()
        repo_name = ''.join(c if c.isalnum() or c in ['-', '_'] else '-' for c in repo_name)
        repo_name = repo_name[:50]  # Max length
        
        repo_data = {
            'name': repo_name,
            'description': f"Code examples for: {metadata['title']}",
            'private': False,
            'auto_init': True,
            'has_issues': True,
            'has_wiki': False
        }
        
        try:
            # Create repo
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo_info = response.json()
                repo_full_name = repo_info['full_name']
                repo_url = repo_info['html_url']
                
                # Wait for repo initialization
                time.sleep(2)
                
                # Add code files
                for i, example in enumerate(code_examples, 1):
                    # Determine file extension
                    lang = example.get('language', 'txt')
                    ext_map = {
                        'python': 'py',
                        'javascript': 'js',
                        'typescript': 'ts',
                        'java': 'java',
                        'cpp': 'cpp',
                        'go': 'go',
                        'rust': 'rs'
                    }
                    ext = ext_map.get(lang, 'txt')
                    
                    file_name = f"example_{i}.{ext}"
                    
                    # Encode content to base64
                    import base64
                    content_bytes = example['code'].encode('utf-8')
                    content_base64 = base64.b64encode(content_bytes).decode('utf-8')
                    
                    file_data = {
                        'message': f'Add {file_name}',
                        'content': content_base64
                    }
                    
                    file_url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_name}"
                    file_response = requests.put(file_url, headers=headers, json=file_data)
                    
                    if file_response.status_code not in [200, 201]:
                        print(f"   ⚠️  Failed to add {file_name}")
                    
                    time.sleep(1)  # Rate limiting
                
                return {
                    'success': True,
                    'url': repo_url,
                    'repo_name': repo_name,
                    'platform': 'github',
                    'files_added': len(code_examples)
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create repo: {response.status_code}',
                    'details': response.text
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def export_distribution_log(self, filename: str = 'data/analytics/distribution_log.json'):
        """Export distribution history"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(self.distribution_log, f, indent=2)
        print(f"💾 Distribution log exported to {filename}")
    
    def get_distribution_stats(self) -> Dict:
        """Get distribution statistics"""
        total_distributions = len(self.distribution_log)
        total_successes = sum(log['success_count'] for log in self.distribution_log)
        total_failures = sum(log['failed_count'] for log in self.distribution_log)
        
        # Count by platform
        by_platform = {}
        for log in self.distribution_log:
            for platform, result in log['platforms'].items():
                if platform not in by_platform:
                    by_platform[platform] = {'success': 0, 'failed': 0}
                
                if result['success']:
                    by_platform[platform]['success'] += 1
                else:
                    by_platform[platform]['failed'] += 1
        
        return {
            'total_distributions': total_distributions,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'success_rate': (total_successes / (total_successes + total_failures) * 100) if (total_successes + total_failures) > 0 else 0,
            'by_platform': by_platform
        }


# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Distribution Manager V2")
    print("=" * 80)
    
    # Initialize
    distributor = DistributionManagerV2()
    
    # Check credential status
    print("\n📋 Credential Status:")
    creds = distributor.credentials
    
    platforms_status = {
        'Dev.to': bool(creds.get('devto', {}).get('api_key')),
        'Twitter': bool(creds.get('twitter', {}).get('bearer_token')),
        'Medium': bool(creds.get('medium', {}).get('integration_token')),
        'GitHub': bool(creds.get('github', {}).get('token')),
        'LinkedIn': bool(creds.get('linkedin', {}).get('access_token'))
    }
    
    for platform, configured in platforms_status.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"  {platform}: {status}")
    
    print("\n" + "=" * 80)
    print("\nTo use this distribution manager:")
    print("1. Ensure all credentials are set in .env file")
    print("2. Load a content package from content generator")
    print("3. Call: distributor.distribute_content_package(package, platforms=['devto', 'twitter'])")
    print("4. Review drafts and publish manually or set publish_immediately=True")