# 睡眠质量管理功能扩展提案

**模块编号**: 08
**分类**: 通用功能扩展 - 睡眠管理
**状态**: ✅ 已实现
**优先级**: 高
**创建日期**: 2025-12-31
**实施日期**: 2026-01-02
**版本**: v1.0

---

## 功能概述

睡眠质量管理模块提供全面的睡眠监测、评估和改善建议，帮助用户改善睡眠质量。

### 核心功能

1. **睡眠记录** - 入睡/起床时间、睡眠时长、睡眠质量
2. **睡眠评估** - PSQI、Epworth、ISI量表
3. **睡眠问题识别** - 失眠、呼吸暂停、不宁腿
4. **睡眠卫生建议** - 习惯、环境、作息建议

---

## 子模块 1: 睡眠记录

### 功能描述

记录每日睡眠信息，追踪睡眠模式和趋势。

### 记录内容

#### 睡眠时间
- **上床时间**
- **入睡时间**（实际开始睡觉时间）
- **起床时间**
- **睡眠时长**（实际睡眠时间）
- **在床时长**（从上床到起床的总时间）

#### 睡眠效率
- **睡眠效率** = 睡眠时长 / 在床时长 × 100%
- 正常：>85%
- 失眠：<85%

#### 睡眠阶段
- **浅睡**
- **深睡**
- **REM睡眠**
- **清醒**

#### 睡眠质量
- 主观睡眠质量：好/中/差
- 睡后恢复感：充分/一般/不足
- 晨起状态

#### 夜间觉醒
- **觉醒次数**
- **觉醒时长**
- **觉醒原因**（尿意、噪音、不适等）

### 数据结构

```json
{
  "sleep_tracking": {
    "sleep_records": [
      {
        "date": "2025-06-20",
        "bedtime": "23:00",
        "sleep_onset_time": "23:30",
        "wake_time": "07:00",
        "out_of_bed_time": "07:15",

        "sleep_duration_hours": 7.0,
        "time_in_bed_hours": 8.25,
        "sleep_latency_minutes": 30,
        "sleep_efficiency": 84.8,

        "sleep_stages": {
          "light_sleep": "3.5h",
          "deep_sleep": "1.5h",
          "rem_sleep": "2.0h",
          "awake": "0.5h"
        },

        "awakenings": {
          "count": 2,
          "total_duration_minutes": 15,
          "causes": ["bathroom", "noise"]
        },

        "sleep_quality": "fair",
        "rested_feeling": "somewhat",
        "morning_mood": "neutral",

        "factors": {
          "caffeine_after_2pm": false,
          "alcohol": false,
          "exercise": true,
          "exercise_time": "18:00",
          "screen_time_before_bed": 60,
          "bedroom_temperature": 22
        },

        "notes": "",
        "created_at": "2025-06-20T07:15:00.000Z"
      }
    ],

    "weekly_summary": {
      "week_start": "2025-06-16",
      "week_end": "2025-06-22",

      "average_sleep_duration": 6.8,
      "average_bedtime": "23:15",
      "average_wake_time": "07:05",
      "average_sleep_latency": 28,
      "average_sleep_efficiency": 83.5,

      "sleep_quality_distribution": {
        "good": 2,
        "fair": 4,
        "poor": 1
      },

      "total_records": 7,
      "longest_sleep": 7.5,
      "shortest_sleep": 5.5
    },

    "patterns": {
      "weekday_vs_weekend": {
        "weekday_avg_duration": 6.5,
        "weekend_avg_duration": 7.8
      },
      "optimal_bedtime": "22:30-23:00",
      "optimal_wake_time": "06:30-07:00"
    }
  }
}
```

### 命令接口

```bash
# 记录睡眠
/sleep record 23:00 07:00 good            # 记录上床、起床时间、睡眠质量
/sleep record bedtime 23:00 onset 23:30 wake 07:00  # 详细记录
/sleep record 23:00 07:00 fair 2 awakenings  # 记录觉醒次数

# 查看记录
/sleep history                            # 查看睡眠历史
/sleep history week                       # 查看本周记录
/sleep pattern                            # 查看睡眠模式
/sleep summary week                       # 本周睡眠总结

# 睡眠统计
/sleep average                            # 平均睡眠时长
/sleep efficiency                         # 睡眠效率
/sleep latency                            # 入睡时间
```

---

## 子模块 2: 睡眠评估量表

### 功能描述

使用标准化量表评估睡眠质量和睡眠问题严重程度。

#### 1. PSQI（匹兹堡睡眠质量指数）

**7个成分**（每个0-3分）：

**C1. 主观睡眠质量**：
- 0分：很好
- 1分：较好
- 2分：较差
- 3分：很差

**C2. 入睡时间**：
- 0分：≤15分钟
- 1分：16-30分钟
- 2分：31-60分钟
- 3分：>60分钟

**C3. 睡眠时间**：
- 0分：>7小时
- 1分：6-7小时
- 2分：5-6小时
- 3分：<5小时

**C4. 睡眠效率**（睡眠时长/在床时长）：
- 0分：>85%
- 1分：75-84%
- 2分：65-74%
- 3分：<65%

**C5. 睡眠障碍**：
- 0分：无问题
- 1分：轻度问题（<1次/周）
- 2分：中度问题（1-2次/周）
- 3分：重度问题（≥3次/周）

**C6. 催眠药物使用**：
- 0分：无
- 1分：<1次/周
- 2分：1-2次/周
- 3分：≥3次/周

**C7. 日间功能障碍**：
- 0分：无
- 1分：轻度（<1次/周）
- 2分：中度（1-2次/周）
- 3分：重度（≥3次/周）

**总分**：0-21分
- ≤5分：睡眠质量好
- 6-10分：睡眠质量一般
- ≥11分：睡眠质量差

#### 2. Epworth嗜睡量表（ESS）

**8种情况下打瞌睡的可能**（0-3分）：
- 0分：不会打瞌睡
- 1分：打瞌睡可能性很小
- 2分：打瞌睡可能性中等
- 3分：很可能打瞌睡

**情境**：
1. 坐着阅读时
2. 看电视时
3. 在公共场所坐着不动时（如剧场、会议）
4. 连续坐1小时乘车时
5. 下午躺下休息时（条件允许时）
6. 坐着与人交谈时
7. 午饭后静坐时（未饮酒）
8. 等红绿灯驾车时

**总分**：0-24分
- 0-7分：正常
- 8-10分：轻度嗜睡
- 11-15分：中度嗜睡
- 16-24分：重度嗜睡

#### 3. ISI（失眠严重度指数）

**7个问题**（0-4分）：
1. 入睡困难
2. 维持睡眠困难
3. 早醒
4. 对睡眠模式满意程度
5. 白天疲劳程度
6. 日间功能受损程度
7. 睡眠问题对生活质量的影响

**总分**：0-28分
- 0-7分：无临床显著失眠
- 8-14分：轻度失眠
- 15-21分：中度失眠
- 22-28分：重度失眠

### 数据结构

```json
{
  "sleep_assessments": {
    "psqi": {
      "date": "2025-06-20",
      "total_score": 8,
      "interpretation": "fair",

      "components": {
        "subjective_quality": 2,
        "sleep_latency": 2,
        "sleep_duration": 1,
        "sleep_efficiency": 1,
        "sleep_disturbances": 1,
        "medication_use": 0,
        "daytime_dysfunction": 1
      },

      "history": [
        {
          "date": "2025-03-20",
          "score": 10
        },
        {
          "date": "2024-12-20",
          "score": 12
        }
      ],

      "trend": "improving"
    },

    "epworth": {
      "date": "2025-06-20",
      "total_score": 6,
      "interpretation": "normal",

      "responses": {
        "sitting_reading": 1,
        "watching_tv": 2,
        "sitting_inactive_public": 0,
        "passenger_car": 1,
        "lying_afternoon": 1,
        "sitting_talking": 0,
        "sitting_after_lunch": 1,
        "driving_stopped": 0
      }
    },

    "isi": {
      "date": "2025-06-20",
      "total_score": 11,
      "interpretation": "moderate_insomnia",

      "items": {
        "difficulty_falling_asleep": 2,
        "difficulty_staying_asleep": 1,
        "early_morning_awakening": 2,
        "satisfaction_with_sleep": 2,
        "daytime_fatigue": 2,
        "impairment_daytime_functioning": 1,
        "interference_with_quality_of_life": 1
      }
    },

    "assessment_schedule": {
      "psqi_frequency": "quarterly",
      "next_assessment": "2025-09-20"
    }
  }
}
```

### 命令接口

```bash
# PSQI评估
/sleep psqi                               # 进行PSQI评估
/sleep psqi score 8                       # 记录PSQI分数
/sleep psqi history                       # 查看PSQI历史

# Epworth嗜睡量表
/sleep epworth                            # 进行Epworth评估
/sleep epworth score 6                    # 记录Epworth分数

# ISI失眠严重度
/sleep isi                                # 进行ISI评估
/sleep isi score 11                       # 记录ISI分数

# 查看评估结果
/sleep assessments                        # 查看所有评估
/sleep trend                              # 查看睡眠质量趋势
```

---

## 子模块 3: 睡眠问题识别

### 功能描述

识别常见睡眠问题，提供相应建议。

#### 1. 失眠

**类型**：
- **入睡困难**：入睡时间>30分钟
- **睡眠维持困难**：夜间觉醒>2次或总觉醒时间>30分钟
- **早醒**：比预期提前醒来>30分钟且无法再入睡
- **慢性失眠**：每周≥3次，持续≥3个月

**原因识别**：
- 压力、焦虑
- 不良睡眠习惯
- 环境因素
- 药物、物质（咖啡因、酒精）
- 疾病（疼痛、呼吸暂停）

#### 2. 阻塞性睡眠呼吸暂停（OSA）

**症状**：
- 打鼾（尤其响亮、不规律）
- 观察到呼吸暂停
- 夜间憋醒
- 白天过度嗜睡
- 晨起头痛
- 夜尿增多

**风险评估**：
- STOP-BANG问卷
- 体格检查（BMI、颈围）
- 多导睡眠图（PSG）

**严重程度**：
- 轻度：AHI 5-15
- 中度：AHI 15-30
- 重度：AHI >30

#### 3. 不宁腿综合征（RLS）

**诊断标准**：
- 有活动腿的冲动
- 不适感（爬行、蚁走、酸胀）
- 运动后部分或完全缓解
- 症状在晚间/夜间加重或仅晚间出现

#### 4. 周期性肢体运动（PLMD）

**特征**：
- 睡眠时腿部重复性不自主运动
- 每20-40秒一次
- 导致睡眠片段化

#### 5. 昼夜节律睡眠-觉醒障碍

**类型**：
- **睡眠时相延迟**：入睡和起床时间显著延迟
- **睡眠时相提前**：入睡和起床时间显著提前
- **倒班工作睡眠障碍**：工作时间不规律
- **时差反应**：跨时区旅行后

### 数据结构

```json
{
  "sleep_problems": {
    "insomnia": {
      "present": true,
      "type": "mixed",
      "onset_date": "2024-01-01",
      "duration": "18_months",
      "frequency": "4-5_nights_per_week",

      "symptoms": {
        "difficulty_falling_asleep": true,
        "sleep_maintenance": true,
        "early_morning_awakening": false
      },

      "causes": [
        "work_stress",
        "excessive_worry"
      ],

      "impact": {
        "daytime_fatigue": "moderate",
        "mood_irritability": true,
        "concentration_difficulty": true,
        "work_performance": "mild_impairment"
      }
    },

    "sleep_apnea": {
      "screening": {
        "stop_bang_score": 3,
        "risk": "intermediate",
        "snoring": true,
        "tired": true,
        "observed_apnea": false,
        "pressure": "high",
        "bmi": 28,
        "age": 52,
        "neck_size": "large",
        "gender": "male"
      },

      "diagnosis": {
        "diagnosed": false,
        "ahi": null,
        "severity": null,
        "psg_date": null
      },

      "symptoms": {
        "snoring": true,
        "snoring_loud": true,
        "gasping_choking": false,
        "dry_mouth_morning": true,
        "morning_headache": true,
        "daytime_sleepiness": "moderate",
        "night_sweats": false
      }
    },

    "rls": {
      "present": false,
      "symptoms": []
    },

    "plmd": {
      "present": false,
      "diagnosed": false
    },

    "circadian_rhythm": {
      "disorder": false,
      "type": null
    }
  }
}
```

### 命令接口

```bash
# 失眠评估
/sleep problem insomnia                    # 评估失眠
/sleep problem insomnia type mixed         # 记录失眠类型
/sleep problem insomnia cause stress       # 记录原因

# 呼吸暂停筛查
/sleep apnea screening                    # 呼吸暂停筛查
/sleep apnea stop-bang                    # STOP-BANG问卷
/sleep snoring loud                       # 记录打鼾

# 其他睡眠问题
/sleep problem rls                        # 不宁腿评估
/sleep problem plmd                       # 周期性肢体运动

# 查看问题
/sleep problems                           # 查看所有睡眠问题
```

---

## 子模块 4: 睡眠卫生建议

### 功能描述

提供个性化的睡眠卫生建议，改善睡眠质量。

#### 1. 作息规律建议

- 固定起床时间（包括周末）
- 固定上床时间
- 午睡限制（<30分钟，下午3点前）
- 逐步调整作息（每次15分钟）

#### 2. 睡前准备建议

**睡前1-2小时**：
- 避免屏幕时间（蓝光）
- 避免剧烈运动
- 避免大餐
- 避免兴奋性讨论

**睡前30分钟**：
- 放松活动（阅读、冥想、温水澡）
- 调暗灯光
- 保持卧室安静

**放松技巧**：
- 深呼吸（4-7-8呼吸法）
- 渐进性肌肉放松
- 正念冥想
- 引导想象

#### 3. 睡眠环境建议

**卧室环境**：
- 温度：18-22℃
- 湿度：40-60%
- 光线：黑暗（使用遮光窗帘、眼罩）
- 噪音：安静（使用耳塞、白噪音）

**床上用品**：
- 舒适的床垫和枕头
- 透气的床品
- 合适的被子厚度

#### 4. 生活方式建议

**日间习惯**：
- 规律运动（至少150分钟/周中等强度）
- 早晨或下午户外时间
- 避免长时间午睡

**饮食建议**：
- 限制咖啡因（上午、下午早些时候）
- 避免酒精（影响REM睡眠）
- 晚餐清淡、睡前2-3小时
- 限制液体摄入（睡前2小时）

**物质使用**：
- 咖啡因：下午2点后避免
- 尼古丁：睡前避免（兴奋剂）
- 酒精：避免助眠（破坏睡眠结构）

#### 5. 认知行为疗法（CBT-I）

**睡眠限制**：
- 限制在床时间等于实际睡眠时间
- 逐步增加至理想时长

**刺激控制**：
- 床只用于睡眠和性生活
- 困倦时才上床
- 20分钟无法入睡起床
- 固定起床时间
- 避免日间小睡

**认知重构**：
- 识别和挑战关于睡眠的负面想法
- 建立现实的睡眠期望
- 减少睡眠焦虑

### 数据结构

```json
{
  "sleep_hygiene": {
    "current_practices": {
      "bedroom_temperature": 22,
      "light_level": "dim",
      "noise_level": "quiet",
      "mattress_comfort": "good",
      "pillow_comfort": "good",

      "bedtime_routine": "inconsistent",
      "screen_time_before_bed": 60,
      "relaxation_activities": ["reading"],

      "caffeine_cutoff": "4pm",
      "alcohol_use": "occasional",
      "exercise_time": "evening",
      "exercise_frequency": "3x_weekly",

      "naps": {
        "takes_naps": true,
        "frequency": "weekends",
        "duration_minutes": 45
      }
    },

    "recommendations": {
      "schedule": [
        "set_consistent_bedtime_2300",
        "set_consistent_waketime_0700",
        "limit_nap_to_30_minutes",
        "avoid_napping_after_3pm"
      ],

      "bedtime_routine": [
        "start_routine_1_hour_before_bed",
        "avoid_screens_30_minutes_before_bed",
        "dim_lights",
        "practice_relaxation_technique",
        "take_warm_bath"
      ],

      "environment": [
        "optimize_temperature_18-22C",
        "use_blackout_curtains",
        "use_white_noise_machine",
        "remove_clock_from_view"
      ],

      "lifestyle": [
        "move_exercise_to_morning_or_afternoon",
        "stop_caffeine_by_2pm",
        "avoid_alcohol_before_bed",
        "avoid_heavy_meals_3_hours_before_bed"
      ],

      "cbt_i_elements": [
        "stimulus_control",
        "sleep_restrictions",
        "cognitive_restructuring",
        "relaxation_training"
      ]
    },

    "action_plan": {
      "priority_1": "establish_consistent_schedule",
      "priority_2": "create_bedtime_routine",
      "priority_3": "optimize_bedroom",
      "timeline": "4-6_weeks"
    }
  }
}
```

### 命令接口

```bash
# 睡眠卫生评估
/sleep hygiene                             # 评估睡眠卫生
/sleep hygiene temperature 22              # 记录卧室温度
/sleep hygiene screen-time 60              # 记录屏幕时间

# 获取建议
/sleep recommendations                     # 获取睡眠建议
/sleep recommendations schedule            # 作息建议
/sleep recommendations environment          # 环境建议

# 行动计划
/sleep action-plan                         # 创建改善计划
/sleep action-plan priority 1 establish_consistent_schedule
```

---

## 医学安全原则

### ⚠️ 安全红线

1. **不诊断睡眠疾病**
   - 不诊断失眠、OSA等
   - 诊断需睡眠专科医生

2. **不开具助眠药物**
   - 不推荐具体药物
   - 药物需医生处方

3. **不替代睡眠治疗**
   - CBT-I需专业人员
   - OSA需CPAP等治疗

4. **不处理紧急情况**
   - 严重嗜睡需就医
   - 呼吸暂停需紧急处理

### ✅ 系统能做到的

- 睡眠记录和追踪
- 睡眠质量评估
- 睡眠问题识别
- 睡眠卫生建议
- 睡眠趋势分析

---

## 注意事项

### 睡眠评估

- 定期评估（每季度）
- 结合主观和客观指标
- 注意变化趋势
- 异常需就医

### 睡眠问题

- 失眠>3个月需就医
- 疑似OSA需睡眠检查
- 不宁腿需神经科评估
- 严重嗜睡需排除其他疾病

### 改善建议

- 循序渐进
- 多管齐下
- 持之以恒
- 必要时寻求专业帮助

---

## 参考资源

### 睡眠评估
- [AASM 睡眠评分标准](https://aasm.org/)
- [失眠诊疗指南](https://aasm.org/)

### 睡眠呼吸暂停
- [STOP-BANG问卷](https://www.stopbang.ca/)
- [OSA诊疗指南](https://aasm.org/)

### 睡眠卫生
- [睡眠卫生建议](https://www.cdc.gov/sleep/)
- [CBT-I治疗](https://www.ncbi.nlm.nih.gov/)

---

**文档版本**: v1.0
**最后更新**: 2025-12-31
**维护者**: WellAlly Tech
