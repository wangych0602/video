import logging
from typing import Dict, Any
from .BaseAgent import BaseAgent
from ..services.evaluation_engine import EvaluationEngine
from ..services.ai_provider import get_active_provider
from ..prompts.teaching_evaluation_prompt import TeachingEvaluationPrompt

logger = logging.getLogger('ai_analysis.teaching_evaluation_agent')


class TeachingEvaluationAgent(BaseAgent):
    # 教学评价Agent
    # 综合分析视频和语音分析结果，生成教学评价
    
    name = 'teaching_evaluation'
    description = '综合分析课堂视频和语音数据，生成专业的教学评价报告'
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.evaluation_engine = EvaluationEngine(config)
        self.ai_provider = None
        self.use_ai = config.get('use_ai', False) if config else False
        
        # 教师信息
        self.teacher_role = config.get('teacher_role', '教师') if config else '教师'
        self.course_type = config.get('course_type', '常规课程') if config else '常规课程'
        self.student_age = config.get('student_age', '12-15岁') if config else '12-15岁'
        self.class_goal = config.get('class_goal', '掌握本节课知识点') if config else '掌握本节课知识点'
    
    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入数据
        if not input_data:
            self.log_error('输入数据为空')
            return False
        
        video_result = input_data.get('video_result')
        speech_result = input_data.get('speech_result')
        
        if not video_result and not speech_result:
            self.log_error('视频分析结果和语音分析结果都为空')
            return False
        
        return True
    
    def run(self, input_data: Dict) -> Dict:
        # 执行教学评价
        try:
            self.log_info('开始教学评价...')
            
            # 验证输入
            if not self.validate_input(input_data):
                return self.handle_error('输入数据验证失败')
            
            video_result = input_data.get('video_result', {})
            speech_result = input_data.get('speech_result', {})
            task_id = input_data.get('task_id')
            
            # 更新进度
            self._update_progress(55, '开始教学评价')
            
            # 基于规则的评价
            self._update_progress(60, '计算各维度评分')
            rule_based_result = self.evaluation_engine.evaluate(video_result, speech_result)
            
            if not rule_based_result.get('success'):
                self.log_error(f'规则评价失败: {rule_based_result.get("error")}')
                return self.handle_error(rule_based_result.get('error', '规则评价失败'))
            
            self._update_progress(70, '规则评价完成')
            
            # AI 增强评价（可选）
            ai_enhanced_result = None
            if self.use_ai:
                try:
                    self._update_progress(75, 'AI增强评价中')
                    ai_enhanced_result = self._ai_enhanced_evaluation(video_result, speech_result)
                    self._update_progress(85, 'AI增强评价完成')
                except Exception as e:
                    self.log_warning(f'AI增强评价失败，使用规则评价结果: {e}')
            
            # 合并结果
            final_result = self._merge_results(rule_based_result, ai_enhanced_result)
            
            self._update_progress(90, '生成评价报告')
            
            # 保存结果
            self.set_result('overall_score', final_result['overall_score'])
            self.set_result('knowledge_score', final_result['knowledge_score'])
            self.set_result('interaction_score', final_result['interaction_score'])
            self.set_result('expression_score', final_result['expression_score'])
            self.set_result('classroom_management_score', final_result['classroom_management_score'])
            self.set_result('teaching_structure_score', final_result['teaching_structure_score'])
            self.set_result('grade', final_result['grade'])
            self.set_result('strengths', final_result['strengths'])
            self.set_result('weaknesses', final_result['weaknesses'])
            self.set_result('suggestions', final_result['suggestions'])
            self.set_result('evaluation_method', 'ai_enhanced' if ai_enhanced_result else 'rule_based')
            
            self._update_progress(100, '教学评价完成')
            
            self.log_info(f'教学评价完成，总分: {final_result["overall_score"]}, 等级: {final_result["grade"]}')
            
            return {
                'success': True,
                'agent': self.name,
                'overall_score': final_result['overall_score'],
                'knowledge_score': final_result['knowledge_score'],
                'interaction_score': final_result['interaction_score'],
                'expression_score': final_result['expression_score'],
                'classroom_management_score': final_result['classroom_management_score'],
                'teaching_structure_score': final_result['teaching_structure_score'],
                'grade': final_result['grade'],
                'strengths': final_result['strengths'],
                'weaknesses': final_result['weaknesses'],
                'suggestions': final_result['suggestions'],
                'evaluation_method': final_result.get('evaluation_method', 'rule_based'),
                'result': self.result,
            }
            
        except Exception as e:
            self.log_error(f'教学评价失败: {e}')
            return self.handle_error(str(e))
    
    def _ai_enhanced_evaluation(self, video_result: Dict, speech_result: Dict) -> Dict:
        # AI 增强评价
        if not self.ai_provider:
            self.ai_provider = get_active_provider()
        
        # 获取 prompt
        messages = TeachingEvaluationPrompt.get_messages(
            video_result=video_result,
            speech_result=speech_result,
            teacher_role=self.teacher_role,
            course_type=self.course_type,
            student_age=self.student_age,
            class_goal=self.class_goal,
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
                    'overall_score': result.get('overall_score', 0),
                    'knowledge_score': result.get('knowledge_score', 0),
                    'interaction_score': result.get('interaction_score', 0),
                    'expression_score': result.get('expression_score', 0),
                    'classroom_management_score': result.get('classroom_management_score', 0),
                    'teaching_structure_score': result.get('teaching_structure_score', 0),
                    'grade': result.get('grade', ''),
                    'strengths': result.get('strengths', []),
                    'weaknesses': result.get('weaknesses', []),
                    'suggestions': result.get('suggestions', []),
                }
        except Exception as e:
            self.log_warning(f'解析AI响应失败: {e}')
        
        return None
    
    def _merge_results(self, rule_result: Dict, ai_result: Dict = None) -> Dict:
        # 合并规则评价和 AI 评价结果
        if not ai_result:
            return rule_result
        
        # 以规则评价为基础，AI 评价作为补充
        merged = rule_result.copy()
        
        # 分数取加权平均（规则 60%，AI 40%）
        weight_rule = 0.6
        weight_ai = 0.4
        
        merged['overall_score'] = round(
            rule_result['overall_score'] * weight_rule + ai_result['overall_score'] * weight_ai, 1
        )
        merged['knowledge_score'] = round(
            rule_result['knowledge_score'] * weight_rule + ai_result['knowledge_score'] * weight_ai, 1
        )
        merged['interaction_score'] = round(
            rule_result['interaction_score'] * weight_rule + ai_result['interaction_score'] * weight_ai, 1
        )
        merged['expression_score'] = round(
            rule_result['expression_score'] * weight_rule + ai_result['expression_score'] * weight_ai, 1
        )
        merged['classroom_management_score'] = round(
            rule_result['classroom_management_score'] * weight_rule + ai_result['classroom_management_score'] * weight_ai, 1
        )
        merged['teaching_structure_score'] = round(
            rule_result['teaching_structure_score'] * weight_rule + ai_result['teaching_structure_score'] * weight_ai, 1
        )
        
        # 优势、不足、建议合并去重
        merged['strengths'] = list(set(rule_result['strengths'] + ai_result.get('strengths', [])))[:5]
        merged['weaknesses'] = list(set(rule_result['weaknesses'] + ai_result.get('weaknesses', [])))[:4]
        merged['suggestions'] = list(set(rule_result['suggestions'] + ai_result.get('suggestions', [])))[:6]
        
        merged['evaluation_method'] = 'ai_enhanced'
        
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