# 教学评价 Prompt 模板

class TeachingEvaluationPrompt:
    # 教学评价提示词模板
    
    # 系统提示词
    SYSTEM_PROMPT = """你是一位专业的教学评价专家，拥有20年以上的教育经验。
你的任务是根据课堂视频分析和语音分析的数据，对教师的教学质量进行全面、客观、专业的评价。

请遵循以下评价原则：
1. 客观公正：基于数据进行评价，不加入主观臆断
2. 全面系统：从多个维度进行综合评价
3. 具体可操作：给出具体的改进建议，而非空泛的评价
4. 鼓励为主：肯定优点的同时，建设性地指出不足
5. 因材施教：考虑课程类型和学生特点进行评价

评价维度包括：
- 知识掌握度（25%）：知识点的准确性、深度、广度
- 互动参与度（20%）：课堂互动频率、质量、学生参与程度
- 表达清晰度（20%）：语言表达、语速、逻辑清晰度
- 课堂管理（15%）：课堂秩序、时间管理、节奏把控
- 教学结构（20%）：教学环节完整性、内容组织、教学设计

请以JSON格式输出评价结果，包含以下字段：
- overall_score: 总分（0-100）
- knowledge_score: 知识掌握度得分
- interaction_score: 互动参与度得分
- expression_score: 表达清晰度得分
- classroom_management_score: 课堂管理得分
- teaching_structure_score: 教学结构得分
- grade: 等级（优秀/良好/中等/及格/待提高）
- strengths: 优势列表（3-5条）
- weaknesses: 不足列表（2-3条）
- suggestions: 改进建议列表（3-5条）
"""

    # 用户提示词模板
    USER_PROMPT_TEMPLATE = """请根据以下课堂数据，对教师的教学质量进行评价。

【教师信息】
- 教师角色：{teacher_role}
- 课程类型：{course_type}
- 学生年龄：{student_age}
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
- 语音片段：{speech_segments}

请从知识掌握度、互动参与度、表达清晰度、课堂管理、教学结构五个维度进行全面评价，给出具体的分数和详细的分析建议。
"""

    # 简化版提示词（用于快速评价）
    SIMPLE_PROMPT_TEMPLATE = """请根据以下课堂数据，简要评价教师的教学质量。

课程类型：{course_type}
学生年龄：{student_age}
课堂目标：{class_goal}

主要知识点：{knowledge_points}
课堂互动情况：{student_interaction}
教师表达情况：{speaking_rate}

请给出：
1. 总体评分（0-100）
2. 三个主要优点
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
        # 填充默认值
        defaults = {
            'teacher_role': '教师',
            'course_type': '常规课程',
            'student_age': '12-15岁',
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
            'speech_segments': '无数据',
        }
        defaults.update(kwargs)
        return cls.USER_PROMPT_TEMPLATE.format(**defaults)
    
    @classmethod
    def get_simple_prompt(cls, **kwargs) -> str:
        # 获取简化版提示词
        defaults = {
            'course_type': '常规课程',
            'student_age': '12-15岁',
            'class_goal': '掌握本节课知识点',
            'knowledge_points': '无数据',
            'student_interaction': '无数据',
            'speaking_rate': '无数据',
        }
        defaults.update(kwargs)
        return cls.SIMPLE_PROMPT_TEMPLATE.format(**defaults)
    
    @classmethod
    def get_messages(cls, video_result: dict, speech_result: dict, 
                     teacher_role: str = '教师', course_type: str = '常规课程',
                     student_age: str = '12-15岁', class_goal: str = '掌握本节课知识点') -> list:
        # 获取完整的消息列表
        return [
            {
                'role': 'system',
                'content': cls.get_system_prompt()
            },
            {
                'role': 'user',
                'content': cls.get_user_prompt(
                    teacher_role=teacher_role,
                    course_type=course_type,
                    student_age=student_age,
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
                    speech_segments=str(speech_result.get('speech_segments', [])),
                )
            }
        ]