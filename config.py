"""每日新闻应用配置文件"""

# ==================== 摘要引擎配置 ====================
SUMMARIZER_CONFIG = {
    'summarizer_backend': 'local',  # 'claude' | 'openai' | 'local'

    # ---- Claude API 配置 ----
    # 'api_key': 'sk-ant-xxx',
    # 'model': 'claude-sonnet-4-6',

    # ---- OpenAI 兼容API 配置 ----
    # 'api_key': 'sk-xxx',
    # 'api_base': 'https://api.deepseek.com/v1',
    # 'model': 'deepseek-chat',
}

# ==================== 输出配置 ====================
OUTPUT_DIR = 'output'
MAX_NEWS_PER_CATEGORY = 10
SCHEDULE_TIME = '22:00'

# ==================== Google News RSS（国内新闻主力源）====================
# 按分类搜索关键词，hl=zh-CN&gl=CN 确保返回中文结果
GOOGLE_NEWS_RSS = {
    '科技': 'https://news.google.com/rss/search?q=%E7%A7%91%E6%8A%80&hl=zh-CN&gl=CN&ceid=CN:zh-Hans',
    '政治': 'https://news.google.com/rss/search?q=%E6%94%BF%E6%B2%BB&hl=zh-CN&gl=CN&ceid=CN:zh-Hans',
    '军事': 'https://news.google.com/rss/search?q=%E5%86%9B%E4%BA%8B&hl=zh-CN&gl=CN&ceid=CN:zh-Hans',
    '娱乐': 'https://news.google.com/rss/search?q=%E5%A8%B1%E4%B9%90&hl=zh-CN&gl=CN&ceid=CN:zh-Hans',
    '金融': 'https://news.google.com/rss/search?q=%E8%B4%A2%E7%BB%8F&hl=zh-CN&gl=CN&ceid=CN:zh-Hans',
}

# ==================== 国际新闻 RSS ====================
INTERNATIONAL_RSS = {
    '科技': [
        ('https://feeds.arstechnica.com/arstechnica/index', 'ArsTechnica'),
        ('https://feeds.feedburner.com/TechCrunch/', 'TechCrunch'),
    ],
    '政治': [
        ('https://feeds.bbci.co.uk/zhongwen/simp/rss.xml', 'BBC中文'),
        ('https://rsshub.app/reuters/world', '路透社'),
    ],
    '军事': [
        ('https://rsshub.app/defensenews/navy', '防务新闻'),
    ],
    '娱乐': [
        ('https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml', 'BBC娱乐'),
    ],
    '金融': [
        ('https://rsshub.app/reuters/business', '路透社财经'),
    ],
}

# ==================== 其他可用中文源 ====================
EXTRA_RSS = [
    ('https://36kr.com/feed', '36氪'),
    ('https://rsshub.app/36kr/newsflashes', '36氪快讯'),
]

# ==================== 分类关键词（用于将未分类新闻归入合适类别）====================
CATEGORY_KEYWORDS = {
    '科技': [
        '科技', '技术', 'AI', '人工智能', '芯片', '半导体', '手机', '互联网',
        '5G', '6G', '量子', '机器人', '新能源', '自动驾驶', '大模型',
        'Tech', 'iPhone', 'Google', 'Apple', 'Tesla', 'SpaceX', 'NASA',
        '卫星', '火箭', '航天', '软件', '硬件', '数据', '云计算',
        'GPT', 'OpenAI', '英伟达', 'NVIDIA', '华为', '小米', '比亚迪',
    ],
    '政治': [
        '政治', '政府', '国务院', '人大', '政协', '外交', '选举',
        '总统', '总理', '国会', '议会', '政策', '法案', '制裁',
        '协议', '谈判', '峰会', '访问', '表态', '声明', '联合国',
        '台海', '台湾', '欧盟', '北约', '日本', '韩国',
    ],
    '军事': [
        '军事', '军队', '武器', '导弹', '航母', '战斗机', '坦克',
        '军演', '国防', '战争', '冲突', '部队', '军费', '解放军',
        '海军', '空军', '核武器', '弹道', '潜艇', '俄乌', '巴以',
    ],
    '娱乐': [
        '娱乐', '明星', '电影', '电视剧', '综艺', '音乐', '演员',
        '导演', '票房', '颁奖', '游戏', '电竞', '直播', '网红',
        '演唱会', '专辑', '选秀', '偶像', '粉丝', 'NBA', '足球',
    ],
    '金融': [
        '金融', '股市', '股票', 'A股', '美股', '港股', '基金',
        '期货', '债券', '汇率', '利率', '央行', '降息', '加息',
        '银行', '投资', '融资', 'IPO', '上市', '经济', '通胀',
        '比特币', '黄金', '石油', '房产', '美联储', '人民币',
    ],
}

# HTTP请求配置
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}
