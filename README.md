<div align="center">

# AI Agent 工程实践技能包

**让 AI 少犯错、交付可验证、环境问题能自己查——五个从真实长任务里沉淀出来的技能**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](./LICENSE)
![Lang](https://img.shields.io/badge/语言-简体中文-1f6feb?style=flat-square)
![Type](https://img.shields.io/badge/type-agent%20skill-8957e5?style=flat-square)
[![Last commit](https://img.shields.io/github/last-commit/lueuru/agent-engineering-skills?style=flat-square)](https://github.com/lueuru/agent-engineering-skills/commits)

</div>

---

## 这是什么

五个 **AI Agent 技能（Skill）**。它们不解决业务问题，解决的是**"AI 干活本身不靠谱"**这件事：

| 痛点 | 典型表现 | 对应技能 |
|---|---|---|
| 判据全绿，但验的不是这份代码 | "测试都过了" → 上线发现坏的还是坏的 | `verify-criteria-selfcheck` |
| 仓库主页太单薄 | README 只有三行、没有徽章与介绍 | `github-repo-beautify` |
| 说"帮你清理磁盘" | 扫完就删，不可逆 | `windows-cleanup-audit` |
| Agent 客户端起不来 | 一堆插件加载报错，不知道从哪查 | `dsh-profile-repair` |
| 长会话想复盘 | 会话文件是 zstd 压缩的 JSONL，读不了 | `dsh-session-log-analysis` |

**前三个是通用的**（任何项目都能用），**后两个是特定环境**（DeepSeek Harness Desktop 桌面版）的排障技能。

## 技能清单

### 通用

#### 1. `verify-criteria-selfcheck` — 验收判据的防假通过加固

给"验收判据 / 自动化测试"补一层自检。当出现下面这些症状时用它：

- **全绿但验的不是这份代码**（判据跑在临时副本上，你改的是源目录）
- **清单永远命不中**（正则写错、类型比较恒假、数组和 0 比较恒 false）
- **判据自己写错，却输出像真结论** —— 这是最坏的一类：它比没有判据更危险
- 清理脚本 / 迁移脚本 / CI 校验需要加固

核心是**真反证**：改完判据后**故意弄坏一次**，确认它真的会红。
没做过这一步，"通过"两个字不作数。

#### 2. `github-repo-beautify` — 仓库主页美化

美化 GitHub 仓库主页与 README：排版布局、状态徽章、统计卡片、封面头图、
目录折叠、主题配色、贡献者展示；也用于生成社交预览图与配置仓库元信息
（description / homepage / topics）。

内置两条"踩过才知道"的经验：
- **第三方服务存活清单**（实测哪些图床/统计服务还活着，避免推荐已下线的服务）
- **"shields.io 绿色假象"判据** —— 徽章服务出错时会返回 **HTTP 200 + 一张写着
  `badge not found` 的正常图片**，只看状态码会以为一切正常

#### 3. `windows-cleanup-audit` — Windows 磁盘清理审计

处理"清理一下电脑 / C 盘满了 / 清一下垃圾"这类请求。

强制的工作流是 **只读扫描优先**，然后：

- **保护清单**：不可再生的项目资产（密钥库、基底包、签名器）绝不进删除列表
- **本机护栏行为**：Temp 目录可删，但个人目录的删除会被强制走回收站且会失败关闭
- **逃生通道**：护栏挡住自动化时，生成脚本交给用户自己跑，而不是绕过护栏
- 记录了本机特有的坑（PowerShell 吞 stdout、嵌套 `.ps1` 静默空操作、
  某些命令关键字被安全策略拦截）与一个真实根因案例

### 环境特定（DeepSeek Harness Desktop）

#### 4. `dsh-profile-repair` — DSH 启动故障修复

当 DSH 桌面版启动失败、插件/会话在 Web UI 里消失，或报出
`.credentials.yaml.lock`、`timed out waiting for the writer lock`、
`assertEntriesActivated`、`Failed to load plugins` 之类错误时使用。

技能**梳理了六种已知失效模式**并给出各自的处置方式，
其中第一条最容易被忽略：**陈旧的 `.credentials.yaml.lock` 会阻塞每一次启动**（先查它）。

#### 5. `dsh-session-log-analysis` — DSH 会话日志分析

指向一个 DSH 会话目录（`session-*/session.jsonl.zstd`），
做**学习 / 阅读 / 分析 / 总结 / 复盘**：

- zstd 解压
- **真实的 JSONL 事件结构**（字段名是 `user/message` 而不是想当然的 `user` —— 名字猜错就什么都读不出来）
- 长会话怎么摘要（借助 compaction / summary 事件）
- 最终产出一份可交接的"学习地图"

## 安装

```bash
git clone https://github.com/lueuru/agent-engineering-skills.git
cp -r agent-engineering-skills/skills/* ~/.workbuddy/skills/
```

单独取一个：

```bash
cp -r agent-engineering-skills/skills/verify-criteria-selfcheck ~/.workbuddy/skills/
```

> `dsh-*` 两个技能是针对特定安装环境写的，里面的路径与版本号属于该环境，
> 换机器需要按实际情况调整。

## 使用示例

**例 1：测试全绿但问题依旧**

> 「我的检查脚本全过了，但线上还是坏的。」

`verify-criteria-selfcheck` 会先查三件事：判据跑的是不是这份代码、
清单表达式有没有恒真恒假、判据的对象还在不在产品里用。

**例 2：仓库主页太寒酸**

> 「帮我把这个仓库的 README 弄好看点。」

`github-repo-beautify` 会重写 README 排版、加徽章与目录、
生成社交预览图，并配置仓库的 description 与 topics。

**例 3：想清理磁盘但怕删错**

> 「C 盘满了，帮我清一下。」

`windows-cleanup-audit` 会**先只读扫描并出报告**，列出可删项与保护项，
**不会直接动手删**。

## 仓库结构

```
agent-engineering-skills/
├── README.md
├── LICENSE
├── .gitignore
└── skills/
    ├── verify-criteria-selfcheck/SKILL.md
    ├── github-repo-beautify/SKILL.md
    ├── windows-cleanup-audit/SKILL.md
    ├── dsh-profile-repair/SKILL.md
    └── dsh-session-log-analysis/SKILL.md
```

## 这些技能从哪来

不是凭空写的，是**在一个跨月的真实项目上，被同一类问题反复咬出来的**：

- 判据写了 40 项全绿，而线上页面正对访客显示测试占位内容
- 备份脚本质量很高、却**从来没有被调度过**（最新备份停在一个月前）
- 一个"优化"（给脚本加 `defer`）让整页崩掉，而命令行抓取和状态码全是 200
- 规则写了、语法检查通过、**却永远不生效**（插错了位置，成了另一条规则的子块）

这些教训的共同点是：**失败时不出声**。所以这几个技能的重点都不是"怎么做"，
而是**"怎么确认自己真的做对了"**。

## 相关仓库

同一系列的其他技能包（各自独立，可单独使用）：

- **[unity-game-localization-skills](https://github.com/lueuru/unity-game-localization-skills)** —— Unity 老游戏汉化三件套 —— DLL 层文本、资源层文本、BMFont 中文位图字体
- **[android-apk-reverse-skills](https://github.com/lueuru/android-apk-reverse-skills)** —— Android APK 原地改造 —— dex 字符串等长替换、渠道 SDK 剥离、模拟器自动化验证

## 许可证

[MIT](./LICENSE) —— 自由使用、修改、再分发，保留版权声明即可。

