import logging
from typing import Dict, List, Any
from collections import Counter

logger = logging.getLogger('ai_analysis.evaluation_engine')


class EvaluationEngine:
    # 教学评价引擎
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # 各维度权重
        self.weights = {
            'knowledge': 0.25,      # 知识掌握度
            'interaction': 0.20,    # 互动参与度
            'expression': 0.20,     # 表达清晰度
            'classroom_management': 0.15,  # 课堂管理
            'teaching_structure': 0.20,    # 教学结构
        }
    
    def evaluate(self, video_result: Dict, speech_result: Dict) -> Dict:
        # 综合评价
        try:
            # 提取各维度数据
            teacher_actions = video_result.get('teacher_actions', [])
            student_interaction = video_result.get('student_interaction', {})
            classroom_environment = video_result.get('classroom_environment', {})
            
            transcript = speech_result.get('transcript', '')
            keywords = speech_result.get('keywords', [])
            knowledge_points = speech_result.get('knowledge_points', [])
            speaking_rate = speech_result.get('speaking_rate', {})
            speech_segments = speech_result.get('speech_segments', [])
            
            # 计算各维度得分
            knowledge_score = self._evaluate_knowledge(keywords, knowledge_points, transcript)
            interaction_score = self._evaluate_interaction(student_interaction, speech_segments)
            expression_score = self._evaluate_expression(speaking_rate, transcript, speech_segments)
            classroom_management_score = self._evaluate_classroom_management(
                teacher_actions, classroom_environment, speech_segments
            )
            teaching_structure_score = self._evaluate_teaching_structure(
                knowledge_points, teacher_actions, speech_segments
            )
            
            # 计算总分
            overall_score = (
                knowledge_score * self.weights['knowledge'] +
                interaction_score * self.weights['interaction'] +
                expression_score * self.weights['expression'] +
                classroom_management_score * self.weights['classroom_management'] +
                teaching_structure_score * self.weights['teaching_structure']
            )
            
            # 生成优势、不足、建议
            strengths = self._generate_strengths(
                knowledge_score, interaction_score, expression_score,
                classroom_management_score, teaching_structure_score
            )
            weaknesses = self._generate_weaknesses(
                knowledge_score, interaction_score, expression_score,
                classroom_management_score, teaching_structure_score
            )
            suggestions = self._generate_suggestions(
                knowledge_score, interaction_score, expression_score,
                classroom_management_score, teaching_structure_score
            )
            
            return {
                'success': True,
                'overall_score': round(overall_score, 1),
                'knowledge_score': round(knowledge_score, 1),
                'interaction_score': round(interaction_score, 1),
                'expression_score': round(expression_score, 1),
                'classroom_management_score': round(classroom_management_score, 1),
                'teaching_structure_score': round(teaching_structure_score, 1),
                'strengths': strengths,
                'weaknesses': weaknesses,
                'suggestions': suggestions,
                'grade': self._get_grade(overall_score),
            }
            
        except Exception as e:
            logger.error(f'Evaluation failed: {e}')
            return {
                'success': False,
                'error': str(e),
                'overall_score': 0,
                'knowledge_score': 0,
                'interaction_score': 0,
                'expression_score': 0,
                'classroom_management_score': 0,
                'teaching_structure_score': 0,
                'strengths': [],
                'weaknesses': [],
                'suggestions': [],
                'grade': 'N/A',
            }
    
    def _evaluate_knowledge(self, keywords: List, knowledge_points: List, transcript: str) -> float:
        # 知识掌握度评分
        score = 60.0
        
        # 关键词丰富度
        if len(keywords) >= 15:
            score += 10
        elif len(keywords) >= 10:
            score += 7
        elif len(keywords) >= 5:
            score += 4
        
        # 知识点数量
        if len(knowledge_points) >= 8:
            score += 10
        elif len(knowledge_points) >= 5:
            score += 7
        elif len(knowledge_points) >= 3:
            score += 4
        
        # 知识点重要性分布
        high_importance = [kp for kp in knowledge_points if isinstance(kp, dict) and kp.get('importance') == 'high']
        if len(high_importance) >= 3:
            score += 10
        elif len(high_importance) >= 2:
            score += 6
        elif len(high_importance) >= 1:
            score += 3
        
        # 文字稿内容丰富度
        char_count = len(transcript)
        if char_count >= 5000:
            score += 10
        elif char_count >= 3000:
            score += 7
        elif char_count >= 1000:
            score += 4
        
        return min(score, 100)
    
    def _evaluate_interaction(self, student_interaction: Dict, speech_segments: List) -> float:
        # 互动参与度评分
        score = 50.0
        
        # 学生互动次数
        interaction_count = student_interaction.get('interaction_count', 0)
        if interaction_count >= 10:
            score += 15
        elif interaction_count >= 5:
            score += 10
        elif interaction_count >= 3:
            score += 5
        
        # 参与度
        engagement = student_interaction.get('engagement_level', 0)
        if isinstance(engagement, str):
            engagement_map = {'high': 90, 'medium': 70, 'low': 50}
            engagement = engagement_map.get(engagement, 60)
        score += (engagement / 100) * 15
        
        # 学生发言比例
        student_segments = [s for s in speech_segments if s.get('speaker') == 'student']
        teacher_segments = [s for s in speech_segments if s.get('speaker') == 'teacher']
        
        if teacher_segments:
            student_ratio = len(student_segments) / len(teacher_segments)
            if student_ratio >= 0.3:
                score += 10
            elif student_ratio >= 0.2:
                score += 7
            elif student_ratio >= 0.1:
                score += 4
        
        # 互动类型多样性
        interaction_types = student_interaction.get('interaction_types', [])
        if len(interaction_types) >= 4:
            score += 10
        elif len(interaction_types) >= 3:
            score += 7
        elif len(interaction_types) >= 2:
            score += 4
        
        return min(score, 100)
    
    def _evaluate_expression(self, speaking_rate: Dict, transcript: str, speech_segments: List) -> float:
        # 表达清晰度评分
        score = 60.0
        
        # 语速
        pace = speaking_rate.get('pace', 'normal')
        pace_scores = {
            'slow': 75,      # 稍慢但清晰
            'normal': 90,    # 适中最佳
            'fast': 70,      # 偏快
            'very_fast': 50, # 过快
        }
        score += pace_scores.get(pace, 70) - 60
        
        # 语速稳定性（各片段语速差异）
        cpms = [s.get('chars_per_minute', 0) for s in speech_segments if s.get('chars_per_minute')]
        if cpms:
            avg_cpm = sum(cpms) / len(cpms)
            if avg_cpm > 0:
                variance = sum((c - avg_cpm) ** 2 for c in cpms) / len(cpms)
                cv = (variance ** 0.5) / avg_cpm  # 变异系数
                if cv < 0.2:
                    score += 10  # 语速稳定
                elif cv < 0.4:
                    score += 6
                else:
                    score += 2
        
        # 文字稿连贯性
        if transcript:
            # 简单的连贯性指标：句子数量和平均长度
            sentences = [s for s in transcript.replace('！', '。').replace('？', '。').split('。') if s.strip()]
            if sentences:
                avg_len = sum(len(s) for s in sentences) / len(sentences)
                if 10 <= avg_len <= 30:
                    score += 10  # 句子长度适中
                elif 5 <= avg_len <= 40:
                    score += 6
                else:
                    score += 2
        
        # 语音片段完整性
        if speech_segments:
            total_duration = sum(s.get('duration', 0) for s in speech_segments)
            if total_duration > 0:
                avg_duration = total_duration / len(speech_segments)
                if avg_duration >= 30:
                    score += 10
                elif avg_duration >= 15:
                    score += 6
                else:
                    score += 3
        
        return min(score, 100)
    
    def _evaluate_classroom_management(self, teacher_actions: List, classroom_environment: Dict, speech_segments: List) -> float:
        # 课堂管理评分
        score = 60.0
        
        # 教师动作多样性
        action_types = set()
        for action in teacher_actions:
            if isinstance(action, dict):
                action_types.add(action.get('action', ''))
        if len(action_types) >= 5:
            score += 10
        elif len(action_types) >= 3:
            score += 6
        elif len(action_types) >= 2:
            score += 3
        
        # 教师位置变化
        locations = set()
        for action in teacher_actions:
            if isinstance(action, dict):
                locations.add(action.get('location', ''))
        if len(locations) >= 3:
            score += 10
        elif len(locations) >= 2:
            score += 6
        else:
            score += 2
        
        # 教室环境
        lighting = classroom_environment.get('lighting', '')
        if lighting == 'good' or lighting == '良好':
            score += 5
        elif lighting == 'medium' or lighting == '一般':
            score += 3
        
        # 课堂秩序（通过语音片段的连续性判断）
        if speech_segments:
            # 检查是否有长时间空白
            gaps = []
            for i in range(1, len(speech_segments)):
                gap = speech_segments[i].get('start', 0) - speech_segments[i-1].get('end', 0)
                if gap > 0:
                    gaps.append(gap)
            
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                if avg_gap < 5:
                    score += 10  # 课堂紧凑
                elif avg_gap < 10:
                    score += 6
                else:
                    score += 3
        
        # 时间管理
        if teacher_actions:
            total_action_time = sum(a.get('duration', 0) for a in teacher_actions if isinstance(a, dict))
            if total_action_time > 0:
                # 动作分布均匀性
                score += 5
        
        return min(score, 100)
    
    def _evaluate_teaching_structure(self, knowledge_points: List, teacher_actions: List, speech_segments: List) -> float:
        # 教学结构评分
        score = 55.0
        
        # 知识点结构清晰度
        if len(knowledge_points) >= 5:
            score += 10
        elif len(knowledge_points) >= 3:
            score += 6
        elif len(knowledge_points) >= 1:
            score += 3
        
        # 知识点类型多样性
        point_types = set()
        for kp in knowledge_points:
            if isinstance(kp, dict):
                point_types.add(kp.get('type', ''))
        if len(point_types) >= 4:
            score += 10
        elif len(point_types) >= 3:
            score += 7
        elif len(point_types) >= 2:
            score += 4
        
        # 教学环节完整性（导入-讲解-练习-总结）
        stage_keywords = ['首先', '开始', '导入', '回顾', '复习', '接下来', '然后', '其次', '最后', '总结', '小结', '作业']
        stage_count = 0
        for seg in speech_segments:
            text = seg.get('text', '')
            for kw in stage_keywords:
                if kw in text:
                    stage_count += 1
                    break
        
        if stage_count >= 6:
            score += 10
        elif stage_count >= 4:
            score += 7
        elif stage_count >= 2:
            score += 4
        
        # 教学节奏（动作变化频率）
        if teacher_actions:
            action_count = len(teacher_actions)
            if action_count >= 8:
                score += 10
            elif action_count >= 5:
                score += 7
            elif action_count >= 3:
                score += 4
        
        # 时间分配合理性
        if speech_segments:
            total_duration = sum(s.get('duration', 0) for s in speech_segments)
            if total_duration > 0:
                # 检查是否有过长的单一讲解
                max_duration = max(s.get('duration', 0) for s in speech_segments)
                ratio = max_duration / total_duration
                if ratio < 0.3:
                    score += 5  # 时间分配均匀
                elif ratio < 0.5:
                    score += 3
                else:
                    score += 1
        
        return min(score, 100)
    
    def _generate_strengths(self, knowledge: float, interaction: float, expression: float,
                           management: float, structure: float) -> List[str]:
        # 生成优势
        strengths = []
        scores = {
            '知识掌握': knowledge,
            '互动参与': interaction,
            '表达清晰': expression,
            '课堂管理': management,
            '教学结构': structure,
        }
        
        # 找出得分最高的维度
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        for name, score in sorted_scores:
            if score >= 85:
                if name == '知识掌握':
                    strengths.append('知识点讲解全面深入，内容丰富详实')
                elif name == '互动参与':
                    strengths.append('课堂互动活跃，学生参与度高')
                elif name == '表达清晰':
                    strengths.append('语言表达清晰流畅，语速适中')
                elif name == '课堂管理':
                    strengths.append('课堂管理有序，教学节奏把控良好')
                elif name == '教学结构':
                    strengths.append('教学结构完整，环节设计合理')
            elif score >= 75:
                if name == '知识掌握':
                    strengths.append('知识点覆盖较全面，讲解清晰')
                elif name == '互动参与':
                    strengths.append('课堂互动较多，学生参与较好')
                elif name == '表达清晰':
                    strengths.append('语言表达较为清晰，语速基本适中')
                elif name == '课堂管理':
                    strengths.append('课堂管理较为有序')
                elif name == '教学结构':
                    strengths.append('教学结构较为完整')
        
        if not strengths:
            strengths.append('教学态度认真，准备充分')
        
        return strengths[:4]
    
    def _generate_weaknesses(self, knowledge: float, interaction: float, expression: float,
                            management: float, structure: float) -> List[str]:
        # 生成不足
        weaknesses = []
        scores = {
            '知识掌握': knowledge,
            '互动参与': interaction,
            '表达清晰': expression,
            '课堂管理': management,
            '教学结构': structure,
        }
        
        # 找出得分最低的维度
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        
        for name, score in sorted_scores:
            if score < 60:
                if name == '知识掌握':
                    weaknesses.append('知识点讲解不够深入，内容略显单薄')
                elif name == '互动参与':
                    weaknesses.append('课堂互动不足，学生参与度较低')
                elif name == '表达清晰':
                    weaknesses.append('语言表达不够清晰，语速可能过快或过慢')
                elif name == '课堂管理':
                    weaknesses.append('课堂管理有待加强，节奏把控不够好')
                elif name == '教学结构':
                    weaknesses.append('教学结构不够完整，环节设计有待优化')
            elif score < 70:
                if name == '知识掌握':
                    weaknesses.append('知识点覆盖可以更全面一些')
                elif name == '互动参与':
                    weaknesses.append('课堂互动可以更加丰富多样')
                elif name == '表达清晰':
                    weaknesses.append('语言表达可以更加清晰流畅')
                elif name == '课堂管理':
                    weaknesses.append('课堂管理还有提升空间')
                elif name == '教学结构':
                    weaknesses.append('教学结构可以更加完整')
        
        return weaknesses[:3]
    
    def _generate_suggestions(self, knowledge: float, interaction: float, expression: float,
                             management: float, structure: float) -> List[str]:
        # 生成改进建议
        suggestions = []
        scores = {
            'knowledge': knowledge,
            'interaction': interaction,
            'expression': expression,
            'management': management,
            'structure': structure,
        }
        
        # 针对低分维度给出建议
        if scores['knowledge'] < 70:
            suggestions.append('建议增加知识点的深度和广度，多结合实例进行讲解')
        if scores['interaction'] < 70:
            suggestions.append('建议增加课堂互动环节，多提问、多组织小组讨论')
        if scores['expression'] < 70:
            suggestions.append('建议注意语速控制，保持适中节奏，重要内容适当放慢')
        if scores['management'] < 70:
            suggestions.append('建议加强课堂管理，合理分配各环节时间')
        if scores['structure'] < 70:
            suggestions.append('建议优化教学结构，完善导入、讲解、练习、总结各环节')
        
        # 通用建议
        suggestions.append('建议课后收集学生反馈，持续改进教学方法')
        suggestions.append('建议多观摩优秀教师课堂，学习先进教学经验')
        
        return suggestions[:5]
    
    def _get_grade(self, score: float) -> str:
        # 根据分数获取等级
        if score >= 90:
            return '优秀'
        elif score >= 80:
            return '良好'
        elif score >= 70:
            return '中等'
        elif score >= 60:
            return '及格'
        else:
            return '待提高'