# 食物数据库维护指南

**数据库文件**:
- `data-example/food-database.json` - 食物营养数据库
- `data-example/food-categories.json` - 食物分类体系
- `data-example/nutritional-reference.json` - 营养素参考摄入量

**版本**: v1.0
**创建日期**: 2026-01-06
**当前食物数量**: 50种

---

## 数据库结构

### 1. 食物营养数据库 (food-database.json)

```json
{
  "metadata": {
    "version": "1.0.0",
    "created_date": "2026-01-06",
    "last_updated": "2026-01-06",
    "total_foods": 50,
    "data_source": "中国食物成分表(第6版) + USDA FoodData Central",
    "language": "zh-CN"
  },
  "foods": [
    {
      "id": "FD_001",
      "name": "燕麦",
      "name_en": "Oats",
      "aliases": ["燕麦片", "oats", "rolled oats"],
      "category": "grains",
      "subcategory": "whole_grains",
      "standard_portion": {
        "amount": 100,
        "unit": "g",
        "description": "100克"
      },
      "nutrition_per_100g": { ... },
      "special_nutrients": { ... },
      "glycemic_index": { ... },
      "common_portions": [ ... ],
      "health_tags": [ ... ],
      "suitable_for": [ ... ],
      "notes": "备注信息"
    }
  ]
}
```

### 2. 食物分类体系 (food-categories.json)

```json
{
  "metadata": { ... },
  "categories": [
    {
      "id": "CAT_001",
      "code": "grains",
      "name": "谷物类",
      "name_en": "Grains",
      "subcategories": [ ... ]
    }
  ]
}
```

### 3. 营养素参考值 (nutritional-reference.json)

```json
{
  "metadata": { ... },
  "population_groups": { ... },
  "reference_daily_intake": { ... },
  "special_diets": { ... },
  "health_conditions": { ... }
}
```

---

## 如何添加新食物

### 步骤1: 获取营养数据

**权威数据源**:
- **中国食物成分表**: https://fdc.moj.gov.cn/
- **USDA FoodData Central**: https://fooddatacentral.usda.gov/
- **《中国居民膳食指南》**: https://www.cnsoc.org/

### 步骤2: 准备食物信息

创建新食物条目需要以下信息:

#### 必填字段

```json
{
  "id": "FD_051",                    // 唯一ID (FD_001 - FD_999)
  "name": "食物名称",                 // 中文名称
  "name_en": "Food Name",            // 英文名称
  "aliases": ["别名1", "alias1"],     // 别名数组
  "category": "分类代码",             // 主分类
  "subcategory": "子分类代码",       // 子分类

  "standard_portion": {
    "amount": 100,
    "unit": "g",
    "description": "100克"
  },

  "nutrition_per_100g": {
    // 能量与宏量营养素 (必填)
    "calories": 100,                  // 卡路里
    "protein_g": 10,                  // 蛋白质(克)
    "carbs_g": 20,                   // 碳水(克)
    "fat_g": 5,                      // 脂肪(克)
    "fiber_g": 3,                    // 膳食纤维(克)

    // 维生素 (推荐填写)
    "vitamin_a_mcg": 0,
    "vitamin_c_mg": 10,
    "vitamin_d_mcg": 0,
    "vitamin_e_mg": 0.5,
    // ... 更多维生素

    // 矿物质 (推荐填写)
    "calcium_mg": 50,
    "iron_mg": 1,
    "magnesium_mg": 20,
    // ... 更多矿物质
  },

  // 特殊营养素 (可选)
  "special_nutrients": {
    "omega_3_g": 0.5,
    "omega_6_g": 2,
    "choline_mg": 20
  },

  // 升糖指数 (推荐填写)
  "glycemic_index": {
    "value": 55,
    "level": "低",                    // 极低/低/中/高
    "glycemic_load": 11
  },

  // 健康标签 (推荐填写)
  "health_tags": ["高蛋白", "低GI"],

  // 适用人群 (推荐填写)
  "suitable_for": ["素食者", "高血压"],

  // 备注 (可选)
  "notes": "食物的特殊说明"
}
```

### 步骤3: 添加到数据库

1. **打开文件**: `data-example/food-database.json`
2. **更新元数据**:
   ```json
   "metadata": {
     "total_foods": 51,              // 更新食物总数
     "last_updated": "2026-01-06"    // 更新日期
   }
   ```
3. **在 `foods` 数组中添加新食物**:
   - 确保ID唯一
   - 确保category和subcategory存在于分类体系
   - 保持JSON格式正确

### 步骤4: 更新ID分配

在文件末尾添加注释说明当前ID使用情况:

```json
// ID分配记录
// FD_001 - FD_050: 已使用
// FD_051 - FD_999: 可用
```

---

## 食物分类体系

### 10大主分类

| 代码 | 名称 | 子分类数 |
|------|------|---------|
| `grains` | 谷物类 | 3 |
| `vegetables` | 蔬菜类 | 6 |
| `fruits` | 水果类 | 5 |
| `protein` | 蛋白质来源 | 7 |
| `fats_oils` | 油脂类 | 3 |
| `beverages` | 饮料类 | 3 |
| `snacks` | 零食类 | 2 |
| `condiments` | 调味品类 | 3 |
| `processed` | 加工食品 | 3 |
| `traditional_chinese` | 中式传统食品 | 3 |

### 添加新分类

如需添加新子分类,编辑 `data-example/food-categories.json`:

```json
{
  "id": "CAT_XXX",
  "code": "new_category",
  "name": "新分类名称",
  "name_en": "New Category",
  "subcategories": [
    {
      "code": "new_subcategory",
      "name": "子分类名称",
      "name_en": "Subcategory Name",
      "examples": ["示例1", "示例2"]
    }
  ]
}
```

---

## 营养素数据质量标准

### 数据准确性

1. **使用权威来源**:
   - 优先使用《中国食物成分表(第6版)》
   - 补充USDA FoodData Central数据
   - 标注数据来源

2. **数据验证**:
   - 交叉验证多个来源
   - 确保单位正确 (mg, mcg, g等)
   - 检查数值合理性

### 完整性要求

**必需营养素** (至少包含):
- ✅ 卡路里
- ✅ 蛋白质
- ✅ 碳水化合物
- ✅ 脂肪
- ✅ 膳食纤维

**推荐营养素** (尽可能包含):
- 维生素: A, C, D, E, K, B族
- 矿物质: 钙, 铁, 镁, 锌, 钾, 磷

**可选营养素**:
- 特殊营养素: Omega-3/6, 胆碱, 植物化合物

---

## 批量更新工具

### 验证脚本

运行验证脚本检查数据质量:

```bash
# 验证JSON格式
cat data-example/food-database.json | jq .

# 统计食物数量
grep -c '"id": "FD_' data-example/food-database.json

# 检查重复ID
sort data-example/food-database.json | uniq -d

# 验证分类存在
grep -o '"category": "[^"]*"' data-example/food-database.json | sort -u
```

### 数据导入模板

创建 `data-example/import-template.json`:

```json
{
  "import_batch": "batch_name",
  "import_date": "2026-01-06",
  "import_source": "数据来源说明",
  "foods": [
    // 批量食物数据
  ]
}
```

---

## 更新日志

### v1.0.0 (2026-01-06)

**初始版本**:
- ✅ 50种常见食物
- ✅ 10大分类,30+子分类
- ✅ 完整营养素参考值
- ✅ 特殊饮食指南

**食物分类统计**:
- 谷物类: 9种
- 蛋白质来源: 17种 (肉2、禽1、鱼1、蛋1、豆4、坚果4、乳2)
- 蔬菜类: 9种
- 水果类: 10种
- 油脂类: 2种
- 饮料类: 2种
- 零食类: 1种

**计划扩展**:
- ⏳ Tier 2: 扩展至100种食物 (+50种蔬果)
- ⏳ Tier 3: 扩展至300种食物 (+200种常见食物)
- ⏳ 品牌食品数据库
- ⏳ 用户自定义食物功能

---

## 注意事项

### ⚠️ 数据安全

1. **备份**: 修改前创建备份
   ```bash
   cp data-example/food-database.json data-example/food-database.json.backup
   ```

2. **版本控制**: 使用Git管理更改
   ```bash
   git add data-example/food-database.json
   git commit -m "添加新食物: XXX"
   ```

### ⚠️ 常见错误

1. **JSON格式错误**:
   - 使用工具验证: `jq . data-example/food-database.json`
   - 检查逗号、引号、括号

2. **重复ID**:
   - 确保每个食物有唯一ID
   - 使用递增编号 (FD_001, FD_002, ...)

3. **分类不匹配**:
   - 确保category和subcategory存在于分类体系
   - 如需新分类,先更新food-categories.json

4. **营养素单位错误**:
   - 重量: g (克)
   - 维生素: mg (毫克) 或 mcg (微克)
   - 矿物质: mg (毫克)
   - 能量: kcal (卡路里)

---

## 贡献指南

### 如何贡献

1. **Fork项目** (如果使用Git)
2. **创建分支**: `git checkout -b add-foods`
3. **添加食物数据**:
   - 遵循数据结构
   - 使用权威来源
   - 验证数据准确性
4. **测试**:
   - 运行验证脚本
   - 检查JSON格式
5. **提交**: 创建Pull Request

### 贡献标准

- ✅ 数据来自权威来源
- ✅ 营养素数据完整
- ✅ 包含至少必需营养素
- ✅ JSON格式正确
- ✅ 有明确的食物分类
- ✅ 包含中英文名称

---

## 参考资源

### 营养数据来源
- **中国食物成分表**: https://fdc.moj.gov.cn/
- **USDA FoodData Central**: https://fooddatacentral.usda.gov/
- **中国居民膳食指南**: https://www.cnsoc.org/

### GI值参考
- **国际GI值数据库**: https://www.glycemicindex.com/
- **悉尼大学GI研究**: https://www.gisymbol.com/

### 营养素参考值
- **中国DRIs**: http://www.cnsoc.org/
- **美国DRIs**: https://www.nal.usda.gov/fnic/dri-calculator/

---

**维护者**: WellAlly Tech
**最后更新**: 2026-01-06
**文档版本**: v1.0
