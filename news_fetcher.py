import feedparser
import requests
from bs4 import BeautifulSoup
import re
import logging
from typing import List, Dict
from config import (GOOGLE_NEWS_RSS, INTERNATIONAL_RSS, EXTRA_RSS,
                    CATEGORY_KEYWORDS, REQUEST_HEADERS, MAX_NEWS_PER_CATEGORY)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NewsFetcher:
    """新闻抓取与分类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    def fetch_rss(self, url: str, source: str = "") -> List[Dict]:
        """通用RSS抓取"""
        news = []
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = resp.apparent_encoding or 'utf-8'
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:40]:
                title = entry.get('title', '').strip()
                link = entry.get('link', '')
                summary = entry.get('summary', '')
                if summary:
                    summary = BeautifulSoup(summary, 'html.parser').get_text().strip()[:500]

                # 提取原始发布来源
                src = source
                entry_source = entry.get('source', {})
                if isinstance(entry_source, dict) and entry_source.get('title'):
                    src = entry_source['title']

                if title:
                    news.append({
                        'title': title,
                        'link': link,
                        'snippet': summary,
                        'source': src,
                        'published': entry.get('published', ''),
                    })
        except Exception as e:
            logger.warning(f"RSS抓取失败 [{source}]: {url} - {e}")
        return news

    def fetch_all(self) -> Dict[str, Dict[str, List[Dict]]]:
        """
        抓取并分类所有新闻
        返回: {类别: {国内: [...], 国际: [...]}}
        """
        logger.info("开始抓取新闻...")
        result = {}
        for cat in CATEGORY_KEYWORDS:
            result[cat] = {'国内': [], '国际': []}

        # 1) Google News RSS → 国内新闻（按分类）
        for cat, url in GOOGLE_NEWS_RSS.items():
            items = self.fetch_rss(url, f'Google新闻-{cat}')
            result[cat]['国内'] = items[:MAX_NEWS_PER_CATEGORY]
            logger.info(f"  Google News [{cat}]: {len(items)} 条")

        # 2) 国际新闻 RSS（按分类）
        for cat, feeds in INTERNATIONAL_RSS.items():
            intl_items = []
            for url, src in feeds:
                intl_items.extend(self.fetch_rss(url, src))
            # 去重
            seen = set()
            unique = []
            for n in intl_items:
                if n['title'] not in seen:
                    seen.add(n['title'])
                    unique.append(n)
            result[cat]['国际'] = unique[:MAX_NEWS_PER_CATEGORY]
            logger.info(f"  国际 [{cat}]: {len(unique)} 条")

        # 3) 额外中文源 → 根据关键词归入对应类别
        extra_items = []
        for url, src in EXTRA_RSS:
            extra_items.extend(self.fetch_rss(url, src))

        for news in extra_items:
            text = news['title'] + ' ' + news.get('snippet', '')
            for cat, keywords in CATEGORY_KEYWORDS.items():
                matched = any(kw in text for kw in keywords)
                if matched and len(result[cat]['国内']) < MAX_NEWS_PER_CATEGORY:
                    # 检查是否重复
                    existing_titles = {n['title'] for n in result[cat]['国内']}
                    if news['title'] not in existing_titles:
                        result[cat]['国内'].append(news)
                    break

        # 汇总
        total_domestic = sum(len(v['国内']) for v in result.values())
        total_intl = sum(len(v['国际']) for v in result.values())
        logger.info(f"共抓取: 国内 {total_domestic} 条, 国际 {total_intl} 条")

        return result

    def fetch_article(self, url: str) -> str:
        """抓取文章正文"""
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = resp.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            for sel in ['#artibody', '.article-content', '.content', 'article']:
                el = soup.select_one(sel)
                if el:
                    return el.get_text('\n', strip=True)[:3000]
            paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
            return '\n'.join(sorted(paragraphs, key=len, reverse=True)[:15])
        except Exception:
            return ''
