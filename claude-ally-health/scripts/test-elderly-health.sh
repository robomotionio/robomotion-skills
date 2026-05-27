#!/bin/bash

# 老年人健康功能测试脚本
# 测试认知功能评估、跌倒风险评估、多重用药管理模块

# 颜色代码
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_RUN=$((TESTS_RUN + 1))
    echo -n "Running test $TESTS_RUN: $test_name ... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}FAILED${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# 分节函数
print_section() {
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  $1${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# 主测试开始
echo ""
echo -e "${YELLOW}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║   老年人健康功能测试                              ║${NC}"
echo -e "${YELLOW}║   Elderly Health Module Tests                     ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# 第一部分: 命令文件验证
print_section "第一部分: 命令文件验证 (Command Files)"

run_test "cognitive.md exists" "test -f .claude/commands/cognitive.md"
run_test "fall.md exists" "test -f .claude/commands/fall.md"
run_test "polypharmacy.md exists" "test -f .claude/commands/polypharmacy.md"

# 第二部分: 数据文件验证
print_section "第二部分: 数据文件验证 (Data Files)"

run_test "cognitive-assessment.json exists" "test -f data/cognitive-assessment.json"
run_test "fall-risk-assessment.json exists" "test -f data/fall-risk-assessment.json"
run_test "polypharmacy-management.json exists" "test -f data/polypharmacy-management.json"

# 第三部分: 专家文件验证
print_section "第三部分: 专家文件验证 (Specialist Files)"

run_test "geriatrics.md exists" "test -f .claude/specialists/geriatrics.md"

# 第四部分: JSON结构验证
print_section "第四部分: JSON结构验证 (JSON Structure)"

run_test "Cognitive has mmse section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'cognitive_assessment' in d and 'mmse' in d['cognitive_assessment'] else 1)\""
run_test "Cognitive has moca section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'cognitive_assessment' in d and 'moca' in d['cognitive_assessment'] else 1)\""
run_test "Cognitive has cognitive_domains section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'cognitive_assessment' in d and 'cognitive_domains' in d['cognitive_assessment'] else 1)\""
run_test "Cognitive has functional_impact section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'cognitive_assessment' in d and 'functional_impact' in d['cognitive_assessment'] else 1)\""

run_test "Fall has fall_history section" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'fall_risk_assessment' in d and 'fall_history' in d['fall_risk_assessment'] else 1)\""
run_test "Fall has balance_tests section" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'fall_risk_assessment' in d and 'balance_tests' in d['fall_risk_assessment'] else 1)\""
run_test "Fall has home_safety section" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'fall_risk_assessment' in d and 'home_safety' in d['fall_risk_assessment'] else 1)\""

run_test "Polypharmacy has medication_list section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'polypharmacy_management' in d and 'medication_list' in d['polypharmacy_management'] else 1)\""
run_test "Polypharmacy has beers_criteria_violations section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'polypharmacy_management' in d and 'beers_criteria_violations' in d['polypharmacy_management'] else 1)\""
run_test "Polypharmacy has drug_interactions section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'polypharmacy_management' in d and 'drug_interactions' in d['polypharmacy_management'] else 1)\""
run_test "Polypharmacy has anticholinergic_burden section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'polypharmacy_management' in d and 'anticholinergic_burden' in d['polypharmacy_management'] else 1)\""

# 第五部分: 统计数据验证
print_section "第五部分: 统计数据验证 (Statistics Section)"

run_test "Cognitive has statistics section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'statistics' in d else 1)\""
run_test "Cognitive statistics has total_assessments" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'statistics' in d and 'total_assessments' in d['statistics'] else 1)\""
run_test "Cognitive statistics has impaired_domains" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'statistics' in d and 'impaired_domains' in d['statistics'] else 1)\""

run_test "Fall has statistics section" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'statistics' in d else 1)\""
run_test "Fall statistics has total_falls" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'statistics' in d and 'total_falls' in d['statistics'] else 1)\""
run_test "Fall statistics has risk_level" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'statistics' in d and 'risk_level' in d['statistics'] else 1)\""

run_test "Polypharmacy has statistics section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'statistics' in d else 1)\""
run_test "Polypharmacy statistics has total_medications" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'statistics' in d and 'total_medications' in d['statistics'] else 1)\""
run_test "Polypharmacy statistics has inappropriate_medications" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'statistics' in d and 'inappropriate_medications' in d['statistics'] else 1)\""
run_test "Polypharmacy statistics has interaction_count" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'statistics' in d and 'interaction_count' in d['statistics'] else 1)\""

# 第六部分: 设置数据验证
print_section "第六部分: 设置数据验证 (Settings Section)"

run_test "Cognitive has settings section" "python3 -c \"import json; d=json.load(open('data/cognitive-assessment.json')); exit(0 if 'settings' in d and 'reminder_months' in d['settings'] else 1)\""
run_test "Fall has settings section" "python3 -c \"import json; d=json.load(open('data/fall-risk-assessment.json')); exit(0 if 'settings' in d and 'reminder_months' in d['settings'] else 1)\""
run_test "Polypharmacy has settings section" "python3 -c \"import json; d=json.load(open('data/polypharmacy-management.json')); exit(0 if 'settings' in d and 'review_months' in d['settings'] else 1)\""

# 第七部分: 医学安全验证
print_section "第七部分: 医学安全验证 (Medical Safety)"

run_test "Cognitive.md has safety section" "grep -q '安全红线' .claude/commands/cognitive.md"
run_test "Cognitive.md has system capabilities section" "grep -q '系统能做到的' .claude/commands/cognitive.md"
run_test "Fall.md has safety section" "grep -q '安全红线' .claude/commands/fall.md"
run_test "Fall.md has system capabilities section" "grep -q '系统能做到的' .claude/commands/fall.md"
run_test "Polypharmacy.md has safety section" "grep -q '安全红线' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has system capabilities section" "grep -q '系统能做到的' .claude/commands/polypharmacy.md"

run_test "No dementia diagnosis in cognitive.md" "! grep -E '(诊断为.*痴呆|确诊阿尔茨海默病|肯定性痴呆)' .claude/commands/cognitive.md | grep -v '^#' | grep -q ."
run_test "No medication adjustment in polypharmacy.md" "! grep -E '^(?!.*精简原则)(?!.*原则)(停用|减少|调整)' .claude/commands/polypharmacy.md | grep -v '^#' | grep -v '不建议' | grep -v '需医生' | grep -v '建议' | grep -q ."
run_test "No injury treatment in fall.md" "! grep -E '处理.*损伤|治疗.*骨折|应该没事' .claude/commands/fall.md | grep -v '^#' | grep -v '需就医' | grep -v '跌后处理' | grep -v '\*\*不处理' | grep -q ."

# 第八部分: 命令功能完整性验证
print_section "第八部分: 命令功能完整性验证 (Command Completeness)"

run_test "Cognitive.md has mmse action" "grep -q '### 1. MMSE测试' .claude/commands/cognitive.md"
run_test "Cognitive.md has moca action" "grep -q '### 2. MoCA测试' .claude/commands/cognitive.md"
run_test "Cognitive.md has domain action" "grep -q '### 3. 认知域评估' .claude/commands/cognitive.md"
run_test "Cognitive.md has adl action" "grep -q '### 4. 日常活动能力评估' .claude/commands/cognitive.md"
run_test "Cognitive.md has iadl action" "grep -q '### 5. 工具性日常活动能力评估' .claude/commands/cognitive.md"
run_test "Cognitive.md has status action" "grep -q '### 6. 查看认知状态' .claude/commands/cognitive.md"
run_test "Cognitive.md has trend action" "grep -q '### 7. 查看变化趋势' .claude/commands/cognitive.md"
run_test "Cognitive.md has risk action" "grep -q '### 8. 认知功能风险评估' .claude/commands/cognitive.md"

run_test "Fall.md has record action" "grep -q '### 1. 记录跌倒事件' .claude/commands/fall.md"
run_test "Fall.md has history action" "grep -q '### 2. 查看跌倒历史' .claude/commands/fall.md"
run_test "Fall.md has tug action" "grep -q '### 3. TUG测试' .claude/commands/fall.md"
run_test "Fall.md has berg action" "grep -q '### 4. Berg平衡量表' .claude/commands/fall.md"
run_test "Fall.md has single-leg-stance action" "grep -q '### 5. 单腿站立测试' .claude/commands/fall.md"
run_test "Fall.md has gait action" "grep -q '### 6. 步态分析' .claude/commands/fall.md"
run_test "Fall.md has home action" "grep -q '### 7. 居家环境评估' .claude/commands/fall.md"
run_test "Fall.md has risk action" "grep -q '### 8. 跌倒风险评估' .claude/commands/fall.md"

run_test "Polypharmacy.md has add action" "grep -q '### 1. 添加用药' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has list action" "grep -q '### 2. 查看用药清单' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has beers action" "grep -q '### 3. Beers标准筛查' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has interaction action" "grep -q '### 5. 药物相互作用检查' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has anticholinergic action" "grep -q '### 6. 抗胆碱能负荷评估' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has deprescribe action" "grep -q '### 7. 用药精简计划' .claude/commands/polypharmacy.md"

# 第九部分: 专家文件验证
print_section "第九部分: 专家文件验证 (Specialist File)"

run_test "Geriatrics.md has role definition" "grep -q '角色定义' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has professional fields" "grep -q '专业领域' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has safety red lines" "grep -q '安全红线' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has appropriate expressions" "grep -q '合适表达' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has prohibited expressions" "grep -q '禁止表达' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has analysis framework" "grep -q '分析框架' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has cognitive assessment focus" "grep -q '认知功能评估关注' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has fall risk focus" "grep -q '跌倒风险评估关注' .claude/specialists/geriatrics.md"
run_test "Geriatrics.md has polypharmacy focus" "grep -q '多重用药管理关注' .claude/specialists/geriatrics.md"

# 第十部分: 医学标准参考验证
print_section "第十部分: 医学标准参考验证 (Medical Standards)"

run_test "Cognitive.md has MMSE reference" "grep -q 'Folstein' .claude/commands/cognitive.md"
run_test "Cognitive.md has MoCA reference" "grep -q 'Nasreddine' .claude/commands/cognitive.md"
run_test "Fall.md has TUG reference" "grep -q 'Podsiadlo' .claude/commands/fall.md"
run_test "Fall.md has Berg reference" "grep -q 'Berg' .claude/commands/fall.md"
run_test "Polypharmacy.md has Beers reference" "grep -q 'Beers标准' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has ACB reference" "grep -q 'ACB' .claude/commands/polypharmacy.md"
run_test "Geriatrics.md has comprehensive references" "grep -q '参考资源' .claude/specialists/geriatrics.md"

# 第十一部分: YAML frontmatter验证
print_section "第十一部分: YAML Frontmatter验证"

run_test "Cognitive.md has YAML frontmatter" "grep -q '^---' .claude/commands/cognitive.md"
run_test "Cognitive.md has description in frontmatter" "grep -A5 '^---' .claude/commands/cognitive.md | grep -q 'description:'"
run_test "Fall.md has YAML frontmatter" "grep -q '^---' .claude/commands/fall.md"
run_test "Fall.md has description in frontmatter" "grep -A5 '^---' .claude/commands/fall.md | grep -q 'description:'"
run_test "Polypharmacy.md has YAML frontmatter" "grep -q '^---' .claude/commands/polypharmacy.md"
run_test "Polypharmacy.md has description in frontmatter" "grep -A5 '^---' .claude/commands/polypharmacy.md | grep -q 'description:'"

# 第十二部分: 智能参数识别验证
print_section "第十二部分: 智能参数识别验证 (Parameter Recognition)"

run_test "Cognitive.md has MMSE pattern recognition" "grep -q 'mmse\[' .claude/commands/cognitive.md"
run_test "Cognitive.md has MoCA pattern recognition" "grep -q 'moca\[' .claude/commands/cognitive.md"
run_test "Cognitive.md has domain pattern recognition" "grep -q '(memory\|executive\|language\|visuospatial)' .claude/commands/cognitive.md"
run_test "Fall.md has TUG pattern recognition" "grep -q 'tug\[' .claude/commands/fall.md"
run_test "Fall.md has Berg pattern recognition" "grep -q 'berg\[' .claude/commands/fall.md"
run_test "Fall.md has gait speed pattern recognition" "grep -q 'speed\[' .claude/commands/fall.md"
run_test "Polypharmacy.md has medication pattern recognition" "grep -q 'mg' .claude/commands/polypharmacy.md && grep -q 'qd' .claude/commands/polypharmacy.md"

# 测试总结
echo ""
echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  测试总结 | Test Summary                             ${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "总测试数 | Total tests run:    ${TESTS_RUN}"
echo -e "${GREEN}通过数 | Passed:             ${TESTS_PASSED}${NC}"
echo -e "${RED}失败数 | Failed:             ${TESTS_FAILED}${NC}"
echo ""

# 返回结果
if [ ${TESTS_FAILED} -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过! All tests passed!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ 有测试失败! Some tests failed!${NC}"
    echo ""
    exit 1
fi
