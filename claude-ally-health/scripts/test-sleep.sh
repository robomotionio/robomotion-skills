#!/bin/bash

# 睡眠质量管理功能测试脚本
# 版本: v1.0
# 创建日期: 2026-01-02

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
echo "睡眠质量管理功能测试"
echo "========================================="
echo ""

# ========================================
# 第一组：基础功能测试 (15个测试)
# ========================================

echo -e "${YELLOW}第一组：基础功能测试 (15个)${NC}"
echo ""

# 命令文件测试
test_file ".claude/commands/sleep.md" "睡眠命令文件存在"
test_disclaimer_in_file ".claude/commands/sleep.md" "命令包含医学免责声明"

# 数据文件测试
test_file "data-example/sleep-tracker.json" "睡眠数据文件存在"
test_json_structure "data-example/sleep-tracker.json" "sleep_tracking" "数据结构正确"
test_json_structure "data-example/sleep-tracker.json" "user_profile" "用户档案结构正确"

# 日志目录测试
test_directory_exists "data-example/sleep-logs" "睡眠日志目录存在"
test_directory_exists "data-example/sleep-logs/2025-06" "月度日志目录存在"
test_file "data-example/sleep-logs/2025-06/2025-06-20.json" "睡眠日志文件存在"
test_json_structure "data-example/sleep-logs/2025-06/2025-06-20.json" "sleep_records" "日志结构正确"

# 索引文件测试
test_file "data-example/sleep-logs/.index.json" "索引文件存在"
test_json_structure "data-example/sleep-logs/.index.json" "months" "索引结构正确"

# 技能文件测试
test_file ".claude/skills/sleep-analyzer/SKILL.md" "睡眠分析技能文件存在"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 技能包含医学安全边界 ... "
if grep -q "医学安全\|重要声明\|免责声明\|安全原则" ".claude/skills/sleep-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    echo "   未找到医学安全边界声明"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("技能包含医学安全边界")
fi

# 测试脚本测试
test_file "scripts/test-sleep.sh" "测试脚本文件存在"
test_directory_exists ".claude/skills/sleep-analyzer" "技能目录存在"

echo ""

# ========================================
# 第二组：医学安全测试 (10个测试)
# ========================================

echo -e "${YELLOW}第二组：医学安全测试 (10个)${NC}"
echo ""

# 医学免责声明测试
test_disclaimer_in_file ".claude/commands/sleep.md" "包含医学免责声明"
test_keyword_in_file ".claude/commands/sleep.md" "诊断.*疾病" "包含不诊断疾病声明"
test_keyword_in_file ".claude/commands/sleep.md" "开具.*药物" "包含不开具药物声明"
test_keyword_in_file ".claude/commands/sleep.md" "替代.*治疗" "包含不替代治疗声明"

# 评估量表测试
test_keyword_in_file ".claude/commands/sleep.md" "PSQI" "包含PSQI量表说明"
test_keyword_in_file ".claude/commands/sleep.md" "Epworth" "包含Epworth量表说明"
test_keyword_in_file ".claude/commands/sleep.md" "ISI" "包含ISI量表说明"

# 就医建议测试
test_keyword_in_file ".claude/commands/sleep.md" "何时需要就医" "包含就医引导建议"
test_keyword_in_file ".claude/commands/sleep.md" "参考资源" "包含参考资源链接"

echo ""

# ========================================
# 第三组：数据结构测试 (10个测试)
# ========================================

echo -e "${YELLOW}第三组：数据结构测试 (10个)${NC}"
echo ""

# sleep-tracker.json 结构测试
test_json_structure "data-example/sleep-tracker.json" "sleep_tracking" "sleep_tracking模块存在"
test_json_structure "data-example/sleep-tracker.json" "sleep_assessments" "sleep_assessments模块存在"
test_json_structure "data-example/sleep-tracker.json" "sleep_problems" "sleep_problems模块存在"
test_json_structure "data-example/sleep-tracker.json" "sleep_hygiene" "sleep_hygiene模块存在"
test_json_structure "data-example/sleep-tracker.json" "sleep_analytics" "sleep_analytics模块存在"
test_json_structure "data-example/sleep-tracker.json" "typical_bedtime" "typical_bedtime字段存在"
test_json_structure "data-example/sleep-tracker.json" "statistics" "statistics字段存在"

# 睡眠日志结构测试
test_json_structure "data-example/sleep-logs/2025-06/2025-06-20.json" "sleep_times" "sleep_times字段存在"
test_json_structure "data-example/sleep-logs/2025-06/2025-06-20.json" "sleep_metrics" "sleep_metrics字段存在"
test_json_structure "data-example/sleep-logs/2025-06/2025-06-20.json" "sleep_quality" "sleep_quality字段存在"

echo ""

# ========================================
# 第四组：集成测试 (10个测试)
# ========================================

echo -e "${YELLOW}第四组：集成测试 (10个)${NC}"
echo ""

# 慢性病管理集成测试
test_file "data-example/hypertension-tracker.json" "高血压数据文件存在（用于集成）"
test_file "data-example/diabetes-tracker.json" "糖尿病数据文件存在（用于集成）"
test_file "data-example/fitness-tracker.json" "运动数据文件存在（用于集成）"

# 睡眠与运动关联分析测试
test_keyword_in_file ".claude/skills/sleep-analyzer/SKILL.md" "运动" "睡眠分析支持运动关联"
test_keyword_in_file ".claude/skills/fitness-analyzer/SKILL.md" "睡眠" "运动分析支持睡眠关联"

# 健康趋势分析器集成测试
test_file ".claude/skills/health-trend-analyzer/SKILL.md" "健康趋势分析器技能存在"
test_keyword_in_file ".claude/skills/sleep-analyzer/SKILL.md" "相关性分析" "睡眠分析支持数据关联分析"

# 睡眠问题识别测试
test_keyword_in_file ".claude/commands/sleep.md" "失眠" "失眠评估功能说明"
test_keyword_in_file ".claude/commands/sleep.md" "呼吸暂停" "呼吸暂停筛查功能说明"
test_keyword_in_file ".claude/commands/sleep.md" "STOP-BANG" "STOP-BANG问卷说明"

echo ""

# ========================================
# 测试报告
# ========================================

echo "========================================="
echo "测试报告"
echo "========================================="
echo ""
echo "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 部分测试失败${NC}"
    echo ""
    echo "失败的测试:"
    for test_name in "${FAILED_TEST_NAMES[@]}"; do
        echo "  - $test_name"
    done
    exit 1
fi
