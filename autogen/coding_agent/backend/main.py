import requests
import re
from typing import List, Dict, Optional
import time

class WebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def scrape_page(self, url: str) -> str:
        """Scrape content from a given URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error scraping {url}: {e}")
            return ""

    def extract_links(self, html_content: str) -> List[str]:
        """Extract all links from HTML content"""
        link_pattern = r'href=["\']([^"\']+)["\']'
        return re.findall(link_pattern, html_content)

class KeywordFlagger:
    def __init__(self, keywords: List[str]):
        self.keywords = [kw.lower() for kw in keywords]

    def check_content(self, content: str) -> Dict[str, List[str]]:
        """Check content for flagged keywords and return matches"""
        content_lower = content.lower()
        matches = {}

        for keyword in self.keywords:
            if keyword in content_lower:
                # Find all occurrences
                positions = [m.start() for m in re.finditer(re.escape(keyword), content_lower)]
                matches[keyword] = positions

        return matches

    def add_keyword(self, keyword: str):
        """Add a new keyword to monitor"""
        self.keywords.append(keyword.lower())

class NotificationService:
    def __init__(self, email_config: Optional[Dict] = None):
        self.email_config = email_config or {}

    def send_alert(self, message: str, priority: str = "normal"):
        """Send an alert notification"""
        print(f"[{priority.upper()}] ALERT: {message}")
        # In a real implementation, this would send email/SMS/etc.

    def send_daily_report(self, stats: Dict):
        """Send a daily report with statistics"""
        report = f"Daily Report:\n"
        for key, value in stats.items():
            report += f"- {key}: {value}\n"
        print(report)

def main():
    # Initialize components
    scraper = WebScraper("https://example.com")
    flagger = KeywordFlagger(["urgent", "critical", "error", "warning"])
    notifier = NotificationService()

    # Scrape some content
    content = scraper.scrape_page("https://example.com")

    # Check for flagged keywords
    matches = flagger.check_content(content)

    # Send notifications if matches found
    if matches:
        for keyword, positions in matches.items():
            notifier.send_alert(f"Keyword '{keyword}' found {len(positions)} times", "high")

    # Send daily report
    stats = {
        "pages_scraped": 1,
        "keywords_found": len(matches),
        "total_matches": sum(len(pos) for pos in matches.values())
    }
    notifier.send_daily_report(stats)

if __name__ == "__main__":
    main()
