#!/usr/bin/env python3
"""
每日新闻速递 - 自动抓取、分类、总结新闻并生成报告
用法:
    python main.py              # 立即执行一次
    python main.py --schedule   # 定时执行（每天22:00）
    python main.py --time 18:00 # 指定时间定时执行
"""

import os
import argparse
import time
import logging

import schedule

from config import SUMMARIZER_CONFIG, OUTPUT_DIR, SCHEDULE_TIME
from news_fetcher import NewsFetcher
from summarizer import Summarizer
from report_generator import ReportGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('daily_news.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


def run_once():
    """执行一次完整的新闻抓取+总结+报告流程"""
    logger.info("=" * 60)
    logger.info("开始执行每日新闻任务")
    logger.info("=" * 60)

    fetcher = NewsFetcher()
    summarizer = Summarizer(SUMMARIZER_CONFIG)
    report_gen = ReportGenerator(OUTPUT_DIR)

    # 1. 抓取并分类所有新闻
    classified = fetcher.fetch_all()

    # 2. 为每条新闻生成摘要
    logger.info("正在生成AI摘要...")
    for cat, regions in classified.items():
        for region, news_list in regions.items():
            for i, news in enumerate(news_list):
                title = news['title']
                snippet = news.get('snippet', '')
                summary = summarizer.summarize(title, snippet)
                news['summary'] = summary
                logger.info(f"  [{cat}][{region}] #{i+1} {title[:35]}...")
                time.sleep(0.2)

    # 3. 生成报告
    filepath = report_gen.generate(classified)
    logger.info(f"报告已生成: {filepath}")

    # 4. 尝试打开报告
    try:
        os.startfile(os.path.abspath(filepath))
    except Exception:
        pass

    logger.info("=" * 60)
    logger.info("每日新闻任务完成！")
    logger.info("=" * 60)
    return filepath


def main():
    parser = argparse.ArgumentParser(description='每日新闻速递')
    parser.add_argument('--schedule', action='store_true', help='定时执行模式')
    parser.add_argument('--time', type=str, default=SCHEDULE_TIME,
                        help=f'定时执行时间，24小时制，默认 {SCHEDULE_TIME}')
    args = parser.parse_args()

    if args.schedule:
        logger.info(f"启动定时模式，每天 {args.time} 执行")
        schedule.every().day.at(args.time).do(run_once)
        run_once()
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        run_once()


if __name__ == '__main__':
    main()
