# 影像Hot — 消费电子影像资讯聚合站

对标卡兹克 AI Hot，专注手机/消费电子影像的垂直资讯聚合。

## 架构

```
RSS信源 → GitHub Actions(每6h) → AI处理(DeepSeek+Claude) → 飞书多维表格 → 静态JSON → GitHub Pages
```

- **0 服务器成本**：GitHub Actions 免费额度运行爬虫，GitHub Pages 托管前端
- **AI 分工**：DeepSeek 做翻译+摘要（便宜），Claude 做打标+推荐+评分（质量高）
- **数据存储**：飞书多维表格，自动清理90天前旧数据

## 快速开始

### 1. 创建飞书多维表格

1. 打开 [飞书多维表格](https://www.feishu.cn/product/base) 新建一个表格
2. 创建以下字段（字段名必须完全一致）：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | 文本 | 文章中文标题 |
| 原标题 | 文本 | 原始语言标题 |
| 来源 | 单选 | PetaPixel/GSMArena/DPReview/... |
| 原文链接 | 链接 | 点击跳转原文 |
| 发布时间 | 日期 | 文章原始发布时间 |
| 中文摘要 | 多行文本 | AI生成 ≤100字 |
| AI推荐理由 | 多行文本 | 1-2句推荐 |
| 分类标签 | 多选 | 7大标签选1-2个 |
| 语言 | 单选 | 中文/English |
| 内容哈希 | 文本 | SHA256去重用 |
| 质量评分 | 数字 | 1-10 |
| 处理状态 | 单选 | ready/error |

3. **分类标签**的多选选项设为：
   - 传感器硬件
   - 镜头与光学
   - ISP & 影像芯片
   - 计算摄影 & AI 影像
   - 拆机 & 实测 & 样张
   - 产品洞察 & 行业资讯
   - 摄影美学 & 技术科普

4. 从表格URL中提取参数：
   - 浏览器打开表格 → URL格式为 `https://xxx.feishu.cn/base/APPTOKEN/table/TABLEID`
   - `APPTOKEN` = `FEISHU_BITABLE_APP_TOKEN`
   - `TABLEID` = `FEISHU_TABLE_ID`

### 2. 创建飞书应用权限

1. 打开 [飞书开放平台](https://open.feishu.cn/) → 创建企业自建应用
2. 应用内开通权限：**多维表格** → `bitable:app`（全部权限）
3. 发布应用并获得审批
4. 将应用添加到多维表格的协作者中

### 3. 配置 GitHub Secrets

在仓库 Settings → Secrets and variables → Actions → New repository secret：

| Secret | 值 |
|--------|-----|
| `FEISHU_APP_ID` | `cli_aa87198c11bb1cc2` |
| `FEISHU_APP_SECRET` | 你的飞书 App Secret |
| `FEISHU_BITABLE_APP_TOKEN` | 从表格URL提取 |
| `FEISHU_TABLE_ID` | 从表格URL提取 |
| `CLAUDE_API_KEY` | 你的 Anthropic API Key |
| `DEEPSEEK_API_KEY` | 你的 DeepSeek API Key |

### 4. 启用 GitHub Pages

Settings → Pages → Source: GitHub Actions

### 5. 触发首次运行

Actions → Crawl & Process → Run workflow

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export FEISHU_APP_ID=xxx
export FEISHU_APP_SECRET=xxx
export FEISHU_BITABLE_APP_TOKEN=xxx
export FEISHU_TABLE_ID=xxx
export CLAUDE_API_KEY=xxx
export DEEPSEEK_API_KEY=xxx

# 运行完整流水线
python scripts/run_full_pipeline.py

# 生成前端JSON
python scripts/generate_site_json.py

# 启动前端预览
python -m http.server 8080 -d frontend
# 浏览器打开 http://localhost:8080
```

## 信源列表

**国际（自动翻译为中文）：**
- PetaPixel, DPReview, GSMArena, DXOMARK
- DigitalCameraWorld, PhotographyBlog, ThePhoBlographer
- SonyAlphaRumors, CanonRumors, FujiRumors, NikonRumors

**国内（中文直用）：**
- Chiphell 摄影区/相机区（RSSHub）
- 智东西、ZEALER（预留web scraping接口）

## 项目结构

```
├── .github/workflows/    # CI/CD 定时任务
├── src/
│   ├── crawlers/         # RSS爬取 + 去重
│   ├── ai/               # DeepSeek翻译摘要 + Claude打标推荐
│   ├── feishu/           # 飞书API客户端 + CRUD
│   └── utils/            # 配置
├── scripts/              # 可执行脚本
└── frontend/             # 静态网站
    ├── index.html
    ├── css/style.css
    ├── js/
    └── data/             # 自动生成的JSON数据
```
