# 儿童健康命令设计方案

**日期**: 2025-01-14
**设计者**: Claude + User
**状态**: 已确认

---

## 1. 概述

本设计为 Claude-Ally-Health 项目新增6个儿童健康相关的斜杠命令，覆盖0-18岁全年龄段的医学健康和心理健康需求。

### 1.1 新增命令列表

| 命令 | 核心功能 | 目标年龄段 | 优先级 |
|------|----------|------------|--------|
| `/child-safety` | 意外伤害预防与风险评估 | 0-18岁 | ⭐⭐⭐ |
| `/child-development` | 发育里程碑追踪与延迟预警 | 0-6岁重点 | ⭐⭐⭐ |
| `/child-illness` | 常见疾病记录与护理 | 0-18岁 | ⭐⭐ |
| `/child-sleep` | 睡眠管理与问题识别 | 0-18岁 | ⭐⭐ |
| `/child-nutrition` | 营养评估与饮食管理 | 0-18岁 | ⭐ |
| `/child-mental` | 心理健康筛查与追踪 | 3-18岁 | ⭐ |

### 1.2 与现有命令的关系

```
儿童健康管理系统
├── 现有命令
│   ├── /child-vaccine     (疫苗接种)
│   ├── /growth            (生长曲线)
│   └── /growth puberty    (青春期发育)
│
└── 新增命令
    ├── /child-development (发育里程碑)
    ├── /child-mental     (心理健康)
    ├── /child-sleep      (睡眠管理)
    ├── /child-nutrition  (营养饮食)
    ├── /child-illness    (疾病管理)
    └── /child-safety     (安全预防)
```

---

## 2. 数据存储架构

### 2.1 文件结构

每个命令独立存储在 `data-example/` 目录：

```
data-example/
├── child-development-tracker.json   (发育里程碑)
├── child-mental-tracker.json        (心理健康)
├── child-sleep-tracker.json         (睡眠管理)
├── child-nutrition-tracker.json     (营养饮食)
├── child-illness-tracker.json       (疾病管理)
└── child-safety-tracker.json        (安全预防)
```

### 2.2 共享依赖

所有命令依赖 `data-example/profile.json` 中的儿童基础信息：
- 姓名
- 出生日期
- 性别

---

## 3. 各命令详细设计

### 3.1 `/child-safety` - 意外伤害预防

#### 操作类型
- `record` - 记录安全评估
- `check` - 安全检查
- `risk` - 风险评估
- `prevent` - 预防建议
- `emergency` - 急救信息
- `checklist` - 检查清单

#### 数据结构
```json
{
  "safety_assessments": [
    {
      "date": "2025-01-14",
      "age_group": "5-6岁",
      "home_safety": {
        "fall_prevention": "safe",
        "burn_prevention": "safe",
        "poison_prevention": "needs_attention",
        "water_safety": "not_applicable"
      },
      "car_safety": {
        "car_seat": false,
        "seatbelt": "always"
      },
      "overall_score": "good"
    }
  ],
  "risk_factors": [],
  "emergency_contacts": [
    { "name": "家长", "phone": "138****1234" },
    { "name": "儿科急诊", "phone": "120" }
  ]
}
```

#### 参考标准
- WHO伤害预防指南
- 中国儿童安全指南

---

### 3.2 `/child-development` - 发育里程碑

#### 操作类型
- `record` - 记录发育评估
- `check` - 发育检查
- `milestone` - 里程碑清单
- `delay` - 发育延迟预警
- `history` - 历史记录

#### 数据结构
```json
{
  "child_profile": {
    "child_id": "child_20200101",
    "name": "小明",
    "birth_date": "2020-01-01",
    "gender": "male",
    "premature": false,
    "corrected_age": null
  },
  "milestone_tracking": {
    "gross_motor": [
      { "age": "3_months", "skill": "抬头", "achieved": true, "date": "2020-04-15" },
      { "age": "6_months", "skill": "独坐", "achieved": true, "date": "2020-07-10" },
      { "age": "12_months", "skill": "独走", "achieved": false, "date": null }
    ],
    "fine_motor": [],
    "language": [],
    "social": [],
    "cognitive": []
  },
  "assessment": {
    "overall_status": "normal",
    "delays": [],
    "alerts": []
  }
}
```

#### 参考标准
- ASQ-3（年龄与阶段问卷）
- Denver II（丹佛发育筛查测验）
- 中国0-6岁儿童发育量表

#### 关键里程碑
| 月龄 | 大运动 | 精细动作 | 语言 | 社交 |
|------|--------|----------|------|------|
| 4月 | 抬头稳 | 追视物体 | 咿呀发声 | 认生 |
| 6月 | 独坐 | 拇食指捏物 | 单音节 | 笑出声 |
| 9月 | 爬行 | 拇食指捏物 | 双音节 | 害怕 |
| 12月 | 独走 | 拿两物 | 有意识叫人 | 指认 |
| 18月 | 独走稳 | 搭积木 | 单词 | 模仿 |
| 24月 | 跑 | 画线 | 双词句 | 并行游戏 |
| 36月 | 双脚跳 | 画圆 | 简单对话 | 合作游戏 |

---

### 3.3 `/child-illness` - 常见疾病管理

#### 操作类型
- `record` - 记录疾病
- `symptom` - 症状记录
- `fever` - 发热管理
- `medicine` - 用药记录
- `recovery` - 康复追踪

#### 数据结构
```json
{
  "illness_records": [
    {
      "id": "illness_20250114",
      "date": "2025-01-14",
      "condition": "急性上呼吸道感染",
      "symptoms": ["发热", "咳嗽", "流涕"],
      "severity": "mild",
      "onset_date": "2025-01-12",
      "fever_tracking": [
        { "time": "2025-01-12T20:00", "temperature": 38.5, "medication": "布洛芬" }
      ],
      "medications": ["布洛芬混悬液", "氨溴索口服液"],
      "doctor_visit": false,
      "recovery_date": null,
      "notes": ""
    }
  ],
  "frequent_illnesses": {
    "urti_count": 3,
    "last_urti_date": "2025-01-14"
  }
}
```

#### 参考标准
- 儿科学诊断标准
- 发热管理指南

#### 常见疾病类型
- 急性上呼吸道感染（感冒）
- 急性支气管炎
- 腹泻
- 手足口病
- 水痘
- 流行性感冒

---

### 3.4 `/child-sleep` - 睡眠管理

#### 操作类型
- `record` - 记录睡眠
- `schedule` - 作息管理
- `problem` - 睡眠问题
- `analysis` - 睡眠分析
- `routine` - 作息建议

#### 数据结构
```json
{
  "sleep_records": [
    {
      "date": "2025-01-14",
      "bedtime": "21:00",
      "fall_asleep_time": "21:30",
      "wake_time": "07:00",
      "total_sleep": "9.5h",
      "night_wakeups": 1,
      "sleep_quality": "good",
      "issues": []
    }
  ],
  "sleep_problems": {
    "night_terrors": false,
    "bedwetting": false,
    "sleep_walking": false,
    "teeth_grinding": false
  },
  "routine": {
    "bedtime_routine": ["洗澡", "绘本", "安抚"],
    "screen_time_before_bed": "30min"
  }
}
```

#### 参考标准
- WHO儿童睡眠指南
- 中国睡眠协会标准

#### 各年龄段推荐睡眠时长
| 年龄 | 推荐睡眠 | 睡眠模式 |
|------|----------|----------|
| 0-3月 | 14-17小时 | 吃睡模式 |
| 4-12月 | 12-16小时 | 2-3次小睡 |
| 1-2岁 | 11-14小时 | 1-2次小睡 |
| 3-5岁 | 10-13小时 | 1次小睡 |
| 6-12岁 | 9-12小时 | 夜间睡眠 |
| 13-18岁 | 8-10小时 | 夜间睡眠 |

---

### 3.5 `/child-nutrition` - 营养饮食

#### 操作类型
- `record` - 记录饮食
- `pickyeater` - 挑食评估
- `growth` - 生长营养评估
- `deficiency` - 营养缺乏筛查
- `advice` - 饮食建议

#### 数据结构
```json
{
  "dietary_records": [
    {
      "date": "2025-01-14",
      "meals": {
        "breakfast": ["牛奶", "鸡蛋", "面包"],
        "lunch": ["米饭", "青菜", "鸡肉"],
        "dinner": ["面条", "西红柿", "牛肉"],
        "snacks": ["苹果", "酸奶"]
      },
      "water_intake": "800ml",
      "vitamin_supplements": ["维生素D"]
    }
  ],
  "picky_eating": {
    "level": "mild",
    "refused_foods": ["胡萝卜", "青椒"],
    "preferred_foods": ["鸡肉", "水果"]
  },
  "nutritional_assessment": {
    "protein_adequacy": "adequate",
    "iron_status": "adequate",
    "vitamin_d_status": "supplement_recommended",
    "calcium_intake": "adequate"
  }
}
```

#### 参考标准
- 中国居民膳食指南（儿童版）
- WHO营养标准

---

### 3.6 `/child-mental` - 心理健康

#### 操作类型
- `record` - 记录评估
- `mood` - 情绪追踪
- `behavior` - 行为评估
- `anxiety` - 焦虑筛查
- `adhd` - 注意力筛查
- `report` - 综合报告

#### 数据结构
```json
{
  "assessments": [
    {
      "date": "2025-01-14",
      "age": "5y1m",
      "mood_rating": 7,
      "behavior_score": "normal",
      "anxiety_screening": "low_risk",
      "attention_screening": "normal",
      "notes": ""
    }
  ],
  "behavior_tracking": {
    "mood_changes": [],
    "sleep_issues": false,
    "social_withdrawal": false,
    "aggression": false
  },
  "scales": {
    "sdq": null,
    "rcads": null,
    "conners": null
  }
}
```

#### 参考标准
- SDQ（长处和困难问卷）
- RCADS（儿童焦虑量表）
- Conners量表（注意力评估）

---

## 4. 错误处理

### 4.1 共享错误处理

| 场景 | 错误消息 | 处理方式 |
|------|----------|----------|
| 缺少儿童基础信息 | `⚠️ 未找到儿童档案，请先设置 /profile child-name` | 引导用户设置profile |
| 年龄超出范围 | `⚠️ 该功能适用于X-Y岁儿童，当前年龄：Z岁` | 提示适用范围 |
| 测量值异常 | `⚠️ 输入值超出合理范围（X-Y），请确认后重新输入` | 拒绝并提示 |
| 数据文件损坏 | `⚠️ 数据文件损坏，正在初始化新文件` | 自动重建 |
| 日期无效 | `⚠️ 日期不能是未来日期` | 验证并拒绝 |

### 4.2 特殊情况处理

**发育里程碑：**
- 早产儿（<37周）：自动使用矫正月龄至2岁
- 发育延迟：标记预警但不下诊断
- 超前发育：正常记录，不特别标注

**心理健康：**
- 发现高风险症状：建议就医但不诊断
- 3岁以下：简化评估（行为观察为主）

**睡眠管理：**
- 新生儿：按吃睡模式记录，不适用固定作息
- 夜奶记录：0-2岁自动追踪

**疾病管理：**
- 高热（>39℃）：自动标记紧急提醒
- 用药：仅记录，不做用药建议

**安全预防：**
- 按年龄自动切换检查项目

---

## 5. 医学安全原则

### 5.1 安全红线

1. 不做医学诊断
2. 不推荐具体药物/品牌
3. 不替代专业医疗建议
4. 不处理紧急情况（引导就医）

### 5.2 系统能做的

- 健康数据记录与追踪
- 风险预警与筛查
- 健康建议科普
- 就医时机提示

### 5.3 免责声明

```
⚠️ 重要提示：
本系统仅供健康记录和参考评估，
不能替代专业医疗诊断。
如有异常或疑虑，请及时就医。
```

---

## 6. 实施计划

### 阶段划分

| 阶段 | 命令 | 优先级 |
|------|------|--------|
| 第1阶段 | `/child-safety` | ⭐⭐⭐ |
| 第2阶段 | `/child-development` | ⭐⭐⭐ |
| 第3阶段 | `/child-illness` | ⭐⭐ |
| 第4阶段 | `/child-sleep` | ⭐⭐ |
| 第5阶段 | `/child-nutrition` | ⭐ |
| 第6阶段 | `/child-mental` | ⭐ |

### 每个阶段的工作内容

1. 创建命令文件 (`.claude/commands/child-*.md`)
2. 创建数据结构示例 (`data-example/*-tracker.json`)
3. 更新数据结构文档 (`docs/data-structures.md`)
4. 测试各操作类型
5. 更新索引文件（如需要）

---

## 7. 附录

### 7.1 命令快捷方式

为方便使用，可考虑添加快捷方式：
- `/child-safety` → `/cs`
- `/child-development` → `/cd`
- `/child-illness` → `/ci`
- `/child-sleep` → `/csl`
- `/child-nutrition` → `/cn`
- `/child-mental` → `/cm`

### 7.2 数据备份建议

- 所有儿童健康数据存储在本地
- 建议定期备份 `data-example/` 目录
- 数据不上传云端，保护隐私

---

*设计文档版本: 1.0*
*最后更新: 2025-01-14*
