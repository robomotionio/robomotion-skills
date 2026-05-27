# 孕期与产后功能扩展提案

**模块编号**: 05
**分类**: 按人群分类 - 孕期与产后
**状态**: ✅ 已实现
**优先级**: 高
**创建日期**: 2025-12-31
**完成日期**: 2026-01-01

---

## 功能概述

产后恢复追踪模块，全面关注产后身心健康恢复。

### 核心功能

1. **产后恢复时间表** - 42天、6个月、1年检查提醒
2. **产后身体恢复** - 恶露、子宫复旧、伤口愈合、盆底肌
3. **产后心理健康** - EPDS抑郁筛查、情绪支持
4. **哺乳管理** - 喂奶方式、频率、乳腺炎预防
5. **产后避孕指导** - 避孕方式选择和建议

---

## 数据结构

```json
{
  "postpartum_tracking": {
    "delivery_date": "2025-01-01",
    "delivery_mode": "vaginal",
    "postpartum_days": 45,
    "parity": 1,

    "recovery_assessment": {
      "lochia": {
        "current": "white",
        "duration_days": 25,
        "normal": true
      },
      "uterine_involution": {
        "fundal_height": "below_pubis",
        "completed": true,
        "days_postpartum": 28
      },
      "perineal_wound": {
        "present": true,
        "healed": true,
        "episiotomy": true
      },
      "c_section_incision": {
        "present": false
      },
      "pelvic_floor": {
        "assessment": "mild_weakness",
        "urinary_incontinence": "stress",
        "frequency": "occasional"
      }
    },

    "mental_health": {
      "epds_score": 8,
      "screening_date": "2025-02-10",
      "interpretation": "normal",
      "bonding": "good"
    },

    "breastfeeding": {
      "mode": "exclusive",
      "frequency": "8-10_per_day",
      "latch": "good",
      "milk_supply": "adequate",
      "issues": [],
      "mastitis": {
        "history": false
      }
    },

    "contraception": {
      "method": "condom",
      "satisfied": true,
      "planned_method": "IUD",
      "timeline": "3_months_postpartum"
    },

    "checkups": [
      {
        "type": "6_week_checkup",
        "scheduled": "2025-02-12",
        "completed": true,
        "findings": "normal_recovery"
      },
      {
        "type": "6_month_checkup",
        "scheduled": "2025-07-01",
        "completed": false
      }
    ]
  }
}
```

---

## 命令接口

```bash
/postpartum start 2025-01-01 vaginal       # 开始产后追踪
/postpartum recovery lochia white         # 记录恶露情况
/postpartum recovery uterine normal       # 记录子宫复旧
/postpartum epds                           # 进行产后抑郁筛查
/postpartum breastfeeding exclusive       # 记录哺乳情况
/postpartum contraception IUD             # 记录避孕方式
/postpartum status                        # 查看产后状态
```

---

## 注意事项

- 产后6周检查很重要
- 异常出血需就医
- 抑郁症状需重视
- 哺乳问题需咨询
- 避孕需尽早考虑

---

## 实现状态

✅ **已完成** (2026-01-01)

### 已实现功能

1. **多胎妊娠支持** (1.1子模块)
   - 支持单胎、双胎、三胎、四胎妊娠
   - 智能检测功能（从中英文超声笔记自动识别）
   - 调整的预产期和体重增长建议
   - TTTS监测和胎儿档案管理

2. **产后护理追踪** (1.2子模块)
   - 三种追踪期选项：6周、6个月、1年
   - 母亲恢复追踪（恶露、疼痛、母乳喂养、盆底肌）
   - EPDS心理健康筛查（0-30分，4级风险分级）
   - 红旗警示系统（母亲和婴儿）
   - 新生儿护理追踪（喂养、睡眠、体重、尿布）

### 测试覆盖

- **21个原生测试用例**全部通过
- **测试方法**：
  - 使用Shell脚本 + Python JSON验证
  - 无需Node.js依赖
  - 原生Claude Code测试框架

### 文件清单

**命令定义**：
- [/.claude/commands/pregnancy.md](../.claude/commands/pregnancy.md) - 孕期命令（含多胎扩展）
- [/.claude/commands/postpartum.md](../.claude/commands/postpartum.md) - 产后护理命令

**数据结构**：
- [/data/pregnancy-tracker.json](../data/pregnancy-tracker.json) - 孕期数据（含多胎支持）
- [/data/postpartum-tracker.json](../data/postpartum-tracker.json) - 产后数据结构
- [/data/index.json](../data/index.json) - 数据索引（已更新）

**测试脚本**：
- [/scripts/test.sh](../scripts/test.sh) - 主测试运行器（21个测试用例）

**文档**：
- [/docs/postpartum-care-guide.md](../docs/postpartum-care-guide.md) - 产后护理用户指南（中文）
- [/data-example/postpartum-tracker.json](../data-example/postpartum-tracker.json) - 示例数据

### 医学安全

- EPDS评分≥13：⚠️ 立即转介
- EPDS第10题≥2：🚨 紧急干预（自杀意念）
- 产后出血>1卫生巾/小时：⚠️ 联系医生
- 婴儿呼吸窘迫：🚨 立即紧急干预
- TTTS监测：双胎妊娠特别警示

### 运行测试

```bash
# 运行所有测试
./scripts/test.sh
```

---

**文档版本**: v2.0
**最后更新**: 2026-01-01
**维护者**: WellAlly Tech
