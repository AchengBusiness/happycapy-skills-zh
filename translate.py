"""
Translate skill names to Chinese in the SQLite DB.
Runs in background, can be called repeatedly (idempotent).
"""
import sqlite3, re, sys

DB_PATH = '/tmp/skills-db/skills.db'

# ============================================================
# Exact overrides (en_name lowercase → zh_name)
# ============================================================
OVERRIDES = {
    # Anthropic / Claude
    'claude code': 'Claude 代码助手',
    'claude': 'Claude AI 助手',
    'anthropic': 'Anthropic AI',
    # OpenAI
    'openai': 'OpenAI 接口',
    'chatgpt': 'ChatGPT 助手',
    'gpt': 'GPT 语言模型',
    'dall-e': 'DALL-E 图像生成',
    'whisper': 'Whisper 语音识别',
    # Google
    'gemini': 'Gemini AI 模型',
    'google': 'Google 服务',
    'gmail': 'Gmail 邮件',
    'google drive': 'Google Drive 云盘',
    'google docs': 'Google Docs 文档',
    'google sheets': 'Google Sheets 表格',
    'google calendar': 'Google 日历',
    'google maps': 'Google 地图',
    'google analytics': 'Google 分析',
    'google search': 'Google 搜索',
    'google cloud': 'Google 云服务',
    'google bigquery': 'Google BigQuery',
    'youtube': 'YouTube 视频',
    # Microsoft
    'microsoft': 'Microsoft 服务',
    'azure': 'Azure 云服务',
    'github': 'GitHub 代码托管',
    'github actions': 'GitHub Actions CI/CD',
    'copilot': 'Copilot AI 助手',
    'teams': 'Teams 协作工具',
    'office 365': 'Office 365',
    'onedrive': 'OneDrive 云盘',
    'outlook': 'Outlook 邮件',
    'sharepoint': 'SharePoint 协作',
    'power bi': 'Power BI 数据可视化',
    'power automate': 'Power Automate 自动化',
    'excel': 'Excel 电子表格',
    'word': 'Word 文档处理',
    'powerpoint': 'PowerPoint 演示',
    # AWS
    'aws': 'AWS 亚马逊云',
    'amazon': 'Amazon 服务',
    's3': 'S3 对象存储',
    'lambda': 'Lambda 无服务器函数',
    'ec2': 'EC2 云服务器',
    'rds': 'RDS 关系型数据库',
    'dynamodb': 'DynamoDB NoSQL 数据库',
    'cloudfront': 'CloudFront CDN',
    'sagemaker': 'SageMaker 机器学习',
    'bedrock': 'Bedrock AI 服务',
    # Vercel / Next.js
    'vercel': 'Vercel 部署平台',
    'nextjs': 'Next.js 全栈框架',
    'next.js': 'Next.js 全栈框架',
    # Social / Communication
    'slack': 'Slack 团队协作',
    'discord': 'Discord 社区聊天',
    'telegram': 'Telegram 即时通讯',
    'twitter': 'Twitter/X 社交媒体',
    'x (twitter)': 'X(Twitter) 社交媒体',
    'instagram': 'Instagram 图片社交',
    'linkedin': 'LinkedIn 职业社交',
    'facebook': 'Facebook 社交平台',
    'whatsapp': 'WhatsApp 即时通讯',
    'tiktok': 'TikTok 短视频',
    'reddit': 'Reddit 社区论坛',
    'youtube': 'YouTube 视频平台',
    # Dev tools
    'git': 'Git 版本控制',
    'docker': 'Docker 容器化',
    'kubernetes': 'Kubernetes 容器编排',
    'k8s': 'Kubernetes 容器编排',
    'terraform': 'Terraform 基础设施',
    'ansible': 'Ansible 自动化运维',
    'jenkins': 'Jenkins CI/CD',
    'circleci': 'CircleCI 持续集成',
    'gitlab': 'GitLab 代码平台',
    'bitbucket': 'Bitbucket 代码托管',
    'jira': 'Jira 项目管理',
    'confluence': 'Confluence 知识库',
    'notion': 'Notion 工作空间',
    'airtable': 'Airtable 数据库表格',
    'trello': 'Trello 看板工具',
    'asana': 'Asana 任务管理',
    'linear': 'Linear 工程管理',
    'figma': 'Figma 界面设计',
    'postman': 'Postman API 调试',
    'vscode': 'VS Code 编辑器',
    # Databases
    'postgresql': 'PostgreSQL 数据库',
    'postgres': 'PostgreSQL 数据库',
    'mysql': 'MySQL 数据库',
    'mongodb': 'MongoDB 文档数据库',
    'redis': 'Redis 缓存数据库',
    'sqlite': 'SQLite 轻量数据库',
    'elasticsearch': 'Elasticsearch 搜索引擎',
    'supabase': 'Supabase 后端即服务',
    'firebase': 'Firebase 实时数据库',
    'prisma': 'Prisma ORM',
    # AI / ML
    'langchain': 'LangChain AI 框架',
    'langsmith': 'LangSmith 调试平台',
    'langgraph': 'LangGraph 流程编排',
    'llamaindex': 'LlamaIndex 数据框架',
    'huggingface': 'HuggingFace 模型库',
    'hugging face': 'HuggingFace 模型库',
    'pytorch': 'PyTorch 深度学习',
    'tensorflow': 'TensorFlow 机器学习',
    'keras': 'Keras 深度学习',
    'openai api': 'OpenAI API 接口',
    'midjourney': 'Midjourney 图像生成',
    'stable diffusion': 'Stable Diffusion 图像生成',
    'ollama': 'Ollama 本地大模型',
    'mistral': 'Mistral AI 模型',
    'llama': 'Llama 开源模型',
    'pinecone': 'Pinecone 向量数据库',
    'weaviate': 'Weaviate 向量数据库',
    'chroma': 'Chroma 向量数据库',
    'crewai': 'CrewAI 多智能体',
    'autogen': 'AutoGen 多智能体',
    # Frontend
    'react': 'React 前端框架',
    'vue': 'Vue.js 前端框架',
    'vue.js': 'Vue.js 前端框架',
    'angular': 'Angular 前端框架',
    'svelte': 'Svelte 前端框架',
    'tailwind': 'Tailwind CSS 样式',
    'tailwindcss': 'Tailwind CSS 样式',
    'typescript': 'TypeScript 类型语言',
    'javascript': 'JavaScript 脚本语言',
    'nodejs': 'Node.js 运行环境',
    'node.js': 'Node.js 运行环境',
    # Backend / API
    'fastapi': 'FastAPI 高性能 API',
    'django': 'Django Web 框架',
    'flask': 'Flask 轻量框架',
    'express': 'Express.js 后端框架',
    'nestjs': 'NestJS 后端框架',
    'graphql': 'GraphQL 接口查询',
    'grpc': 'gRPC 远程调用',
    'rest api': 'REST API 设计',
    'stripe': 'Stripe 支付处理',
    # Data
    'pandas': 'Pandas 数据分析',
    'numpy': 'NumPy 数值计算',
    'jupyter': 'Jupyter 交互笔记',
    'streamlit': 'Streamlit 数据应用',
    'grafana': 'Grafana 监控看板',
    'prometheus': 'Prometheus 监控指标',
    'nginx': 'Nginx Web 服务器',
    'apache': 'Apache Web 服务器',
    'cloudflare': 'Cloudflare CDN 安全',
    'netlify': 'Netlify 前端部署',
    'heroku': 'Heroku 应用平台',
    'sentry': 'Sentry 错误追踪',
    'datadog': 'Datadog 监控平台',
    'twilio': 'Twilio 通讯服务',
    'sendgrid': 'SendGrid 邮件服务',
    'resend': 'Resend 邮件发送',
    'shopify': 'Shopify 电商平台',
    'wordpress': 'WordPress 内容管理',
    'contentful': 'Contentful 内容平台',
    'sanity': 'Sanity 内容管理',
    'webflow': 'Webflow 无代码建站',
    'python': 'Python 编程语言',
    'rust': 'Rust 系统编程',
    'golang': 'Go 语言编程',
    'go': 'Go 语言编程',
    'java': 'Java 编程语言',
    'kotlin': 'Kotlin 编程语言',
    'swift': 'Swift 编程语言',
    'php': 'PHP 编程语言',
    'ruby': 'Ruby 编程语言',
    'rails': 'Ruby on Rails 框架',
    'scala': 'Scala 编程语言',
    'elixir': 'Elixir 编程语言',
    'haskell': 'Haskell 函数式编程',
    'r': 'R 统计语言',
    'matlab': 'MATLAB 科学计算',
    'bash': 'Bash 脚本编程',
    'shell': 'Shell 脚本编程',
    'powershell': 'PowerShell 自动化',
    'lua': 'Lua 脚本语言',
    'dart': 'Dart 编程语言',
    'flutter': 'Flutter 跨平台开发',
    'react native': 'React Native 移动开发',
    'expo': 'Expo 移动开发',
    'android': 'Android 移动开发',
    'ios': 'iOS 移动开发',
    'unity': 'Unity 游戏引擎',
    'unreal': 'Unreal Engine 游戏引擎',
    'blender': 'Blender 3D 建模',
    'three.js': 'Three.js 3D 渲染',
    'threejs': 'Three.js 3D 渲染',
    'webgl': 'WebGL 图形渲染',
    'ffmpeg': 'FFmpeg 视频处理',
    'imagemagick': 'ImageMagick 图像处理',
    'mcp': 'MCP 模型上下文协议',
    'playwright': 'Playwright 浏览器自动化',
    'selenium': 'Selenium 自动化测试',
    'jest': 'Jest 单元测试',
    'pytest': 'Pytest 测试框架',
    'webpack': 'Webpack 模块打包',
    'vite': 'Vite 前端构建',
    'auth0': 'Auth0 身份认证',
    'oauth': 'OAuth 授权协议',
    'jwt': 'JWT 令牌认证',
    'kafka': 'Kafka 消息队列',
    'rabbitmq': 'RabbitMQ 消息中间件',
    'celery': 'Celery 任务队列',
    'airflow': 'Apache Airflow 工作流',
    'opentelemetry': 'OpenTelemetry 可观测性',
    'vault': 'HashiCorp Vault 密钥管理',
    'pagerduty': 'PagerDuty 告警管理',
    'linear': 'Linear 工程管理',
    'clickup': 'ClickUp 项目管理',
    'monday': 'Monday.com 工作管理',
    'zendesk': 'Zendesk 客服系统',
    'intercom': 'Intercom 客户沟通',
    'hubspot': 'HubSpot CRM',
    'salesforce': 'Salesforce CRM',
    'mailchimp': 'Mailchimp 邮件营销',
    'segment': 'Segment 数据集成',
    'mixpanel': 'Mixpanel 用户分析',
    'amplitude': 'Amplitude 产品分析',
    'posthog': 'PostHog 产品分析',
    'plaid': 'Plaid 金融数据',
    'composio': 'Composio 工具集成',
    'tavily': 'Tavily AI 搜索',
    'perplexity': 'Perplexity AI 搜索',
    'exa': 'Exa 语义搜索',
    'firecrawl': 'Firecrawl 网页抓取',
    'browserbase': 'BrowserBase 浏览器自动化',
    'stagehand': 'Stagehand 浏览器 AI',
    'apify': 'Apify 网页爬取平台',
    'bright data': 'Bright Data 数据采集',
    'oxylabs': 'Oxylabs 代理服务',
}

# ============================================================
# Word-by-word dictionary
# ============================================================
WORD_MAP = {
    # Action verbs
    'search': '搜索', 'find': '查找', 'get': '获取', 'fetch': '抓取',
    'create': '创建', 'generate': '生成', 'build': '构建', 'make': '创建',
    'update': '更新', 'edit': '编辑', 'modify': '修改', 'change': '更改',
    'delete': '删除', 'remove': '移除', 'clean': '清理', 'clear': '清除',
    'send': '发送', 'post': '发布', 'publish': '发布', 'share': '分享',
    'read': '读取', 'write': '写入', 'save': '保存', 'store': '存储',
    'load': '加载', 'import': '导入', 'export': '导出', 'sync': '同步',
    'run': '运行', 'execute': '执行', 'deploy': '部署', 'launch': '启动',
    'start': '启动', 'stop': '停止', 'restart': '重启', 'kill': '终止',
    'monitor': '监控', 'track': '追踪', 'watch': '监视', 'check': '检查',
    'analyze': '分析', 'parse': '解析', 'process': '处理', 'transform': '转换',
    'convert': '转换', 'format': '格式化', 'validate': '验证', 'test': '测试',
    'debug': '调试', 'fix': '修复', 'resolve': '解决', 'patch': '修补',
    'install': '安装', 'setup': '设置', 'configure': '配置', 'init': '初始化',
    'connect': '连接', 'integrate': '集成', 'link': '链接', 'bind': '绑定',
    'manage': '管理', 'control': '控制', 'handle': '处理', 'operate': '操作',
    'schedule': '调度', 'automate': '自动化', 'orchestrate': '编排',
    'optimize': '优化', 'improve': '提升', 'enhance': '增强', 'boost': '加速',
    'summarize': '摘要', 'translate': '翻译', 'classify': '分类', 'detect': '检测',
    'extract': '提取', 'scrape': '抓取', 'crawl': '爬取', 'collect': '收集',
    'upload': '上传', 'download': '下载', 'backup': '备份', 'restore': '恢复',
    'compress': '压缩', 'encrypt': '加密', 'decrypt': '解密', 'hash': '哈希',
    'sign': '签名', 'verify': '验证', 'authenticate': '认证', 'authorize': '授权',
    'notify': '通知', 'alert': '告警', 'report': '报告', 'log': '日志',
    'list': '列举', 'view': '查看', 'show': '展示', 'display': '显示',
    'filter': '过滤', 'sort': '排序', 'paginate': '分页', 'query': '查询',
    'calculate': '计算', 'count': '统计', 'sum': '求和', 'aggregate': '聚合',
    'predict': '预测', 'recommend': '推荐', 'suggest': '建议', 'answer': '回答',
    'chat': '对话', 'ask': '询问', 'interview': '面试', 'review': '审查',
    'draft': '起草', 'compose': '撰写', 'write': '写作', 'generate': '生成',
    'resize': '调整大小', 'crop': '裁剪', 'compress': '压缩', 'convert': '转换',
    'stream': '流式', 'record': '录制', 'capture': '捕获', 'screenshot': '截图',
    'scan': '扫描', 'ocr': 'OCR识别', 'recognize': '识别', 'transcribe': '转录',
    'clone': '克隆', 'fork': '分叉', 'merge': '合并', 'rebase': '变基',
    'commit': '提交', 'push': '推送', 'pull': '拉取', 'diff': '比较差异',
    # Nouns - Tech
    'agent': '智能代理', 'agents': '智能代理', 'assistant': '助手',
    'bot': '机器人', 'chatbot': '聊天机器人', 'automation': '自动化',
    'workflow': '工作流', 'pipeline': '流水线', 'integration': '集成',
    'api': 'API 接口', 'webhook': 'Webhook 回调', 'sdk': 'SDK 工具包',
    'cli': 'CLI 命令行', 'tool': '工具', 'tools': '工具集', 'plugin': '插件',
    'extension': '扩展', 'addon': '附件', 'module': '模块', 'package': '包',
    'library': '库', 'framework': '框架', 'platform': '平台', 'service': '服务',
    'server': '服务器', 'client': '客户端', 'app': '应用', 'application': '应用',
    'dashboard': '仪表盘', 'interface': '界面', 'ui': '用户界面', 'ux': '用户体验',
    'database': '数据库', 'storage': '存储', 'cache': '缓存', 'queue': '队列',
    'model': '模型', 'models': '模型', 'llm': '大语言模型', 'ai': 'AI 智能',
    'ml': '机器学习', 'data': '数据', 'analytics': '分析', 'metrics': '指标',
    'monitor': '监控', 'monitoring': '监控', 'logging': '日志', 'tracing': '追踪',
    'security': '安全', 'auth': '认证', 'authentication': '身份认证',
    'authorization': '权限控制', 'permission': '权限', 'role': '角色',
    'email': '邮件', 'notification': '通知', 'message': '消息', 'sms': '短信',
    'file': '文件', 'files': '文件', 'document': '文档', 'documents': '文档',
    'image': '图像', 'images': '图像', 'photo': '照片', 'video': '视频',
    'audio': '音频', 'pdf': 'PDF 文档', 'csv': 'CSV 数据', 'excel': 'Excel 表格',
    'code': '代码', 'coding': '编程', 'programming': '编程', 'developer': '开发者',
    'deployment': '部署', 'infrastructure': '基础设施', 'cloud': '云服务',
    'container': '容器', 'microservice': '微服务', 'serverless': '无服务器',
    'network': '网络', 'firewall': '防火墙', 'proxy': '代理', 'load': '负载',
    'balancer': '均衡器', 'gateway': '网关', 'router': '路由',
    'test': '测试', 'testing': '测试', 'unit': '单元', 'e2e': '端到端',
    'report': '报告', 'reports': '报告', 'summary': '摘要', 'digest': '摘要',
    'search': '搜索', 'scraper': '爬虫', 'crawler': '网络爬虫',
    'payment': '支付', 'billing': '账单', 'invoice': '发票', 'subscription': '订阅',
    'calendar': '日历', 'event': '事件', 'meeting': '会议', 'reminder': '提醒',
    'task': '任务', 'tasks': '任务', 'todo': '待办事项', 'project': '项目',
    'ticket': '工单', 'issue': '问题', 'bug': '缺陷', 'feature': '功能',
    'documentation': '文档', 'docs': '文档', 'readme': '说明文档',
    'comment': '注释', 'review': '代码审查', 'pr': '拉取请求',
    'repository': '代码仓库', 'repo': '代码仓库', 'branch': '分支',
    'release': '发布', 'version': '版本', 'changelog': '更新日志',
    'user': '用户', 'users': '用户', 'account': '账户', 'profile': '资料',
    'team': '团队', 'organization': '组织', 'company': '公司',
    'customer': '客户', 'contact': '联系人', 'lead': '潜在客户',
    'post': '帖子', 'content': '内容', 'blog': '博客', 'article': '文章',
    'comment': '评论', 'reply': '回复', 'thread': '线程', 'channel': '频道',
    'room': '房间', 'group': '群组', 'community': '社区',
    'chart': '图表', 'graph': '图形', 'visualization': '可视化',
    'map': '地图', 'location': '位置', 'address': '地址', 'geo': '地理',
    'weather': '天气', 'news': '新闻', 'feed': '信息流', 'rss': 'RSS 订阅',
    'translation': '翻译', 'language': '语言', 'locale': '本地化',
    'price': '价格', 'stock': '股票', 'crypto': '加密货币', 'finance': '金融',
    'health': '健康', 'fitness': '健身', 'medical': '医疗', 'doctor': '医生',
    'education': '教育', 'course': '课程', 'quiz': '测验', 'learning': '学习',
    'recipe': '菜谱', 'food': '食物', 'restaurant': '餐厅', 'travel': '旅行',
    'flight': '航班', 'hotel': '酒店', 'booking': '预订', 'reservation': '预约',
    'ecommerce': '电子商务', 'shop': '商店', 'product': '产品', 'order': '订单',
    'inventory': '库存', 'warehouse': '仓库', 'shipping': '物流',
    # Modifiers / Adjectives
    'smart': '智能', 'intelligent': '智能', 'advanced': '高级', 'enhanced': '增强',
    'automated': '自动化', 'automatic': '自动', 'realtime': '实时', 'real-time': '实时',
    'instant': '即时', 'fast': '快速', 'quick': '快速', 'rapid': '快速',
    'easy': '简易', 'simple': '简单', 'powerful': '强大', 'flexible': '灵活',
    'secure': '安全', 'private': '私密', 'public': '公开', 'open': '开放',
    'free': '免费', 'premium': '高级版', 'pro': '专业版', 'enterprise': '企业版',
    'multi': '多', 'cross': '跨', 'full': '全', 'complete': '完整',
    'custom': '自定义', 'dynamic': '动态', 'static': '静态', 'live': '实时',
    'personal': '个人', 'team': '团队', 'shared': '共享', 'collaborative': '协作',
    # Common prefixes
    'auto': '自动', 'batch': '批量', 'bulk': '批量', 'mass': '批量',
    'daily': '每日', 'weekly': '每周', 'monthly': '每月',
    'open': '开放', 'closed': '封闭', 'private': '私有',
    'web': 'Web 网页', 'mobile': '移动端', 'desktop': '桌面端',
}

# ============================================================
# Translate one skill name
# ============================================================
def translate_name(name: str) -> str:
    if not name:
        return '未命名工具'

    nl = name.lower().strip()

    # 1. Exact override
    if nl in OVERRIDES:
        return OVERRIDES[nl]

    # 2. Check if already has CJK
    if re.search(r'[\u4e00-\u9fff\u3000-\u303f]', name):
        return name

    # 3. Try word-by-word
    # Split on spaces, dashes, underscores, dots (but keep them for context)
    parts = re.split(r'[\s\-_/|:,]+', name)
    translated_parts = []
    for part in parts:
        p_lower = part.lower()
        if p_lower in WORD_MAP:
            translated_parts.append(WORD_MAP[p_lower])
        elif p_lower in OVERRIDES:
            translated_parts.append(OVERRIDES[p_lower])
        else:
            translated_parts.append(part)

    result = ' '.join(translated_parts)

    # 4. If result still has no CJK, add category-based suffix or wrap
    if not re.search(r'[\u4e00-\u9fff]', result):
        # Just append 工具
        return name + ' 工具'

    return result


# ============================================================
# Main: translate untranslated skills in DB
# ============================================================
def run_translation():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get skills without Chinese translation
    rows = c.execute(
        "SELECT id, name, description, category FROM skills WHERE zh_name IS NULL OR zh_name = '' OR zh_name = name"
    ).fetchall()

    print(f'Skills needing translation: {len(rows)}', flush=True)

    updated = 0
    for i, (sid, name, desc, cat) in enumerate(rows):
        zh = translate_name(name)
        c.execute('UPDATE skills SET zh_name = ? WHERE id = ?', (zh, sid))
        updated += 1

        if i % 1000 == 0:
            conn.commit()
            print(f'  [{i}/{len(rows)}] translated...', flush=True)

    conn.commit()
    print(f'Done! Translated {updated} skills.', flush=True)
    conn.close()


if __name__ == '__main__':
    run_translation()
