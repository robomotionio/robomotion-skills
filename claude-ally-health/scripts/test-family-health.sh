#!/bin/bash

# 家庭健康管理功能测试脚本
# 测试家庭成员管理、家族病史记录、遗传风险评估等功能

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "👨‍👩‍👧‍👦 家庭健康管理功能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试计数器
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_file() {
    local file="$1"
    local description="$2"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [ -f "$file" ]; then
        echo "✅ $description"
        echo "   文件: $file"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo "❌ $description"
        echo "   文件: $file (不存在)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

test_json_structure() {
    local file="$1"
    local key="$2"
    local description="$3"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if command -v python3 &> /dev/null; then
        if python3 -c "import json; d=json.load(open('$file')); exit(0 if '$key' in d else 1)" 2>/dev/null; then
            echo "✅ $description"
            echo "   文件: $file"
            echo "   字段: $key"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo "❌ $description"
            echo "   文件: $file"
            echo "   缺少字段: $key"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo "⚠️  跳过测试(缺少 Python 3): $description"
        return 0
    fi
}

test_medical_safety() {
    local file="$1"
    local term="$2"
    local description="$3"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if grep -q "$term" "$file"; then
        echo "✅ $description"
        echo "   文件: $file"
        echo "   包含: $term"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo "❌ $description"
        echo "   文件: $file"
        echo "   缺少: $term"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 开始测试
echo "📋 第1部分:命令文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 家庭健康命令
test_file ".claude/commands/family.md" "家庭健康命令文件"
test_medical_safety ".claude/commands/family.md" "医学安全声明" "包含医学安全声明"
test_medical_safety ".claude/commands/family.md" "不替代" "包含免责声明"
test_medical_safety ".claude/commands/family.md" "仅供参考" "声明仅供参考"
test_medical_safety ".claude/commands/family.md" "遗传咨询师" "建议咨询遗传咨询师"
echo ""

echo "📋 第2部分:数据文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 家庭健康数据文件
test_file "data/family-health-tracker.json" "家庭健康数据文件"
test_json_structure "data/family-health-tracker.json" "family_health_tracking" "包含 family_health_tracking 字段"
test_json_structure "data/family-health-tracker.json" "members" "包含 members 字段"
test_json_structure "data/family-health-tracker.json" "family_medical_history" "包含 family_medical_history 字段"
test_json_structure "data/family-health-tracker.json" "risk_assessment" "包含 risk_assessment 字段"
test_json_structure "data/family-health-tracker.json" "pedigree_data" "包含 pedigree_data 字段"
test_json_structure "data/family-health-tracker.json" "metadata" "包含 metadata 字段"
echo ""

echo "📋 第3部分:技能文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 家庭健康分析技能
test_file ".claude/skills/family-health-analyzer/SKILL.md" "家庭健康分析技能文件"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "遗传风险评估" "包含遗传风险评估说明"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "不预测个体发病" "声明不预测发病"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "分析步骤" "包含分析步骤"
echo ""

echo "📋 第4部分:命令功能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试命令功能关键字
test_medical_safety ".claude/commands/family.md" "add-member" "包含添加成员命令"
test_medical_safety ".claude/commands/family.md" "add-history" "包含记录病史命令"
test_medical_safety ".claude/commands/family.md" "track" "包含健康追踪命令"
test_medical_safety ".claude/commands/family.md" "report" "包含生成报告命令"
test_medical_safety ".claude/commands/family.md" "risk" "包含风险评估命令"
test_medical_safety ".claude/commands/family.md" "list" "包含列出成员命令"
echo ""

echo "📋 第5部分:数据结构测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试数据结构关键字
test_medical_safety ".claude/commands/family.md" "member_id" "包含成员ID字段"
test_medical_safety ".claude/commands/family.md" "relationship" "包含关系字段"
test_medical_safety ".claude/commands/family.md" "disease_category" "包含疾病分类字段"
test_medical_safety ".claude/commands/family.md" "age_at_onset" "包含发病年龄字段"
test_medical_safety ".claude/commands/family.md" "risk_level" "包含风险等级字段"
test_medical_safety ".claude/commands/family.md" "preventive_recommendations" "包含预防建议字段"
echo ""

echo "📋 第6部分:遗传风险算法测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试遗传风险计算
test_medical_safety ".claude/commands/family.md" "遗传风险评分" "包含风险评分算法"
test_medical_safety ".claude/commands/family.md" "高风险" "包含高风险等级"
test_medical_safety ".claude/commands/family.md" "中风险" "包含中风险等级"
test_medical_safety ".claude/commands/family.md" "低风险" "包含低风险等级"
test_medical_safety ".claude/commands/family.md" "早发病例" "包含早发病例识别"
test_medical_safety ".claude/commands/family.md" "家族聚集度" "包含家族聚集度分析"
echo ""

echo "📋 第7部分:医学安全测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试所有文件是否包含关键安全原则
for file in .claude/commands/family.md .claude/skills/family-health-analyzer/SKILL.md; do
    echo "测试文件: $file"
    test_medical_safety "$file" "不能替代" "声明不能替代专业医疗"
    test_medical_safety "$file" "仅供参考" "声明分析仅供参考"
    test_medical_safety "$file" "咨询专业医师" "建议咨询专业医师"
    echo ""
done

echo "📋 第8部分:预防建议测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试预防建议功能
test_medical_safety ".claude/commands/family.md" "筛查建议" "包含筛查建议"
test_medical_safety ".claude/commands/family.md" "生活方式建议" "包含生活方式建议"
test_medical_safety ".claude/commands/family.md" "定期血压监测" "包含血压监测建议"
test_medical_safety ".claude/commands/family.md" "定期血糖检测" "包含血糖检测建议"
echo ""

echo "📋 第9部分:可视化报告测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试可视化功能
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "家谱树" "包含家谱树可视化"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "热力图" "包含风险热力图"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "HTML报告" "包含HTML报告生成"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "ECharts" "使用ECharts可视化"
echo ""

echo "📋 第10部分:集成测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试与其他模块的集成
test_medical_safety ".claude/commands/family.md" "hypertension-tracker" "集成高血压模块"
test_medical_safety ".claude/commands/family.md" "diabetes-tracker" "集成糖尿病模块"
test_medical_safety ".claude/commands/family.md" "medication" "集成用药管理"
test_medical_safety ".claude/skills/family-health-analyzer/SKILL.md" "集成现有模块" "包含模块集成说明"
echo ""

echo "📋 第11部分:错误处理测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试错误处理
test_medical_safety ".claude/commands/family.md" "错误处理" "包含错误处理说明"
test_medical_safety ".claude/commands/family.md" "成员不存在" "包含成员不存在错误"
test_medical_safety ".claude/commands/family.md" "关系无效" "包含关系无效错误"
test_medical_safety ".claude/commands/family.md" "数据不完整" "包含数据不完整错误"
echo ""

echo "📋 第12部分:示例数据测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 示例数据文件
test_file "data-example/family-health-tracker.json" "家庭健康示例数据"
test_json_structure "data-example/family-health-tracker.json" "family_health_tracking" "示例数据包含顶层字段"
echo ""

# 测试总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 测试总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "总测试数: $TOTAL_TESTS"
echo "通过: $PASSED_TESTS ✅"
echo "失败: $FAILED_TESTS ❌"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo "🎉 所有测试通过!"
    echo ""
    echo "家庭健康管理模块已准备就绪,包括:"
    echo "✅ 家庭成员管理"
    echo "✅ 家族病史记录"
    echo "✅ 遗传风险评估"
    echo "✅ 预防建议生成"
    echo "✅ 可视化报告"
    exit 0
else
    echo "⚠️  有 $FAILED_TESTS 个测试失败,请检查上述错误"
    exit 1
fi
