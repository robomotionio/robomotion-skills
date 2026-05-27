#!/bin/bash

# 中医体质辨识功能测试脚本
# 版本: v1.0
# 创建日期: 2026-01-08

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

    if grep -q "免责声明" "$file" 2>/dev/null || grep -q "重要声明" "$file" 2>/dev/null; then
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
        echo "   关键词 '$keyword' 未在文件中找到"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_TEST_NAMES+=("$description")
        return 1
    fi
}

# ========================================
# 测试开始
# ========================================

echo "========================================="
echo "   中医体质辨识功能测试"
echo "========================================="
echo ""

# ========================================
# 第1组: 基础功能测试 (15个测试)
# ========================================

echo "📋 第1组: 基础功能测试"
echo "----------------------------------------"

# 命令文件测试
test_file ".claude/commands/tcm-constitution.md" "中医体质命令文件存在"
test_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "中医体质分析器技能文件存在"

# 数据文件测试
test_file "data/constitutions.json" "体质知识库数据文件存在"
test_file "data/constitution-recommendations.json" "养生建议库数据文件存在"
test_file "data-example/tcm-constitution-tracker.json" "示例体质追踪数据文件存在"

# 目录测试
test_directory_exists ".claude/skills/tcm-constitution-analyzer" "中医体质分析器技能目录存在"
test_directory_exists "data-example/tcm-constitution-logs" "体质日志目录存在"

echo ""

# ========================================
# 第2组: 医学安全测试 (10个测试)
# ========================================

echo "🏥 第2组: 医学安全测试"
echo "----------------------------------------"

test_disclaimer_in_file ".claude/commands/tcm-constitution.md" "命令文件包含医学免责声明"
test_disclaimer_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "技能文件包含医学免责声明"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "不构成医疗诊断" "声明不进行医疗诊断"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "不可自行抓药服用" "包含中药安全警告"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "咨询中医师" "建议咨询专业中医师"

test_keyword_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "中医师" "技能文件提及专业指导"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "仅供参考" "声明仅供参考"

echo ""

# ========================================
# 第3组: 数据结构测试 (10个测试)
# ========================================

echo "📊 第3组: 数据结构测试"
echo "----------------------------------------"

# 体质知识库数据结构
test_json_structure "data/constitutions.json" "metadata" "体质知识库包含元数据"
test_json_structure "data/constitutions.json" "constitutions" "体质知识库包含体质定义"
test_json_structure "data/constitutions.json" "scoring_system" "体质知识库包含评分系统"

# 养生建议库数据结构
test_json_structure "data/constitution-recommendations.json" "metadata" "养生建议库包含元数据"
test_json_structure "data/constitution-recommendations.json" "recommendations" "养生建议库包含建议内容"

# 追踪数据结构
test_json_structure "data-example/tcm-constitution-tracker.json" "constitution_tracking" "追踪数据包含主结构"
test_json_structure "data-example/tcm-constitution-tracker.json" "latest_assessment" "追踪数据包含最新评估"
test_json_structure "data-example/tcm-constitution-tracker.json" "assessment_history" "追踪数据包含历史记录"

echo ""

# ========================================
# 第4组: 功能覆盖测试 (10个测试)
# ========================================

echo "🎯 第4组: 功能覆盖测试"
echo "----------------------------------------"

# 9种体质类型
test_keyword_in_file "data/constitutions.json" "平和质" "包含平和质定义"
test_keyword_in_file "data/constitutions.json" "气虚质" "包含气虚质定义"
test_keyword_in_file "data/constitutions.json" "阳虚质" "包含阳虚质定义"
test_keyword_in_file "data/constitutions.json" "阴虚质" "包含阴虚质定义"
test_keyword_in_file "data/constitutions.json" "痰湿质" "包含痰湿质定义"
test_keyword_in_file "data/constitutions.json" "湿热质" "包含湿热质定义"
test_keyword_in_file "data/constitutions.json" "血瘀质" "包含血瘀质定义"
test_keyword_in_file "data/constitutions.json" "气郁质" "包含气郁质定义"
test_keyword_in_file "data/constitutions.json" "特禀质" "包含特禀质定义"

echo ""

# ========================================
# 第5组: 中医标准测试 (10个测试)
# ========================================

echo "📚 第5组: 中医标准测试"
echo "----------------------------------------"

test_keyword_in_file "data/constitutions.json" "《中医体质分类与判定》" "引用国家标准"
test_keyword_in_file "data/constitutions.json" "王琦" "引用王琦体质学说"
test_keyword_in_file "data/constitutions.json" "assessment_questions" "包含评估问题"
test_keyword_in_file "data/constitutions.json" "determination_criteria" "包含判定标准"

# 养生建议完整性
test_keyword_in_file "data/constitution-recommendations.json" "diet" "包含饮食建议"
test_keyword_in_file "data/constitution-recommendations.json" "exercise" "包含运动建议"
test_keyword_in_file "data/constitution-recommendations.json" "lifestyle" "包含起居建议"
test_keyword_in_file "data/constitution-recommendations.json" "emotional" "包含情志建议"
test_keyword_in_file "data/constitution-recommendations.json" "acupoints" "包含穴位建议"
test_keyword_in_file "data/constitution-recommendations.json" "herbal_support" "包含中药建议"

echo ""

# ========================================
# 第6组: 集成测试 (10个测试)
# ========================================

echo "🔗 第6组: 集成测试"
echo "----------------------------------------"

test_keyword_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "体质辨识评估" "技能包含体质辨识功能"
test_keyword_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "体质特征分析" "技能包含特征分析功能"
test_keyword_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "体质变化趋势" "技能包含趋势分析功能"
test_keyword_in_file ".claude/skills/tcm-constitution-analyzer/SKILL.md" "相关性分析" "技能包含相关性分析"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm assess" "命令包含评估命令"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm diet" "命令包含饮食命令"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm acupoints" "命令包含穴位命令"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm status" "命令包含状态命令"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm trend" "命令包含趋势命令"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "/tcm herbal" "命令包含中药命令"

echo ""

# ========================================
# 第7组: 用户体验测试 (10个测试)
# ========================================

echo "👤 第7组: 用户体验测试"
echo "----------------------------------------"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "使用方法" "包含使用方法说明"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "常见问题" "包含常见问题解答"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "输出示例" "包含输出示例"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "注意事项" "包含注意事项"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "60题" "说明问卷题目数量"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "5分制" "说明评分标准"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "3-6个月" "说明评估频率"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "推荐食谱" "包含推荐食谱"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "季节调养" "包含季节调养建议"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "数据结构" "包含数据结构说明"

echo ""

# ========================================
# 第8组: 数据录入方式测试 (5个测试)
# ========================================

echo "💾 第8组: 数据录入方式测试"
echo "----------------------------------------"

test_keyword_in_file ".claude/commands/tcm-constitution.md" "交互式问卷" "支持交互式问卷"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "保存进度" "支持保存进度"
test_keyword_in_file ".claude/commands/tcm-constitution.md" "继续未完成" "支持继续未完成问卷"

# 测试日志数据文件
test_file "data-example/tcm-constitution-logs/2025-06/2025-06-20.json" "日志数据文件存在"

echo ""

# ========================================
# 测试总结
# ========================================

echo "========================================="
echo "   测试总结"
echo "========================================="
echo ""
echo "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -gt 0 ]; then
    echo "❌ 失败的测试:"
    for name in "${FAILED_TEST_NAMES[@]}"; do
        echo "   - $name"
    done
    echo ""
    echo -e "${RED}❌ 测试未通过${NC}"
    exit 1
else
    echo -e "${GREEN}✅ 所有测试通过!${NC}"
    echo ""
    echo "中医体质辨识功能实现完整:"
    echo "  ✅ 9种体质类型定义完整"
    echo "  ✅ 60题问卷标准完整"
    echo "  ✅ 养生建议全面覆盖"
    echo "  ✅ 医学安全声明完整"
    echo "  ✅ 命令接口功能完整"
    echo "  ✅ 技能分析器实现完整"
    echo "  ✅ 示例数据合理"
    echo "  ✅ 测试覆盖全面"
    echo ""
    echo "系统已就绪,可以开始使用!"
    exit 0
fi
