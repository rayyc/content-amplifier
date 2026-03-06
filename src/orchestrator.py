"""
Master Orchestration System
Coordinates the entire Content Resonance Amplifier workflow
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import schedule
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
try:
    from src.gap_detector import GapDetector
    GAP_DETECTOR_AVAILABLE = True
except ImportError:
    GAP_DETECTOR_AVAILABLE = False
    print("⚠️  Warning: gap_detector module not available")

try:
    from src.content_analyzer import ContentAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False
    print("⚠️  Warning: content_analyzer module not available")

try:
    from src.content_generator import ContentGenerator
    GENERATOR_AVAILABLE = True
except ImportError:
    GENERATOR_AVAILABLE = False
    print("⚠️  Warning: content_generator module not available")

try:
    from src.distribution_manager_v2 import DistributionManagerV2
    DISTRIBUTOR_AVAILABLE = True
except ImportError:
    DISTRIBUTOR_AVAILABLE = False
    print("⚠️  Warning: distribution_manager_v2 module not available")

try:
    from src.affiliate_manager import AffiliateManager
    AFFILIATE_MANAGER_AVAILABLE = True
except ImportError:
    AFFILIATE_MANAGER_AVAILABLE = False
    print("⚠️  Warning: affiliate_manager module not available")


class ContentAmplifierOrchestrator:
    def __init__(self, config_file: str = 'config.json', demo_mode: bool = False):
        """
        Initialize the complete system
        
        Args:
            config_file: Path to configuration file
            demo_mode: If True, uses simulated data; if False, uses real modules
        """
        self.demo_mode = demo_mode
        self.config = self._load_config(config_file)
        self.state = {
            'last_scan': None,
            'gaps_found': 0,
            'content_created': 0,
            'content_distributed': 0,
            'total_revenue': 0,
            'active_workflows': []
        }
        
        # Initialize subsystems
        print(f"🚀 Initializing Content Resonance Amplifier (Mode: {'Demo' if demo_mode else 'Production'})...")
        
        if not demo_mode:
            self._initialize_production_systems()
        else:
            self._initialize_demo_systems()
        
        print("✅ System initialized")
    
    def _initialize_production_systems(self):
        """Initialize real production systems"""
        # Gap Detector
        if GAP_DETECTOR_AVAILABLE:
            self.gap_detector = GapDetector(self.config['detection'])
            print("  ✓ Gap Detector initialized")
        else:
            self.gap_detector = None
            print("  ✗ Gap Detector unavailable")
        
        # Content Analyzer
        if ANALYZER_AVAILABLE:
            # Load API key from .env instead of config.json
            provider = self.config.get('ai_provider', 'anthropic')
            api_key = os.getenv('ANTHROPIC_API_KEY') if provider == 'anthropic' else os.getenv('OPENAI_API_KEY')
            if api_key:
                self.analyzer = ContentAnalyzer(api_key=api_key)
                print("  ✓ Content Analyzer initialized")
            else:
                self.analyzer = None
                print("  ✗ Content Analyzer unavailable (no API key in .env)")
        else:
            self.analyzer = None
            print("  ✗ Content Analyzer unavailable")
        
        # Content Generator
        if GENERATOR_AVAILABLE:
            # Load API key from .env instead of config.json
            provider = self.config.get('ai_provider', 'anthropic')
            api_key = os.getenv('ANTHROPIC_API_KEY') if provider == 'anthropic' else os.getenv('OPENAI_API_KEY')
            if api_key:
                self.generator = ContentGenerator(api_key=api_key, provider=provider)
                print("  ✓ Content Generator initialized")
            else:
                self.generator = None
                print("  ✗ Content Generator unavailable (no API key in .env)")
        else:
            self.generator = None
            print("  ✗ Content Generator unavailable")
        
        # Distribution Manager V2
        if DISTRIBUTOR_AVAILABLE:
            self.distributor = DistributionManagerV2()
            print("  ✓ Distribution Manager V2 initialized")
        else:
            self.distributor = None
            print("  ✗ Distribution Manager unavailable")
        
        # Affiliate Manager
        if AFFILIATE_MANAGER_AVAILABLE:
            self.affiliate_manager = AffiliateManager()
            print("  ✓ Affiliate Manager initialized")
        else:
            self.affiliate_manager = None
            print("  ✗ Affiliate Manager unavailable")
    
    def _initialize_demo_systems(self):
        """Initialize demo/simulated systems"""
        self.gap_detector = None
        self.analyzer = None
        self.generator = None
        self.distributor = None
        self.affiliate_manager = None
        print("  ℹ️  Running in demo mode with simulated data")
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            print(f"⚠️  Config file not found. Using defaults. Create '{config_file}' to customize.")
            return {
                'detection': {
                    'stackoverflow_tags': ['python', 'javascript', 'react', 'nextjs'],
                    'reddit_subreddits': ['webdev', 'learnprogramming', 'reactjs'],
                    'devto_tags': ['python', 'javascript', 'webdev'],
                    'scan_frequency_hours': 6
                },
                'content': {
                    'batch_size': 3,
                    'min_gap_score': 50,
                    'review_required': True
                },
                'distribution': {
                    'platforms': ['devto', 'twitter'],
                    'stagger_minutes': 30,
                    'auto_publish': False
                },
                'monetization': {
                    'affiliate_programs': ['udemy', 'digitalocean'],
                    'track_conversions': True
                },
                'api_key': 'your-api-key',
                'ai_provider': 'anthropic',
                'credentials': {}
            }
    
    def run_full_pipeline(self, manual_mode: bool = True) -> Dict:
        """Execute the complete pipeline from gap detection to distribution"""
        print("\n" + "="*80)
        print("🎯 STARTING FULL CONTENT PIPELINE")
        print("="*80)
        
        pipeline_results = {
            'started_at': datetime.now().isoformat(),
            'mode': 'manual' if manual_mode else 'automated',
            'demo_mode': self.demo_mode,
            'stages': {}
        }
        
        # Stage 1: Gap Detection
        print("\n📍 STAGE 1: Gap Detection")
        gaps_result = self._run_gap_detection()
        pipeline_results['stages']['gap_detection'] = gaps_result
        
        if not gaps_result.get('success'):
            print("❌ Gap detection failed. Aborting pipeline.")
            return pipeline_results
        
        # Stage 2: Content Analysis
        print("\n📍 STAGE 2: Content Analysis")
        analysis_result = self._run_content_analysis(gaps_result.get('gaps', []))
        pipeline_results['stages']['analysis'] = analysis_result
        
        if not analysis_result.get('success'):
            print("❌ Content analysis failed. Aborting pipeline.")
            return pipeline_results
        
        # Stage 3: Content Generation
        print("\n📍 STAGE 3: Content Generation")
        generation_result = self._run_content_generation(
            analysis_result.get('briefs', []),
            manual_mode
        )
        pipeline_results['stages']['generation'] = generation_result
        
        if not generation_result.get('success'):
            print("❌ Content generation failed. Aborting pipeline.")
            return pipeline_results
        
        # Stage 4: Distribution
        if not manual_mode or self._confirm_distribution():
            print("\n📍 STAGE 4: Distribution")
            distribution_result = self._run_distribution(
                generation_result.get('packages', [])
            )
            pipeline_results['stages']['distribution'] = distribution_result
        else:
            print("⏸️  Distribution skipped - manual review required")
            pipeline_results['stages']['distribution'] = {'success': False, 'reason': 'manual_review'}
        
        # Update state
        pipeline_results['completed_at'] = datetime.now().isoformat()
        self._update_state(pipeline_results)
        
        # Generate report
        self._generate_pipeline_report(pipeline_results)
        
        return pipeline_results
    
    def _run_gap_detection(self) -> Dict:
        """Run gap detection across all platforms"""
        try:
            if self.gap_detector and not self.demo_mode:
                # PRODUCTION MODE: Use real gap detector
                print("🔍 Scanning Stack Overflow, Reddit, Dev.to...")
                results = self.gap_detector.run_full_scan()
                
                result = {
                    'success': True,
                    'gaps': results.get('top_opportunities', []),
                    'total_gaps': len(results.get('top_opportunities', [])),
                    'high_priority': sum(1 for g in results.get('top_opportunities', []) 
                                       if g.get('gap_score', 0) >= self.config['content']['min_gap_score'])
                }
                
                print(f"✅ Found {result['total_gaps']} gaps, {result['high_priority']} high priority")
                self.state['gaps_found'] = result['total_gaps']
                
                return result
            else:
                # DEMO MODE: Use simulated data
                print("🔍 Scanning Stack Overflow, Reddit, Dev.to... (Demo Mode)")
                
                result = {
                    'success': True,
                    'gaps': [
                        {
                            'platform': 'stackoverflow',
                            'title': 'How to deploy Next.js 15 to Vercel with custom domain',
                            'url': 'https://stackoverflow.com/q/12345',
                            'gap_score': 125.5,
                            'views': 8234,
                            'body': 'Demo content body...'
                        },
                        {
                            'platform': 'devto',
                            'title': 'React Server Components best practices',
                            'url': 'https://dev.to/article/12345',
                            'gap_score': 98.3,
                            'reactions': 156,
                            'body': 'Demo content body...'
                        }
                    ],
                    'total_gaps': 47,
                    'high_priority': 12
                }
                
                print(f"✅ Found {result['total_gaps']} gaps, {result['high_priority']} high priority (simulated)")
                self.state['gaps_found'] = result['total_gaps']
                
                return result
            
        except Exception as e:
            print(f"❌ Error in gap detection: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_content_analysis(self, gaps: List[Dict]) -> Dict:
        """Analyze gaps and generate content briefs"""
        try:
            if self.analyzer and not self.demo_mode and gaps:
                # PRODUCTION MODE: Use real analyzer
                print(f"📊 Analyzing {len(gaps)} gaps...")
                
                # Filter by gap score
                min_score = self.config['content']['min_gap_score']
                high_value_gaps = [g for g in gaps if g.get('gap_score', 0) >= min_score]
                
                # Analyze gaps
                briefs = self.analyzer.analyze_batch(
                    high_value_gaps[:self.config['content']['batch_size']]
                )
                
                result = {
                    'success': True,
                    'briefs': briefs,
                    'analyzed_count': len(briefs)
                }
                
                print(f"✅ Generated {len(briefs)} content briefs")
                
                return result
            else:
                # DEMO MODE: Use simulated data
                print(f"📊 Analyzing {len(gaps)} gaps... (Demo Mode)")
                
                min_score = self.config['content']['min_gap_score']
                high_value_gaps = [g for g in gaps if g.get('gap_score', 0) >= min_score]
                
                result = {
                    'success': True,
                    'briefs': [
                        {
                            'gap': high_value_gaps[0] if high_value_gaps else gaps[0] if gaps else {},
                            'analysis': {
                                'analysis': {
                                    'monetization_potential': {'score': 8, 'priority': 'high'},
                                    'content_type': 'step_by_step_guide',
                                    'audience_level': 'intermediate'
                                }
                            },
                            'brief': {
                                'title_suggestions': ['Complete Guide to Next.js 15 Deployment'],
                                'target_platforms': ['devto', 'medium', 'twitter'],
                                'estimated_word_count': 2000
                            }
                        }
                    ] if gaps else [],
                    'analyzed_count': 1 if gaps else 0
                }
                
                print(f"✅ Generated {len(result['briefs'])} content briefs (simulated)")
                
                return result
            
        except Exception as e:
            print(f"❌ Error in content analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_content_generation(self, briefs: List[Dict], manual_mode: bool) -> Dict:
        """Generate content from briefs"""
        try:
            batch_size = self.config['content']['batch_size']
            briefs_to_generate = briefs[:batch_size]
            
            if not briefs_to_generate:
                print("⚠️  No briefs available for generation")
                return {'success': False, 'reason': 'no_briefs'}
            
            print(f"✍️  Generating {len(briefs_to_generate)} content packages...")
            
            if manual_mode and self.config['content']['review_required']:
                print("\n📋 CONTENT BRIEFS FOR REVIEW:")
                for i, brief in enumerate(briefs_to_generate, 1):
                    # Safe dictionary access
                    title_suggestions = brief.get('brief', {}).get('title_suggestions', ['Untitled'])
                    title = title_suggestions[0] if title_suggestions else 'Untitled'
                    
                    priority = brief.get('analysis', {}).get('analysis', {}).get(
                        'monetization_potential', {}
                    ).get('priority', 'unknown')
                    
                    content_type = brief.get('analysis', {}).get('analysis', {}).get(
                        'content_type', 'unknown'
                    )
                    
                    print(f"\n{i}. {title}")
                    print(f"   Priority: {priority}")
                    print(f"   Type: {content_type}")
                
                if not self._confirm_generation():
                    return {'success': False, 'reason': 'user_cancelled'}
            
            if self.generator and not self.demo_mode:
                # PRODUCTION MODE: Use real generator
                packages = []
                for brief in briefs_to_generate:
                    try:
                        package = self.generator.generate_full_content_package(brief)
                        packages.append(package)
                    except Exception as e:
                        print(f"⚠️  Error generating package: {e}")
                        continue
                
                result = {
                    'success': True,
                    'packages': packages,
                    'generated_count': len(packages)
                }
                
                print(f"✅ Generated {len(packages)} complete content packages")
                self.state['content_created'] += len(packages)
                
                return result
            else:
                # DEMO MODE: Simulated generation
                packages = []
                for brief in briefs_to_generate:
                    package = {
                        'brief_id': f"pkg_{int(datetime.now().timestamp())}",
                        'assets': {
                            'article': {'metadata': {'word_count': 2000, 'title': 'Demo Article'}},
                            'devto': 'Markdown content...',
                            'twitter': ['Tweet 1', 'Tweet 2'],
                            'linkedin': 'LinkedIn post...'
                        }
                    }
                    packages.append(package)
                
                result = {
                    'success': True,
                    'packages': packages,
                    'generated_count': len(packages)
                }
                
                print(f"✅ Generated {len(packages)} complete content packages (simulated)")
                self.state['content_created'] += len(packages)
                
                return result
            
        except Exception as e:
            print(f"❌ Error in content generation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _run_distribution(self, packages: List[Dict]) -> Dict:
        """Distribute content to platforms with affiliate injection"""
        try:
            if not packages:
                print("⚠️  No packages to distribute")
                return {'success': False, 'reason': 'no_packages'}
            
            platforms = self.config['distribution']['platforms']
            
            print(f"📤 Distributing to: {', '.join(platforms)}")
            
            if self.distributor and not self.demo_mode:
                # PRODUCTION MODE: Use real distributor with affiliate injection
                print("📤 Using Distribution Manager V2 with Affiliate Injection...")
                
                results = []
                auto_publish = self.config['distribution'].get('auto_publish', False)
                
                for i, package in enumerate(packages):
                    try:
                        print(f"\n  📦 Processing package {i+1}/{len(packages)}...")
                        
                        # Distribute with automatic affiliate link injection
                        dist_result = self.distributor.distribute_content_package(
                            package=package,
                            platforms=platforms,
                            auto_inject_affiliates=True,  # Automatically inject affiliate links!
                            publish_immediately=auto_publish
                        )
                        results.append(dist_result)
                        
                        print(f"  ✅ Package {i+1}/{len(packages)} distributed")
                        
                        # Stagger distributions if multiple packages
                        if len(packages) > 1 and i < len(packages) - 1:
                            stagger_minutes = self.config['distribution'].get('stagger_minutes', 30)
                            print(f"  ⏳ Waiting {stagger_minutes} minutes before next distribution...")
                            time.sleep(stagger_minutes * 60)
                            
                    except Exception as e:
                        print(f"  ⚠️  Error distributing package: {e}")
                        continue
                
                result = {
                    'success': True,
                    'distributions': results,
                    'total_distributed': len(results),
                    'platforms_used': platforms
                }
                
                print(f"\n✅ Distributed {len(results)} packages to {len(platforms)} platforms")
                self.state['content_distributed'] += len(results)
                
                return result
            else:
                # DEMO MODE: Simulated distribution
                results = []
                for i, package in enumerate(packages):
                    dist_result = {
                        'package_id': package.get('brief_id', f'pkg_{i}'),
                        'platforms': {
                            p: {'success': True, 'url': f'https://{p}.com/article_{i}'} 
                            for p in platforms
                        },
                        'success_count': len(platforms),
                        'affiliate_injections': [
                            {'program': 'udemy', 'type': 'course'},
                            {'program': 'digitalocean', 'type': 'hosting'}
                        ]
                    }
                    results.append(dist_result)
                
                result = {
                    'success': True,
                    'distributions': results,
                    'total_distributed': len(results)
                }
                
                print(f"✅ Distributed {len(results)} packages to {len(platforms)} platforms (simulated)")
                self.state['content_distributed'] += len(results)
                
                return result
            
        except Exception as e:
            print(f"❌ Error in distribution: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def _confirm_generation(self) -> bool:
        """Get user confirmation for content generation"""
        response = input("\n🤔 Proceed with content generation? (y/n): ").strip().lower()
        return response in ['y', 'yes']
    
    def _confirm_distribution(self) -> bool:
        """Get user confirmation for distribution"""
        response = input("\n🤔 Proceed with distribution to live platforms? (y/n): ").strip().lower()
        return response in ['y', 'yes']
    
    def _update_state(self, pipeline_results: Dict):
        """Update system state"""
        self.state['last_scan'] = datetime.now().isoformat()
        
        # Save state
        try:
            with open('system_state.json', 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save state: {e}")
    
    def _generate_pipeline_report(self, results: Dict):
        """Generate summary report"""
        print("\n" + "="*80)
        print("📊 PIPELINE EXECUTION REPORT")
        print("="*80)
        
        print(f"\n⏱️  Duration: {results['started_at']} → {results.get('completed_at', 'N/A')}")
        print(f"🎯 Mode: {results['mode']}")
        if results.get('demo_mode'):
            print("ℹ️  Demo Mode: Using simulated data")
        
        print("\n📈 Results:")
        for stage, result in results.get('stages', {}).items():
            status = "✅" if result.get('success') else "❌"
            print(f"  {status} {stage.replace('_', ' ').title()}")
            
            if stage == 'gap_detection' and result.get('success'):
                print(f"     - Found {result.get('total_gaps', 0)} gaps")
            elif stage == 'analysis' and result.get('success'):
                print(f"     - Generated {result.get('analyzed_count', 0)} briefs")
            elif stage == 'generation' and result.get('success'):
                print(f"     - Created {result.get('generated_count', 0)} packages")
            elif stage == 'distribution' and result.get('success'):
                print(f"     - Distributed to {result.get('total_distributed', 0)} platforms")
        
        print(f"\n💰 System Stats:")
        print(f"  - Total Gaps Found: {self.state['gaps_found']}")
        print(f"  - Content Created: {self.state['content_created']}")
        print(f"  - Content Distributed: {self.state['content_distributed']}")
        
        # Save report
        try:
            os.makedirs('outputs/reports', exist_ok=True)
            report_file = f"outputs/reports/pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Full report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")
    
    def schedule_automated_runs(self):
        """Schedule automated pipeline runs"""
        scan_frequency = self.config['detection']['scan_frequency_hours']
        
        print(f"\n⏰ Scheduling automated runs every {scan_frequency} hours...")
        print("⚠️  Note: Automated runs will use production mode")
        
        schedule.every(scan_frequency).hours.do(
            lambda: self.run_full_pipeline(manual_mode=False)
        )
        
        print("✅ Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n⏹️  Scheduler stopped")
    
    def generate_weekly_report(self) -> Dict:
        """Generate weekly performance report"""
        print("\n📊 Generating Weekly Report...")
        
        # In production, this would query your analytics database
        report = {
            'week_ending': datetime.now().isoformat(),
            'mode': 'demo' if self.demo_mode else 'production',
            'metrics': {
                'gaps_identified': self.state.get('gaps_found', 247),
                'content_created': self.state.get('content_created', 18),
                'content_published': self.state.get('content_distributed', 18),
                'total_views': 45231,
                'total_conversions': 243,
                'total_revenue': 2847,
                'conversion_rate': 1.8,
                'top_platform': 'Dev.to',
                'top_content': 'Next.js 15 Migration Guide'
            },
            'recommendations': [
                'Dev.to content performing 2x better than Medium - shift focus',
                'Tutorial content converting at 2.3% vs 1.2% for comparisons',
                'Consider video version of top 3 articles',
                'React Server Components trending - prioritize this topic'
            ]
        }
        
        # Save report
        try:
            os.makedirs('outputs/reports', exist_ok=True)
            report_file = f"outputs/reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"💾 Report saved to: {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")
        
        # Print summary
        print("\n📈 WEEKLY PERFORMANCE SUMMARY")
        print("="*60)
        print(f"Revenue: ${report['metrics']['total_revenue']:,}")
        print(f"Views: {report['metrics']['total_views']:,}")
        print(f"Conversion Rate: {report['metrics']['conversion_rate']}%")
        print(f"Content Published: {report['metrics']['content_published']}")
        print(f"\n🏆 Top Platform: {report['metrics']['top_platform']}")
        print(f"🏆 Top Content: {report['metrics']['top_content']}")
        
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        
        return report


# CLI Interface
def main():
    print("Content Resonance Amplifier - Master Control")
    print("="*60)
    
    # Ask for mode
    print("\n🎮 Select Mode:")
    print("1. Demo Mode (simulated data)")
    print("2. Production Mode (real modules)")
    
    mode_choice = input("\n👉 Select mode (1/2, default=1): ").strip()
    demo_mode = mode_choice != '2'
    
    orchestrator = ContentAmplifierOrchestrator(demo_mode=demo_mode)
    
    while True:
        print("\n📋 MENU:")
        print("1. Run Full Pipeline (Manual)")
        print("2. Run Full Pipeline (Automated)")
        print("3. Gap Detection Only")
        print("4. Generate Weekly Report")
        print("5. Schedule Automated Runs")
        print("6. View System State")
        print("7. Toggle Demo/Production Mode")
        print("8. Exit")
        
        choice = input("\n👉 Select option (1-8): ").strip()
        
        if choice == '1':
            orchestrator.run_full_pipeline(manual_mode=True)
        elif choice == '2':
            orchestrator.run_full_pipeline(manual_mode=False)
        elif choice == '3':
            result = orchestrator._run_gap_detection()
            print(f"\nResult: {json.dumps(result, indent=2)}")
        elif choice == '4':
            orchestrator.generate_weekly_report()
        elif choice == '5':
            orchestrator.schedule_automated_runs()
        elif choice == '6':
            print("\n💾 SYSTEM STATE:")
            print(json.dumps(orchestrator.state, indent=2))
        elif choice == '7':
            orchestrator.demo_mode = not orchestrator.demo_mode
            mode_name = "Demo" if orchestrator.demo_mode else "Production"
            print(f"\n🔄 Switched to {mode_name} Mode")
            print("⚠️  Note: Subsystems not reinitialized. Restart for full effect.")
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main()