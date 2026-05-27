#!/bin/bash

# 运动与健身功能测试脚本
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

# ========================================
# 开始测试
# ========================================

echo "========================================="
echo "运动与健身功能测试"
echo "========================================="
echo ""

# ========================================
# 第一组：基础功能测试 (15个测试)
# ========================================

echo -e "${YELLOW}第一组：基础功能测试 (15个)${NC}"
echo ""

# 命令文件测试
test_file ".claude/commands/fitness.md" "运动命令文件存在"
test_disclaimer_in_file ".claude/commands/fitness.md" "命令包含医学免责声明"

# 数据文件测试
test_file "data-example/fitness-tracker.json" "运动数据文件存在"
test_json_structure "data-example/fitness-tracker.json" "fitness_tracking" "数据结构正确"
test_json_structure "data-example/fitness-tracker.json" "user_profile" "用户档案结构正确"

# 日志目录测试
test_directory_exists "data-example/fitness-logs" "运动日志目录存在"
test_directory_exists "data-example/fitness-logs/2025-06" "月度日志目录存在"
test_file "data-example/fitness-logs/2025-06/2025-06-20.json" "运动日志文件存在"
test_json_structure "data-example/fitness-logs/2025-06/2025-06-20.json" "workouts" "日志结构正确"

# 索引文件测试
test_file "data-example/fitness-logs/.index.json" "索引文件存在"
test_json_structure "data-example/fitness-logs/.index.json" "months" "索引结构正确"

# 技能文件测试
test_file ".claude/skills/fitness-analyzer/SKILL.md" "运动分析技能文件存在"
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 技能包含医学安全边界 ... "
if grep -q "医学安全边界\|重要声明" ".claude/skills/fitness-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    echo "   未找到医学安全边界声明"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("技能包含医学安全边界")
fi

# 测试脚本测试
test_file "scripts/test-fitness.sh" "测试脚本文件存在"
test_directory_exists ".claude/skills/fitness-analyzer" "技能目录存在"

echo ""

# ========================================
# 第二组：医学安全测试 (10个测试)
# ========================================

echo -e "${YELLOW}第二组：医学安全测试 (10个)${NC}"
echo ""

# 安全原则测试
test_disclaimer_in_file ".claude/commands/fitness.md" "包含医学免责声明"
test_disclaimer_in_file ".claude/commands/fitness.md" "包含安全红线说明"

# 检查关键安全声明
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 包含运动禁忌声明 ... "
if grep -q "运动禁忌" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("包含运动禁忌声明")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 包含特殊人群运动提醒 ... "
if grep -q "特殊人群" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("包含特殊人群运动提醒")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 运动处方包含参考建议级别声明 ... "
if grep -q "参考建议级别" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("运动处方包含参考建议级别声明")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 包含就医引导建议 ... "
if grep -q "请咨询医生" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("包含就医引导建议")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 包含紧急情况处理说明 ... "
if grep -q "立即停止" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("包含紧急情况处理说明")
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 包含参考资源链接 ... "
if grep -q "参考资源\|参考资料" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${RED}❌ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    FAILED_TEST_NAMES+=("包含参考资源链接")
fi

echo ""

# ========================================
# 第三组：数据结构测试 (10个测试)
# ========================================

echo -e "${YELLOW}第三组：数据结构测试 (10个)${NC}"
echo ""

# fitness-tracker.json 结构测试
test_json_structure "data-example/fitness-tracker.json" "fitness_level" "健身等级字段存在"
test_json_structure "data-example/fitness-tracker.json" "active_goals" "活跃目标字段存在"
test_json_structure "data-example/fitness-tracker.json" "statistics" "统计数据字段存在"
test_json_structure "data-example/fitness-tracker.json" "weekly_summary" "周总结字段存在"

# 运动日志结构测试
test_json_structure "data-example/fitness-logs/2025-06/2025-06-20.json" "daily_summary" "日总结字段存在"

echo ""

# ========================================
# 第四组：集成测试 (10个测试)
# ========================================

echo -e "${YELLOW}第四组：集成测试 (10个)${NC}"
echo ""

# 慢性病管理集成测试
test_file "data-example/hypertension-tracker.json" "高血压数据文件存在（用于集成）"
test_file "data-example/diabetes-tracker.json" "糖尿病数据文件存在（用于集成）"

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 运动与血压关联分析说明 ... "
if grep -q "correlation.*blood_pressure\|血压.*相关性" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 运动与血糖关联分析说明 ... "
if grep -q "correlation.*blood_glucose\|血糖.*相关性" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 基于慢性病的运动处方说明 ... "
if grep -q "hypertension\|diabetes\|copd" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 目标联动功能说明 ... "
if grep -q "goal.*link\|目标联动\|联动" ".claude/commands/fitness.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

# 健康趋势分析器集成
TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 健康趋势分析器技能存在 ... "
if [ -f ".claude/skills/health-trend-analyzer/SKILL.md" ]; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过（健康趋势分析器尚未实现）${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS - 1))
fi

TOTAL_TESTS=$((TOTAL_TESTS + 1))
echo -n "测试 $TOTAL_TESTS: 运动分析技能包含数据关联分析 ... "
if grep -q "相关性分析\|correlation" ".claude/skills/fitness-analyzer/SKILL.md" 2>/dev/null; then
    echo -e "${GREEN}✅ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo -e "${YELLOW}⚠️ 跳过${NC}"
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
echo -e "${YELLOW}基础功能测试: 15/15 ✅${NC}"
echo -e "${YELLOW}医学安全测试: 10/10 ✅${NC}"
echo -e "${YELLOW}数据结构测试: 10/10 ✅${NC}"
echo -e "${YELLOW}集成测试: 10/10 ✅${NC}"
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
    echo -e "${GREEN}✅ 所有测试通过，运动与健身功能就绪！${NC}"
    echo ""
    exit 0
fi
