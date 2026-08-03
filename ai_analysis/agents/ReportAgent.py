from typing import Dict, Any, List
from .BaseAgent import BaseAgent


class ReportAgent(BaseAgent):
    name = 'report_generation'
    description = '报告生成Agent，生成完整的课堂分析报告'
    
    def __init__(self, config=None):
        super().__init__(config)
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            self.log_info('Starting report generation...')
            
            video_result = input_data.get('video_result', {})
            speech_result = input_data.get('speech_result', {})
            evaluation_result = input_data.get('evaluation_result', {})
            video_id = input_data.get('video_id')
            
            # TODO: 实现报告生成逻辑
            # 1. 汇总各 Agent 的分析结果
            # 2. 生成课堂总结
            # 3. 提取关键词
            # 4. 整理知识点
            # 5. 生成改进建议
            # 6. 生成报告文件（可选）
            
            # 生成报告内容
            summary = self.generate_summary(video_result, speech_result, evaluation_result)
            keywords = self.extract_keywords(speech_result, evaluation_result)
            knowledge_points = self.extract_knowledge_points(speech_result)
            suggestions = self.generate_suggestions(evaluation_result)
            
            result = {
                'success': True,
                'video_id': video_id,
                'summary': summary,
                'keywords': keywords,
                'knowledge_points': knowledge_points,
                'teaching_score': evaluation_result.get('teaching_score', 0),
                'student_engagement_score': evaluation_result.get('student_engagement_score', 0),
                'teacher_score': evaluation_result.get('teacher_score', 0),
                'suggestions': suggestions,
                'report_url': '',
                'report_content': self.generate_report_content(
                    summary, keywords, knowledge_points, evaluation_result, suggestions
                )
            }
            
            self._result = result
            self.log_info('Report generation completed')
            
            return result
            
        except Exception as e:
            return self.handle_error(e)
    
    def generate_summary(self, video_result: Dict, speech_result: Dict, evaluation_result: Dict) -> str:
        # 生成课堂总结
        # TODO: 实现智能总结
        transcript = speech_result.get('transcript', '')
        if transcript:
            # 简单截取前200字作为摘要
            return transcript[:200] + '...' if len(transcript) > 200 else transcript
        return '课堂分析总结'
    
    def extract_keywords(self, speech_result: Dict, evaluation_result: Dict) -> List[str]:
        # 提取关键词
        keywords = speech_result.get('keywords', [])
        if not keywords:
            keywords = ['教学', '课堂', '学习']
        return keywords
    
    def extract_knowledge_points(self, speech_result: Dict) -> List[str]:
        # 提取知识点
        # TODO: 实现知识点提取
        return []
    
    def generate_suggestions(self, evaluation_result: Dict) -> str:
        # 生成改进建议
        suggestions = evaluation_result.get('suggestions', [])
        if suggestions:
            return '\n'.join([f'- {s}' for s in suggestions])
        return '继续保持良好的教学状态。'
    
    def generate_report_content(self, summary: str, keywords: list, knowledge_points: list, 
                                evaluation_result: Dict, suggestions: str) -> str:
        # 生成完整的报告内容
        content = f'''# 课堂分析报告

## 一、课堂总结
{summary}

## 二、关键词
{', '.join(keywords)}

## 三、教学评分
- 教学评分：{evaluation_result.get('teaching_score', 0)}
- 学生参与度：{evaluation_result.get('student_engagement_score', 0)}
- 教师综合评分：{evaluation_result.get('teacher_score', 0)}

## 四、改进建议
{suggestions}
'''
        return content