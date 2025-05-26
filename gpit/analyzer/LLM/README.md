# 大语言模型推理系统
@SHAOYU: inference相关的代码，均有cursor中的claude 4 sonnet生成

这是一个基于模板化代码生成的大语言模型推理系统，支持多种推理引擎和灵活的配置管理。

## 特性

- **多引擎支持**: 支持VllmEngine和SglangEngine
- **模板化代码生成**: 根据engine类型自动生成推理代码
- **子进程隔离**: 使用子进程执行推理，避免内存污染
- **配置管理**: 支持预定义配置和自定义配置
- **灵活参数**: 支持运行时参数覆盖

## 文件结构

```
gpit/analyzer/LLM/
├── engines.py              # 推理引擎定义
├── inference.py            # 核心推理函数
├── inference_config.py     # 配置管理系统
├── example_usage.py        # 使用示例
└── README.md              # 说明文档
```

## 快速开始

### 1. 基本使用

```python
from engines import VllmEngine
from inference import infer

# 创建引擎实例
vllm_engine = VllmEngine()

# 使用预定义配置进行推理
result = infer(
    engine=vllm_engine,
    prompts="你好，请介绍一下你自己。",
    model="qwen_small"  # 使用预定义配置
)

print(f"推理结果: {result}")
```

### 2. 使用直接模型路径

```python
result = infer(
    engine=vllm_engine,
    prompts="什么是人工智能？",
    model="Qwen/Qwen3-1.7B",  # 直接指定模型路径
    temperature=0.7,
    max_tokens=200
)
```

### 3. 使用配置对象

```python
from inference_config import load_inference_config

# 加载预定义配置
config = load_inference_config("creative_mode")

result = infer(
    engine=vllm_engine,
    prompts="写一首关于春天的诗",
    model=config,
    max_tokens=150  # 覆盖配置中的参数
)
```

## 配置管理

### 预定义配置

系统提供以下预定义配置：

- `qwen_small`: 小型模型配置 (Qwen3-1.7B)
- `qwen_medium`: 中型模型配置 (Qwen3-4B)  
- `qwen_large`: 大型模型配置 (Qwen3-14B)
- `creative_mode`: 创意模式配置 (高温度)
- `precise_mode`: 精确模式配置 (低温度)

### 创建自定义配置

```python
from inference_config import config_manager, InferenceConfig

# 从模板创建新配置
custom_config = config_manager.create_config_from_template(
    "qwen_small",
    "my_config",
    temperature=0.8,
    max_tokens=1024
)

# 直接创建配置
config = InferenceConfig(
    model_path="path/to/model",
    temperature=0.7,
    max_tokens=2048,
    tensor_parallel_size=2
)

# 保存配置
config_manager.save_config("my_custom_config", config)
```

### 列出可用配置

```python
from inference_config import config_manager

configs = config_manager.list_configs()
for name, source in configs.items():
    config = config_manager.get_config(name)
    print(f"{name} ({source}): {config.model_path}")
```

## Engine类型

### VllmEngine

适用于VLLM框架的推理引擎，支持：
- 多GPU并行推理
- 高性能批处理
- 内存优化

### SglangEngine  

适用于SGLang框架的推理引擎，支持：
- 结构化生成
- 异步推理
- 对话模板

## 参数说明

### InferenceConfig参数

| 参数 | 类型 | 默认值 | 说明 |
|-----|------|--------|------|
| model_path | str | - | 模型路径 |
| temperature | float | 0.6 | 采样温度 |
| top_p | float | 0.95 | 核采样参数 |
| repetition_penalty | float | 1.0 | 重复惩罚 |
| max_tokens | int | 4096 | 最大生成长度 |
| dtype | str | "float16" | 数据类型 |
| tensor_parallel_size | int | 1 | 并行GPU数量 |
| gpu_memory_utilization | float | 0.7 | GPU内存使用率 |
| enable_chunked_prefill | bool | False | 分块预填充 |
| timeout | int | 300 | 超时时间(秒) |

## 高级用法

### 批量推理

```python
from engines import VllmEngine
from inference import infer

engine = VllmEngine()
prompts = [
    "什么是机器学习？",
    "解释深度学习的概念。",
    "Python的优势是什么？"
]

results = []
for prompt in prompts:
    result = infer(
        engine=engine,
        prompts=prompt,
        model="qwen_small",
        temperature=0.6
    )
    results.append(result)
```

### 错误处理

```python
try:
    result = infer(
        engine=vllm_engine,
        prompts="你的问题",
        model="nonexistent_config"
    )
except ValueError as e:
    print(f"配置错误: {e}")
except RuntimeError as e:
    print(f"推理错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

### 自定义超时

```python
result = infer(
    engine=vllm_engine,
    prompts="复杂的推理任务",
    model="qwen_large",
    timeout=600  # 10分钟超时
)
```

## 注意事项

1. **环境依赖**: 确保已安装相应的推理框架 (vllm/sglang)
2. **GPU内存**: 根据模型大小调整`gpu_memory_utilization`参数
3. **超时设置**: 对于大模型或长文本，适当增加timeout值
4. **并行推理**: 多GPU推理时需要调整`tensor_parallel_size`
5. **临时文件**: 系统会自动清理临时推理文件

## 示例运行

运行示例代码：

```bash
# 运行基本示例
python inference.py

# 运行完整示例
python example_usage.py

# 运行配置管理示例
python inference_config.py
```

## 故障排除

### 常见问题

1. **模型加载失败**: 检查模型路径是否正确
2. **GPU内存不足**: 减少`gpu_memory_utilization`或`tensor_parallel_size`
3. **推理超时**: 增加timeout参数
4. **依赖缺失**: 确保安装了相应的推理框架

### 调试模式

如需调试生成的推理代码，可以在临时文件删除前查看：

```python
# 在inference.py中临时注释掉文件删除行
# os.unlink(temp_file_path)
```

## 扩展开发

### 添加新的Engine

1. 继承`Engine`基类
2. 实现必要的抽象方法
3. 在`generate_inference_code`中添加相应逻辑

### 添加新的配置类型

1. 在`inference_config.py`中扩展`InferenceConfig`
2. 更新`ConfigManager`的预定义配置
3. 测试新配置的兼容性 