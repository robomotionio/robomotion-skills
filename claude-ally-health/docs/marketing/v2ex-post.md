# [分享] 用 Claude Code 构建的个人健康管理系统

最近做了一个项目，想和大家分享一下。

## 背景

作为开发者，我希望能完全掌控自己的健康数据。市面上的健康应用要么：
- 数据上传云端（隐私担忧）
- 需要复杂配置
- 缺乏智能分析

## 项目介绍

**Claude-Ally-Health** 是一个基于文件的个人健康信息管理系统，使用 Claude Code CLI 进行数据管理。

### 核心功能

- 📁 **纯文件存储** - 无数据库，无需云端
- 🖼️ **医疗报告智能识别** - OCR 提取化验数据
- 💊 **药物相互作用检测** - 五级预警系统 (A/B/C/D/X)
- 👨‍⚕️ **13个专科 AI 协作** - 多学科会诊
- ☢️ **辐射剂量追踪** - 医学辐射管理
- 💾 **完全本地化** - 数据完全私有

### 技术栈

- 存储：JSON + 文件系统
- CLI：Claude Code Slash Commands
- AI：多智能体架构
- 视觉：GLM 4.5V 图像识别

### 快速开始

```bash
git clone https://github.com/huifer/Claude-Ally-Health.git

# 设置个人信息
/profile set 175 70 1990-01-01

# 保存医疗报告
/save-report /path/to/report.jpg

# 启动多学科会诊
/consult
```

### 项目地址

https://github.com/huifer/Claude-Ally-Health

### 为什么分享

1. 展示 Claude Code 的强大能力
2. 探讨本地化健康数据的可行性
3. 希望获得社区反馈

欢迎 star / fork / 提 issue！

---

大家对于本地化的健康数据管理有什么看法？会觉得比云端方案更有吸引力吗？
