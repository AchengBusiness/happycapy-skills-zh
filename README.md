# HappyCapy 技能目录 · 中文版

> 收录 30,000+ HappyCapy AI 沙箱技能，全部翻译成中文，支持实时搜索与一键安装。

## 功能亮点

- **30,000+ 技能** — 全网最全 HappyCapy 技能目录
- **中英文搜索** — FTS5 全文检索，毫秒级响应
- **五大分类** — 效率工具 / 开发编程 / AI & 数据 / 系统运维 / 内容创作
- **一键安装** — 所有技能直链 skillsmp.com 安装页，点击即跳转
- **官方技能标识** — 特别标注官方出品技能
- **深色模式** — 自动跟随系统，全设备适配
- **PWA 支持** — 可添加到桌面

## 在线访问

**GitHub Pages（静态版）：**
https://achengbusiness.github.io/happycapy-skills-zh/

## 本地部署（完整版，含实时搜索后端）

```bash
git clone https://github.com/AchengBusiness/happycapy-skills-zh.git
cd happycapy-skills-zh
pip install fastapi uvicorn
python crawler.py      # 爬取技能数据（约 1-2 小时）
python translate.py    # 翻译技能名称
python server.py       # 启动服务 → http://localhost:8080
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `happycapy-skills-zh.html` | 静态版（内嵌 4,221 个技能，无需后端） |
| `app.html` | 动态版前端（配合 server.py 使用）|
| `server.py` | FastAPI 后端，SQLite FTS5 全文检索 |
| `crawler.py` | 爬虫脚本，726 个搜索词，覆盖全量技能 |
| `translate.py` | 中文翻译引擎，300+ 词典 + 精准覆盖 |

## 作者

**阿成 · ACheng** · [@AchengBusiness](https://github.com/AchengBusiness) · [@chenchen119967](https://x.com/chenchen119967)

HappyCapy 邀请链接: https://happycapy.ai/signup?invite_ref=aGHAUcHN

---

*数据来源：HappyCapy 公开 API · 仅供学习参考*
