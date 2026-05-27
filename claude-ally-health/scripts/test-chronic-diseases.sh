#!/bin/bash

# 慢性病管理功能测试脚本
# 测试高血压、糖尿病和COPD管理系统的完整性

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏥 慢性病管理功能测试"
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
        echo "⚠️  跳过测试（缺少 Python 3）: $description"
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
echo "📋 第1部分：命令文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 高血压管理命令
test_file ".claude/commands/hypertension.md" "高血压管理命令文件"
test_medical_safety ".claude/commands/hypertension.md" "医学安全声明" "包含医学安全声明"
test_medical_safety ".claude/commands/hypertension.md" "不替代医生" "包含免责声明"
echo ""

# 糖尿病管理命令
test_file ".claude/commands/diabetes.md" "糖尿病管理命令文件"
test_medical_safety ".claude/commands/diabetes.md" "医学安全声明" "包含医学安全声明"
test_medical_safety ".claude/commands/diabetes.md" "不替代医生" "包含免责声明"
echo ""

# COPD管理命令
test_file ".claude/commands/copd.md" "COPD管理命令文件"
test_medical_safety ".claude/commands/copd.md" "医学安全声明" "包含医学安全声明"
test_medical_safety ".claude/commands/copd.md" "不替代医生" "包含免责声明"
echo ""

echo "📋 第2部分：数据文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 高血压数据文件
test_file "data/hypertension-tracker.json" "高血压数据文件"
test_json_structure "data/hypertension-tracker.json" "hypertension_management" "包含 hypertension_management 字段"
echo ""

# 糖尿病数据文件
test_file "data/diabetes-tracker.json" "糖尿病数据文件"
test_json_structure "data/diabetes-tracker.json" "diabetes_management" "包含 diabetes_management 字段"
echo ""

# COPD数据文件
test_file "data/copd-tracker.json" "COPD数据文件"
test_json_structure "data/copd-tracker.json" "copd_management" "包含 copd_management 字段"
echo ""

echo "📋 第3部分：示例数据文件测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 示例数据文件
test_file "data-example/hypertension-tracker.json" "高血压示例数据"
test_file "data-example/diabetes-tracker.json" "糖尿病示例数据"
test_file "data-example/copd-tracker.json" "COPD示例数据"
echo ""

echo "📋 第4部分：医学安全原则测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试所有命令文件是否包含关键安全原则
for file in .claude/commands/hypertension.md .claude/commands/diabetes.md .claude/commands/copd.md; do
    echo "测试文件: $file"
    test_medical_safety "$file" "不能替代" "声明不能替代专业医疗"
    test_medical_safety "$file" "仅供参考" "声明分析仅供参考"
    echo ""
done

echo "📋 第5部分：功能完整性测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 高血压功能关键字
echo "测试高血压管理功能..."
test_medical_safety ".claude/commands/hypertension.md" "record" "支持血压记录功能"
test_medical_safety ".claude/commands/hypertension.md" "trend" "支持趋势分析功能"
test_medical_safety ".claude/commands/hypertension.md" "medication" "支持用药管理功能"
test_medical_safety ".claude/commands/hypertension.md" "risk" "支持风险评估功能"
echo ""

# 糖尿病功能关键字
echo "测试糖尿病管理功能..."
test_medical_safety ".claude/commands/diabetes.md" "record" "支持血糖记录功能"
test_medical_safety ".claude/commands/diabetes.md" "hba1c" "支持HbA1c追踪功能"
test_medical_safety ".claude/commands/diabetes.md" "hypo" "支持低血糖事件功能"
test_medical_safety ".claude/commands/diabetes.md" "screening" "支持并发症筛查功能"
echo ""

# COPD功能关键字
echo "测试COPD管理功能..."
test_medical_safety ".claude/commands/copd.md" "fev1" "支持肺功能监测功能"
test_medical_safety ".claude/commands/copd.md" "cat" "支持CAT评分功能"
test_medical_safety ".claude/commands/copd.md" "exacerbation" "支持急性加重记录功能"
test_medical_safety ".claude/commands/copd.md" "vaccine" "支持疫苗接种记录功能"
echo ""

echo "📋 第6部分：数据结构验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if command -v python3 &> /dev/null; then
    echo "验证JSON格式..."

    # 测试JSON格式是否有效
    for file in data/hypertension-tracker.json data/diabetes-tracker.json data/copd-tracker.json \
                data-example/hypertension-tracker.json data-example/diabetes-tracker.json data-example/copd-tracker.json; do
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if python3 -m json.tool "$file" > /dev/null 2>&1; then
            echo "✅ JSON格式有效: $file"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo "❌ JSON格式无效: $file"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    done
    echo ""
else
    echo "⚠️  跳过JSON格式验证（缺少 Python 3）"
    echo ""
fi

echo "📋 第7部分：集成功能测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 测试是否与药物管理系统集成
echo "测试与药物管理系统的集成..."
test_medical_safety ".claude/commands/hypertension.md" "/medication" "高血压用药调用药物管理"
test_medical_safety ".claude/commands/diabetes.md" "/medication" "糖尿病用药调用药物管理"
test_medical_safety ".claude/commands/copd.md" "/medication" "COPD用药调用药物管理"
echo ""

# 测试YAML头部格式
echo "测试命令文件YAML头部..."
for file in .claude/commands/hypertension.md .claude/commands/diabetes.md .claude/commands/copd.md; do
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if head -1 "$file" | grep -q "^---"; then
        echo "✅ YAML头部正确: $file"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ YAML头部缺失: $file"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done
echo ""

# 测试汇总
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 测试结果汇总"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "总测试数: $TOTAL_TESTS"
echo "通过: $PASSED_TESTS ✅"
echo "失败: $FAILED_TESTS ❌"
echo ""

# 计算通过率
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "通过率: $PASS_RATE%"
    echo ""

    if [ $PASS_RATE -ge 90 ]; then
        echo "🎉 优秀！测试通过率 ≥90%"
    elif [ $PASS_RATE -ge 70 ]; then
        echo "✅ 良好！测试通过率 ≥70%"
    elif [ $PASS_RATE -ge 50 ]; then
        echo "⚠️  通过率 <70%，建议检查失败项目"
    else
        echo "❌ 通过率 <50%，存在严重问题"
    fi
else
    echo "⚠️  未执行任何测试"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ 测试完成"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 返回退出码
if [ $FAILED_TESTS -eq 0 ]; then
    exit 0
else
    exit 1
fi
