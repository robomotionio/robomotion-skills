#!/bin/bash
# Claude Code Native Test Runner
# Tests for Women's Health Module

set -e  # Exit on error

echo "================================"
echo "Claude Code Health Tracking Tests"
echo "================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
  local test_name="$1"
  local test_command="$2"

  echo -n "Testing: $test_name ... "

  if eval "$test_command" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
    return 0
  else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
    return 1
  fi
}

# Test 1: Validate JSON structures
echo "Test Suite 1: JSON Structure Validation"
echo "-------------------------------------"

run_test "pregnancy-tracker.json is valid JSON" \
  "python3 -m json.tool data/pregnancy-tracker.json"

run_test "postpartum-tracker.json is valid JSON" \
  "python3 -m json.tool data/postpartum-tracker.json"

run_test "index.json is valid JSON" \
  "python3 -m json.tool data/index.json"

run_test "profile.json is valid JSON" \
  "python3 -m json.tool data/profile.json" 2>/dev/null || true

echo ""

# Test 2: Check required fields in data structures
echo "Test Suite 2: Required Field Validation"
echo "-----------------------------------------"

run_test "pregnancy-tracker has multi_pregnancy_support" \
  "python3 -c \"import json; data=json.load(open('data/pregnancy-tracker.json')); exit(0 if 'multi_pregnancy_support' in data else 1)\""

run_test "postpartum-tracker has epds_reference" \
  "python3 -c \"import json; data=json.load(open('data/postpartum-tracker.json')); exit(0 if 'epds_reference' in data else 1)\""

run_test "postpartum-tracker has red_flags.maternal" \
  "python3 -c \"import json; data=json.load(open('data/postpartum-tracker.json')); exit(0 if 'red_flags' in data and 'maternal' in data['red_flags'] else 1)\""

run_test "postpartum-tracker has red_flags.baby" \
  "python3 -c \"import json; data=json.load(open('data/postpartum-tracker.json')); exit(0 if 'red_flags' in data and 'baby' in data['red_flags'] else 1)\""

echo ""

# Test 3: Medical safety - EPDS thresholds
echo "Test Suite 3: Medical Safety Validation"
echo "----------------------------------------"

run_test "EPDS reference has risk_thresholds" \
  "python3 -c \"import json; data=json.load(open('data/postpartum-tracker.json')); exit(0 if 'risk_thresholds' in data.get('epds_reference', {}) else 1)\""

run_test "EPDS low_risk range is 0-9" \
  "python3 -c \"import json; d=json.load(open('data/postpartum-tracker.json')); rt=d['epds_reference']['risk_thresholds']; exit(0 if rt['low_risk']['min']==0 and rt['low_risk']['max']==9 else 1)\""

run_test "EPDS high_risk range is 13-30" \
  "python3 -c \"import json; d=json.load(open('data/postpartum-tracker.json')); rt=d['epds_reference']['risk_thresholds']; exit(0 if rt['high_risk']['min']==13 and rt['high_risk']['max']==30 else 1)\""

run_test "EPDS emergency threshold Q10≥2" \
  "python3 -c \"import json; d=json.load(open('data/postpartum-tracker.json')); exit(0 if d['epds_reference']['risk_thresholds']['emergency']['q10_threshold']==2 else 1)\""

echo ""

# Test 4: Multi-pregnancy support
echo "Test Suite 4: Multi-Pregnancy Support"
echo "--------------------------------------"

run_test "pregnancy-tracker supports 4 pregnancy types" \
  "python3 -c \"import json; d=json.load(open('data/pregnancy-tracker.json')); types=d.get('multi_pregnancy_support', {}).get('supported_types', []); exit(0 if len(types)==4 else 1)\""

run_test "Supported types include twins, triplets, quadruplets" \
  "python3 -c \"import json; d=json.load(open('data/pregnancy-tracker.json')); types=d.get('multi_pregnancy_support', {}).get('supported_types', []); exit(0 if 'twins' in types and 'triplets' in types and 'quadruplets' in types else 1)\""

run_test "Max fetal count is 4" \
  "python3 -c \"import json; d=json.load(open('data/pregnancy-tracker.json')); exit(0 if d.get('multi_pregnancy_support', {}).get('max_fetal_count')==4 else 1)\""

echo ""

# Test 5: Command files exist
echo "Test Suite 5: Command Files Exist"
echo "----------------------------------"

run_test "pregnancy.md command exists" \
  "test -f .claude/commands/pregnancy.md"

run_test "postpartum.md command exists" \
  "test -f .claude/commands/postpartum.md"

run_test "profile.md command exists" \
  "test -f .claude/commands/profile.md"

echo ""

# Test 6: Data directories exist
echo "Test Suite 6: Data Directories"
echo "-------------------------------"

run_test "data directory exists" \
  "test -d data"

run_test "data-example directory exists" \
  "test -d data-example"

run_test "docs directory exists" \
  "test -d docs"

echo ""

# Summary
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
  echo -e "${RED}Failed: $TESTS_FAILED${NC}"
  exit 1
else
  echo -e "${GREEN}All tests passed!${NC}"
  exit 0
fi
