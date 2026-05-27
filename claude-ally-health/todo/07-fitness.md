# 运动与健身功能扩展提案

**模块编号**: 07
**分类**: 通用功能扩展 - 运动与健身
**状态**: ✅ 已实现
**优先级**: 高
**创建日期**: 2025-12-31
**完成日期**: 2026-01-02

---

## 功能概述

运动与健身模块提供全面的运动记录、健身目标管理和运动处方功能，帮助用户建立健康的生活方式。

### 核心功能

1. **运动记录** - 类型、时长、强度、卡路里消耗
2. **健身目标管理** - 减重、增肌、耐力、灵活性
3. **运动数据分析** - 周统计、强度分布、习惯分析
4. **运动处方** - 基于健康状况的个性化建议

---

## 子模块 1: 运动记录

### 功能描述

记录每次运动的详细信息，包括运动类型、时长、强度、消耗卡路里等。

### 支持的运动类型

#### 有氧运动
- 跑步（户外/跑步机）
- 快走
- 骑行（户外/动感单车）
- 游泳
- 跳绳
- 有氧操
- 椭圆机
- 划船机

#### 力量训练
- 自重训练（俯卧撑、仰卧起坐、深蹲）
- 器械训练
- 自由重量（哑铃、杠铃）
- 弹力带训练

#### 球类运动
- 篮球
- 足球
- 羽毛球
- 乒乓球
- 网球
- 排球

#### 其他运动
- 瑜伽
- 普拉提
- 太极拳
- 舞蹈
- 登山
- 滑雪

### 数据结构

```json
{
  "fitness_tracking": {
    "user_profile": {
      "fitness_level": "beginner",
      "preferences": ["running", "yoga"],
      "restrictions": ["knee_issue"],
      "goals": ["weight_loss", "stress_relief"]
    },

    "workouts": [
      {
        "id": "workout_20250620001",
        "date": "2025-06-20",
        "time": "07:00",
        "duration_minutes": 30,

        "type": "running",
        "subtype": "outdoor",

        "intensity": "moderate",
        "rpe": 13,
        "heart_rate": {
          "avg": 145,
          "max": 165,
          "min": 120,
          "zones": {
            "zone_1": 0,
            "zone_2": 5,
            "zone_3": 20,
            "zone_4": 5,
            "zone_5": 0
          }
        },

        "distance_km": 5.0,
        "pace_min_per_km": 6.0,
        "cadence": 170,

        "calories_burned": 300,
        "met": 8.0,

        "route": "公园环线",
        "weather": {
          "temperature": 22,
          "condition": "sunny",
          "humidity": 60
        },

        "how_felt": "good",
        "notes": "感觉很舒服，配速稳定",
        "created_at": "2025-06-20T07:30:00.000Z"
      }
    ],

    "weekly_summary": {
      "week_start": "2025-06-16",
      "week_end": "2025-06-22",

      "total_workouts": 4,
      "total_duration_minutes": 150,
      "total_distance_km": 18.5,
      "total_calories_burned": 1200,

      "workout_days": [1, 2, 4, 6],
      "rest_days": [3, 5, 7],

      "intensity_distribution": {
        "low": 20,
        "moderate": 60,
        "high": 20
      },

      "type_distribution": {
        "running": 50,
        "yoga": 25,
        "strength": 25
      }
    }
  }
}
```

### 命令接口

```bash
# 记录运动
/fitness record running 30 minutes         # 记录跑步30分钟
/fitness record cycling 45 moderate       # 记录中等强度骑行45分钟
/fitness record yoga 60 low               # 记录低强度瑜伽60分钟

# 详细记录
/fitness record running 30 distance 5km hr 145 calories 300
# 记录跑步30分钟，5公里，平均心率145，消耗300卡路里

# 查看记录
/fitness history                          # 查看运动历史
/fitness history week                     # 查看本周记录
/fitness history 7                        # 查看最近7次记录

# 统计分析
/fitness summary week                     # 本周运动总结
/fitness summary month                    # 本月运动总结
/fitness stats                            # 运动统计数据
```

---

## 子模块 2: 健身目标管理

### 功能描述

设定、追踪和达成健身目标，包括减重、增肌、耐力提升等。

### 支持的目标类型

#### 1. 减重目标
- 目标减重量（公斤）
- 目标体重（公斤）
- 目标体脂率（%）
- 目标达成日期
- 当前进度

#### 2. 增肌目标
- 目标增重量（公斤）
- 目标肌肉量（公斤）
- 目标维度（胸围、臂围等）
- 力量提升目标

#### 3. 耐力目标
- 跑步距离目标（5K、10K、半马、全马）
- 骑行距离目标
- 游泳距离目标
- 运动时长目标

#### 4. 健康目标
- 降低静息心率
- 降低血压
- 改善血糖
- 提升柔韧性

#### 5. 习惯养成目标
- 每周运动天数
- 每天步数目标
- 每周运动时长
- 连续运动天数

### SMART原则

- **Specific（具体）**：明确的目标
- **Measurable（可衡量）**：可量化
- **Achievable（可实现）**：现实可行
- **Relevant（相关）**：与健康状况相关
- **Time-bound（有时限）**：设定截止日期

### 数据结构

```json
{
  "fitness_goals": {
    "active_goals": [
      {
        "goal_id": "goal_20250101",
        "category": "weight_loss",
        "title": "减重5公斤",

        "start_date": "2025-01-01",
        "target_date": "2025-06-30",
        "created_date": "2025-01-01T00:00:00.000Z",

        "baseline_value": 75.0,
        "current_value": 70.5,
        "target_value": 70.0,
        "unit": "kg",

        "progress": 90,
        "remaining": 0.5,
        "status": "on_track",

        "milestones": [
          {
            "title": "减重2.5公斤",
            "target_value": 72.5,
            "achieved_date": "2025-03-15",
            "achieved": true
          },
          {
            "title": "减重5公斤",
            "target_value": 70.0,
            "achieved_date": null,
            "achieved": false
          }
        ],

        "action_plan": [
          "每周运动4次，每次30-60分钟",
          "每天减少500卡路里摄入",
          "每天记录饮食",
          "每周称重1次"
        ],

        "obstacles": [
          "weekend_social_events",
          "work_stress"
        ],

        "coping_strategies": [
          "提前规划饮食",
          "压力管理技巧"
        ],

        "motivation": 8,
        "confidence": 7,
        "importance": 9,
        "notes": ""
      }
    ],

    "completed_goals": [
      {
        "goal_id": "goal_20241001",
        "title": "完成10公里跑",
        "completed_date": "2024-12-15",
        "final_value": 10.0,
        "target_value": 10.0
      }
    ],

    "goal_templates": [
      {
        "name": "5公里跑新手计划",
        "duration_weeks": 8,
        "category": "endurance",
        "description": "从0基础到完成5公里跑"
      }
    ]
  }
}
```

### 命令接口

```bash
# 设定目标
/fitness goal weight-loss 5kg 2025-06-30   # 设定减重5公斤目标
/fitness goal 5k-race 2025-08-15           # 设定完成5公里跑目标
/fitness goal workout-days 4               # 设定每周运动4天目标

# 更新进度
/fitness goal progress weight-loss 0.5kg   # 更新减重进度
/fitness goal complete 5k-race             # 标记目标完成

# 查看目标
/fitness goal list                         # 查看所有目标
/fitness goal active                       # 查看进行中目标
/fitness goal weight-loss                  # 查看特定目标
/fitness goal progress weight-loss         # 查看目标进度
```

---

## 子模块 3: 运动数据分析

### 功能描述

分析运动数据，识别运动模式，提供个性化建议。

### 分析维度

#### 1. 运动量分析
- 周运动量（时长、距离、卡路里）
- 月运动量
- 年运动量
- 运动量趋势

#### 2. 运动强度分布
- 低强度运动占比（Zone 1-2）
- 中等强度运动占比（Zone 3）
- 高强度运动占比（Zone 4-5）
- 强度分布建议

#### 3. 运动习惯分析
- 常用运动时间
- 运动频率
- 休息日分布
- 运动类型偏好

#### 4. 进步追踪
- 跑步配速提升
- 力量训练重量增加
- 耐力提升
- 体重变化与运动关系

#### 5. 运动建议
- 基于健康状况的运动建议
- 运动类型推荐
- 运动频率建议
- 运动强度建议

### 数据结构

```json
{
  "fitness_analytics": {
    "analysis_period": "last_3_months",
    "from_date": "2025-03-20",
    "to_date": "2025-06-20",

    "volume_analysis": {
      "total_workouts": 48,
      "total_duration_hours": 36,
      "total_distance_km": 240,
      "total_calories": 28800,

      "average_per_week": {
        "workouts": 4,
        "duration_hours": 3,
        "distance_km": 20,
        "calories": 2400
      },

      "trend": "increasing",
      "month_over_month_change": "+15%"
    },

    "intensity_analysis": {
      "distribution": {
        "low": 25,
        "moderate": 55,
        "high": 20
      },
      "recommendation": "ideal_balance",
      "zone_2_training": "adequate"
    },

    "habit_analysis": {
      "preferred_time": "morning",
      "preferred_day": "weekday",
      "workout_frequency": "4x_per_week",
      "rest_day_frequency": "3x_per_week",
      "consistency_score": 85
    },

    "progress_tracking": {
      "running_pace": {
        "start": "7:30_min_per_km",
        "current": "6:00_min_per_km",
        "improvement": "+20%"
      },
      "distance": {
        "start_longest": "3_km",
        "current_longest": "12_km",
        "improvement": "+300%"
      }
    },

    "insights": [
      "有氧运动占比适中，建议增加力量训练",
      "运动频率稳定，习惯良好",
      "休息日充足，恢复充分",
      "早晨运动表现最佳"
    ],

    "recommendations": [
      "每周增加2次力量训练",
      "尝试不同运动类型避免单调",
      "适当增加高强度间歇训练"
    ]
  }
}
```

### 命令接口

```bash
# 运动分析
/fitness analysis                         # 综合运动分析
/fitness analysis volume                  # 运动量分析
/fitness analysis intensity               # 运动强度分析
/fitness analysis habit                   # 运动习惯分析
/fitness analysis progress                # 进步追踪

# 查看洞察
/fitness insights                         # 查看运动洞察
/fitness recommendations                  # 查看个性化建议

# 对比分析
/fitness compare week month               # 本周vs本月对比
/fitness compare this_month last_month    # 本月vs上月对比
```

---

## 子模块 4: 运动处方

### 功能描述

基于用户的健康状况、年龄、健身水平，提供个性化的运动处方和建议。

### 运动处方要素

#### 1. 运动频率（Frequency）
- 每周运动天数
- 运动间隔

#### 2. 运动强度（Intensity）
- 目标心率区间
- RPE（主观疲劳度）
- MET值

#### 3. 运动时间（Time）
- 每次运动时长
- 热身时间
- 正式训练时间
- 放松时间

#### 4. 运动类型（Type）
- 有氧运动
- 力量训练
- 柔韧性训练
- 平衡训练

#### 5. 运动量（Volume）
- 每周总时长
- 每周总距离
- 每周消耗卡路里

### 基于健康状况的运动处方

#### 高血压
- **推荐运动**：有氧运动（快走、慢跑、骑行）
- **频率**：每周5-7天
- **强度**：中等强度（40-60%储备心率）
- **时间**：每次30-60分钟
- **注意**：避免憋气动作，监测血压

#### 糖尿病
- **推荐运动**：有氧运动+力量训练
- **频率**：每周至少150分钟中等强度有氧
- **时间**：避免空腹运动，餐后1-2小时最佳
- **注意**：监测血糖，注意低血糖

#### 骨质疏松
- **推荐运动**：负重运动、平衡训练
- **类型**：散步、跳舞、太极拳
- **避免**：高冲击运动、弯腰扭转动作
- **注意**：预防跌倒

#### 肥胖
- **推荐运动**：低冲击有氧运动
- **类型**：快走、游泳、椭圆机
- **频率**：每周5天，逐渐增加
- **目标**：每周消耗2000-2500卡路里

### 数据结构

```json
{
  "exercise_prescription": {
    "user_id": "user_001",
    "assessment_date": "2025-06-20",

    "health_conditions": [
      "hypertension",
      "obesity"
    ],

    "fitness_level": "beginner",
    "age": 45,
    "max_hr": 175,
    "resting_hr": 72,

    "prescription": {
      "aerobic_exercise": {
        "recommended": true,
        "types": ["brisk_walking", "cycling", "swimming"],
        "frequency": "5-7_days_per_week",
        "intensity": {
          "target_hr_zone": "90-115_bpm",
          "rpe": "11-13",
          "description": "moderate"
        },
        "duration": "30-60_minutes",
        "volume": "150-300_minutes_per_week"
      },

      "strength_training": {
        "recommended": true,
        "frequency": "2-3_days_per_week",
        "intensity": "moderate",
        "exercises": ["squats", "wall_push-ups", "plank"],
        "sets": 2,
        "reps": "12-15"
      },

      "flexibility": {
        "recommended": true,
        "frequency": "2-3_days_per_week",
        "duration": "10-15_minutes",
        "types": ["static_stretching", "yoga"]
      },

      "warm_up": {
        "duration": "5-10_minutes",
        "activities": ["light_walking", "arm_circles", "leg_swings"]
      },

      "cool_down": {
        "duration": "5-10_minutes",
        "activities": ["light_walking", "stretching"]
      }
    },

    "precautions": [
      "避免憋气（瓦尔萨瓦动作）",
      "运动前后监测血压",
      "如有胸痛、头晕立即停止",
      "逐渐增加运动强度",
      "保持充足水分"
    ],

    "contra_indications": [
      "uncontrolled_hypertension",
      "recent_cardiac_event"
    ],

    "goals": [
      "lower_blood_pressure",
      "weight_loss",
      "improve_cardiovascular_health"
    ],

    "progression_plan": {
      "week_1_2": "20_minutes_moderate_intensity",
      "week_3_4": "30_minutes_moderate_intensity",
      "week_5_8": "30-45_minutes_moderate_intensity",
      "week_9_12": "add_strength_training_2x_week"
    },

    "follow_up": "2025-09-20",
    "review_frequency": "3_months"
  }
}
```

### 命令接口

```bash
# 获取运动处方
/fitness prescription                      # 获取个性化运动处方
/fitness prescription hypertension         # 基于高血压的运动处方
/fitness prescription weight-loss          # 减重运动处方

# 查看注意事项
/fitness precautions                      # 运动注意事项
/fitness contra-indications               # 运动禁忌

# 进阶计划
/fitness progression                      # 查看进阶计划
```

---

## 医学安全原则

### ⚠️ 安全红线

1. **不给出具体运动处方**
   - 运动处方需医生或运动专家制定
   - 系统仅提供一般性建议

2. **不处理运动损伤**
   - 不诊断运动损伤
   - 损伤需就医

3. **不评估心血管风险**
   - 不评估运动风险
   - 运动前需医生评估

4. **不替代专业指导**
   - 复杂运动需专业教练指导
   - 系统仅提供记录和分析

### ✅ 系统能做到的

- 运动数据记录和分析
- 运动目标管理
- 运动趋势识别
- 一般性运动建议
- 基于健康状况的参考建议

---

## 注意事项

### 运动安全

- 运动前充分热身
- 运动后适当拉伸
- 逐渐增加运动量
- 注意身体信号
- 保持水分补充

### 特殊人群

- 慢性疾病患者运动需医生许可
- 孕妇运动需产科医生建议
- 老年人注意平衡和防跌倒
- 儿童运动需适合年龄

### 运动禁忌

- 发热、急性疾病期间不运动
- 空腹或饱餐后立即运动
- 酒精后不运动
- 极端天气户外运动需谨慎

---

## 参考资源

### 运动指南
- [WHO身体活动和久坐行为指南](https://www.who.int/publications/i/item/9789240015128)
- [美国身体活动指南](https://health.gov/paguidelines/)

### 运动处方
- [ACSM运动测试与处方指南](https://www.acsm.org/)
- [运动处方专业培训](https://www.acsm.org/certifications)

### 特殊人群运动
- [高血压患者运动指南](https://www.ahajournals.org/)
- [糖尿病患者运动指南](https://www.diabetes.org/)

---

**文档版本**: v1.0
**最后更新**: 2025-12-31
**维护者**: WellAlly Tech
