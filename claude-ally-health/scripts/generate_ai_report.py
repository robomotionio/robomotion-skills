#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI健康报告生成器
生成包含AI洞察和交互式图表的HTML健康报告
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from ai_prediction import AIPredictionEngine


class AIHealthReportGenerator:
    """AI健康报告生成器"""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.prediction_engine = AIPredictionEngine(base_dir)
        self.output_dir = self.base_dir / "ai-reports"
        self.output_dir.mkdir(exist_ok=True)

    def generate_report(self, report_type: str = "comprehensive", time_range: str = "last_quarter") -> str:
        """
        生成AI健康报告

        Args:
            report_type: 报告类型 (comprehensive/quick_summary/risk_assessment/trend_analysis)
            time_range: 时间范围

        Returns:
            生成的HTML文件路径
        """
        # 收集数据
        report_data = self._collect_report_data(report_type, time_range)

        # 生成HTML内容
        html_content = self._generate_html_content(report_data, report_type)

        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"ai-health-report-{timestamp}.html"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(filepath)

    def _collect_report_data(self, report_type: str, time_range: str) -> Dict[str, Any]:
        """收集报告数据"""
        # 读取用户档案
        profile_path = self.base_dir / "profile.json"
        if profile_path.exists():
            with open(profile_path, 'r', encoding='utf-8') as f:
                user_profile = json.load(f)
        else:
            user_profile = {}

        # 执行风险预测
        predictions = {}
        if report_type in ['comprehensive', 'risk_assessment']:
            predictions['hypertension'] = self.prediction_engine.predict_hypertension_risk()
            predictions['diabetes'] = self.prediction_engine.predict_diabetes_risk()
            predictions['cardiovascular'] = self.prediction_engine.predict_cardiovascular_risk()

        # 构建报告数据
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'report_type': report_type,
                'time_range': time_range,
                'version': '1.0.0'
            },
            'user_profile': user_profile,
            'predictions': predictions,
            'summary': self._generate_summary(predictions),
            'recommendations': self._generate_recommendations(predictions)
        }

        return report_data

    def _generate_summary(self, predictions: dict) -> dict:
        """生成总体摘要"""
        high_risks = []
        moderate_risks = []
        low_risks = []

        for risk_type, prediction in predictions.items():
            if prediction.get('error'):
                continue

            risk_level = prediction.get('risk_level', 'low')
            risk_name = prediction.get('risk_name', risk_type)

            if risk_level == 'high':
                high_risks.append(risk_name)
            elif risk_level == 'moderate':
                moderate_risks.append(risk_name)
            else:
                low_risks.append(risk_name)

        return {
            'high_risks': high_risks,
            'moderate_risks': moderate_risks,
            'low_risks': low_risks,
            'overall_assessment': self._assess_overall_health(high_risks, moderate_risks)
        }

    def _assess_overall_health(self, high_risks: list, moderate_risks: list) -> str:
        """评估整体健康状况"""
        if len(high_risks) >= 2:
            return "需要关注"
        elif len(high_risks) == 1 or len(moderate_risks) >= 2:
            return "一般"
        elif len(moderate_risks) == 1:
            return "良好"
        else:
            return "优秀"

    def _generate_recommendations(self, predictions: dict) -> list:
        """生成综合建议"""
        recommendations = []

        for risk_type, prediction in predictions.items():
            if prediction.get('error'):
                continue

            risk_recommendations = prediction.get('recommendations', [])
            recommendations.extend(risk_recommendations)

        # 按优先级排序
        level_3 = [r for r in recommendations if r.get('level') == 3]
        level_1 = [r for r in recommendations if r.get('level') == 1]
        level_2 = [r for r in recommendations if r.get('level') == 2]

        return level_3 + level_1 + level_2[:5]

    def _generate_html_content(self, report_data: dict, report_type: str) -> str:
        """生成HTML内容"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI健康分析报告 - {report_data['metadata']['generated_at'][:10]}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .risk-high {{ background-color: #fee2e2; border-left: 4px solid #ef4444; }}
        .risk-moderate {{ background-color: #fef3c7; border-left: 4px solid #f59e0b; }}
        .risk-low {{ background-color: #d1fae5; border-left: 4px solid #10b981; }}
        @media print {{
            .no-print {{ display: none; }}
            body {{ font-size: 12px; }}
        }}
    </style>
</head>
<body class="bg-gray-50">
    <div class="max-w-6xl mx-auto p-6 bg-white shadow-lg">
        <!-- 报告头部 -->
        <header class="border-b-2 border-blue-600 pb-4 mb-6">
            <h1 class="text-3xl font-bold text-blue-900">AI健康分析报告</h1>
            <p class="text-gray-600 mt-2">
                生成时间: {report_data['metadata']['generated_at'][:19].replace('T', ' ')} |
                报告类型: {self._translate_report_type(report_type)} |
                版本: {report_data['metadata']['version']}
            </p>
        </header>

        <!-- 总体评估 -->
        <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 border-b pb-2">📊 总体评估</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-blue-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-600">整体健康状况</div>
                    <div class="text-2xl font-bold text-blue-900">{report_data['summary']['overall_assessment']}</div>
                </div>
                <div class="bg-green-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-600">低风险项</div>
                    <div class="text-2xl font-bold text-green-700">{len(report_data['summary']['low_risks'])}</div>
                </div>
                <div class="bg-red-50 p-4 rounded-lg">
                    <div class="text-sm text-gray-600">高风险项</div>
                    <div class="text-2xl font-bold text-red-700">{len(report_data['summary']['high_risks'])}</div>
                </div>
            </div>
        </section>

        <!-- 风险预测 -->
        <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 border-b pb-2">🎯 健康风险预测</h2>
            <div class="space-y-4">
                {self._generate_risk_cards_html(report_data['predictions'])}
            </div>
        </section>

        <!-- 个性化建议 -->
        <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 border-b pb-2">💡 个性化建议</h2>
            <div class="space-y-4">
                {self._generate_recommendations_html(report_data['recommendations'])}
            </div>
        </section>

        <!-- 风险分布图 -->
        <section class="mb-8">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4 border-b pb-2">📈 风险分布</h2>
            <div id="riskChart" style="width: 100%; height: 400px;"></div>
        </section>

        <!-- 免责声明 -->
        <footer class="mt-12 pt-6 border-t-2 border-gray-300">
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div class="font-bold text-yellow-800">⚠️ 重要声明</div>
                <ul class="mt-2 text-sm text-yellow-700 space-y-1">
                    <li>• 本AI分析仅供参考，不构成医疗诊断或治疗建议</li>
                    <li>• 风险预测基于统计学模型和群体数据，不能确定个体结果</li>
                    <li>• 所有医疗建议请咨询专业医生</li>
                    <li>• 请结合个人实际情况和医生建议进行健康决策</li>
                </ul>
            </div>
        </footer>
    </div>

    <script>
        // 风险分布饼图
        const riskChart = echarts.init(document.getElementById('riskChart'));
        const riskData = {self._get_chart_data(report_data['predictions'])};

        const option = {{
            title: {{
                text: '健康风险分布',
                left: 'center'
            }},
            tooltip: {{
                trigger: 'item',
                formatter: '{{{{a}}}} <br/>{{{{b}}}}: {{{{c}}}}%'
            }},
            legend: {{
                orient: 'vertical',
                left: 'left'
            }},
            series: [
                {{
                    name: '风险等级',
                    type: 'pie',
                    radius: '50%',
                    data: riskData,
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }}
                    }}
                }}
            ]
        }};

        riskChart.setOption(option);

        // 响应式调整
        window.addEventListener('resize', function() {{
            riskChart.resize();
        }});
    </script>
</body>
</html>"""
        return html

    def _translate_report_type(self, report_type: str) -> str:
        """翻译报告类型"""
        translations = {
            'comprehensive': '综合报告',
            'quick_summary': '快速摘要',
            'risk_assessment': '风险评估',
            'trend_analysis': '趋势分析'
        }
        return translations.get(report_type, report_type)

    def _generate_risk_cards_html(self, predictions: dict) -> str:
        """生成风险卡片HTML"""
        html = ""
        for risk_type, prediction in predictions.items():
            if prediction.get('error'):
                continue

            risk_level = prediction.get('risk_level', 'low')
            risk_class = f"risk-{risk_level}"

            html += f"""
            <div class="{risk_class} p-4 rounded-lg">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-lg font-semibold">{prediction.get('risk_name', risk_type)}</h3>
                        <p class="text-sm text-gray-600 mt-1">模型: {prediction.get('model', 'N/A')}</p>
                    </div>
                    <div class="text-right">
                        <div class="text-2xl font-bold">{prediction.get('probability_percent', 'N/A')}</div>
                        <div class="text-sm">{prediction.get('risk_level_cn', 'N/A')}</div>
                    </div>
                </div>
                <p class="mt-2 text-sm">时间范围: 未来{prediction.get('time_horizon_years', 10)}年</p>
            </div>
            """
        return html

    def _generate_recommendations_html(self, recommendations: list) -> str:
        """生成建议HTML"""
        html = ""
        for rec in recommendations[:10]:  # 最多显示10条
            level = rec.get('level', 1)
            level_class = {
                1: 'border-l-4 border-green-500 bg-green-50',
                2: 'border-l-4 border-yellow-500 bg-yellow-50',
                3: 'border-l-4 border-red-500 bg-red-50'
            }.get(level, 'border-l-4 border-gray-500 bg-gray-50')

            level_badge = {
                1: 'Level 1: 一般性建议',
                2: 'Level 2: 参考性建议',
                3: 'Level 3: 医疗建议'
            }.get(level, '建议')

            html += f"""
            <div class="{level_class} p-4 rounded">
                <div class="flex justify-between items-start">
                    <h4 class="font-semibold">{rec.get('title', '建议')}</h4>
                    <span class="text-xs px-2 py-1 bg-white rounded">{level_badge}</span>
                </div>
                <p class="mt-2 text-sm">{rec.get('content', '')}</p>
                {self._generate_actionable_steps_html(rec.get('actionable_steps', []))}
                {self._generate_disclaimer_html(rec.get('disclaimer'))}
            </div>
            """
        return html

    def _generate_actionable_steps_html(self, steps: list) -> str:
        """生成可执行步骤HTML"""
        if not steps:
            return ""

        html = "<ul class='mt-2 text-sm space-y-1'>"
        for step in steps:
            html += f"<li>• {step}</li>"
        html += "</ul>"
        return html

    def _generate_disclaimer_html(self, disclaimer: Optional[str]) -> str:
        """生成免责声明HTML"""
        if not disclaimer:
            return ""
        return f"<p class='mt-2 text-xs text-red-600 italic'>⚠️ {disclaimer}</p>"

    def _get_chart_data(self, predictions: dict) -> str:
        """获取图表数据"""
        high_count = sum(1 for p in predictions.values() if p.get('risk_level') == 'high')
        moderate_count = sum(1 for p in predictions.values() if p.get('risk_level') == 'moderate')
        low_count = sum(1 for p in predictions.values() if p.get('risk_level') == 'low')

        return f"""[
            {{value: {high_count}, name: '高风险', itemStyle: {{color: '#ef4444'}}}},
            {{value: {moderate_count}, name: '中等风险', itemStyle: {{color: '#f59e0b'}}}},
            {{value: {low_count}, name: '低风险', itemStyle: {{color: '#10b981'}}}}
        ]"""


def main():
    """主函数"""
    generator = AIHealthReportGenerator()

    print("📄 生成AI健康报告...")
    print("=" * 50)

    # 生成综合报告
    filepath = generator.generate_report('comprehensive')
    print(f"\n✅ 报告生成成功!")
    print(f"文件路径: {filepath}")
    print(f"\n在浏览器中打开查看:")
    print(f"  open {filepath}")


if __name__ == "__main__":
    main()
