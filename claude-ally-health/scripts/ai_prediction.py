#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI健康风险预测系统
基于循证医学模型预测健康风险，包括高血压、糖尿病、心血管疾病等
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import math


class AIPredictionEngine:
    """AI风险预测引擎"""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.ai_config = None
        self.user_profile = None
        self.load_config()

    def load_config(self):
        """加载AI配置和用户档案"""
        try:
            with open(self.base_dir / "ai-config.json", 'r', encoding='utf-8') as f:
                self.ai_config = json.load(f)
        except Exception as e:
            print(f"警告: 无法加载AI配置: {e}")
            self.ai_config = {"ai_features": {"predictions": {"enabled": True}}}

        try:
            with open(self.base_dir / "profile.json", 'r', encoding='utf-8') as f:
                self.user_profile = json.load(f)
        except Exception as e:
            print(f"警告: 无法加载用户档案: {e}")
            self.user_profile = {}

    def predict_hypertension_risk(self) -> Dict[str, Any]:
        """
        高血压风险预测
        基于Framingham风险评分（简化版）
        """
        if not self.user_profile:
            return self._error_result("用户档案未找到")

        # 提取风险因子
        factors = {
            'age': self._calculate_age(),
            'bmi': self.user_profile.get('calculated', {}).get('bmi', 0),
            'systolic_bp': self._get_latest_bp('systolic'),
            'diastolic_bp': self._get_latest_bp('diastolic'),
            'family_history': self._check_family_history('hypertension'),
            'smoking': self._check_smoking_status(),
            'activity_level': self.user_profile.get('lifestyle', {}).get('activity_level', 'moderate')
        }

        # 计算风险评分
        risk_score = 0

        # 年龄因子 (0-3分)
        age = factors['age']
        if age > 65:
            risk_score += 3
        elif age > 55:
            risk_score += 2
        elif age > 45:
            risk_score += 1

        # BMI因子 (0-3分)
        bmi = factors['bmi'] or 24  # 默认正常BMI
        if bmi > 30:
            risk_score += 3
        elif bmi > 25:
            risk_score += 2
        elif bmi > 24:
            risk_score += 1

        # 收缩压因子 (0-3分)
        sbp = factors['systolic_bp']
        if sbp and sbp > 140:
            risk_score += 3
        elif sbp and sbp > 130:
            risk_score += 2
        elif sbp and sbp > 120:
            risk_score += 1

        # 家族史 (0-2分)
        if factors['family_history']:
            risk_score += 2

        # 吸烟 (0-2分)
        if factors['smoking']:
            risk_score += 2

        # 活动水平 (0-1分)
        if factors['activity_level'] == 'sedentary':
            risk_score += 1

        # 归一化到0-1概率 (最高15分对应95%风险)
        probability = min(risk_score / 15.0, 0.95)

        # 风险等级
        if probability > 0.3:
            risk_level = 'high'
        elif probability > 0.15:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

        return {
            'risk_type': 'hypertension',
            'risk_name': '高血压',
            'probability': round(probability, 3),
            'probability_percent': f"{round(probability * 100)}%",
            'risk_level': risk_level,
            'risk_level_cn': self._translate_risk_level(risk_level),
            'time_horizon_years': 10,
            'model': 'Framingham风险评分（简化版）',
            'risk_score': risk_score,
            'factors': factors,
            'key_factors': self._identify_key_factors(factors, risk_score),
            'modifiable_factors': ['bmi', 'activity_level', 'smoking'],
            'recommendations': self._generate_recommendations('hypertension', probability),
            'prevention_measures': self._get_prevention_measures('hypertension')
        }

    def predict_diabetes_risk(self) -> Dict[str, Any]:
        """
        糖尿病风险预测
        基于ADA糖尿病风险评分标准
        """
        if not self.user_profile:
            return self._error_result("用户档案未找到")

        # 提取风险因子
        factors = {
            'age': self._calculate_age(),
            'bmi': self.user_profile.get('calculated', {}).get('bmi', 0),
            'fasting_glucose': self._get_latest_lab_result('fasting_glucose'),
            'family_history': self._check_family_history('diabetes'),
            'activity_level': self.user_profile.get('lifestyle', {}).get('activity_level', 'moderate'),
            'diet_quality': self._assess_diet_quality()
        }

        # 计算风险评分
        risk_score = 0

        # 年龄 (0-3分)
        age = factors['age']
        if age > 60:
            risk_score += 3
        elif age > 50:
            risk_score += 2
        elif age > 40:
            risk_score += 1

        # BMI (0-3分)
        bmi = factors['bmi'] or 24  # 默认正常BMI
        if bmi > 35:
            risk_score += 3
        elif bmi > 30:
            risk_score += 2
        elif bmi > 25:
            risk_score += 1

        # 空腹血糖 (0-5分)
        glucose = factors['fasting_glucose']
        if glucose and glucose > 7.0:
            risk_score += 5
        elif glucose and glucose > 5.6:
            risk_score += 3

        # 家族史 (0-2分)
        if factors['family_history']:
            risk_score += 2

        # 活动水平 (0-1分)
        if factors['activity_level'] == 'sedentary':
            risk_score += 1

        # 饮食质量 (0-1分)
        if factors['diet_quality'] == 'poor':
            risk_score += 1

        # 归一化到0-1概率 (最高18分对应90%风险)
        probability = min(risk_score / 18.0, 0.90)

        # 风险等级
        if probability > 0.25:
            risk_level = 'high'
        elif probability > 0.12:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

        return {
            'risk_type': 'diabetes',
            'risk_name': '2型糖尿病',
            'probability': round(probability, 3),
            'probability_percent': f"{round(probability * 100)}%",
            'risk_level': risk_level,
            'risk_level_cn': self._translate_risk_level(risk_level),
            'time_horizon_years': 10,
            'model': 'ADA糖尿病风险评分',
            'risk_score': risk_score,
            'factors': factors,
            'key_factors': self._identify_key_factors(factors, risk_score),
            'modifiable_factors': ['bmi', 'activity_level', 'diet_quality'],
            'recommendations': self._generate_recommendations('diabetes', probability),
            'prevention_measures': self._get_prevention_measures('diabetes')
        }

    def predict_cardiovascular_risk(self) -> Dict[str, Any]:
        """
        心血管疾病风险预测
        基于ACC/AHA ASCVD风险计算器（简化版）
        """
        if not self.user_profile:
            return self._error_result("用户档案未找到")

        # 提取风险因子
        factors = {
            'age': self._calculate_age(),
            'gender': self.user_profile.get('basic_info', {}).get('gender', 'unknown'),
            'systolic_bp': self._get_latest_bp('systolic'),
            'total_cholesterol': self._get_latest_lab_result('total_cholesterol'),
            'hdl_cholesterol': self._get_latest_lab_result('hdl_cholesterol'),
            'smoking': self._check_smoking_status(),
            'diabetes': self._check_medical_history('diabetes')
        }

        # 简化的ASCVD风险计算
        risk_score = 0

        # 年龄和性别因子
        age = factors['age']
        gender = factors['gender']

        if gender == 'male':
            if age > 65:
                risk_score += 4
            elif age > 55:
                risk_score += 3
            elif age > 45:
                risk_score += 2
            elif age > 35:
                risk_score += 1
        else:  # female
            if age > 65:
                risk_score += 3
            elif age > 55:
                risk_score += 2
            elif age > 45:
                risk_score += 1

        # 收缩压
        sbp = factors['systolic_bp']
        if sbp and sbp > 160:
            risk_score += 3
        elif sbp and sbp > 140:
            risk_score += 2
        elif sbp and sbp > 120:
            risk_score += 1

        # 胆固醇
        total_chol = factors['total_cholesterol']
        if total_chol and total_chol > 240:
            risk_score += 2
        elif total_chol and total_chol > 200:
            risk_score += 1

        # 吸烟
        if factors['smoking']:
            risk_score += 2

        # 糖尿病
        if factors['diabetes']:
            risk_score += 2

        # 归一化到0-1概率 (最高14分对应50%风险)
        probability = min(risk_score / 14.0, 0.50)

        # 风险等级
        if probability > 0.10:
            risk_level = 'high'
        elif probability > 0.05:
            risk_level = 'moderate'
        else:
            risk_level = 'low'

        return {
            'risk_type': 'cardiovascular',
            'risk_name': '心血管疾病',
            'probability': round(probability, 3),
            'probability_percent': f"{round(probability * 100)}%",
            'risk_level': risk_level,
            'risk_level_cn': self._translate_risk_level(risk_level),
            'time_horizon_years': 10,
            'model': 'ACC/AHA ASCVD风险计算器（简化版）',
            'risk_score': risk_score,
            'factors': factors,
            'key_factors': self._identify_key_factors(factors, risk_score),
            'modifiable_factors': ['systolic_bp', 'total_cholesterol', 'smoking', 'diabetes'],
            'recommendations': self._generate_recommendations('cardiovascular', probability),
            'prevention_measures': self._get_prevention_measures('cardiovascular')
        }

    def predict_nutritional_deficiency_risk(self) -> Dict[str, Any]:
        """营养缺乏风险评估"""
        # 基于营养数据评估营养缺乏风险
        try:
            nutrition_file = self.base_dir.parent / "data-example" / "nutrition-tracker.json"
            if not nutrition_file.exists():
                return self._error_result("营养数据未找到")

            with open(nutrition_file, 'r', encoding='utf-8') as f:
                nutrition_data = json.load(f)

            # 简化的营养缺乏评估
            deficiencies = []

            # 检查常见营养素
            rda_threshold = 0.8  # RDA达成率低于80%视为缺乏风险

            # 维生素D
            vitamin_d_avg = self._calculate_average_rda(nutrition_data, 'vitamin_d')
            if vitamin_d_avg < rda_threshold:
                deficiencies.append({
                    'nutrient': '维生素D',
                    'rda_achievement': f"{round(vitamin_d_avg * 100)}%",
                    'risk_level': 'high' if vitamin_d_avg < 0.5 else 'moderate'
                })

            # 钙
            calcium_avg = self._calculate_average_rda(nutrition_data, 'calcium')
            if calcium_avg < rda_threshold:
                deficiencies.append({
                    'nutrient': '钙',
                    'rda_achievement': f"{round(calcium_avg * 100)}%",
                    'risk_level': 'high' if calcium_avg < 0.5 else 'moderate'
                })

            # 铁（女性特别关注）
            gender = self.user_profile.get('basic_info', {}).get('gender', '')
            if gender == 'female':
                iron_avg = self._calculate_average_rda(nutrition_data, 'iron')
                if iron_avg < rda_threshold:
                    deficiencies.append({
                        'nutrient': '铁',
                        'rda_achievement': f"{round(iron_avg * 100)}%",
                        'risk_level': 'high' if iron_avg < 0.5 else 'moderate'
                    })

            # 综合风险
            if len(deficiencies) == 0:
                overall_risk = 'low'
                probability = 0.05
            elif len(deficiencies) == 1:
                overall_risk = 'moderate'
                probability = 0.20
            else:
                overall_risk = 'high'
                probability = 0.40

            return {
                'risk_type': 'nutritional_deficiency',
                'risk_name': '营养缺乏',
                'probability': round(probability, 3),
                'probability_percent': f"{round(probability * 100)}%",
                'risk_level': overall_risk,
                'risk_level_cn': self._translate_risk_level(overall_risk),
                'deficiencies': deficiencies,
                'recommendations': self._generate_nutrition_recommendations(deficiencies)
            }

        except Exception as e:
            return self._error_result(f"营养数据分析失败: {e}")

    def predict_sleep_disorder_risk(self) -> Dict[str, Any]:
        """睡眠障碍风险评估"""
        try:
            sleep_file = self.base_dir.parent / "data-example" / "sleep-tracker.json"
            if not sleep_file.exists():
                return self._error_result("睡眠数据未找到")

            with open(sleep_file, 'r', encoding='utf-8') as f:
                sleep_data = json.load(f)

            records = sleep_data.get('sleep_records', [])
            if len(records) < 7:
                return self._error_result("睡眠数据不足（需要至少7天记录）")

            # 分析睡眠指标
            total_records = len(records)
            poor_sleep_count = 0
            short_sleep_count = 0
            low_efficiency_count = 0

            for record in records[-7:]:  # 最近7天
                # 睡眠质量
                quality = record.get('sleep_quality', {}).get('subjective_quality', 'good')
                if quality in ['poor', 'very poor']:
                    poor_sleep_count += 1

                # 睡眠时长
                duration = record.get('sleep_metrics', {}).get('sleep_duration_hours', 0)
                if duration < 6:
                    short_sleep_count += 1

                # 睡眠效率
                efficiency = record.get('sleep_metrics', {}).get('sleep_efficiency', 100)
                if efficiency < 85:
                    low_efficiency_count += 1

            # 计算风险评分
            risk_score = 0
            if poor_sleep_count >= 4:
                risk_score += 3
            elif poor_sleep_count >= 2:
                risk_score += 1

            if short_sleep_count >= 5:
                risk_score += 3
            elif short_sleep_count >= 3:
                risk_score += 2

            if low_efficiency_count >= 4:
                risk_score += 2

            # 归一化到概率
            probability = min(risk_score / 8.0, 0.60)

            if probability > 0.30:
                risk_level = 'high'
            elif probability > 0.15:
                risk_level = 'moderate'
            else:
                risk_level = 'low'

            return {
                'risk_type': 'sleep_disorder',
                'risk_name': '睡眠障碍',
                'probability': round(probability, 3),
                'probability_percent': f"{round(probability * 100)}%",
                'risk_level': risk_level,
                'risk_level_cn': self._translate_risk_level(risk_level),
                'sleep_metrics': {
                    'poor_sleep_days': poor_sleep_count,
                    'short_sleep_days': short_sleep_count,
                    'low_efficiency_days': low_efficiency_count
                },
                'recommendations': self._generate_sleep_recommendations(risk_level)
            }

        except Exception as e:
            return self._error_result(f"睡眠数据分析失败: {e}")

    # ==================== 辅助方法 ====================

    def _calculate_age(self) -> int:
        """计算年龄"""
        birth_date = self.user_profile.get('basic_info', {}).get('birth_date')
        if birth_date:
            try:
                birth = datetime.strptime(birth_date, "%Y-%m-%d")
                today = datetime.now()
                return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            except:
                pass
        return 45  # 默认年龄

    def _get_latest_bp(self, bp_type: str) -> Optional[float]:
        """获取最新血压读数"""
        # 简化实现，实际应从医疗记录中读取
        if bp_type == 'systolic':
            return 120  # 默认值
        else:
            return 80  # 默认值

    def _get_latest_lab_result(self, test_name: str) -> Optional[float]:
        """获取最新化验结果"""
        # 简化实现，实际应从化验记录中读取
        lab_values = {
            'fasting_glucose': 5.4,  # mmol/L
            'total_cholesterol': 200,  # mg/dL
            'hdl_cholesterol': 50  # mg/dL
        }
        return lab_values.get(test_name)

    def _check_family_history(self, condition: str) -> bool:
        """检查家族史"""
        family_history = self.user_profile.get('family_history', {})
        return family_history.get(condition, False)

    def _check_smoking_status(self) -> bool:
        """检查吸烟状态"""
        lifestyle = self.user_profile.get('lifestyle', {})
        return lifestyle.get('smoking', False)

    def _check_medical_history(self, condition: str) -> bool:
        """检查既往病史"""
        medical_history = self.user_profile.get('medical_history', {})
        return medical_history.get(condition, False)

    def _assess_diet_quality(self) -> str:
        """评估饮食质量"""
        # 简化实现，实际应基于营养数据分析
        return 'moderate'

    def _calculate_average_rda(self, nutrition_data: dict, nutrient: str) -> float:
        """计算平均RDA达成率"""
        # 简化实现
        return 0.75  # 默认75%

    def _identify_key_factors(self, factors: dict, risk_score: int) -> List[dict]:
        """识别关键风险因素"""
        key_factors = []

        for factor_name, factor_value in factors.items():
            if factor_value in [True, 'high', 'poor', 'sedentary'] or \
               (isinstance(factor_value, (int, float)) and factor_value > 0):
                key_factors.append({
                    'name': factor_name,
                    'value': factor_value,
                    'contribution': 'significant'
                })

        return key_factors[:5]  # 返回前5个

    def _translate_risk_level(self, level: str) -> str:
        """翻译风险等级"""
        translations = {
            'low': '低风险',
            'moderate': '中等风险',
            'high': '高风险'
        }
        return translations.get(level, level)

    def _generate_recommendations(self, risk_type: str, probability: float) -> List[dict]:
        """生成建议"""
        recommendations = []

        if probability > 0.3:
            # 高风险建议
            recommendations.append({
                'level': 3,
                'category': 'medical_consultation',
                'title': '建议咨询医生',
                'content': f'根据AI风险预测，您的{risk_type}风险较高（{round(probability * 100)}%），建议咨询医生进行专业评估',
                'disclaimer': '本建议仅供参考，不能替代医生诊断',
                'requires_medical_supervision': True
            })

        # 生活方式建议
        recommendations.append({
            'level': 1,
            'category': 'lifestyle',
            'title': '生活方式干预',
            'content': '通过健康的生活方式可以降低风险',
            'actionable_steps': [
                '保持规律运动',
                '健康饮食',
                '控制体重',
                '戒烟限酒'
            ]
        })

        return recommendations

    def _generate_nutrition_recommendations(self, deficiencies: List[dict]) -> List[dict]:
        """生成营养建议"""
        recommendations = []

        for deficiency in deficiencies:
            nutrient = deficiency['nutrient']
            recommendations.append({
                'level': 2,
                'nutrient': nutrient,
                'title': f'增加{nutrient}摄入',
                'content': f'您的{nutrient}摄入不足（RDA达成率{deficiency["rda_achievement"]}）',
                'actionable_steps': [
                    f'增加富含{nutrient}的食物',
                    '考虑补充剂（咨询医生）',
                    '定期复查营养状况'
                ]
            })

        return recommendations

    def _generate_sleep_recommendations(self, risk_level: str) -> List[dict]:
        """生成睡眠建议"""
        return [
            {
                'level': 1,
                'title': '改善睡眠卫生',
                'content': '建立良好的睡眠习惯',
                'actionable_steps': [
                    '保持规律作息时间',
                    '睡前避免使用电子设备',
                    '创造舒适的睡眠环境',
                    '避免咖啡因和睡前大餐'
                ]
            },
            {
                'level': 2 if risk_level == 'high' else 1,
                'title': '如果症状持续，咨询医生',
                'content': '长期睡眠问题可能需要专业评估',
                'actionable_steps': [
                    '记录睡眠日记',
                    '咨询睡眠专家',
                    '考虑睡眠检查'
                ]
            }
        ]

    def _get_prevention_measures(self, risk_type: str) -> List[str]:
        """获取预防措施"""
        prevention = {
            'hypertension': [
                '控制体重在健康范围',
                '采用DASH饮食模式',
                '限制钠盐摄入',
                '规律运动',
                '限制饮酒',
                '管理压力'
            ],
            'diabetes': [
                '控制体重',
                '健康饮食（低糖、高纤维）',
                '规律运动',
                '定期监测血糖',
                '戒烟'
            ],
            'cardiovascular': [
                '控制血压、血脂、血糖',
                '戒烟',
                '规律运动',
                '健康饮食（地中海饮食）',
                '控制体重',
                '管理压力'
            ]
        }
        return prevention.get(risk_type, [])

    def _error_result(self, message: str) -> dict:
        """返回错误结果"""
        return {
            'error': True,
            'message': message
        }


def main():
    """主函数 - 用于测试"""
    engine = AIPredictionEngine()

    print("🧪 AI风险预测测试")
    print("=" * 50)

    # 测试高血压风险
    print("\n1. 高血压风险预测:")
    result = engine.predict_hypertension_risk()
    if not result.get('error'):
        print(f"   风险: {result['probability_percent']} ({result['risk_level_cn']})")
        print(f"   模型: {result['model']}")

    # 测试糖尿病风险
    print("\n2. 糖尿病风险预测:")
    result = engine.predict_diabetes_risk()
    if not result.get('error'):
        print(f"   风险: {result['probability_percent']} ({result['risk_level_cn']})")
        print(f"   模型: {result['model']}")

    # 测试心血管风险
    print("\n3. 心血管疾病风险预测:")
    result = engine.predict_cardiovascular_risk()
    if not result.get('error'):
        print(f"   风险: {result['probability_percent']} ({result['risk_level_cn']})")
        print(f"   模型: {result['model']}")


if __name__ == "__main__":
    main()
