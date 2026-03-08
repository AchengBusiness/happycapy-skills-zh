# HappyCapy 技能目录 · 中文版

> 收录 **56,000+** HappyCapy AI 技能，100% 中文翻译，支持智能搜索与分类筛选。

## v2.0 更新亮点

| 项目 | v1.0 | v2.0 | 变化 |
|------|------|------|------|
| 技能总数 | 62,093 | 56,454 | 去重合并 -9% |
| 中文名称覆盖 | 99.9% | 99.92% | 基本持平 |
| 中文描述覆盖 | 9.8% (6,075个) | **100%** (56,454个) | **+90%** |
| 图标覆盖 | 0% (无此字段) | **99.8%** | **新增功能** |
| 分类数量 | 5个 | **10个** | 更细化 |
| 官方技能 | 3,435 | 2,971 | 去重后减少 |

### 主要升级内容

**1. 中文描述全覆盖**
- 第一版只有 **9.8%** 的技能有中文描述
- 第二版达到 **100%** 全中文描述，彻底告别英文看不懂

**2. 新增图标显示**
- 第一版没有图标，只显示首字母
- 第二版新增 **500+** 品牌图标映射，覆盖率 **99.8%**

**3. 分类更精细**
- 第一版：5个分类（效率、开发、运维、AI、创作）
- 第二版：**10个分类**（新增数据分析、安全防护、媒体处理、办公协作、财务金融）

**4. 数据去重优化**
- 第一版有大量重复技能
- 第二版按 name+author 去重，从 62,093 精简到 **56,454** 个唯一技能

**5. 首屏加载优化**
- 第一版单文件加载，速度慢
- 第二版分两阶段加载：首屏 1000 个官方技能（408KB）+ 后台加载完整数据

**6. 搜索功能增强**
- 支持中英文混合搜索
- 支持多关键词（空格分隔，AND逻辑）
- 支持模糊匹配和首字母缩写

**7. 数据格式优化**
- 第一版：数组格式 `[name, zh_name, ...]`
- 第二版：对象格式 `{name, zh_name, icon, ...}`，更易读易维护

## 功能亮点

- **56,000+ 技能** — 全网最全 HappyCapy 技能目录，去重优化
- **100% 中文** — 技能名称和描述全部翻译成中文
- **99.8% 图标** — 500+ 品牌图标映射，界面更直观
- **十大分类** — 开发编程 / AI & ML / 数据分析 / 运维部署 / 效率工具 / 安全防护 / 媒体处理 / 办公协作 / 内容创作 / 财务金融
- **智能搜索** — 支持中英文、多关键词、模糊匹配、首字母缩写
- **快速加载** — 首屏 1000 个官方技能秒开，完整数据后台加载
- **一键安装** — 所有技能直链 skillsmp.com 安装页
- **深色模式** — 自动跟随系统，全设备适配

## 在线访问

**v2.0 新版（推荐）：**
https://achengbusiness.github.io/happycapy-skills-zh/

**v1.0 旧版：**
https://achengbusiness.github.io/happycapy-skills-zh/happycapy-skills-zh.html

## 文件说明

### v2.0 文件

| 文件 | 说明 |
|------|------|
| `index.html` | v2.0 主页面（推荐使用） |
| `skills_enhanced.json` | 完整数据（56,454 技能，25MB） |
| `skills_initial.json` | 首屏数据（1,000 官方技能，408KB） |

### v1.0 文件（保留）

| 文件 | 说明 |
|------|------|
| `happycapy-skills-zh.html` | v1.0 静态版页面 |
| `skills.json.gz` | v1.0 数据（压缩格式） |
| `app.html` | 动态版前端（配合 server.py） |
| `server.py` | FastAPI 后端，SQLite FTS5 检索 |
| `crawler.py` | 爬虫脚本 |
| `translate.py` | 翻译引擎 |

## 本地部署

```bash
git clone https://github.com/AchengBusiness/happycapy-skills-zh.git
cd happycapy-skills-zh
python -m http.server 8080
# 访问 http://localhost:8080
```

## 数据格式

```json
{
  "version": 5,
  "total": 56454,
  "skills": [
    {
      "name": "slack",
      "zh_name": "Slack 集成",
      "author": "openclaw",
      "desc": "Slack 工作区集成：消息发送、频道管理...",
      "category": "efficiency",
      "url": "https://skillsmp.com/skills/...",
      "stars": 268438,
      "official": 1,
      "icon": "https://cdn.simpleicons.org/slack/4A154B"
    }
  ]
}
```

## 分类说明

| 分类 | 英文 | 数量 |
|------|------|------|
| 开发编程 | dev | 22,926 |
| 效率工具 | efficiency | 6,629 |
| AI & ML | ai | 6,317 |
| 运维部署 | ops | 5,679 |
| 数据分析 | data | 4,254 |
| 媒体处理 | media | 4,001 |
| 内容创作 | create | 3,216 |
| 安全防护 | security | 1,886 |
| 办公协作 | productivity | 894 |
| 财务金融 | finance | 652 |

## 作者

**阿成 · ACheng** · [@AchengBusiness](https://github.com/AchengBusiness) · [@chenchen119967](https://x.com/chenchen119967)

HappyCapy 邀请链接: https://happycapy.ai/signup?invite_ref=aGHAUcHN

---

*数据来源：HappyCapy 公开 API · 仅供学习参考*
