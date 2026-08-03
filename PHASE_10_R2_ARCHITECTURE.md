# Phase 10.R.2 - 多AI模型Provider架构升级

## 概述

本次重构将原有的单一 AI Provider 架构升级为多 Provider 架构，支持 7 种主流 AI 模型提供商，实现统一的接口抽象和灵活的配置管理。

## 一、数据库变化

### AIModelConfig 模型变更

#### 新增字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `model_type` | CharField | 模型类型（chat/vision/speech_to_text/embedding/multimodal） |
| `description` | TextField | 模型描述 |
| `timeout` | PositiveIntegerField | 超时时间（秒），默认 60 |
| `status` | BooleanField | 状态，默认 False |

#### 修改字段

| 字段名 | 修改内容 |
|--------|----------|
| `api_key` | 最大长度从 200 增加到 500 |
| `provider` | 更新 choices，新增 qwen, deepseek, glm, ollama |

#### Provider 类型（7种）

1. **openai** - OpenAI (GPT-4o, GPT-4V, Whisper)
2. **gemini** - Google Gemini (Gemini 1.5 Pro)
3. **claude** - Anthropic Claude (Claude 3.5 Sonnet)
4. **qwen** - 阿里通义千问 (Qwen-Plus, Qwen-VL-Plus)
5. **deepseek** - DeepSeek (DeepSeek Chat)
6. **glm** - 智谱 GLM (GLM-4, GLM-4V)
7. **ollama** - Ollama 本地模型 (Llama 3, etc.)

#### 模型类型（5种）

1. **chat** - 文本对话
2. **vision** - 视觉分析
3. **speech_to_text** - 语音识别
4. **embedding** - 向量嵌入
5. **multimodal** - 多模态

## 二、新增文件

### Provider 架构文件

```
ai_analysis/providers/
├── __init__.py              # 模块初始化
├── base.py                  # BaseProvider 基类
├── factory.py               # ProviderFactory 工厂类
├── openai_provider.py       # OpenAI Provider
├── gemini_provider.py       # Google Gemini Provider
├── claude_provider.py       # Anthropic Claude Provider
├── qwen_provider.py         # 阿里通义千问 Provider
├── deepseek_provider.py     # DeepSeek Provider
├── glm_provider.py          # 智谱 GLM Provider
└── ollama_provider.py       # Ollama 本地模型 Provider
```

### 核心数据类

#### ProviderConfig
```python
@dataclass
class ProviderConfig:
    api_key: str = ""
    api_base: str = ""
    model_name: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    extra_params: Dict[str, Any] = field(default_factory=dict)
```

#### ChatMessage
```python
@dataclass
class ChatMessage:
    role: str  # user / assistant / system
    content: str
    images: List[str] = field(default_factory=list)
```

#### ProviderResponse
```python
@dataclass
class ProviderResponse:
    success: bool
    content: str = ""
    usage: Dict[str, int] = field(default_factory=dict)
    error: str = ""
    raw_response: Any = None
```

## 三、Provider 能力矩阵

| Provider | 对话(chat) | 视觉(vision) | 语音(speech_to_text) | 向量(embedding) | 默认模型 |
|----------|-----------|-------------|---------------------|----------------|----------|
| OpenAI | ✅ | ✅ | ✅ | ✅ | gpt-4o |
| Gemini | ✅ | ✅ | ✅ | ✅ | gemini-1.5-pro |
| Claude | ✅ | ✅ | ❌ | ❌ | claude-3-5-sonnet |
| Qwen | ✅ | ✅ | ❌ | ✅ | qwen-plus |
| DeepSeek | ✅ | ❌ | ❌ | ✅ | deepseek-chat |
| GLM | ✅ | ✅ | ❌ | ✅ | glm-4 |
| Ollama | ✅ | ✅* | ❌ | ✅ | llama3 |

*注：Ollama 的视觉能力取决于具体模型

## 四、调用流程

### 1. 工厂模式调用

```python
from ai_analysis.providers import ProviderFactory

# 获取视觉分析 Provider
vision_provider = ProviderFactory.get_vision_provider()

# 分析图片
response = vision_provider.analyze_image(
    image_path="/path/to/image.jpg",
    prompt="请分析这张图片"
)

if response.success:
    print(response.content)
    print(response.usage)
```

### 2. 直接创建 Provider

```python
from ai_analysis.providers import ProviderFactory
from ai_analysis.providers.base import ProviderConfig

config = ProviderConfig(
    api_key="your-api-key",
    model_name="gpt-4o",
    max_tokens=2048,
    temperature=0.7
)

provider = ProviderFactory.get_provider("openai", config)
response = provider.chat_completion("Hello!")
```

### 3. Agent 调用流程（兼容层）

```
VideoAnalysisAgent
    ↓
ai_provider.get_active_provider()  [兼容层]
    ↓
ProviderFactory.get_chat_provider()  [新架构]
    ↓
具体 Provider (OpenAI/Gemini/Claude/...)
    ↓
ProviderResponse (统一响应格式)
```

### 4. 配置优先级

1. 查询所有 `is_active=True` 的配置
2. 按 `priority` 排序（数字越小优先级越高）
3. 检查每个 Provider 的能力是否匹配需求
4. 返回第一个匹配的 Provider

## 五、Admin 后台功能

### 新增功能

1. **能力展示** - 列表中显示每个模型支持的能力（💬对话 👁️视觉 🎤语音 🔢向量）
2. **批量操作**
   - 测试连接 - 测试选中的配置是否能正常连接
   - 启用选中的配置
   - 禁用选中的配置
3. **快速编辑** - 列表中可直接编辑 is_active 和 priority
4. **模型类型筛选** - 按模型类型筛选配置

### 字段分组

1. **基本配置** - provider, model_type, model_name, description, is_active, priority
2. **API配置** - api_key, api_base
3. **模型参数** - max_tokens, temperature, timeout
4. **状态** - status
5. **时间信息** - created_time, updated_time

## 六、向后兼容性

### 兼容层设计

为了保证现有代码不修改即可工作，提供了两个兼容层：

#### 1. ai_provider.py 兼容层
- `get_provider(provider_type, config)` - 兼容旧接口
- `get_active_provider()` - 兼容旧接口
- `CompatProvider` - 包装新 Provider，提供旧接口

#### 2. speech_provider.py 兼容层
- `get_speech_provider(provider_type, config)` - 兼容旧接口
- `get_active_speech_provider()` - 兼容旧接口
- `CompatSpeechProvider` - 包装新 Provider，提供旧接口

### 迁移路径

1. **阶段 1（当前）** - 所有代码通过兼容层调用，无需修改
2. **阶段 2** - 逐步修改 Agent，直接使用 ProviderFactory
3. **阶段 3** - 移除兼容层，完全使用新架构

## 七、测试结果

### 1. 后端启动状态
- ✅ Django 5.2 正常启动
- ✅ 无 DRF 兼容性错误
- ✅ 所有 URL 正常注册

### 2. 健康检查 API
```json
{
  "ffmpeg_status": "ok",
  "ffprobe_status": "ok",
  "redis_status": "ok",
  "celery_status": "unknown",
  "api_key_status": "not_configured",
  "overall_status": "degraded"
}
```

### 3. 数据库迁移
- ✅ 迁移文件创建成功（0006_aimodelconfig_*.py）
- ✅ 新增字段：model_type, description, timeout, status
- ✅ 修改字段：api_key(长度), provider(choices)

### 4. Provider 实例化测试
- ✅ OpenAIProvider - 正常实例化
- ✅ GeminiProvider - 正常实例化
- ✅ ClaudeProvider - 正常实例化
- ✅ QwenProvider - 正常实例化
- ✅ DeepSeekProvider - 正常实例化
- ✅ GLMProvider - 正常实例化
- ✅ OllamaProvider - 正常实例化
- ✅ ProviderFactory - 正常工作

### 5. 兼容层测试
- ✅ ai_provider.get_active_provider() - 正常工作
- ✅ speech_provider.get_active_speech_provider() - 正常工作
- ✅ 旧接口返回格式兼容

## 八、配置示例

### OpenAI 配置
```python
AIModelConfig.objects.create(
    provider="openai",
    model_type="multimodal",
    model_name="gpt-4o",
    api_key="sk-xxx",
    api_base="https://api.openai.com/v1",
    is_active=True,
    priority=1,
    max_tokens=4096,
    temperature=0.7,
    description="OpenAI GPT-4o 多模态模型"
)
```

### 本地 Ollama 配置
```python
AIModelConfig.objects.create(
    provider="ollama",
    model_type="chat",
    model_name="llama3",
    api_base="http://host.docker.internal:11434/api",
    is_active=True,
    priority=10,
    description="本地 Llama 3 模型"
)
```

## 九、下一步计划

### P0 - 核心功能
1. 完善各 Provider 的错误处理和重试机制
2. 添加 Token 用量统计和成本计算
3. 实现 Provider 自动降级（主 Provider 失败时自动切换）

### P1 - 体验优化
4. 添加 Provider 性能监控（响应时间、成功率）
5. 实现流式输出支持
6. 添加批量处理能力

### P2 - 高级功能
7. 支持 Fine-tuning 模型
8. 添加 Function Calling 支持
9. 实现多模态融合分析

## 十、文件清单

### 新增文件
- `ai_analysis/providers/__init__.py`
- `ai_analysis/providers/base.py`
- `ai_analysis/providers/factory.py`
- `ai_analysis/providers/openai_provider.py`
- `ai_analysis/providers/gemini_provider.py`
- `ai_analysis/providers/claude_provider.py`
- `ai_analysis/providers/qwen_provider.py`
- `ai_analysis/providers/deepseek_provider.py`
- `ai_analysis/providers/glm_provider.py`
- `ai_analysis/providers/ollama_provider.py`
- `ai_analysis/migrations/0006_aimodelconfig_description_aimodelconfig_model_type_and_more.py`

### 修改文件
- `ai_analysis/models.py` - 更新 AIModelConfig 模型
- `ai_analysis/admin.py` - 更新 Admin 配置
- `ai_analysis/services/ai_provider.py` - 改为兼容层
- `ai_analysis/services/speech_provider.py` - 改为兼容层

---

**完成时间**：2026-08-04
**版本**：Phase 10.R.2 v1.0
**状态**：✅ 已完成
