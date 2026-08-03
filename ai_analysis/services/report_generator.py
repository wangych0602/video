import os
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger('ai_analysis.report_generator')


class ReportGenerator:
    # 报告生成服务
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.media_root = self.config.get('media_root', 'media')
        self.reports_dir = os.path.join(self.media_root, 'reports')
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_report(self, video_result: Dict, speech_result: Dict, 
                        evaluation_result: Dict, task_id: int = None) -> Dict:
        # 生成完整报告
        try:
            # 1. 生成课堂总结
            summary = self._generate_summary(video_result, speech_result, evaluation_result)
            
            # 2. 生成教师报告
            teacher_report = self._generate_teacher_report(
                video_result, speech_result, evaluation_result
            )
            
            # 3. 生成学校报告
            school_report = self._generate_school_report(
                video_result, speech_result, evaluation_result
            )
            
            # 4. 生成HTML内容
            html_content = self._generate_html(
                summary, teacher_report, school_report, 
                video_result, speech_result, evaluation_result
            )
            
            # 5. 生成PDF（可选）
            pdf_path = None
            try:
                pdf_path = self._generate_pdf(
                    summary, teacher_report, school_report,
                    video_result, speech_result, evaluation_result,
                    task_id
                )
            except Exception as e:
                logger.warning(f'PDF generation failed: {e}')
            
            return {
                'success': True,
                'title': summary.get('title', '课堂分析报告'),
                'summary': summary,
                'teacher_report': teacher_report,
                'school_report': school_report,
                'html_content': html_content,
                'pdf_path': pdf_path,
            }
            
        except Exception as e:
            logger.error(f'Report generation failed: {e}')
            return {
                'success': False,
                'error': str(e),
                'title': '',
                'summary': {},
                'teacher_report': {},
                'school_report': {},
                'html_content': '',
                'pdf_path': None,
            }
    
    def _generate_summary(self, video_result: Dict, speech_result: Dict, 
                          evaluation_result: Dict) -> Dict:
        # 生成课堂总结
        # 提取基本信息
        video_info = video_result.get('video_info', {})
        duration = video_info.get('duration', 0)
        duration_str = self._format_duration(duration)
        
        # 提取关键词
        keywords = speech_result.get('keywords', [])
        keyword_list = [k.get('word', k) if isinstance(k, dict) else k for k in keywords[:10]]
        
        # 提取知识点
        knowledge_points = speech_result.get('knowledge_points', [])
        kp_list = [kp.get('name', kp) if isinstance(kp, dict) else kp for kp in knowledge_points[:8]]
        
        # 提取评分
        overall_score = evaluation_result.get('overall_score', 0)
        grade = evaluation_result.get('grade', '')
        
        # 提取优势和不足
        strengths = evaluation_result.get('strengths', [])
        weaknesses = evaluation_result.get('weaknesses', [])
        suggestions = evaluation_result.get('suggestions', [])
        
        return {
            'title': '课堂分析报告',
            'duration': duration_str,
            'overall_score': overall_score,
            'grade': grade,
            'keywords': keyword_list,
            'knowledge_points': kp_list,
            'strengths': strengths[:3],
            'weaknesses': weaknesses[:2],
            'suggestions': suggestions[:3],
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    
    def _generate_teacher_report(self, video_result: Dict, speech_result: Dict,
                                  evaluation_result: Dict) -> Dict:
        # 生成教师报告
        # 教师动作分析
        teacher_actions = video_result.get('teacher_actions', [])
        action_types = set()
        for action in teacher_actions:
            if isinstance(action, dict):
                action_types.add(action.get('action', ''))
        
        # 表达分析
        speaking_rate = speech_result.get('speaking_rate', {})
        pace = speaking_rate.get('pace', 'normal')
        avg_cpm = speaking_rate.get('avg_chars_per_minute', 0)
        
        # 互动分析
        student_interaction = video_result.get('student_interaction', {})
        interaction_count = student_interaction.get('interaction_count', 0)
        engagement = student_interaction.get('engagement_level', 'medium')
        
        # 各维度评分
        scores = {
            'knowledge': evaluation_result.get('knowledge_score', 0),
            'interaction': evaluation_result.get('interaction_score', 0),
            'expression': evaluation_result.get('expression_score', 0),
            'classroom_management': evaluation_result.get('classroom_management_score', 0),
            'teaching_structure': evaluation_result.get('teaching_structure_score', 0),
        }
        
        # 优势和不足
        strengths = evaluation_result.get('strengths', [])
        weaknesses = evaluation_result.get('weaknesses', [])
        suggestions = evaluation_result.get('suggestions', [])
        
        return {
            'teacher_actions': {
                'total': len(teacher_actions),
                'types': list(action_types),
            },
            'expression': {
                'pace': pace,
                'avg_cpm': avg_cpm,
            },
            'interaction': {
                'count': interaction_count,
                'engagement': engagement,
            },
            'scores': scores,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
        }
    
    def _generate_school_report(self, video_result: Dict, speech_result: Dict,
                                 evaluation_result: Dict) -> Dict:
        # 生成学校报告
        # 教室环境
        classroom_env = video_result.get('classroom_environment', {})
        
        # 学生参与度
        student_interaction = video_result.get('student_interaction', {})
        engagement = student_interaction.get('engagement_level', 'medium')
        
        # 教学质量评估
        overall_score = evaluation_result.get('overall_score', 0)
        grade = evaluation_result.get('grade', '')
        
        # 知识点覆盖
        knowledge_points = speech_result.get('knowledge_points', [])
        kp_count = len(knowledge_points)
        
        # 课堂时长
        video_info = video_result.get('video_info', {})
        duration = video_info.get('duration', 0)
        
        return {
            'classroom_environment': classroom_env,
            'student_engagement': engagement,
            'teaching_quality': {
                'score': overall_score,
                'grade': grade,
            },
            'knowledge_coverage': {
                'count': kp_count,
                'points': [kp.get('name', kp) if isinstance(kp, dict) else kp for kp in knowledge_points[:5]],
            },
            'class_duration': self._format_duration(duration),
            'recommendation': self._get_school_recommendation(overall_score),
        }
    
    def _generate_html(self, summary: Dict, teacher_report: Dict, school_report: Dict,
                       video_result: Dict, speech_result: Dict, 
                       evaluation_result: Dict) -> str:
        # 生成HTML报告
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{summary.get('title', '课堂分析报告')}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f5f7fa; color: #303133; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 16px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 12px; }}
        .header .meta {{ opacity: 0.9; font-size: 14px; }}
        .score-card {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .score-overall {{ text-align: center; padding: 20px 0; }}
        .score-number {{ font-size: 64px; font-weight: bold; color: #67c23a; }}
        .score-grade {{ font-size: 24px; color: #606266; margin-top: 8px; }}
        .score-dimensions {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 16px; margin-top: 24px; }}
        .dimension {{ text-align: center; }}
        .dimension-score {{ font-size: 28px; font-weight: bold; color: #409eff; }}
        .dimension-label {{ font-size: 13px; color: #909399; margin-top: 4px; }}
        .section {{ background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
        .section-title {{ font-size: 18px; font-weight: 600; color: #303133; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #409eff; display: inline-block; }}
        .keywords {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .keyword {{ background: #ecf5ff; color: #409eff; padding: 6px 14px; border-radius: 16px; font-size: 14px; }}
        .list {{ list-style: none; }}
        .list li {{ padding: 8px 0; padding-left: 20px; position: relative; }}
        .list li::before {{ content: "•"; position: absolute; left: 0; color: #409eff; font-weight: bold; }}
        .strengths li::before {{ color: #67c23a; }}
        .weaknesses li::before {{ color: #f56c6c; }}
        .suggestions li::before {{ color: #e6a23c; }}
        .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
        .footer {{ text-align: center; color: #909399; font-size: 13px; padding: 20px; }}
        @media (max-width: 768px) {{
            .score-dimensions {{ grid-template-columns: repeat(2, 1fr); }}
            .two-col {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{summary.get('title', '课堂分析报告')}</h1>
            <div class="meta">
                生成时间：{summary.get('generated_at', '')} | 
                课堂时长：{summary.get('duration', '')}
            </div>
        </div>
        
        <div class="score-card">
            <div class="score-overall">
                <div class="score-number">{summary.get('overall_score', 0)}</div>
                <div class="score-grade">{summary.get('grade', '')}</div>
            </div>
            <div class="score-dimensions">
                <div class="dimension">
                    <div class="dimension-score">{teacher_report.get('scores', {}).get('knowledge', 0)}</div>
                    <div class="dimension-label">知识掌握</div>
                </div>
                <div class="dimension">
                    <div class="dimension-score">{teacher_report.get('scores', {}).get('interaction', 0)}</div>
                    <div class="dimension-label">互动参与</div>
                </div>
                <div class="dimension">
                    <div class="dimension-score">{teacher_report.get('scores', {}).get('expression', 0)}</div>
                    <div class="dimension-label">表达清晰</div>
                </div>
                <div class="dimension">
                    <div class="dimension-score">{teacher_report.get('scores', {}).get('classroom_management', 0)}</div>
                    <div class="dimension-label">课堂管理</div>
                </div>
                <div class="dimension">
                    <div class="dimension-score">{teacher_report.get('scores', {}).get('teaching_structure', 0)}</div>
                    <div class="dimension-label">教学结构</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">关键词</div>
            <div class="keywords">
                {''.join(f'<span class="keyword">{kw}</span>' for kw in summary.get('keywords', []))}
            </div>
        </div>
        
        <div class="two-col">
            <div class="section">
                <div class="section-title">主要优势</div>
                <ul class="list strengths">
                    {''.join(f'<li>{s}</li>' for s in summary.get('strengths', []))}
                </ul>
            </div>
            <div class="section">
                <div class="section-title">待改进</div>
                <ul class="list weaknesses">
                    {''.join(f'<li>{w}</li>' for w in summary.get('weaknesses', []))}
                </ul>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">改进建议</div>
            <ul class="list suggestions">
                {''.join(f'<li>{s}</li>' for s in summary.get('suggestions', []))}
            </ul>
        </div>
        
        <div class="section">
            <div class="section-title">知识点覆盖</div>
            <div class="keywords">
                {''.join(f'<span class="keyword">{kp}</span>' for kp in summary.get('knowledge_points', []))}
            </div>
        </div>
        
        <div class="footer">
            本报告由AI课堂分析系统自动生成
        </div>
    </div>
</body>
</html>'''
        return html
    
    def _generate_pdf(self, summary: Dict, teacher_report: Dict, school_report: Dict,
                      video_result: Dict, speech_result: Dict, 
                      evaluation_result: Dict, task_id: int = None) -> str:
        # 生成PDF报告
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib.colors import HexColor
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib import colors
            
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'report_{task_id}_{timestamp}.pdf' if task_id else f'report_{timestamp}.pdf'
            filepath = os.path.join(self.reports_dir, filename)
            
            # 创建PDF文档
            doc = SimpleDocTemplate(filepath, pagesize=A4, 
                                    leftMargin=2*cm, rightMargin=2*cm,
                                    topMargin=2*cm, bottomMargin=2*cm)
            
            styles = getSampleStyleSheet()
            
            # 自定义样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#409eff'),
                spaceAfter=20,
                alignment=1,  # 居中
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=HexColor('#303133'),
                spaceBefore=15,
                spaceAfter=10,
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                leading=18,
                textColor=HexColor('#606266'),
            )
            
            score_style = ParagraphStyle(
                'ScoreStyle',
                parent=styles['Normal'],
                fontSize=48,
                textColor=HexColor('#67c23a'),
                alignment=1,
                spaceAfter=10,
            )
            
            # 构建内容
            story = []
            
            # 标题
            story.append(Paragraph(summary.get('title', '课堂分析报告'), title_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 基本信息
            info_text = f'生成时间：{summary.get("generated_at", "")} | 课堂时长：{summary.get("duration", "")}'
            story.append(Paragraph(info_text, ParagraphStyle('Info', parent=normal_style, alignment=1)))
            story.append(Spacer(1, 1*cm))
            
            # 总分
            overall_score = summary.get('overall_score', 0)
            grade = summary.get('grade', '')
            story.append(Paragraph(f'{overall_score} 分', score_style))
            story.append(Paragraph(f'等级：{grade}', ParagraphStyle('Grade', parent=normal_style, alignment=1, fontSize=14)))
            story.append(Spacer(1, 1*cm))
            
            # 各维度评分表格
            scores = teacher_report.get('scores', {})
            score_data = [
                ['维度', '得分'],
                ['知识掌握度', str(scores.get('knowledge', 0))],
                ['互动参与度', str(scores.get('interaction', 0))],
                ['表达清晰度', str(scores.get('expression', 0))],
                ['课堂管理', str(scores.get('classroom_management', 0))],
                ['教学结构', str(scores.get('teaching_structure', 0))],
            ]
            score_table = Table(score_data, colWidths=[8*cm, 4*cm])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#409eff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('FONTSIZE', (0, 1), (-1, -1), 11),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            story.append(score_table)
            story.append(Spacer(1, 1*cm))
            
            # 关键词
            story.append(Paragraph('关键词', heading_style))
            keywords = ', '.join(summary.get('keywords', []))
            story.append(Paragraph(keywords, normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 主要优势
            story.append(Paragraph('主要优势', heading_style))
            for s in summary.get('strengths', []):
                story.append(Paragraph(f'• {s}', normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 待改进
            story.append(Paragraph('待改进', heading_style))
            for w in summary.get('weaknesses', []):
                story.append(Paragraph(f'• {w}', normal_style))
            story.append(Spacer(1, 0.5*cm))
            
            # 改进建议
            story.append(Paragraph('改进建议', heading_style))
            for i, s in enumerate(summary.get('suggestions', []), 1):
                story.append(Paragraph(f'{i}. {s}', normal_style))
            
            # 生成PDF
            doc.build(story)
            
            return filepath
            
        except ImportError:
            logger.warning('reportlab not installed, skipping PDF generation')
            return None
        except Exception as e:
            logger.error(f'PDF generation error: {e}')
            raise
    
    def _format_duration(self, seconds: float) -> str:
        # 格式化时长
        if not seconds:
            return '00:00'
        seconds = int(float(seconds))
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f'{hours:02d}:{minutes:02d}:{secs:02d}'
        return f'{minutes:02d}:{secs:02d}'
    
    def _get_school_recommendation(self, score: float) -> str:
        # 获取学校推荐
        if score >= 90:
            return '优秀课堂，建议作为示范课推广'
        elif score >= 80:
            return '良好课堂，建议继续保持并优化细节'
        elif score >= 70:
            return '中等课堂，建议针对性改进'
        elif score >= 60:
            return '及格课堂，建议重点提升'
        else:
            return '待提高课堂，建议全面改进'