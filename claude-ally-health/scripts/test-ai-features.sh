#!/bin/bash
# AI功能测试脚本
# 测试AI健康助手的核心功能

set -e  # 遇到错误立即退出

echo "🧪 AI健康助手功能测试"
echo "=========================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_case() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "测试 $TOTAL_TESTS: $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo "1. 测试AI配置文件"
echo "--------------------------"

test_case "AI配置文件存在" "[ -f data/ai-config.json ]"
test_case "AI历史记录存在" "[ -f data/ai-history.json ]"
test_case "AI配置JSON格式正确" "python3 -c 'import json; json.load(open(\"data/ai-config.json\"))'"
test_case "AI历史JSON格式正确" "python3 -c 'import json; json.load(open(\"data/ai-history.json\"))'"

echo ""
echo "2. 测试AI Skill文件"
echo "--------------------------"

test_case "AI分析器Skill存在" "[ -f .claude/skills/ai-analyzer/SKILL.md ]"
test_case "AI命令文件存在" "[ -f .claude/commands/ai.md ]"

echo ""
echo "3. 测试AI脚本"
echo "--------------------------"

test_case "AI预测脚本存在" "[ -f scripts/ai_prediction.py ]"
test_case "AI报告生成器存在" "[ -f scripts/generate_ai_report.py ]"
test_case "AI预测脚本可执行" "[ -x scripts/ai_prediction.py ]"
test_case "AI报告生成器可执行" "[ -x scripts/generate_ai_report.py ]"

echo ""
echo "4. 测试Python导入"
echo "--------------------------"

test_case "ai_prediction模块可导入" "python3 -c 'import sys; sys.path.append(\"scripts\"); from ai_prediction import AIPredictionEngine'"
test_case "generate_ai_report模块可导入" "python3 -c 'import sys; sys.path.append(\"scripts\"); from generate_ai_report import AIHealthReportGenerator'"

echo ""
echo "5. 测试风险预测功能"
echo "--------------------------"

# 测试高血压风险预测
echo "测试高血压风险预测..."
if python3 scripts/ai_prediction.py > /tmp/ai_test_output.txt 2>&1; then
    if grep -q "高血压风险预测" /tmp/ai_test_output.txt; then
        echo -e "${GREEN}✓ 高血压风险预测正常${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ 高血压风险预测失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}✗ 风险预测脚本执行失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "6. 测试AI报告生成"
echo "--------------------------"

# 测试报告生成
echo "测试AI报告生成..."
if python3 scripts/generate_ai_report.py > /tmp/ai_report_test.txt 2>&1; then
    if grep -q "报告生成成功" /tmp/ai_report_test.txt; then
        echo -e "${GREEN}✓ AI报告生成正常${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ AI报告生成失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
else
    echo -e "${RED}✗ 报告生成脚本执行失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo "7. 测试数据索引更新"
echo "--------------------------"

test_case "index.json包含ai_config" "grep -q 'ai_config' data/index.json"
test_case "index.json包含ai_history" "grep -q 'ai_history' data/index.json"
test_case "index.json包含AI统计" "grep -q 'ai_analysis_count' data/index.json"

echo ""
echo "8. 测试AI报告输出目录"
echo "--------------------------"

test_case "AI报告目录存在" "[ -d data/ai-reports ]"

echo ""
echo "=========================="
echo "测试总结"
echo "=========================="
echo "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 所有测试通过!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  有 $FAILED_TESTS 个测试失败${NC}"
    exit 1
fi
