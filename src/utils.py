"""
Utility Functions
Common helpers used across the Content Resonance Amplifier system
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(log_dir: str = 'logs', log_level: str = 'INFO'):
    """Setup logging configuration"""
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_directory(path: str):
    """Ensure directory exists, create if not"""
    Path(path).mkdir(parents=True, exist_ok=True)


def load_json(filepath: str, default: Any = None) -> Any:
    """Load JSON file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        logger.error(f"Error loading JSON from {filepath}: {e}")
        return default


def save_json(filepath: str, data: Any, indent: int = 2):
    """Save data to JSON file with error handling"""
    try:
        ensure_directory(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.info(f"Saved data to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {filepath}: {e}")
        return False


def load_env_config() -> Dict:
    """Load configuration from .env file"""
    from dotenv import load_dotenv
    load_dotenv()
    
    return {
        'anthropic_key': os.getenv('ANTHROPIC_API_KEY'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'devto_key': os.getenv('DEVTO_API_KEY'),
        'twitter': {
            'bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
            'api_key': os.getenv('TWITTER_API_KEY'),
            'api_secret': os.getenv('TWITTER_API_SECRET'),
            'access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'access_token_secret': os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        },
        'medium_token': os.getenv('MEDIUM_TOKEN'),
        'github_token': os.getenv('GITHUB_TOKEN'),
        'linkedin_token': os.getenv('LINKEDIN_ACCESS_TOKEN')
    }


# ============================================================================
# DATA PROCESSING
# ============================================================================

def generate_content_id(title: str, platform: str = '') -> str:
    """Generate unique content ID from title"""
    source = f"{title}_{platform}_{datetime.now().isoformat()}"
    return hashlib.md5(source.encode()).hexdigest()[:12]


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """Sanitize text for use as filename"""
    # Remove invalid characters
    valid_chars = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    filename = ''.join(c for c in text if c in valid_chars)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Truncate if too long
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename.lower()


def chunk_list(items: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts_deep(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts_deep(result[key], value)
        else:
            result[key] = value
    return result


# ============================================================================
# TEXT PROCESSING
# ============================================================================

def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple implementation)"""
    # Remove common words
    common_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'
    }
    
    # Split and clean
    words = text.lower().split()
    keywords = [
        word.strip('.,!?;:"()[]{}') 
        for word in words 
        if len(word) > 3 and word.lower() not in common_words
    ]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int = 280, suffix: str = '...') -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def word_count(text: str) -> int:
    """Count words in text"""
    return len(text.split())


def estimate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """Estimate reading time in minutes"""
    words = word_count(text)
    minutes = max(1, round(words / words_per_minute))
    return minutes


# ============================================================================
# URL UTILITIES
# ============================================================================

def add_utm_parameters(url: str, source: str, medium: str, campaign: str = '') -> str:
    """Add UTM parameters to URL for tracking"""
    separator = '&' if '?' in url else '?'
    
    params = f"utm_source={source}&utm_medium={medium}"
    if campaign:
        params += f"&utm_campaign={campaign}"
    
    return f"{url}{separator}{params}"


def shorten_url(url: str, service: str = 'bitly', api_key: str = None) -> str:
    """Shorten URL using service (placeholder for implementation)"""
    # This would integrate with URL shortening services
    # For now, just return the original URL
    logger.warning("URL shortening not implemented, returning original URL")
    return url


# ============================================================================
# DATE/TIME UTILITIES
# ============================================================================

def format_date(date_str: str, format: str = '%Y-%m-%d') -> str:
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime(format)
    except:
        return date_str


def days_ago(date_str: str) -> int:
    """Calculate days ago from ISO date string"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        delta = datetime.now() - dt
        return delta.days
    except:
        return 0


def is_recent(date_str: str, days: int = 7) -> bool:
    """Check if date is within the last N days"""
    return days_ago(date_str) <= days


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config(config: Dict) -> bool:
    """Validate configuration has required fields"""
    required_fields = ['detection', 'content', 'distribution']
    
    for field in required_fields:
        if field not in config:
            logger.error(f"Missing required config field: {field}")
            return False
    
    logger.info("Configuration validated successfully")
    return True


def validate_api_key(api_key: str, provider: str = 'anthropic') -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    
    if provider == 'anthropic':
        return api_key.startswith('sk-ant-')
    elif provider == 'openai':
        return api_key.startswith('sk-')
    
    return len(api_key) > 20


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    return url.startswith('http://') or url.startswith('https://')


# ============================================================================
# FORMATTING
# ============================================================================

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format amount as currency"""
    if currency == 'USD':
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """Format as percentage"""
    return f"{value:.{decimal_places}f}%"


# ============================================================================
# CONTENT UTILITIES
# ============================================================================

def generate_seo_title(title: str, keywords: List[str]) -> str:
    """Generate SEO-optimized title"""
    # If title already contains main keyword, return as is
    if keywords and keywords[0].lower() in title.lower():
        return title
    
    # Otherwise, prepend main keyword
    if keywords:
        return f"{keywords[0]} - {title}"
    
    return title


def generate_meta_description(content: str, max_length: int = 160) -> str:
    """Generate meta description from content"""
    # Get first paragraph or first N characters
    first_para = content.split('\n\n')[0]
    return truncate_text(first_para, max_length)


def extract_code_blocks(markdown: str) -> List[Dict]:
    """Extract code blocks from markdown"""
    import re
    
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, markdown, re.DOTALL)
    
    code_blocks = []
    for i, match in enumerate(matches, 1):
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        
        code_blocks.append({
            'index': i,
            'language': language,
            'code': code
        })
    
    return code_blocks


# ============================================================================
# PERFORMANCE
# ============================================================================

def calculate_engagement_rate(views: int, interactions: int) -> float:
    """Calculate engagement rate"""
    if views == 0:
        return 0.0
    return (interactions / views) * 100


def calculate_conversion_rate(views: int, conversions: int) -> float:
    """Calculate conversion rate"""
    if views == 0:
        return 0.0
    return (conversions / views) * 100


def calculate_roi(revenue: float, cost: float) -> float:
    """Calculate ROI percentage"""
    if cost == 0:
        return 0.0
    return ((revenue - cost) / cost) * 100


# ============================================================================
# ERROR HANDLING
# ============================================================================

class ContentAmplifierError(Exception):
    """Base exception for Content Amplifier"""
    pass


class GapDetectionError(ContentAmplifierError):
    """Error during gap detection"""
    pass


class ContentGenerationError(ContentAmplifierError):
    """Error during content generation"""
    pass


class DistributionError(ContentAmplifierError):
    """Error during distribution"""
    pass


def handle_api_error(error: Exception, operation: str) -> Dict:
    """Handle API errors with structured response"""
    logger.error(f"API Error during {operation}: {str(error)}")
    
    return {
        'success': False,
        'error': str(error),
        'operation': operation,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# SYSTEM INFO
# ============================================================================

def get_system_stats() -> Dict:
    """Get system statistics"""
    return {
        'timestamp': datetime.now().isoformat(),
        'data_dir_size': get_directory_size('data'),
        'outputs_dir_size': get_directory_size('outputs'),
        'logs_dir_size': get_directory_size('logs')
    }


def get_directory_size(path: str) -> int:
    """Get total size of directory in bytes"""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total += os.path.getsize(filepath)
    except:
        pass
    return total


def format_bytes(bytes: int) -> str:
    """Format bytes as human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} PB"


# ============================================================================
# TESTING/DEBUG
# ============================================================================

def print_section(title: str, width: int = 80):
    """Print a section header"""
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def print_status(message: str, status: str = 'info'):
    """Print colored status message"""
    colors = {
        'success': '\033[92m',  # Green
        'error': '\033[91m',    # Red
        'warning': '\033[93m',  # Yellow
        'info': '\033[94m'      # Blue
    }
    reset = '\033[0m'
    
    symbols = {
        'success': '✓',
        'error': '✗',
        'warning': '⚠',
        'info': 'ℹ'
    }
    
    color = colors.get(status, colors['info'])
    symbol = symbols.get(status, symbols['info'])
    
    print(f"{color}{symbol}{reset} {message}")


# Example usage
if __name__ == "__main__":
    print_section("Utility Functions Test")
    
    # Test file operations
    test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
    save_json('test_output.json', test_data)
    loaded = load_json('test_output.json')
    print_status(f"Loaded data: {loaded}", 'success')
    
    # Test text processing
    text = "This is a test text about Python programming and web development"
    keywords = extract_keywords(text, 5)
    print_status(f"Keywords: {keywords}", 'info')
    
    # Test formatting
    print_status(f"Currency: {format_currency(1234.56)}", 'info')
    print_status(f"Number: {format_number(1234567)}", 'info')
    print_status(f"Percentage: {format_percentage(12.345)}", 'info')
    
    # Test performance calculations
    rate = calculate_conversion_rate(1000, 25)
    print_status(f"Conversion rate: {format_percentage(rate)}", 'info')
    
    # Clean up
    os.remove('test_output.json')
    print_status("Test complete", 'success')