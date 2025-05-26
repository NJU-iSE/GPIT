# Large Language Model Inference System
@SHAOYU: inference相关的代码，均有cursor中的claude 4 sonnet生成

This is a large language model inference system based on templated code generation, supporting multiple inference engines and flexible configuration management.

## Features

- **Multiple Engine Support**: Supports VllmEngine and SglangEngine
- **Templated Code Generation**: Automatically generates inference code based on engine type
- **Subprocess Isolation**: Uses subprocess to execute inference, avoiding memory pollution
- **Configuration Management**: Supports predefined configurations and custom configurations
- **Flexible Parameters**: Supports runtime parameter override

## File Structure

```
gpit/analyzer/LLM/
├── engines.py              # Inference engine definitions
├── inference.py            # Core inference functions
├── inference_config.py     # Configuration management system
├── example_usage.py        # Usage examples
└── README.md              # Documentation
```

## Quick Start

### 1. Basic Usage

```python
from engines import VllmEngine
from inference import infer

# Create engine instance
vllm_engine = VllmEngine()

# Use predefined configuration for inference
result = infer(
    engine=vllm_engine,
    prompts="Hello, please introduce yourself.",
    model="qwen_small"  # Use predefined configuration
)

print(f"Inference result: {result}")
```

### 2. Using Direct Model Path

```python
result = infer(
    engine=vllm_engine,
    prompts="What is artificial intelligence?",
    model="Qwen/Qwen3-1.7B",  # Directly specify model path
    temperature=0.7,
    max_tokens=200
)
```

### 3. Using Configuration Object

```python
from inference_config import load_inference_config

# Load predefined configuration
config = load_inference_config("creative_mode")

result = infer(
    engine=vllm_engine,
    prompts="Write a poem about spring",
    model=config,
    max_tokens=150  # Override parameters in configuration
)
```

## Configuration Management

### Predefined Configurations

The system provides the following predefined configurations:

- `qwen_small`: Small model configuration (Qwen3-1.7B)
- `qwen_medium`: Medium model configuration (Qwen3-4B)
- `qwen_large`: Large model configuration (Qwen3-14B)
- `creative_mode`: Creative mode configuration (high temperature)
- `precise_mode`: Precise mode configuration (low temperature)

### Creating Custom Configurations

```python
from inference_config import config_manager, InferenceConfig

# Create new configuration from template
custom_config = config_manager.create_config_from_template(
    "qwen_small",
    "my_config",
    temperature=0.8,
    max_tokens=1024
)

# Create configuration directly
config = InferenceConfig(
    model_path="path/to/model",
    temperature=0.7,
    max_tokens=2048,
    tensor_parallel_size=2
)

# Save configuration
config_manager.save_config("my_custom_config", config)
```

### List Available Configurations

```python
from inference_config import config_manager

configs = config_manager.list_configs()
for name, source in configs.items():
    config = config_manager.get_config(name)
    print(f"{name} ({source}): {config.model_path}")
```

## Engine Types

### VllmEngine

Inference engine for VLLM framework, supports:
- Multi-GPU parallel inference
- High-performance batch processing
- Memory optimization

### SglangEngine

Inference engine for SGLang framework, supports:
- Structured generation
- Asynchronous inference
- Dialogue templates

## Parameter Description

### InferenceConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| model_path | str | - | Model path |
| temperature | float | 0.6 | Sampling temperature |
| top_p | float | 0.95 | Nucleus sampling parameter |
| repetition_penalty | float | 1.0 | Repetition penalty |
| max_tokens | int | 4096 | Maximum generation length |
| dtype | str | "float16" | Data type |
| tensor_parallel_size | int | 1 | Number of parallel GPUs |
| gpu_memory_utilization | float | 0.7 | GPU memory utilization |
| enable_chunked_prefill | bool | False | Chunked prefill |
| timeout | int | 300 | Timeout in seconds |

## Advanced Usage

### Batch Inference

```python
from engines import VllmEngine
from inference import infer

engine = VllmEngine()
prompts = [
    "What is machine learning?",
    "Explain the concepts of deep learning.",
    "What are the advantages of Python?"
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

### Error Handling

```python
try:
    result = infer(
        engine=vllm_engine,
        prompts="Your question",
        model="nonexistent_config"
    )
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Inference error: {e}")
except Exception as e:
    print(f"Other error: {e}")
```

### Custom Timeout

```python
result = infer(
    engine=vllm_engine,
    prompts="Complex inference task",
    model="qwen_large",
    timeout=600  # 10 minutes timeout
)
```

## Notes

1. **Environment Dependencies**: Ensure the corresponding inference frameworks (vllm/sglang) are installed
2. **GPU Memory**: Adjust the `gpu_memory_utilization` parameter according to model size
3. **Timeout Settings**: Increase timeout value appropriately for large models or long text
4. **Parallel Inference**: Adjust `tensor_parallel_size` for multi-GPU inference
5. **Temporary Files**: The system automatically cleans up temporary inference files

## Example Execution

Run example code:

```bash
# Run basic examples
python inference.py

# Run complete examples
python example_usage.py

# Run configuration management examples
python inference_config.py
```

## Troubleshooting

### Common Issues

1. **Model loading failure**: Check if model path is correct
2. **Insufficient GPU memory**: Reduce `gpu_memory_utilization` or `tensor_parallel_size`
3. **Inference timeout**: Increase timeout parameter
4. **Missing dependencies**: Ensure corresponding inference frameworks are installed

### Debug Mode

To debug generated inference code, you can temporarily comment out the file deletion line:

```python
# Temporarily comment out the file deletion line in inference.py
# os.unlink(temp_file_path)
```

## Extension Development

### Adding New Engine

1. Inherit from `Engine` base class
2. Implement necessary abstract methods
3. Add corresponding logic in `generate_inference_code`

### Adding New Configuration Types

1. Extend `InferenceConfig` in `inference_config.py`
2. Update predefined configurations in `ConfigManager`
3. Test compatibility of new configurations 