import os
import json
from datetime import datetime
from typing import Dict, List
from jinja2 import Template

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日新闻速递 - {{ date }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
                         "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: #0f0f1a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px 16px; }

        /* ========== 顶部标题 ========== */
        .header {
            text-align: center;
            padding: 30px 20px 20px;
        }
        .header h1 {
            font-size: 2em;
            background: linear-gradient(90deg, #f093fb, #f5576c, #fda085);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }
        .header .date { font-size: 0.95em; color: #888; }

        /* ========== 分类标签栏 ========== */
        .cat-tabs {
            display: flex;
            gap: 6px;
            padding: 16px 0;
            overflow-x: auto;
            justify-content: center;
        }
        .cat-tab {
            padding: 10px 22px;
            border-radius: 24px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            white-space: nowrap;
            background: rgba(255,255,255,0.06);
            color: #aaa;
            border: 1px solid transparent;
            transition: all 0.25s;
            user-select: none;
        }
        .cat-tab:hover { background: rgba(255,255,255,0.12); color: #ddd; }
        .cat-tab.active {
            background: linear-gradient(135deg, rgba(245,87,108,0.25), rgba(240,147,251,0.2));
            color: #fff;
            border-color: rgba(245,87,108,0.5);
        }

        /* ========== 内容面板 ========== */
        .panel { display: none; }
        .panel.active { display: block; }

        /* ========== 国内/国际切换 ========== */
        .region-bar {
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 4px;
        }
        .region-btn {
            flex: 1;
            text-align: center;
            padding: 10px;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.95em;
            color: #888;
            transition: all 0.2s;
            user-select: none;
        }
        .region-btn.active {
            background: rgba(245,87,108,0.2);
            color: #f5576c;
        }
        .region-btn:hover:not(.active) { color: #ccc; }
        .region-btn .count {
            display: inline-block;
            min-width: 20px;
            height: 20px;
            line-height: 20px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            font-size: 0.75em;
            margin-left: 4px;
            padding: 0 6px;
        }
        .region-btn.active .count {
            background: rgba(245,87,108,0.3);
        }

        /* ========== 新闻列表 ========== */
        .news-feed { }
        .news-card {
            background: rgba(255,255,255,0.04);
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 14px;
            border: 1px solid rgba(255,255,255,0.06);
            transition: border-color 0.2s;
        }
        .news-card:hover { border-color: rgba(245,87,108,0.3); }
        .news-top {
            display: flex;
            align-items: flex-start;
            gap: 14px;
        }
        .news-rank {
            flex-shrink: 0;
            width: 30px;
            height: 30px;
            line-height: 30px;
            text-align: center;
            border-radius: 8px;
            font-size: 0.85em;
            font-weight: 700;
            color: #fff;
        }
        .rank-1 { background: linear-gradient(135deg, #f5576c, #ff6b6b); }
        .rank-2 { background: linear-gradient(135deg, #f093fb, #c56cf0); }
        .rank-3 { background: linear-gradient(135deg, #4facfe, #00f2fe); }
        .rank-other { background: rgba(255,255,255,0.12); }
        .news-body { flex: 1; min-width: 0; }
        .news-title {
            font-size: 1.08em;
            font-weight: 600;
            color: #fff;
            text-decoration: none;
            line-height: 1.55;
            display: block;
            margin-bottom: 6px;
        }
        .news-title:hover { color: #f5576c; }
        .news-meta {
            font-size: 0.8em;
            color: #666;
            margin-bottom: 10px;
        }
        .news-meta .source-tag {
            display: inline-block;
            padding: 1px 8px;
            border-radius: 4px;
            background: rgba(255,255,255,0.08);
            margin-right: 6px;
        }
        .news-snippet {
            font-size: 0.9em;
            color: #999;
            line-height: 1.7;
            margin-bottom: 12px;
            padding-left: 12px;
            border-left: 3px solid rgba(255,255,255,0.1);
        }
        .news-summary {
            font-size: 0.9em;
            line-height: 1.7;
            padding: 12px 14px;
            background: rgba(245,87,108,0.06);
            border-radius: 10px;
            border-left: 3px solid rgba(245,87,108,0.5);
            color: #d4a0ab;
        }
        .news-summary::before {
            content: "总结 ";
            font-weight: bold;
            color: #f5576c;
        }
        .empty-msg {
            text-align: center;
            padding: 50px 20px;
            color: #555;
            font-size: 0.95em;
        }
        .footer {
            text-align: center;
            padding: 30px 20px;
            color: #444;
            font-size: 0.85em;
        }
        @media (max-width: 600px) {
            .header h1 { font-size: 1.5em; }
            .cat-tabs { gap: 4px; padding: 12px 0; }
            .cat-tab { padding: 8px 14px; font-size: 0.9em; }
            .news-card { padding: 14px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>每日新闻速递</h1>
            <div class="date">{{ date }} {{ weekday }} · 晚间更新</div>
        </div>

        <!-- 顶部分类标签 -->
        <div class="cat-tabs">
            {% for cat_name in categories.keys() %}
            <div class="cat-tab {{ 'active' if loop.first }}" onclick="switchCat('{{ cat_name }}')">
                {{ category_icons.get(cat_name, '') }} {{ cat_name }}
            </div>
            {% endfor %}
        </div>

        <!-- 各分类面板 -->
        {% for cat_name, regions in categories.items() %}
        <div class="panel {{ 'active' if loop.first }}" id="panel-{{ cat_name }}">
            <div class="region-bar">
                <div class="region-btn active" onclick="switchRegion(this, '{{ cat_name }}', 'domestic')">
                    国内<span class="count">{{ regions['国内']|length }}</span>
                </div>
                <div class="region-btn" onclick="switchRegion(this, '{{ cat_name }}', 'intl')">
                    国际<span class="count">{{ regions['国际']|length }}</span>
                </div>
            </div>

            <div class="news-feed" id="feed-{{ cat_name }}-domestic">
                {% if regions['国内'] %}
                    {% for news in regions['国内'] %}
                    <div class="news-card">
                        <div class="news-top">
                            <span class="news-rank {{ 'rank-' + loop.index|string if loop.index <= 3 else 'rank-other' }}">{{ loop.index }}</span>
                            <div class="news-body">
                                <a class="news-title" href="{{ news.link }}" target="_blank">{{ news.title }}</a>
                                <div class="news-meta">
                                    <span class="source-tag">{{ news.source }}</span>
                                    {% if news.published %}{{ news.published }}{% endif %}
                                </div>
                                {% if news.snippet %}
                                <div class="news-snippet">{{ news.snippet }}</div>
                                {% endif %}
                                <div class="news-summary">{{ news.summary }}</div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-msg">暂无国内{{ cat_name }}新闻</div>
                {% endif %}
            </div>

            <div class="news-feed" id="feed-{{ cat_name }}-intl" style="display:none">
                {% if regions['国际'] %}
                    {% for news in regions['国际'] %}
                    <div class="news-card">
                        <div class="news-top">
                            <span class="news-rank {{ 'rank-' + loop.index|string if loop.index <= 3 else 'rank-other' }}">{{ loop.index }}</span>
                            <div class="news-body">
                                <a class="news-title" href="{{ news.link }}" target="_blank">{{ news.title }}</a>
                                <div class="news-meta">
                                    <span class="source-tag">{{ news.source }}</span>
                                    {% if news.published %}{{ news.published }}{% endif %}
                                </div>
                                {% if news.snippet %}
                                <div class="news-snippet">{{ news.snippet }}</div>
                                {% endif %}
                                <div class="news-summary">{{ news.summary }}</div>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                {% else %}
                    <div class="empty-msg">暂无国际{{ cat_name }}新闻</div>
                {% endif %}
            </div>
        </div>
        {% endfor %}

        <div class="footer">
            自动生成于 {{ datetime_str }} · 数据来源：腾讯新闻、央视新闻、澎湃、BBC中文、路透社等
        </div>
    </div>

    <script>
    function switchCat(name) {
        document.querySelectorAll('.cat-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
        // 激活对应标签和面板
        event.target.closest('.cat-tab').classList.add('active');
        document.getElementById('panel-' + name).classList.add('active');
    }
    function switchRegion(btn, cat, region) {
        var bar = btn.closest('.region-bar');
        bar.querySelectorAll('.region-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        var panel = btn.closest('.panel');
        panel.querySelectorAll('.news-feed').forEach(f => f.style.display = 'none');
        document.getElementById('feed-' + cat + '-' + region).style.display = 'block';
    }
    </script>
</body>
</html>
"""

WEEKDAYS = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
CATEGORY_ICONS = {
    '科技': '',
    '政治': '⚖️',
    '军事': '️',
    '娱乐': ' ',
    '金融': ' ',
}


class ReportGenerator:
    """生成HTML格式的新闻报告"""

    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, classified_news: Dict[str, Dict[str, List[Dict]]]) -> str:
        """生成HTML报告，返回文件路径"""
        now = datetime.now()
        date_str = now.strftime('%Y年%m月%d日')
        weekday = WEEKDAYS[now.weekday()]
        datetime_str = now.strftime('%Y-%m-%d %H:%M:%S')

        template = Template(REPORT_TEMPLATE)
        html = template.render(
            date=date_str,
            weekday=weekday,
            categories=classified_news,
            category_icons=CATEGORY_ICONS,
            datetime_str=datetime_str,
        )

        # 保存HTML文件
        filename = f"daily_news_{now.strftime('%Y%m%d_%H%M')}.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        # 同时保存一份latest
        latest_path = os.path.join(self.output_dir, 'latest.html')
        with open(latest_path, 'w', encoding='utf-8') as f:
            f.write(html)

        # 保存JSON数据
        json_path = os.path.join(self.output_dir, f"news_{now.strftime('%Y%m%d')}.json")
        self._save_json(classified_news, json_path)

        return filepath

    def _save_json(self, classified_news: Dict, filepath: str):
        """保存JSON格式的数据"""
        data = {}
        for cat, regions in classified_news.items():
            data[cat] = {}
            for region, news_list in regions.items():
                data[cat][region] = [
                    {k: v for k, v in news.items()}
                    for news in news_list
                ]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
