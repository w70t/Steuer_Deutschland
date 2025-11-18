"""
Tax Update Monitoring Service
Monitors official German tax sources for updates
"""
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger
from config import BMF_URL, BZST_URL, ELSTER_URL


class TaxUpdateMonitor:
    """Monitor official German tax sources for updates"""

    def __init__(self):
        self.sources = {
            'BMF': {
                'name': 'Bundesministerium der Finanzen',
                'url': BMF_URL,
                'rss_feed': f'{BMF_URL}/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed.xml',
            },
            'BZSt': {
                'name': 'Bundeszentralamt für Steuern',
                'url': BZST_URL,
                'rss_feed': f'{BZST_URL}/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/RSSNewsfeed.xml',
            },
            'ELSTER': {
                'name': 'ELSTER',
                'url': ELSTER_URL,
                'news_url': f'{ELSTER_URL}/eportal/aktuelles',
            }
        }

    async def check_for_updates(self) -> List[Dict]:
        """
        Check all sources for new tax updates

        Returns:
            List of detected updates
        """
        all_updates = []

        for source_key, source_info in self.sources.items():
            try:
                updates = await self._check_source(source_key, source_info)
                all_updates.extend(updates)
            except Exception as e:
                logger.error(f"Error checking {source_key}: {e}")

        return all_updates

    async def _check_source(self, source_key: str, source_info: Dict) -> List[Dict]:
        """
        Check a specific source for updates

        Args:
            source_key: Source identifier (BMF, BZSt, etc.)
            source_info: Source configuration

        Returns:
            List of updates from this source
        """
        updates = []

        try:
            async with aiohttp.ClientSession() as session:
                # Try RSS feed first if available
                if 'rss_feed' in source_info:
                    updates = await self._check_rss_feed(
                        session,
                        source_info['rss_feed'],
                        source_key,
                        source_info['name']
                    )

                # Fallback to web scraping if RSS fails
                if not updates and 'news_url' in source_info:
                    updates = await self._scrape_news_page(
                        session,
                        source_info['news_url'],
                        source_key,
                        source_info['name']
                    )

        except Exception as e:
            logger.error(f"Error checking source {source_key}: {e}")

        return updates

    async def _check_rss_feed(
        self,
        session: aiohttp.ClientSession,
        feed_url: str,
        source_key: str,
        source_name: str
    ) -> List[Dict]:
        """
        Check RSS feed for updates

        Args:
            session: aiohttp session
            feed_url: RSS feed URL
            source_key: Source identifier
            source_name: Source display name

        Returns:
            List of updates
        """
        updates = []

        try:
            async with session.get(feed_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'xml')

                    items = soup.find_all('item')[:5]  # Get latest 5 items

                    for item in items:
                        title = item.find('title').text if item.find('title') else ''
                        link = item.find('link').text if item.find('link') else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') else ''
                        description = item.find('description').text if item.find('description') else ''

                        # Check if it's tax-related
                        if self._is_tax_related(title, description):
                            update_type = self._classify_update(title, description)

                            updates.append({
                                'title': title,
                                'description': description,
                                'source_url': link,
                                'source_name': source_name,
                                'source_key': source_key,
                                'update_type': update_type,
                                'detected_at': datetime.utcnow(),
                                'pub_date': pub_date
                            })

        except Exception as e:
            logger.error(f"Error checking RSS feed {feed_url}: {e}")

        return updates

    async def _scrape_news_page(
        self,
        session: aiohttp.ClientSession,
        news_url: str,
        source_key: str,
        source_name: str
    ) -> List[Dict]:
        """
        Scrape news page for updates

        Args:
            session: aiohttp session
            news_url: News page URL
            source_key: Source identifier
            source_name: Source display name

        Returns:
            List of updates
        """
        updates = []

        try:
            async with session.get(news_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')

                    # Generic scraping - adjust selectors based on actual site structure
                    articles = soup.find_all(['article', 'div'], class_=['news', 'article'], limit=5)

                    for article in articles:
                        title_elem = article.find(['h2', 'h3', 'a'])
                        title = title_elem.text.strip() if title_elem else ''

                        link_elem = article.find('a', href=True)
                        link = link_elem['href'] if link_elem else ''
                        if link and not link.startswith('http'):
                            link = f"{news_url.rsplit('/', 1)[0]}/{link}"

                        desc_elem = article.find(['p', 'div'], class_=['description', 'summary'])
                        description = desc_elem.text.strip() if desc_elem else ''

                        if self._is_tax_related(title, description):
                            update_type = self._classify_update(title, description)

                            updates.append({
                                'title': title,
                                'description': description,
                                'source_url': link,
                                'source_name': source_name,
                                'source_key': source_key,
                                'update_type': update_type,
                                'detected_at': datetime.utcnow()
                            })

        except Exception as e:
            logger.error(f"Error scraping news page {news_url}: {e}")

        return updates

    def _is_tax_related(self, title: str, description: str) -> bool:
        """
        Check if content is tax-related

        Args:
            title: Article title
            description: Article description

        Returns:
            True if tax-related
        """
        tax_keywords = [
            'steuer', 'einkommensteuer', 'lohnsteuer', 'umsatzsteuer',
            'grundfreibetrag', 'steuersatz', 'steuertarif',
            'solidaritätszuschlag', 'kirchensteuer',
            'sozialversicherung', 'krankenversicherung', 'rentenversicherung',
            'beitragsbemessungsgrenze', 'tax', 'income tax'
        ]

        content = f"{title} {description}".lower()
        return any(keyword in content for keyword in tax_keywords)

    def _classify_update(self, title: str, description: str) -> str:
        """
        Classify the type of tax update

        Args:
            title: Article title
            description: Article description

        Returns:
            Update type classification
        """
        content = f"{title} {description}".lower()

        if any(word in content for word in ['steuersatz', 'tarif', 'tax rate']):
            return 'tax_rate'
        elif any(word in content for word in ['grundfreibetrag', 'freibetrag', 'allowance']):
            return 'allowance'
        elif any(word in content for word in ['sozialversicherung', 'social security', 'beitrag']):
            return 'social_security'
        elif any(word in content for word in ['gesetz', 'law', 'reform']):
            return 'tax_law'
        else:
            return 'general'

    async def extract_changes(self, update: Dict) -> Dict:
        """
        Extract specific changes from an update

        Args:
            update: Update information

        Returns:
            Structured changes
        """
        # This would involve more sophisticated parsing
        # For now, return a placeholder structure
        return {
            'summary': update.get('description', ''),
            'effective_date': None,  # Would need to parse from content
            'affected_items': [],  # Would need to extract specific items
        }


# Global instance
tax_update_monitor = TaxUpdateMonitor()
