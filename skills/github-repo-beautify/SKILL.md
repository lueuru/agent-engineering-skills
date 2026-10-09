---
name: github-repo-beautify
description: 美化 GitHub 仓库主页与 README（排版布局、状态徽章、统计卡片、封面头图、目录折叠、主题配色、贡献者展示）时使用。内置 2026-10-07 实测的第三方服务存活清单与「shields.io 绿色假象」判据，避免推荐已下线的图床或把坏图写进 README。也用于生成社交预览图、配置仓库元信息（description/homepage/topics）、校验 README 图片与站内链接。
agent_created: true
---

# GitHub 仓库主页与 README 美化

## 何时用

- 美化 / 重写仓库 README（排版、徽章、卡片、头图、目录、折叠、配色）
- 配置仓库元信息：简介、主页、Topics、About 区域、功能开关
- 生成社交预览图（social preview）
- README 图片裂图排查、站内链接有效性校验

## ★ 动手前必读：三条会直接导致返工的硬事实

### ① 第三方统计图床已大规模下线（2026-10-07 逐个实测，17 个服务）

| 分类 | 服务 | 状态 |
|---|---|---|
| 状态徽章 | `img.shields.io`（静态 + 动态 GitHub 数据） | ✅ **可用，首选** |
| 统计卡片 | `github-readme-stats.vercel.app`（统计卡/语言/置顶） | ❌ 0 字节 |
| 统计卡片 | `github-profile-summary-cards.vercel.app` | ❌ 0 字节 |
| 热力图 | `github-readme-activity-graph.vercel.app` | ❌ 0 字节 |
| 连续提交 | `streak-stats.demolab.com` | ✅ 可用 |
| 连续提交 | `github-readme-streak-stats.herokuapp.com` | ❌ 0 字节 |
| 打字机 | `readme-typing-svg.demolab.com` | ✅ 可用（备用域） |
| 打字机 | `readme-typing-svg.herokuapp.com` | ❌ 0 字节 |
| 头图 | `capsule-render.vercel.app` | ❌ 0 字节 |
| 访客计数 | `github-readme-counter.vercel.app` | ❌ 0 字节 |
| 图标 | `skillicons.dev` | ✅ 可用 |
| 图标 | `devicon.dev` | ❌ HTTPError |

**规律：`*vercel.app` 与 `*herokuapp.com` 的免费实例基本都挂了**（上游作者停维护 + Heroku 关停免费层）。
→ **动态数据区一律用 `img.shields.io`**，它读 GitHub 公开 API，同样是真数据，且有 GitHub 官方背书。

复验脚本：`Desktop\_gh_tools\survey_services.py`（并发探测，可重复运行）。

### ② shields.io 的「绿色假象」——本技能最容易踩的坑

**shields.io 出错时返回 HTTP 200 + 一张写着错误文字的正常图片**：
- 不存在的仓库 → 图内文字 `repo not found`
- 错误的 style → 图内文字 `badge not found`

→ **只看状态码，判据会 100% 全绿而实际藏着两张坏图。**

判据必须**解析 SVG 里的 `<text>` 文字**并匹配 `not found|404|error|invalid|unavailable`。
配套反证用例（用不存在的仓库名 `NoSuchRepoXyz123` 和不存在的 style，判据必须报红）。

### ③ curl 连不上 ≠ 服务挂了

本机 DNS 曾把 `*.vercel.app` 解析到 `199.59.148.7`（`r-199-59-148-7.twttr.com`，Twitter 的机器），
也解析失败过 `api.github.com`（但它明明能用）。**这是 DNS 污染。**

判定流程：
1. `curl`（Python 用独立 SSL + `ProxyHandler({})` 绕过系统代理）
2. **headless Edge `--dump-dom` 复核**（浏览器有独立网络栈）
3. **两者结论一致**才判定服务真的下线

浏览器版（Windows 路径，MSYS 风格路径 Edge 不认）：
```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --disable-gpu \
  --no-sandbox --user-data-dir="C:\path\prof" --virtual-time-budget=15000 \
  --dump-dom "https://目标URL" 2>/dev/null | head -c 300
```

## GitHub 官方排版能力（据 docs.github.com，2026-10-07 核对）

| 能力 | 说明 |
|---|---|
| `<picture>` | **官方支持**，深浅色双图的标准做法 |
| `<div align="center">` | 官方支持（GitHub 自己的 README 也这么用） |
| `<details>/<summary>` | 官方支持，折叠区块 |
| `<table>` | 官方支持，卡片布局靠它 |
| `> [!NOTE]` 等 Alerts | **官方扩展**，5 种（NOTE/TIP/IMPORTANT/WARNING/CAUTION），**不可嵌套**、官方建议全文只用 1–2 个 |
| `<a name="x">` | 自定义锚点，**不会出现在文档大纲** |
| 行内 CSS `style="..."` | 可用但易被官方更新破坏，非必要不用 |
| 相对路径 | **官方推荐**（`/assets/x.png` 相对仓库根），绝对路径在 clone 后失效 |

**注意**：自定义锚点不进大纲；改标题会改锚点，站内互链要同步改。

### ④ 目录锚点（TOC）规则必须实测，别照抄"去标点"的通行说法

`[标题](#锚点)` 一旦算错，**GitHub 不会报错，只是链接安静地点不动**——肉眼很难发现。

★ 通行说法是"转小写 + 空格转连字符 + 去标点"，**这在带 emoji 的中文标题上必错**。
2026-10-07 抓 `github.com/lueuru/AtlanticFleetSite` 的真实 DOM，量出 12 个标题的标准答案，
逐条比对到 **12/12** 才定稿。精确规则：

| 字符类型 | 处理 | 实例 |
|---|---|---|
| emoji（Unicode 类别 `S*`） | → **一个 `-`**，并**吞掉紧随的空格** | `📌 这是什么` → `-这是什么` |
| 中点 `· • ‧ ・` | → **一个 `-`**，并**吞掉紧随的空格** | `框架 · 官网` → `框架--官网` |
| 空格 | → 一个 `-` | `Mod 框架` → `mod-框架` |
| 其余标点（`.` `,` `!`，类别 `P*`） | 丢弃 | `a.b, c!` → `abc` |
| 汉字 / 字母 / 数字（`L*` `N*`） | 保留并转小写 | |
| 尾部连字符 | **去掉** | |
| 头部连字符 | **保留** | `📌 这是什么` 的锚点**带前导 `-`** |
| 连续连字符 | **不压缩** | ` · ` 产生**两个** `-` |

- 目录里要用 **`href` 的 `#-xxx`**，不是 `id` 的 `user-content--xxx`。
- 第一版按"emoji 丢弃 + 压连字符"写，只对 **3/12**，已被真实数据否证——**这就是判据没做真反证的典型**。
- 用 `Desktop\_gh_tools\gen_toc.py`（含完整注释 + `--inplace` 就地替换）。

## 隐私与性能

- **README 里的所有外部图片，GitHub 都会经 `camo.githubusercontent.com` 代理后发给访客**
  → 好处：访客只连 GitHub 一个域名，速度与隐私都更好（不直连第三方、不暴露访客 IP 给图床）
  → 代价：首次访问由 GitHub 服务器去抓源图，**源图挂了就是裂图**
- camo 有缓存，改图后可能延迟生效
- **第三方图床能看到访客 IP 与 User-Agent**（虽然经 camo 中转，但图床仍收到请求）
- **不要把 token / 密钥 / 私有仓库名写进 README** —— 仓库公开后 camo 缓存会长期留存该内容

## 主流做法（8 种）

| # | 做法 | 实现原理 | 适用场景 | 依赖服务 | 优点 | 缺点 |
|---|---|---|---|---|---|---|
| 1 | **shields.io 状态徽章** | 静态 `/badge/文字-颜色` 或动态 `/github/...` 端点，服务端读 GitHub API 生成 SVG | 几乎所有项目 | `img.shields.io` | 免维护、真数据、GitHub 背书、国内可达 | 需判准可用性（见坑②）；过多会显得花哨 |
| 2 | **统计卡片**（commit/star/语言） | 第三方把 GitHub API 数据渲染成 SVG | 想要视觉冲击的个人主页 | `github-readme-stats` 等 | 信息密度高、好看 | **2026 起基本全灭**；且无法自建 |
| 3 | **贡献热力图** | 拉取近一年 commit 时间戳画格子图 | 展示持续投入 | `activity-graph` | 直观体现活跃度 | **已下线**；自己画成本高 |
| 4 | **头图 / 封面** | 本地生成 1280×640 PNG，提交到仓库 | 仓库主页、时间线卡片 | **无**（本地生成） | 完全可控、不依赖第三方、隐私最好 | 改一次要重提交 |
| 5 | **目录（TOC）** | `[链接](#锚点)` 列表；GitHub 也自动生成大纲 | 超过 5 个章节 | **无** | 零成本 | 手动维护，**改标题即失效** → 必须用 `gen_toc.py` 且规则要实测（见坑④） |
| 6 | **折叠区块** | `<details><summary>` | 长内容收纳（全部仓库、配置项） | **无** | 页面短、聚焦重点 | 搜索引擎不索引折叠内容 |
| 7 | **表格卡片区** | `<table>` + `<div align="center">` 组合 | 能力矩阵、模块清单 | **无** | 深浅色自适应（跟随 GitHub 主题） | 窄屏易横向溢出，需实测 |
| 8 | **贡献者展示** | `github/contributors` 端点或 `contrib.rocks` | 多人工项目 | shields.io / contrib.rocks | 一行展示团队 | 单人项目无意义 |

**配色**：跟随 GitHub 主题，不要写死背景色。用徽章自带色系 + 官方 Alerts 的语义色。
**字体**：README 只能用系统字体栈与 emoji，**不要引入外部字体**（加载慢、失败即丑）。

## 可落地方案

### A. 新增 / 修改的文件

| 文件 | 动作 | 说明 |
|---|---|---|
| `README.md` | 重写 | 6 大模块 + 目录 + 折叠 |
| `social-preview.png` | 新增 | 1280×640，提交到仓库根，README 用**相对路径**引用 |
| `.github/PROFILE/README.md` | 可选 | 账号主页 README（需公开且非 fork 才生效） |
| `docs/CONTRIBUTING.md` | 可选 | 贡献指南从 README 拆出，README 留链接 |

### B. 工具脚本（**放仓库外**，否则会被提交进公网）

```
Desktop\_gh_tools\
  _make_social_preview.py    生成 1280x640 预览图（Pillow）
  _verify_readme_images.py   徽章可用性判据（含 SVG 文字反红）
  _gh_fetch_profile.py       拉 GitHub 真实数据
  survey_services.py         第三方服务存活普查
  gen_toc.py                 按 h2/h3 生成目录
```

### C. 资源来源

| 资源 | 来源 | 隐私 |
|---|---|---|
| 预览图 | **本地 Pillow 生成**，不外传 | ✅ 最好 |
| 状态徽章 | `img.shields.io` | 经 camo，访客不直连 |
| 技能图标 | `skillicons.dev`（可用）/ 或**文字徽章**（零依赖） | 经 camo |
| 截图/演示 | 存仓库 `media/` 下，**相对路径**引用 | ✅ 最好 |
| 字体 | **不引入**，用系统字体栈 + emoji | — |

### D. 维护成本

| 项 | 频率 | 工作量 |
|---|---|---|
| 预览图 | 项目大版本时 | 重跑脚本 + 提交 |
| 徽章 | **零维护** | 自动跟随仓库数据 |
| 目录 | 改标题时 | 重跑 `gen_toc.py` |
| 第三方服务存活 | **每季度** | 重跑 `survey_services.py`，挂了换 shields.io |
| 站内链接 | 改目录结构时 | 跑链接校验 |

## 仓库元信息 API

| 用途 | 端点 | 说明 |
|---|---|---|
| 简介 / 主页 / 功能开关 | `PATCH /repos/{o}/{r}` | |
| **Topics** | `PUT /repos/{o}/{r}/topics` | ★ **PATCH 不支持 topics，静默不生效**（返回空数组） |
| 上传文件 | `PUT /contents/{path}` | |
| 读账号数据 | `GET /users/{u}`、`/users/{u}/repos`、`/users/{u}/events/public` | 公开信息，**不需要 token** |

**最低权限：公开仓库只勾 `public_repo`。README 动态图完全不需要 token。**

### 注入令牌（不落盘）

```bash
GH_TOK="ghp_xxx"
ASKPASS=$(mktemp -d)/ap.sh
printf '#!/bin/sh\ncase "$1" in\n  *sername*) echo "lueuru";;\n  *) echo "$GH_TOK_PASS";;\nesac\n' > "$ASKPASS"
chmod +x "$ASKPASS"
GIT_TERMINAL_PROMPT=0 GIT_ASKPASS="$ASKPASS" GH_TOK_PASS="$GH_TOK" \
  git -c credential.helper= -c core.askPass="$ASKPASS" \
      -c http.proxy= -c https.proxy= push origin main
```

★ **必须加三个 `-c proxy=`**：本机有 `http_proxy=127.0.0.1:55023`（工作站 MCP 代理），
它挂掉时 `git push` 报 `CONNECT tunnel failed, response 502`。
★ 用户贴过令牌在对话里 → **必须提醒删令牌**（`github.com/settings/tokens`），并说清删除不影响已推送内容。

## 验收清单

- [ ] 徽章逐个实测通过（含 SVG 文字反红判据 + 假链接反证）
- [ ] **真实浏览器**抓 `github.com/{o}/{r}`，确认渲染区图片数、表格数、折叠数、**0 裂图**
- [ ] 移动端 390px 截图：徽章不溢出右边缘、纯文字不挤成一片
- [ ] 站内链接 5/5 存在（★ **别用 `os.path.normpath`**，它把 `/docs/` 变 `\docs`，Windows 上误报不存在；直接 `rel + 'index.html'`）
- [ ] 预览图**自己看一眼**（不能只信脚本输出成功）
- [ ] 预览图**不贴位图小图标**（GitHub 会缩放它，贴小图标必失真）
- [ ] 提交前扫敏感信息（`ghp_`/密码/私钥）——**README 全文扫，不是只扫新增行**
- [ ] 工具文件已 `mv` 出仓库，API 确认远端 404
- [ ] 推送后用 API 独立复验（`contents/{f}` 的 `sha` 对 `git rev-parse HEAD:{f}`，★ blob SHA1 ≠ 裸 SHA1）

## 已知环境坑

- `raw.githubusercontent.com` 本机**完全不可用**（TCP 超时），`api.github.com` 正常 → 取文件走 API contents 端点 + base64
- `*.vercel.app` 被 DNS 污染到 Twitter 的 IP
- 批量删除阈值 `scope=turn`（本会话累计），清理用 `mv` 不用 `rm`
- Edge 截图必须用 **Windows 路径**（MSYS 风格路径静默不生效）
