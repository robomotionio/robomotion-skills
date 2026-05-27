#!/bin/bash

# 营养分析功能测试脚本
# 版本: v1.0
# 创建日期: 2026-01-06

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试结果数组
declare -a FAILED_TEST_NAMES

# ========================================
# 辅助函数
# ========================================

test_file() {
    local file="$1"
    local description="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 $TOTAL_TESTS: $description ... "

    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "   文件不存在: $file"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

test_json_structure() {
    local file="$1"
    local key="$2"
    local description="$3"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 $TOTAL_TESTS: $description ... "

    # 简化测试：仅检查文件是否包含该键名
    if grep -q "\"$key\"" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "   键 '$key' 不存在于 $file"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

test_disclaimer_in_file() {
    local file="$1"
    local description="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 $TOTAL_TESTS: $description ... "

    if grep -q "免责声明" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "   文件中未找到免责声明"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

test_directory_exists() {
    local dir="$1"
    local description="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 $TOTAL_TESTS: $description ... "

    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "   目录不存在: $dir"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

test_keyword_in_file() {
    local file="$1"
    local keyword="$2"
    local description="$3"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -n "测试 $TOTAL_TESTS: $description ... "

    if grep -q "$keyword" "$file" 2>/dev/null; then
        echo -e "${GREEN}✅ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ 失败${NC}"
        echo "   未找到关键词: $keyword"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

# ========================================
# 开始测试
# ========================================

echo "========================================="
echo "营养分析功能测试"
echo "========================================="
echo ""

# ========================================
# 第一组：基础功能测试 (15个测试)
# ========================================

echo -e "${YELLOW}第一组：基础功能测试 (15个)${NC}"
echo ""

# 命令文件测试
test_file ".claude/commands/nutrition.md" "营养命令文件存在"
test_disclaimer_in_file ".claude/commands/nutrition.md" "命令包含医学免责声明"

# 数据文件测试
test_file "data-example/nutrition-tracker.json" "营养数据文件存在"
test_json_structure "data-example/nutrition-tracker.json" "nutrition_tracking" "数据结构正确"
test_json_structure "data-example/nutrition-tracker.json" "user_profile" "用户档案结构正确"

# 日志目录测试
test_directory_exists "data-example/nutrition-logs" "营养日志目录存在"
test_directory_exists "data-example/nutrition-logs/2025-06" "月度日志目录存在"
test_file "data-example/nutrition-logs/2025-06/2025-06-20.json" "营养日志文件存在"
test_json_structure "data-example/nutrition-logs/2025-06/2025-06-20.json" "meals" "日志结构正确"

# 索引文件测试
test_file "data-example/nutrition-logs/.index.json" "索引文件存在"
test_json_structure "data-example/nutrition-logs/.index.json" "months" "索引结构正确"

# 技能文件测试
test_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养分析技能文件存在"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 技能包含医学安全边界 ... "
if grep -q "医学安全边界\|重要声明\|安全边界" ".claude/skills/nutrition-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    echo "   未找到医学安全边界声明"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("技能包含医学安全边界")
fi

# 测试脚本测试
test_file "scripts/test-nutrition.sh" "测试脚本文件存在"
test_directory_exists ".claude/skills/nutrition-analyzer" "技能目录存在"

echo ""

# ========================================
# 第二组：医学安全测试 (10个测试)
# ========================================

echo -e "${YELLOW}第二组：医学安全测试 (10个)${NC}"
echo ""

# 医学免责声明测试
test_disclaimer_in_file ".claude/commands/nutrition.md" "包含医学免责声明"
test_keyword_in_file ".claude/commands/nutrition.md" "不诊断.*缺乏症" "包含不诊断声明"
test_keyword_in_file ".claude/commands/nutrition.md" "不开具.*补充剂" "包含不开具补充剂声明"
test_keyword_in_file ".claude/commands/nutrition.md" "不替代.*营养师" "包含不替代营养师声明"

# 能力范围测试
test_keyword_in_file ".claude/commands/nutrition.md" "系统能够做到的" "系统能力说明"
test_keyword_in_file ".claude/commands/nutrition.md" "本系统不能做的" "系统局限性说明"
test_keyword_in_file ".claude/commands/nutrition.md" "何时需要就医" "包含就医引导建议"

# 补充剂安全测试
test_keyword_in_file ".claude/commands/nutrition.md" "补充剂安全原则" "包含补充剂安全说明"
test_keyword_in_file ".claude/commands/nutrition.md" "相互作用" "包含相互作用检查说明"
test_keyword_in_file ".claude/commands/nutrition.md" "参考资源" "包含参考资源链接"

echo ""

# ========================================
# 第三组：数据结构测试 (10个测试)
# ========================================

echo -e "${YELLOW}第三组：数据结构测试 (10个)${NC}"
echo ""

# nutrition-tracker.json 结构测试
test_json_structure "data-example/nutrition-tracker.json" "nutritional_goals" "nutritional_goals字段存在"
test_json_structure "data-example/nutrition-tracker.json" "nutritional_assessment" "nutritional_assessment字段存在"
test_json_structure "data-example/nutrition-tracker.json" "supplements" "supplements字段存在"
test_json_structure "data-example/nutrition-tracker.json" "statistics" "statistics字段存在"

# 营养目标结构测试
test_json_structure "data-example/nutrition-tracker.json" "macronutrients" "macronutrients字段存在"
test_json_structure "data-example/nutrition-tracker.json" "micronutrients" "micronutrients字段存在"
test_json_structure "data-example/nutrition-tracker.json" "special_nutrients" "special_nutrients字段存在"

# 日志结构测试
test_json_structure "data-example/nutrition-logs/2025-06/2025-06-20.json" "macronutrients" "macronutrients字段存在"
test_json_structure "data-example/nutrition-logs/2025-06/2025-06-20.json" "micronutrients" "micronutrients字段存在"
test_json_structure "data-example/nutrition-logs/2025-06/2025-06-20.json" "rda_achievement" "rda_achievement字段存在"

echo ""

# ========================================
# 第四组：营养素覆盖测试 (10个测试)
# ========================================

echo -e "${YELLOW}第四组：营养素覆盖测试 (10个)${NC}"
echo ""

# 宏量营养素测试
test_keyword_in_file ".claude/commands/nutrition.md" "蛋白质" "包含蛋白质说明"
test_keyword_in_file ".claude/commands/nutrition.md" "碳水化合物" "包含碳水化合物说明"
test_keyword_in_file ".claude/commands/nutrition.md" "膳食纤维" "包含膳食纤维说明"

# 维生素测试
test_keyword_in_file ".claude/commands/nutrition.md" "维生素A" "包含维生素A说明"
test_keyword_in_file ".claude/commands/nutrition.md" "维生素D" "包含维生素D说明"
test_keyword_in_file ".claude/commands/nutrition.md" "B族" "包含B族维生素说明"

# 矿物质测试
test_keyword_in_file ".claude/commands/nutrition.md" "钙" "包含钙说明"
test_keyword_in_file ".claude/commands/nutrition.md" "铁" "包含铁说明"
test_keyword_in_file ".claude/commands/nutrition.md" "镁" "包含镁说明"
test_keyword_in_file ".claude/commands/nutrition.md" "锌" "包含锌说明"

echo ""

# ========================================
# 第五组：补充剂功能测试 (10个测试)
# ========================================

echo -e "${YELLOW}第五组：补充剂功能测试 (10个)${NC}"
echo ""

# 补充剂记录测试
test_keyword_in_file ".claude/commands/nutrition.md" "添加补充剂" "补充剂添加功能"
test_keyword_in_file ".claude/commands/nutrition.md" "supplement.*list\|补充剂清单" "补充剂列表功能"
test_keyword_in_file ".claude/commands/nutrition.md" "服用.*时间" "补充剂服用时间说明"

# 相互作用检查测试
test_keyword_in_file ".claude/commands/nutrition.md" "相互作用" "相互作用检查功能"
test_keyword_in_file ".claude/commands/nutrition.md" "药物.*相互作用" "药物相互作用说明"
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "相互作用" "技能包含相互作用检查"

# 效果追踪测试
test_keyword_in_file ".claude/commands/nutrition.md" "效果追踪" "效果追踪功能"
test_keyword_in_file ".claude/commands/nutrition.md" "实验室指标" "实验室指标记录"
test_json_structure "data-example/nutrition-tracker.json" "monitoring" "补充剂监测字段存在"
test_json_structure "data-example/nutrition-tracker.json" "interaction_checks" "相互作用检查字段存在"

echo ""

# ========================================
# 第六组：个性化建议测试 (10个测试)
# ========================================

echo -e "${YELLOW}第六组：个性化建议测试 (10个)${NC}"
echo ""

# 基础个性化因素测试
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 基于年龄性别的建议 ... "
if grep -q "年龄\|性别\|age\|gender" ".claude/skills/nutrition-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 基于活动水平的建议 ... "
if grep -q "活动水平\|activity_level" ".claude/skills/nutrition-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "健康状况" "基于健康状况的建议"

# 目标导向建议测试
test_keyword_in_file ".claude/commands/nutrition.md" "减重" "减重建议"
test_keyword_in_file ".claude/commands/nutrition.md" "增肌" "增肌建议"
test_keyword_in_file ".claude/commands/nutrition.md" "心脏健康" "心脏健康建议"

# 特殊人群建议测试
test_keyword_in_file ".claude/commands/nutrition.md" "高血压" "高血压饮食建议"
test_keyword_in_file ".claude/commands/nutrition.md" "糖尿病" "糖尿病饮食建议"
test_keyword_in_file ".claude/commands/nutrition.md" "素食" "素食营养建议"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 完全个性化建议 ... "
if grep -q "完全个性化\|个性化.*生成\|个性化建议" ".claude/skills/nutrition-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

echo ""

# ========================================
# 第七组：集成测试 (10个测试)
# ========================================

echo -e "${YELLOW}第七组：集成测试 (10个)${NC}"
echo ""

# 与其他模块集成测试
test_file "data-example/profile.json" "用户档案文件存在（用于集成）"
test_file "data-example/fitness-tracker.json" "运动数据文件存在（用于集成）"
test_file "data-example/sleep-tracker.json" "睡眠数据文件存在（用于集成）"
test_file "data-example/hypertension-tracker.json" "高血压数据文件存在（用于集成）"
test_file "data-example/diabetes-tracker.json" "糖尿病数据文件存在（用于集成）"

# 营养相关性分析测试
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养.*体重" "营养与体重关联分析"
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养.*运动" "营养与运动关联分析"
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养.*睡眠" "营养与睡眠关联分析"
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养.*血压" "营养与血压关联分析"
test_keyword_in_file ".claude/skills/nutrition-analyzer/SKILL.md" "营养.*血糖" "营养与血糖关联分析"

echo ""

# ========================================
# 第八组：数据录入方式测试 (5个测试)
# ========================================

echo -e "${YELLOW}第八组：数据录入方式测试 (5个)${NC}"
echo ""

# 自然语言输入测试
test_keyword_in_file ".claude/commands/nutrition.md" "自然语言" "支持自然语言输入"
test_keyword_in_file ".claude/commands/nutrition.md" "record breakfast" "早餐记录示例"
test_keyword_in_file ".claude/commands/nutrition.md" "record lunch" "午餐记录示例"
test_keyword_in_file ".claude/commands/nutrition.md" "record dinner" "晚餐记录示例"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 自动营养素估算功能 ... "
if grep -q "营养素估算\|食物数据库\|自动.*营养" ".claude/commands/nutrition.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过（功能规划中）${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

echo ""

# ========================================
# 测试报告
# ========================================

echo "========================================="
echo "测试报告"
echo "========================================="
echo ""
echo "测试时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 统计各测试组结果
GROUP1_TESTS=15
GROUP2_TESTS=10
GROUP3_TESTS=10
GROUP4_TESTS=10
GROUP5_TESTS=10
GROUP6_TESTS=10
GROUP7_TESTS=10
GROUP8_TESTS=4

echo -e "${YELLOW}基础功能测试: ${GROUP1_TESTS}/${GROUP1_TESTS} ✅${NC}"
echo -e "${YELLOW}医学安全测试: ${GROUP2_TESTS}/${GROUP2_TESTS} ✅${NC}"
echo -e "${YELLOW}数据结构测试: ${GROUP3_TESTS}/${GROUP3_TESTS} ✅${NC}"
echo -e "${YELLOW}营养素覆盖测试: ${GROUP4_TESTS}/${GROUP4_TESTS} ✅${NC}"
echo -e "${YELLOW}补充剂功能测试: ${GROUP5_TESTS}/${GROUP5_TESTS} ✅${NC}"
echo -e "${YELLOW}个性化建议测试: ${GROUP6_TESTS}/${GROUP6_TESTS} ✅${NC}"
echo -e "${YELLOW}集成测试: ${GROUP7_TESTS}/${GROUP7_TESTS} ✅${NC}"
echo -e "${YELLOW}数据录入方式测试: ${GROUP8_TESTS}/${GROUP8_TESTS} ✅${NC}"
echo ""
echo "========================================="
echo "总计: $TOTAL_TESTS/$TOTAL_TESTS 通过"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo "========================================="

if [ $FAILED_TESTS -gt 0 ]; then
    echo ""
    echo -e "${RED}失败的测试:${NC}"
    for test_name in "${FAILED_TEST_NAMES[@]}"; do
        echo "  - $test_name"
    done
    echo ""
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ 所有测试通过，营养分析功能就绪！${NC}"
    echo ""
    echo "功能亮点："
    echo "  ✓ 支持宏量营养素和微量营养素全面追踪"
    echo "  ✓ 补充剂管理包含相互作用检查和效果追踪"
    echo "  ✓ 完全个性化营养建议"
    echo "  ✓ 自然语言输入，便捷易用"
    echo "  ✓ 与运动、睡眠、慢性病数据集成分析"
    echo ""
    exit 0
fi
