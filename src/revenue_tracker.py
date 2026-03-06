"""
Revenue Tracking System
Tracks conversions, revenue, and attribution across all content
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import csv


class RevenueTracker:
    def __init__(self, data_dir: str = 'data/revenue'):
        """Initialize revenue tracker"""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.conversions_file = os.path.join(data_dir, 'conversions.json')
        self.revenue_log = os.path.join(data_dir, 'revenue_log.json')
        self.attribution_file = os.path.join(data_dir, 'attribution.json')
        
        self.conversions = self._load_data(self.conversions_file, [])
        self.revenue_history = self._load_data(self.revenue_log, [])
        self.attribution_data = self._load_data(self.attribution_file, {})
    
    def _load_data(self, filepath: str, default):
        """Load data from JSON file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️  Error loading {filepath}: {e}")
                return default
        return default
    
    def _save_data(self, filepath: str, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving to {filepath}: {e}")
    
    def track_conversion(self, 
                        content_id: str,
                        content_title: str,
                        platform: str,
                        conversion_type: str,  # 'affiliate', 'consulting', 'sponsored'
                        amount: float,
                        product_name: str = "",
                        affiliate_program: str = "",
                        notes: str = "") -> Dict:
        """Track a single conversion"""
        
        conversion = {
            'id': f"conv_{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'content_id': content_id,
            'content_title': content_title,
            'platform': platform,
            'conversion_type': conversion_type,
            'amount': amount,
            'product_name': product_name,
            'affiliate_program': affiliate_program,
            'notes': notes
        }
        
        self.conversions.append(conversion)
        self._save_data(self.conversions_file, self.conversions)
        
        # Update attribution
        self._update_attribution(conversion)
        
        # Log to revenue history
        self._log_revenue(conversion)
        
        print(f"✅ Conversion tracked: ${amount:.2f} from {content_title} ({conversion_type})")
        
        return conversion
    
    def track_affiliate_sale(self,
                            content_id: str,
                            content_title: str,
                            platform: str,
                            program: str,  # 'udemy', 'aws', 'digitalocean', etc.
                            product: str,
                            commission: float) -> Dict:
        """Convenience method for tracking affiliate sales"""
        
        return self.track_conversion(
            content_id=content_id,
            content_title=content_title,
            platform=platform,
            conversion_type='affiliate',
            amount=commission,
            product_name=product,
            affiliate_program=program
        )
    
    def track_consulting_lead(self,
                             content_id: str,
                             content_title: str,
                             platform: str,
                             project_value: float,
                             client_name: str = "") -> Dict:
        """Track consulting lead/project"""
        
        return self.track_conversion(
            content_id=content_id,
            content_title=content_title,
            platform=platform,
            conversion_type='consulting',
            amount=project_value,
            notes=f"Client: {client_name}" if client_name else ""
        )
    
    def track_sponsored_post(self,
                            content_id: str,
                            content_title: str,
                            platform: str,
                            sponsor: str,
                            amount: float) -> Dict:
        """Track sponsored content payment"""
        
        return self.track_conversion(
            content_id=content_id,
            content_title=content_title,
            platform=platform,
            conversion_type='sponsored',
            amount=amount,
            product_name=sponsor,
            notes=f"Sponsored by {sponsor}"
        )
    
    def _update_attribution(self, conversion: Dict):
        """Update attribution data"""
        content_id = conversion['content_id']
        
        if content_id not in self.attribution_data:
            self.attribution_data[content_id] = {
                'content_title': conversion['content_title'],
                'platform': conversion['platform'],
                'total_revenue': 0,
                'total_conversions': 0,
                'conversions_by_type': {},
                'first_conversion': conversion['timestamp'],
                'last_conversion': conversion['timestamp']
            }
        
        attr = self.attribution_data[content_id]
        attr['total_revenue'] += conversion['amount']
        attr['total_conversions'] += 1
        attr['last_conversion'] = conversion['timestamp']
        
        # Track by type
        conv_type = conversion['conversion_type']
        if conv_type not in attr['conversions_by_type']:
            attr['conversions_by_type'][conv_type] = {'count': 0, 'revenue': 0}
        
        attr['conversions_by_type'][conv_type]['count'] += 1
        attr['conversions_by_type'][conv_type]['revenue'] += conversion['amount']
        
        self._save_data(self.attribution_file, self.attribution_data)
    
    def _log_revenue(self, conversion: Dict):
        """Log revenue entry"""
        log_entry = {
            'date': datetime.now().date().isoformat(),
            'timestamp': conversion['timestamp'],
            'amount': conversion['amount'],
            'type': conversion['conversion_type'],
            'content_id': conversion['content_id'],
            'platform': conversion['platform']
        }
        
        self.revenue_history.append(log_entry)
        self._save_data(self.revenue_log, self.revenue_history)
    
    def get_total_revenue(self, days: int = None) -> float:
        """Get total revenue, optionally filtered by days"""
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            filtered = [
                r for r in self.revenue_history 
                if datetime.fromisoformat(r['timestamp']) > cutoff
            ]
            return sum(r['amount'] for r in filtered)
        
        return sum(r['amount'] for r in self.revenue_history)
    
    def get_revenue_by_platform(self, days: int = None) -> Dict:
        """Get revenue breakdown by platform"""
        conversions_to_analyze = self.conversions
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            conversions_to_analyze = [
                c for c in self.conversions
                if datetime.fromisoformat(c['timestamp']) > cutoff
            ]
        
        platform_revenue = defaultdict(lambda: {'revenue': 0, 'conversions': 0})
        
        for conv in conversions_to_analyze:
            platform = conv['platform']
            platform_revenue[platform]['revenue'] += conv['amount']
            platform_revenue[platform]['conversions'] += 1
        
        return dict(platform_revenue)
    
    def get_revenue_by_type(self, days: int = None) -> Dict:
        """Get revenue breakdown by conversion type"""
        conversions_to_analyze = self.conversions
        
        if days:
            cutoff = datetime.now() - timedelta(days=days)
            conversions_to_analyze = [
                c for c in self.conversions
                if datetime.fromisoformat(c['timestamp']) > cutoff
            ]
        
        type_revenue = defaultdict(lambda: {'revenue': 0, 'conversions': 0})
        
        for conv in conversions_to_analyze:
            conv_type = conv['conversion_type']
            type_revenue[conv_type]['revenue'] += conv['amount']
            type_revenue[conv_type]['conversions'] += 1
        
        return dict(type_revenue)
    
    def get_top_performing_content(self, limit: int = 10) -> List[Dict]:
        """Get top performing content by revenue"""
        sorted_content = sorted(
            self.attribution_data.items(),
            key=lambda x: x[1]['total_revenue'],
            reverse=True
        )
        
        return [
            {
                'content_id': content_id,
                **data
            }
            for content_id, data in sorted_content[:limit]
        ]
    
    def get_daily_revenue(self, days: int = 30) -> List[Dict]:
        """Get daily revenue for the past N days"""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Group by date
        daily_revenue = defaultdict(float)
        for entry in self.revenue_history:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            if timestamp > cutoff:
                date = timestamp.date().isoformat()
                daily_revenue[date] += entry['amount']
        
        # Fill in missing dates with 0
        result = []
        for i in range(days):
            date = (datetime.now().date() - timedelta(days=days-i-1)).isoformat()
            result.append({
                'date': date,
                'revenue': daily_revenue.get(date, 0)
            })
        
        return result
    
    def generate_revenue_report(self, days: int = 7) -> Dict:
        """Generate comprehensive revenue report"""
        print(f"\n💰 REVENUE REPORT (Last {days} Days)")
        print("=" * 80)
        
        total_revenue = self.get_total_revenue(days)
        all_time_revenue = self.get_total_revenue()
        platform_breakdown = self.get_revenue_by_platform(days)
        type_breakdown = self.get_revenue_by_type(days)
        top_content = self.get_top_performing_content(5)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'summary': {
                'period_revenue': total_revenue,
                'all_time_revenue': all_time_revenue,
                'total_conversions': len([
                    c for c in self.conversions
                    if datetime.fromisoformat(c['timestamp']) > 
                       datetime.now() - timedelta(days=days)
                ]),
                'all_time_conversions': len(self.conversions)
            },
            'by_platform': platform_breakdown,
            'by_type': type_breakdown,
            'top_content': top_content
        }
        
        # Print summary
        print(f"\n📊 Summary:")
        print(f"  Period Revenue: ${total_revenue:,.2f}")
        print(f"  All-Time Revenue: ${all_time_revenue:,.2f}")
        print(f"  Period Conversions: {report['summary']['total_conversions']}")
        print(f"  All-Time Conversions: {report['summary']['all_time_conversions']}")
        
        print(f"\n📈 By Platform:")
        for platform, data in platform_breakdown.items():
            print(f"  {platform}: ${data['revenue']:,.2f} ({data['conversions']} conversions)")
        
        print(f"\n💵 By Type:")
        for conv_type, data in type_breakdown.items():
            print(f"  {conv_type}: ${data['revenue']:,.2f} ({data['conversions']} conversions)")
        
        print(f"\n🏆 Top 5 Performing Content:")
        for i, content in enumerate(top_content[:5], 1):
            print(f"  {i}. {content['content_title']}")
            print(f"     Revenue: ${content['total_revenue']:,.2f} ({content['total_conversions']} conversions)")
        
        # Save report
        try:
            report_file = os.path.join(
                self.data_dir, 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n💾 Report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save report: {e}")
        
        return report
    
    def export_to_csv(self, output_file: str = None):
        """Export all conversions to CSV"""
        if output_file is None:
            output_file = os.path.join(
                self.data_dir,
                f"conversions_export_{datetime.now().strftime('%Y%m%d')}.csv"
            )
        
        # FIXED: Check if conversions exist before accessing [0]
        if not self.conversions:
            print("⚠️  No conversions to export")
            # Create empty CSV with standard headers
            with open(output_file, 'w', newline='') as f:
                headers = [
                    'id', 'timestamp', 'content_id', 'content_title', 'platform',
                    'conversion_type', 'amount', 'product_name', 'affiliate_program', 'notes'
                ]
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
            print(f"📄 Empty CSV created at: {output_file}")
            return output_file
        
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.conversions[0].keys())
                writer.writeheader()
                writer.writerows(self.conversions)
            
            print(f"📄 Conversions exported to: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ Error exporting to CSV: {e}")
            return None
    
    def calculate_roi(self, content_id: str, creation_cost: float = 0) -> Dict:
        """Calculate ROI for specific content"""
        if content_id not in self.attribution_data:
            return {'error': 'Content not found'}
        
        data = self.attribution_data[content_id]
        revenue = data.get('total_revenue', 0)  # IMPROVED: Added .get() for extra safety
        
        # If no creation cost provided, estimate based on time
        if creation_cost == 0:
            creation_cost = 50  # Estimated $50 cost (API calls, time, etc.)
        
        roi = ((revenue - creation_cost) / creation_cost * 100) if creation_cost > 0 else 0
        
        return {
            'content_id': content_id,
            'content_title': data.get('content_title', 'Unknown'),
            'total_revenue': revenue,
            'estimated_cost': creation_cost,
            'profit': revenue - creation_cost,
            'roi_percentage': roi,
            'conversions': data.get('total_conversions', 0)
        }


# Example usage and manual entry interface
def manual_entry_cli():
    """Command-line interface for manual conversion entry"""
    tracker = RevenueTracker()
    
    print("\n💰 Manual Conversion Entry")
    print("=" * 60)
    
    content_id = input("Content ID (or leave blank for auto): ").strip()
    if not content_id:
        content_id = f"manual_{datetime.now().timestamp()}"
    
    content_title = input("Content Title: ").strip()
    if not content_title:
        content_title = "Untitled Content"
    
    platform = input("Platform (devto/medium/twitter/linkedin): ").strip()
    if not platform:
        platform = "unknown"
    
    print("\nConversion Type:")
    print("1. Affiliate Sale")
    print("2. Consulting Lead")
    print("3. Sponsored Post")
    conv_choice = input("Select (1-3): ").strip()
    
    try:
        if conv_choice == '1':
            program = input("Affiliate Program (udemy/aws/digitalocean): ").strip()
            product = input("Product Name: ").strip()
            commission = float(input("Commission Amount ($): ").strip())
            
            tracker.track_affiliate_sale(
                content_id, content_title, platform,
                program, product, commission
            )
        
        elif conv_choice == '2':
            project_value = float(input("Project Value ($): ").strip())
            client_name = input("Client Name (optional): ").strip()
            
            tracker.track_consulting_lead(
                content_id, content_title, platform,
                project_value, client_name
            )
        
        elif conv_choice == '3':
            sponsor = input("Sponsor Name: ").strip()
            amount = float(input("Sponsorship Amount ($): ").strip())
            
            tracker.track_sponsored_post(
                content_id, content_title, platform,
                sponsor, amount
            )
        else:
            print("❌ Invalid selection")
            return
        
        print("\n✅ Conversion recorded!")
        
        # Show quick summary
        print(f"\n📊 Quick Stats:")
        print(f"Total Revenue (All Time): ${tracker.get_total_revenue():,.2f}")
        print(f"Total Revenue (Last 7 Days): ${tracker.get_total_revenue(7):,.2f}")
    
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'entry':
        # Manual entry mode
        manual_entry_cli()
    elif len(sys.argv) > 1 and sys.argv[1] == 'report':
        # Report mode
        tracker = RevenueTracker()
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        tracker.generate_revenue_report(days)
    elif len(sys.argv) > 1 and sys.argv[1] == 'export':
        # Export mode
        tracker = RevenueTracker()
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        tracker.export_to_csv(output_file)
    else:
        # Demo mode
        print("Revenue Tracker - Demo Mode")
        print("\nUsage:")
        print("  python revenue_tracker.py entry           # Manual conversion entry")
        print("  python revenue_tracker.py report [days]   # Generate report")
        print("  python revenue_tracker.py export [file]   # Export to CSV")
        print("\nExample:")
        tracker = RevenueTracker()
        
        # Simulate some conversions
        tracker.track_affiliate_sale(
            'article_001',
            'Next.js 15 Migration Guide',
            'devto',
            'udemy',
            'Complete Next.js Course',
            45.00
        )
        
        tracker.track_consulting_lead(
            'article_001',
            'Next.js 15 Migration Guide',
            'devto',
            2500.00,
            'Acme Corp'
        )
        
        # Generate report
        tracker.generate_revenue_report(30)