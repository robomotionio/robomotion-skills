# 数据示例目录 (Data Examples)

本目录包含健康追踪系统的示例数据文件。

---

## 文件清单

### 营养模块数据

| 文件名 | 说明 | 用途 |
|--------|------|------|
| [food-database.json](./food-database.json) | 食物营养数据库 | 50种常见食物的营养数据 |
| [food-categories.json](./food-categories.json) | 食物分类体系 | 10大分类,30+子分类 |
| [nutritional-reference.json](./nutritional-reference.json) | 营养素参考值 | 各人群RDA、特殊饮食指南 |
| [nutrition-tracker.json](./nutrition-tracker.json) | 营养追踪主数据 | 用户营养目标和评估 |
| [nutrition-logs/](./nutrition-logs/) | 营养日志目录 | 每日饮食记录 |

### 其他模块数据

| 文件名 | 说明 |
|--------|------|
| [profile.json](./profile.json) | 用户基本档案 |
| [fitness-tracker.json](./fitness-tracker.json) | 运动追踪数据 |
| [sleep-tracker.json](./sleep-tracker.json) | 睡眠追踪数据 |
| [hypertension-tracker.json](./hypertension-tracker.json) | 高血压管理数据 |
| [diabetes-tracker.json](./diabetes-tracker.json) | 糖尿病管理数据 |

---

## 快速开始

### 1. 食物数据库使用

**查询食物营养**:
```bash
/nutrition food 燕麦
```

**比较食物**:
```bash
/nutrition compare 燕麦 白米
```

**获取推荐**:
```bash
/nutrition recommend 高纤维
```

### 2. 数据格式说明

**食物数据结构**:
```json
{
  "id": "FD_001",
  "name": "燕麦",
  "name_en": "Oats",
  "category": "grains",
  "nutrition_per_100g": {
    "calories": 389,
    "protein_g": 16.9,
    "carbs_g": 66.3,
    "fat_g": 6.9,
    "fiber_g": 10.6
  }
}
```

---

## 维护指南

### 📖 [食物数据库维护指南](./README-food-database.md)

详细说明如何:
- ✅ 添加新食物到数据库
- ✅ 更新营养素数据
- ✅ 扩展食物分类体系
- ✅ 维护营养素参考值

### 关键要点

1. **数据来源**: 使用权威数据源 (中国食物成分表、USDA)
2. **数据完整性**: 必须包含至少5种基础营养素
3. **格式验证**: 修改后使用 `jq` 工具验证JSON格式
4. **版本控制**: 每次更新修改 `last_updated` 字段

---

## 数据统计

### 食物数据库 (v1.0)

- **总食物数**: 50种
- **分类数**: 10大类, 48个子类
- **营养素数据**: 30+项/食物

**分类分布**:
- 谷物类: 9种
- 蛋白质来源: 17种
- 蔬菜类: 9种
- 水果类: 10种
- 油脂类: 2种
- 饮料类: 2种
- 零食类: 1种

### 营养素参考值

- **人群分组**: 10+组 (性别、年龄、特殊状态)
- **宏量营养素**: 7项 (卡路里、蛋白质、碳水、脂肪、纤维等)
- **维生素**: 13种 (A、C、D、E、K、B族)
- **矿物质**: 11种 (钙、铁、镁、锌等)
- **特殊饮食**: 5种 (DASH、地中海、素食等)

---

## 扩展计划

### 短期目标 (1-2个月)
- [ ] 扩展至100种食物
- [ ] 添加更多常见份量
- [ ] 完善烹饪影响数据

### 中期目标 (3-6个月)
- [ ] 扩展至300种食物
- [ ] 添加品牌食品数据
- [ ] 支持用户自定义食物

### 长期目标 (持续)
- [ ] 持续更新数据
- [ ] 添加季节性食物
- [ ] 集成条形码扫描

---

## 数据安全

⚠️ **重要提示**:
1. 本目录数据为示例数据,不应用于生产环境
2. 真实用户数据应存储在 `data/` 目录
3. 修改数据前请先创建备份
4. 使用Git版本控制跟踪更改

---

## 贡献

欢迎贡献数据改进!

1. 查看 [README-food-database.md](./README-food-database.md)
2. 准备食物数据(使用权威来源)
3. 验证JSON格式
4. 提交Pull Request

---

**目录维护**: WellAlly Tech
**最后更新**: 2026-01-06
**版本**: v1.0
