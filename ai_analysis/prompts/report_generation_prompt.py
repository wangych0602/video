# 报告生成 Prompt 模板

class ReportGenerationPrompt:
    # 报告生成提示词模板
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一位专业的教育分析师，拥有丰富的课堂观察和教学评价经验。
你的任务是根据课堂视频分析、语音分析和教学评价的数据，生成一份专业、全面、结构化的课堂分析报告。

请遵循以下原则：
1. 客观专业：基于数据进行分析，不加入主观臆断
2. 结构清晰：按照标准报告结构组织内容
3. 具体详实：给出具体的数据和例子，而非空泛的评价
4. 建设性：以鼓励和改进为导向，给出可操作的建议
5. 多视角：从教师、学生、学校多个视角进行分析

报告结构：
1. 课堂概览 - 基本信息、总体评价
2. 教学分析 - 教师教学行为、表达、知识传授
3. 互动分析 - 师生互动、学生参与
4. 课堂管理 - 时间管理、秩序、节奏
5. 优势总结 - 本节课的主要亮点
6. 改进建议 - 具体可操作的改进建议

请以JSON格式输出，包含以下字段：
- title: 报告标题
- summary: 课堂总结（200字左右）
- strengths: 优势列表（3-5条）
- weaknesses: 不足列表（2-3条）
- suggestions: 改进建议列表（3-5条）
- scores: 各维度评分（包含knowledge、interaction、expression、classroom_management、teaching_structure）
- overall_score: 总分
- grade: 等级
- teacher_report: 教师视角报告
- school_report: 学校视角报告
"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """请根据以下课堂数据，生成一份专业的课堂分析报告。

【课堂基本信息】
- 课程类型：{course_type}
- 学生年龄：{student_age}
- 课堂时长：{duration}
- 课堂目标：{class_goal}

【视频分析结果】
- 场景分析：{scene_analysis}
- 教师动作：{teacher_actions}
- PPT内容：{ppt_content}
- 黑板内容：{blackboard_content}
- 学生互动：{student_interaction}
- 教室环境：{classroom_environment}

【语音分析结果】
- 课堂文字稿：{transcript}
- 关键词：{keywords}
- 知识点：{knowledge_points}
- 语速分析：{speaking_rate}

【教学评价结果】
- 总分：{overall_score}
- 等级：{grade}
- 知识掌握度：{knowledge_score}
- 互动参与度：{interaction_score}
- 表达清晰度：{expression_score}
- 课堂管理：{classroom_management_score}
- 教学结构：{teaching_structure_score}

请生成一份完整的课堂分析报告，包含课堂概览、教学分析、互动分析、课堂管理、优势总结和改进建议。
"""

    # 简化版提示词
    SIMPLE_PROMPT_TEMPLATE = """请根据以下课堂数据，生成一份简要的课堂分析报告。

课程类型：{course_type}
学生年龄：{student_age}
课堂时长：{duration}

主要知识点：{knowledge_points}
教学评分：{overall_score}分（{grade}）

请给出：
1. 课堂总结（100字左右）
2. 三个主要优势
3. 两个主要不足
4. 三条改进建议

以JSON格式输出。
"""

    @classmethod
    def get_system_prompt(cls) -> str:
        # 获取系统提示词
        return cls.SYSTEM_PROMPT
    
    @classmethod
    def get_user_prompt(cls, **kwargs) -> str:
        # 获取用户提示词
        defaults = {
            'course_type': '常规课程',
            'student_age': '12-15岁',
            'duration': '45分钟',
            'class_goal': '掌握本节课知识点',
            'scene_analysis': '无数据',
            'teacher_actions': '无数据',
            'ppt_content': '无数据',
            'blackboard_content': '无数据',
            'student_interaction': '无数据',
            'classroom_environment': '无数据',
            'transcript': '无数据',
            'keywords': '无数据',
            'knowledge_points': '无数据',
            'speaking_rate': '无数据',
            'overall_score': 0,
            'grade': 'N/A',
            'knowledge_score': 0,
            'interaction_score': 0,
            'expression_score': 0,
            'classroom_management_score': 0,
            'teaching_structure_score': 0,
        }
        defaults.update(kwargs)
        return cls.USER_PROMPT_TEMPLATE.format(**defaults)
    
    @classmethod
    def get_simple_prompt(cls, **kwargs) -> str:
        # 获取简化版提示词
        defaults = {
            'course_type': '常规课程',
            'student_age': '12-15岁',
            'duration': '45分钟',
            'knowledge_points': '无数据',
            'overall_score': 0,
            'grade': 'N/A',
        }
        defaults.update(kwargs)
        return cls.SIMPLE_PROMPT_TEMPLATE.format(**defaults)
    
    @classmethod
    def get_messages(cls, video_result: dict, speech_result: dict, 
                     evaluation_result: dict,
                     course_type: str = '常规课程',
                     student_age: str = '12-15岁',
                     class_goal: str = '掌握本节课知识点') -> list:
        # 获取完整的消息列表
        return [
            {
                'role': 'system',
                'content': cls.get_system_prompt()
            },
            {
                'role': 'user',
                'content': cls.get_user_prompt(
                    course_type=course_type,
                    student_age=student_age,
                    duration=str(video_result.get('video_info', {}).get('duration', '45分钟')),
                    class_goal=class_goal,
                    scene_analysis=str(video_result.get('scene_analysis', {})),
                    teacher_actions=str(video_result.get('teacher_actions', [])),
                    ppt_content=str(video_result.get('ppt_content', [])),
                    blackboard_content=str(video_result.get('blackboard_content', [])),
                    student_interaction=str(video_result.get('student_interaction', {})),
                    classroom_environment=str(video_result.get('classroom_environment', {})),
                    transcript=speech_result.get('transcript', ''),
                    keywords=str(speech_result.get('keywords', [])),
                    knowledge_points=str(speech_result.get('knowledge_points', [])),
                    speaking_rate=str(speech_result.get('speaking_rate', {})),
                    overall_score=evaluation_result.get('overall_score', 0),
                    grade=evaluation_result.get('grade', 'N/A'),
                    knowledge_score=evaluation_result.get('knowledge_score', 0),
                    interaction_score=evaluation_result.get('interaction_score', 0),
                    expression_score=evaluation_result.get('expression_score', 0),
                    classroom_management_score=evaluation_result.get('classroom_management_score', 0),
                    teaching_structure_score=evaluation_result.get('teaching_structure_score', 0),
                )
            }
        ]