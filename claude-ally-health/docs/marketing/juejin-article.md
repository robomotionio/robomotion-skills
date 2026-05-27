# 从零构建 AI 原生个人健康管理系统

![封面](https://via.placeholder.com/800x400/000000/FFFFFF?text=Claude-Ally-Health)

## 前言

作为开发者，我们花大量时间优化代码、优化工作流、优化生产力工具。但有多少人认真思考过：**如何优化自己的健康管理？**

去年我经历了一次健康小状况，需要频繁做各种检查。随之而来的问题是：**如何高效管理这些医疗数据？**

- 纸质报告容易丢失
- PDF 难以检索和分析
- 医院患者门户网站体验很差
- 完全不知道自己的指标趋势如何

## 现有方案的困境

### 方案 1：健康类 APP
- 数据上传云端
- 信任他们不出售数据
- 希望不被黑客攻击
- **结论：算了**

### 方案 2：电子表格
- 手动录入数据
- 缺乏智能分析
- 仍然只是表格
- **结论：太麻烦**

### 方案 3：什么都不做
- 持续丢失报告
- 永远无法追踪趋势
- 健康状况一无所知
- **结论：不可持续**

## 我的解决方案：自己构建

我一直在玩 **Claude Code** - Anthropic 的 CLI 工具，可以用自定义命令扩展 Claude 的能力。

"如果，"我想，"可以直接告诉电脑分析我的血常规报告呢？"

这个想法变成了 **Claude-Ally-Health**。

## 项目架构

```
my-his/
├── .claude/
│   ├── commands/      # Slash 命令定义
│   │   ├── save-report.md
│   │   ├── medication.md
│   │   ├── interaction.md
│   │   ├── consult.md
│   │   └── ...
│   └── specialists/   # AI 医疗专家
│       ├── cardiology.md
│       ├── endocrinology.md
│       ├── gastroenterology.md
│       └── ...（共 13 个专科）
├── data/
│   ├── profile.json
│   ├── medications/
│   ├── 生化检查/
│   ├── 影像检查/
│   └── interactions/
```

### 核心设计思路

每个 `.md` 文件定义一个 CLI 命令。以 `save-report` 为例：

```markdown
---
description: 保存医疗报告
---

请分析上传的医疗报告图片：
1. 提取所有检测项目和参考范围
2. 识别异常结果
3. 保存为 JSON 到 data/生化检查/
```

Claude Code 会解析这个文件，让用户可以执行 `/save-report` 命令。

## 核心功能

### 1. 医疗报告 OCR

```bash
/save-report @血常规.jpg
```

系统会：
- 使用 GLM 4.5V 识别图片
- 提取所有检测值
- 标记异常结果
- 保存结构化 JSON 数据

### 2. 药物相互作用检测

```bash
/interaction check
```

功能包括：
- 药物-药物相互作用
- 药物-疾病相互作用
- 五级严重度系统（A/B/C/D/X）
- 循证医学建议

### 3. 多学科会诊（MTD）

```bash
/consult
```

这是最有趣的部分。系统会并行启动 13 个专科 AI 代理：

```
[心内科] 分析心血管指标...
[内分泌科] 检查激素平衡...
[消化科] 评估肝酶水平...
[血液科] 审查血细胞计数...
...
[协调员] 综合各科意见...
```

每个专家都有领域专业知识，提供针对性建议。

## 技术实现

### 纯文件存储

不需要数据库，只用 JSON：

```json
{
  "date": "2024-01-15",
  "testType": "血常规",
  "results": [
    {
      "item": "血红蛋白",
      "value": "145",
      "unit": "g/L",
      "referenceRange": "130-175",
      "status": "normal"
    },
    {
      "item": "白细胞计数",
      "value": "11.2",
      "unit": "10^9/L",
      "referenceRange": "3.5-9.5",
      "status": "abnormal_high"
    }
  ]
}
```

### 多智能体协作

会诊系统使用协调器模式：

1. **并行启动** 所有专科
2. **分析** 各专科视角的数据
3. **综合** 各科发现为完整报告
4. **优先级排序** 建议事项

### 隐私设计

- 数据存储零外部 API 调用
- 所有处理在本地完成（通过 Claude Code）
- 标准 JSON 格式便于导出
- MIT 开源许可 - 代码可审计

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/huifer/Claude-Ally-Health.git
cd Claude-Ally-Health/my-his

# 在 Claude Code 中打开
claude-code .

# 设置个人档案
/profile set 175 70 1990-01-01

# 保存第一份报告
/save-report @path/to/report.jpg
```

## 项目亮点

| 特性 | 说明 |
|------|------|
| 📁 纯文件存储 | 无数据库，无需云端 |
| 🖼️ 智能报告识别 | AI 提取化验数据 |
| 💊 药物相互作用 | 五级预警系统 |
| 👨‍⚕️ 13 科 AI 协作 | 多学科智能会诊 |
| ☢️ 辐射剂量追踪 | 医学辐射管理 |
| 💾 完全本地化 | 数据完全私有 |
| 🚀 CLI 操作 | 无需编程知识 |

## 下一步计划

- [ ] 多语言支持（日语、德语）
- [ ] Web 可视化面板
- [ ] 健康趋势分析
- [ ] EHR 标准格式导出

## 总结

这个项目是我对两个问题的探索：

1. **AI 如何帮助我们管理健康数据？**
2. **如何在不牺牲隐私的前提下实现？**

目前的答案是：**有了合适的工具，效果非常好。**

Claude Code 的可扩展性让我们能够构建复杂的领域专用工具。无论是健康数据、项目管理，还是其他领域 - Skill 系统都能让 AI 适应你的需求。

## 相关链接

- **GitHub**: https://github.com/huifer/Claude-Ally-Health
- **文档**: https://github.com/huifer/Claude-Ally-Health#readme
- **贡献指南**: https://github.com/huifer/Claude-Ally-Health/blob/main/CONTRIBUTING.md

> ⚠️ 免责声明：本系统仅供个人健康管理使用，不应作为医疗诊断依据。所有医疗决策需咨询专业医生。

---

如果觉得这个项目有趣，欢迎 **Star** ⭐

有任何问题或建议，欢迎在 Issues 中讨论！
