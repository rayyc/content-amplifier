"""
Distribution Automation System
Automates posting to multiple platforms
Requires: pip install requests tweepy
"""

import json
import requests
from typing import Dict, List
from datetime import datetime, timedelta
import time


class DistributionManager:
    def __init__(self, credentials: Dict):
        """
        Initialize with platform credentials
        credentials = {
            'devto': {'api_key': '...'},
            'twitter': {'api_key': '...', 'api_secret': '...', ...},
            'medium': {'integration_token': '...'},
            'github': {'token': '...'}
        }
        """
        self.credentials = credentials
        self.distribution_log = []
    
    def post_to_devto(self, content: str, metadata: Dict) -> Dict:
        """Post article to Dev.to"""
        api_key = self.credentials.get('devto', {}).get('api_key')
        
        if not api_key:
            return {'success': False, 'error': 'No Dev.to API key'}
        
        url = "https://dev.to/api/articles"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        
        # Parse frontmatter and content
        article_data = {
            'article': {
                'title': metadata['title'],
                'published': False,  # Start as draft
                'body_markdown': content,
                'tags': metadata.get('seo_keywords', [])[:4],
                'series': metadata.get('series'),
                'canonical_url': metadata.get('canonical_url')
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=article_data)
            result = response.json()
            
            if response.status_code in [200, 201]:
                print(f"✅ Posted to Dev.to: {result['url']}")
                return {
                    'success': True,
                    'url': result['url'],
                    'id': result['id'],
                    'platform': 'devto'
                }
            else:
                print(f"❌ Dev.to error: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            print(f"❌ Dev.to exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_medium(self, content: str, metadata: Dict) -> Dict:
        """Post article to Medium"""
        token = self.credentials.get('medium', {}).get('integration_token')
        
        if not token:
            return {'success': False, 'error': 'No Medium token'}
        
        # Get user ID first
        user_url = "https://api.medium.com/v1/me"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            user_response = requests.get(user_url, headers=headers)
            user_id = user_response.json()['data']['id']
            
            # Create post
            post_url = f"https://api.medium.com/v1/users/{user_id}/posts"
            post_data = {
                'title': metadata['title'],
                'contentFormat': 'markdown',
                'content': content,
                'tags': metadata.get('seo_keywords', [])[:5],
                'publishStatus': 'draft'  # Start as draft
            }
            
            response = requests.post(post_url, headers=headers, json=post_data)
            result = response.json()
            
            if response.status_code in [200, 201]:
                print(f"✅ Posted to Medium: {result['data']['url']}")
                return {
                    'success': True,
                    'url': result['data']['url'],
                    'id': result['data']['id'],
                    'platform': 'medium'
                }
            else:
                print(f"❌ Medium error: {result}")
                return {'success': False, 'error': result}
                
        except Exception as e:
            print(f"❌ Medium exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_twitter_thread(self, tweets: List[str]) -> Dict:
        """Post Twitter thread"""
        # Note: Requires tweepy with v2 API access
        # This is a simplified version
        
        twitter_creds = self.credentials.get('twitter', {})
        
        if not twitter_creds:
            return {'success': False, 'error': 'No Twitter credentials'}
        
        try:
            import tweepy
            
            client = tweepy.Client(
                bearer_token=twitter_creds.get('bearer_token'),
                consumer_key=twitter_creds.get('api_key'),
                consumer_secret=twitter_creds.get('api_secret'),
                access_token=twitter_creds.get('access_token'),
                access_token_secret=twitter_creds.get('access_token_secret')
            )
            
            tweet_ids = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweets, 1):
                # Add thread numbering
                if len(tweets) > 1:
                    numbered_tweet = f"{i}/{len(tweets)} {tweet_text}"
                else:
                    numbered_tweet = tweet_text
                
                # Post tweet
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
            
            thread_url = f"https://twitter.com/i/web/status/{tweet_ids[0]}"
            print(f"✅ Posted Twitter thread: {thread_url}")
            
            return {
                'success': True,
                'url': thread_url,
                'tweet_ids': tweet_ids,
                'platform': 'twitter'
            }
            
        except Exception as e:
            print(f"❌ Twitter exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_linkedin(self, content: str, metadata: Dict) -> Dict:
        """Post to LinkedIn"""
        # Note: LinkedIn API requires company/organization access
        # This is a simplified version showing the structure
        
        token = self.credentials.get('linkedin', {}).get('access_token')
        
        if not token:
            return {'success': False, 'error': 'No LinkedIn token'}
        
        # Get user ID
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            # This is simplified - actual LinkedIn API is more complex
            user_url = "https://api.linkedin.com/v2/me"
            user_response = requests.get(user_url, headers=headers)
            user_id = user_response.json()['id']
            
            # Create post
            post_url = "https://api.linkedin.com/v2/ugcPosts"
            post_data = {
                'author': f'urn:li:person:{user_id}',
                'lifecycleState': 'PUBLISHED',
                'specificContent': {
                    'com.linkedin.ugc.ShareContent': {
                        'shareCommentary': {
                            'text': content
                        },
                        'shareMediaCategory': 'ARTICLE'
                    }
                },
                'visibility': {
                    'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
                }
            }
            
            response = requests.post(post_url, headers=headers, json=post_data)
            
            if response.status_code in [200, 201]:
                print(f"✅ Posted to LinkedIn")
                return {
                    'success': True,
                    'platform': 'linkedin'
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ LinkedIn exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_github_repo(self, code_examples: List[Dict], metadata: Dict) -> Dict:
        """Create GitHub repo with code examples"""
        token = self.credentials.get('github', {}).get('token')
        
        if not token:
            return {'success': False, 'error': 'No GitHub token'}
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Create repo
        repo_name = metadata['title'].lower().replace(' ', '-')[:50]
        repo_data = {
            'name': repo_name,
            'description': f"Code examples for: {metadata['title']}",
            'private': False,
            'auto_init': True
        }
        
        try:
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=repo_data
            )
            
            if response.status_code == 201:
                repo_info = response.json()
                repo_url = repo_info['html_url']
                
                # Add code files
                for i, example in enumerate(code_examples, 1):
                    file_ext = {'python': 'py', 'javascript': 'js', 'typescript': 'ts'}.get(
                        example.get('language', 'txt'), 'txt'
                    )
                    file_name = f"example_{i}.{file_ext}"
                    
                    file_data = {
                        'message': f'Add {file_name}',
                        'content': requests.utils.quote(example['code'].encode()).decode()
                    }
                    
                    file_url = f"https://api.github.com/repos/{repo_info['full_name']}/contents/{file_name}"
                    requests.put(file_url, headers=headers, json=file_data)
                    time.sleep(1)
                
                print(f"✅ Created GitHub repo: {repo_url}")
                return {
                    'success': True,
                    'url': repo_url,
                    'platform': 'github'
                }
            else:
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            print(f"❌ GitHub exception: {e}")
            return {'success': False, 'error': str(e)}
    
    def distribute_content_package(self, package: Dict, platforms: List[str] = None) -> Dict:
        """Distribute complete content package to specified platforms"""
        print(f"\n📤 Starting distribution...")
        print("=" * 80)
        
        if platforms is None:
            platforms = ['devto', 'twitter', 'linkedin']
        
        results = {
            'package_id': package['brief_id'],
            'distributed_at': datetime.now().isoformat(),
            'platforms': {},
            'success_count': 0,
            'failed_count': 0
        }
        
        article = package['assets']['article']
        metadata = article['metadata']
        
        # Dev.to
        if 'devto' in platforms:
            devto_result = self.post_to_devto(
                package['assets']['devto'],
                metadata
            )
            results['platforms']['devto'] = devto_result
            if devto_result['success']:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
        
        # Twitter
        if 'twitter' in platforms:
            twitter_result = self.post_twitter_thread(
                package['assets']['twitter']
            )
            results['platforms']['twitter'] = twitter_result
            if twitter_result['success']:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
        
        # LinkedIn
        if 'linkedin' in platforms:
            linkedin_result = self.post_to_linkedin(
                package['assets']['linkedin'],
                metadata
            )
            results['platforms']['linkedin'] = linkedin_result
            if linkedin_result['success']:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
        
        # Medium
        if 'medium' in platforms:
            medium_result = self.post_to_medium(
                package['assets']['medium'],
                metadata
            )
            results['platforms']['medium'] = medium_result
            if medium_result['success']:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
        
        # GitHub (for code examples)
        if 'github' in platforms and article['content']['code_examples']:
            github_result = self.create_github_repo(
                article['content']['code_examples'],
                metadata
            )
            results['platforms']['github'] = github_result
            if github_result['success']:
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
        
        print(f"\n✅ Distribution complete!")
        print(f"   Success: {results['success_count']}")
        print(f"   Failed: {results['failed_count']}")
        
        self.distribution_log.append(results)
        return results
    
    def schedule_distribution(self, packages: List[Dict], schedule: Dict) -> List[Dict]:
        """Schedule distribution of multiple packages"""
        # This would integrate with a scheduler like APScheduler
        # For now, just a structure
        
        scheduled_tasks = []
        
        for i, package in enumerate(packages):
            task = {
                'package_id': package['brief_id'],
                'scheduled_for': (datetime.now() + timedelta(hours=i*2)).isoformat(),
                'platforms': schedule.get('platforms', ['devto', 'twitter']),
                'status': 'pending'
            }
            scheduled_tasks.append(task)
        
        return scheduled_tasks
    
    def export_distribution_log(self, filename: str = 'distribution_log.json'):
        """Export distribution history"""
        with open(filename, 'w') as f:
            json.dump(self.distribution_log, f, indent=2)
        print(f"💾 Distribution log exported to {filename}")


# Example usage
if __name__ == "__main__":
    # Load credentials (from environment or config)
    credentials = {
        'devto': {'api_key': 'your-devto-key'},
        'twitter': {
            'bearer_token': 'your-bearer-token',
            'api_key': 'your-api-key',
            'api_secret': 'your-api-secret',
            'access_token': 'your-access-token',
            'access_token_secret': 'your-access-token-secret'
        },
        'medium': {'integration_token': 'your-medium-token'},
        'github': {'token': 'your-github-token'}
    }
    
    # Initialize
    distributor = DistributionManager(credentials)
    
    print("Distribution Manager Ready!")
    print("\nTo use:")
    print("1. Add your platform credentials")
    print("2. Load content package: package = json.load(open('content_package.json'))")
    print("3. Distribute: results = distributor.distribute_content_package(package)")
    print("4. Check results and export log")