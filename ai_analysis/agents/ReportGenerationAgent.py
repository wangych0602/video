import logging
from typing import Dict, Any
from .BaseAgent import BaseAgent
from ..services.report_generator import ReportGenerator
from ..services.ai_provider import get_active_provider
from ..prompts.report_generation_prompt import ReportGenerationPrompt

logger = logging.getLogger('ai_analysis.report_generation_agent')


class ReportGenerationAgent(BaseAgent):
    # 报告生成Agent
    # 综合视频、语音、教学评价结果，生成完整课堂报告
    
    name = 'report_generation'
    description = '综合分析课堂数据，生成专业的课堂分析报告'
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.report_generator = ReportGenerator(config)
        self.ai_provider = None
        self.use_ai = config.get('use_ai', False) if config else False
        self.media_root = config.get('media_root', 'media') if config else 'media'
    
    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入数据
        if not input_data:
            self.log_error('输入数据为空')
            return False
        
        video_result = input_data.get('video_result')
        speech_result = input_data.get('speech_result')
        evaluation_result = input_data.get('evaluation_result')
        
        if not video_result and not speech_result and not evaluation_result:
            self.log_error('所有分析结果都为空')
            return False
        
        return True
    
    def run(self, input_data: Dict) -> Dict:
        # 执行报告生成
        try:
            self.log_info('开始生成报告...')
            
            # 验证输入
            if not self.validate_input(input_data):
                return self.handle_error('输入数据验证失败')
            
            video_result = input_data.get('video_result', {})
            speech_result = input_data.get('speech_result', {})
            evaluation_result = input_data.get('evaluation_result', {})
            task_id = input_data.get('task_id')
            
            # 更新进度
            self._update_progress(85, '开始生成报告')
            
            # 基于规则的报告生成
            self._update_progress(88, '生成报告内容')
            rule_based_report = self.report_generator.generate_report(
                video_result, speech_result, evaluation_result, task_id
            )
            
            if not rule_based_report.get('success'):
                self.log_error(f'报告生成失败: {rule_based_report.get("error")}')
                return self.handle_error(rule_based_report.get('error', '报告生成失败'))
            
            self._update_progress(92, '报告内容生成完成')
            
            # AI 增强报告（可选）
            ai_enhanced_report = None
            if self.use_ai:
                try:
                    self._update_progress(90, 'AI增强报告中')
                    ai_enhanced_report = self._ai_enhanced_report(video_result, speech_result, evaluation_result)
                    self._update_progress(95, 'AI增强报告完成')
                except Exception as e:
                    self.log_warning(f'AI增强报告失败，使用规则报告: {e}')
            
            # 合并结果
            final_report = self._merge_reports(rule_based_report, ai_enhanced_report)
            
            self._update_progress(98, '保存报告')
            
            # 保存结果
            self.set_result('title', final_report['title'])
            self.set_result('summary', final_report['summary'])
            self.set_result('teacher_report', final_report['teacher_report'])
            self.set_result('school_report', final_report['school_report'])
            self.set_result('html_content', final_report['html_content'])
            self.set_result('pdf_path', final_report.get('pdf_path'))
            self.set_result('report_url', final_report.get('report_url', ''))
            
            self._update_progress(100, '报告生成完成')
            
            self.log_info(f'报告生成完成，标题: {final_report["title"]}')
            
            return {
                'success': True,
                'agent': self.name,
                'title': final_report['title'],
                'summary': final_report['summary'],
                'teacher_report': final_report['teacher_report'],
                'school_report': final_report['school_report'],
                'html_content': final_report['html_content'],
                'pdf_path': final_report.get('pdf_path'),
                'report_url': final_report.get('report_url', ''),
                'result': self.result,
            }
            
        except Exception as e:
            self.log_error(f'报告生成失败: {e}')
            return self.handle_error(str(e))
    
    def _ai_enhanced_report(self, video_result: Dict, speech_result: Dict, evaluation_result: Dict) -> Dict:
        # AI 增强报告生成
        if not self.ai_provider:
            self.ai_provider = get_active_provider()
        
        # 获取 prompt
        messages = ReportGenerationPrompt.get_messages(
            video_result=video_result,
            speech_result=speech_result,
            evaluation_result=evaluation_result,
        )
        
        # 调用 AI
        response = self.ai_provider.chat(messages)
        
        # 解析结果
        return self._parse_ai_response(response)
    
    def _parse_ai_response(self, response: str) -> Dict:
        # 解析 AI 响应
        import json
        import re
        
        try:
            # 尝试提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                return {
                    'success': True,
                    'title': result.get('title', '课堂分析报告'),
                    'summary': result.get('summary', ''),
                    'strengths': result.get('strengths', []),
                    'weaknesses': result.get('weaknesses', []),
                    'suggestions': result.get('suggestions', []),
                    'scores': result.get('scores', {}),
                    'overall_score': result.get('overall_score', 0),
                    'grade': result.get('grade', ''),
                    'teacher_report': result.get('teacher_report', {}),
                    'school_report': result.get('school_report', {}),
                }
        except Exception as e:
            self.log_warning(f'解析AI响应失败: {e}')
        
        return None
    
    def _merge_reports(self, rule_report: Dict, ai_report: Dict = None) -> Dict:
        # 合并规则报告和 AI 报告
        if not ai_report:
            return rule_report
        
        merged = rule_report.copy()
        
        # 用 AI 生成的总结替换
        if ai_report.get('summary'):
            merged['summary']['ai_summary'] = ai_report['summary']
        
        # 合并优势、不足、建议
        if ai_report.get('strengths'):
            merged['summary']['strengths'] = list(set(
                merged['summary'].get('strengths', []) + ai_report['strengths']
            ))[:5]
        
        if ai_report.get('weaknesses'):
            merged['summary']['weaknesses'] = list(set(
                merged['summary'].get('weaknesses', []) + ai_report['weaknesses']
            ))[:4]
        
        if ai_report.get('suggestions'):
            merged['summary']['suggestions'] = list(set(
                merged['summary'].get('suggestions', []) + ai_report['suggestions']
            ))[:6]
        
        return merged
    
    def _update_progress(self, progress: int, step: str = ''):
        # 更新进度
        self.set_result('progress', progress)
        self.set_result('current_step', step)
        if hasattr(self, 'progress_callback') and self.progress_callback:
            self.progress_callback(progress, step)
    
    def set_progress_callback(self, callback):
        # 设置进度回调函数
        self.progress_callback = callback