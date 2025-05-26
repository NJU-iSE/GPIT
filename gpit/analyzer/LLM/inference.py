from engines import VllmEngine, SglangEngine, Engine
from inference_config import InferenceConfig, load_inference_config
import subprocess
import tempfile
import os
import json
import re
from pathlib import Path
from typing import Union


def infer(engine: Engine, prompts: str, model: Union[str, InferenceConfig], **kwargs):
    """
    使用engine实例生成模板化代码，启动子进程进行推理并返回结果
    
    Args:
        engine: 实例化的Engine对象 (VllmEngine或SglangEngine)
        prompts: 输入的提示词
        model: 模型路径/名称或InferenceConfig对象，或配置名称
        **kwargs: 其他推理参数，会覆盖配置中的参数
    
    Returns:
        str: 推理生成的文本结果
    """
    
    # 处理配置参数
    if isinstance(model, InferenceConfig):
        config = model
        model_path = config.model_path
    elif isinstance(model, str):
        if model.startswith("/") or model.startswith("./") or "/" in model:
            # 如果是路径，创建默认配置
            config = InferenceConfig(model_path=model)
            model_path = model
        else:
            # 如果是配置名称，加载配置
            config = load_inference_config(model)
            model_path = config.model_path
    else:
        raise ValueError("model 参数必须是字符串(路径或配置名称)或InferenceConfig对象")
    
    # 用kwargs覆盖配置中的参数
    temperature = kwargs.get('temperature', config.temperature)
    top_p = kwargs.get('top_p', config.top_p)
    repetition_penalty = kwargs.get('repetition_penalty', config.repetition_penalty)
    max_tokens = kwargs.get('max_tokens', config.max_tokens)
    timeout = kwargs.get('timeout', config.timeout)
    
    # 生成完整的推理代码
    complete_code = generate_inference_code(
        engine, prompts, model_path, config,
        temperature, top_p, repetition_penalty, max_tokens
    )
    
    # 创建临时文件并写入代码
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(complete_code)
        temp_file_path = temp_file.name
    
    try:
        # 启动子进程执行代码
        result = subprocess.run(
            ['python', temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"推理过程出错: {result.stderr}")
        
        # 解析输出结果
        output = parse_inference_output(result.stdout)
        return output
        
    finally:
        # 清理临时文件
        os.unlink(temp_file_path)


def generate_inference_code(engine, prompts, model_path, config, temperature, top_p, repetition_penalty, max_tokens):
    """
    根据engine类型生成完整的推理代码
    """
    import_code = engine.import_engine
    
    if isinstance(engine, VllmEngine):
        # VllmEngine代码生成 - 使用配置中的参数
        model_loading_code = engine.load_model(
            model_path=model_path,
            dtype=config.dtype,
            tensor_parallel_size=config.tensor_parallel_size,
            gpu_memory_utilization=config.gpu_memory_utilization,
            enable_chunked_prefill=config.enable_chunked_prefill
        )
        sampling_params_code = engine.init_sampling_params(
            temperature, top_p, repetition_penalty, max_tokens
        )
        prompt_code = engine.init_prompt(prompts)
        output_code = engine.get_output(num=1)
        
        # 添加结果输出代码
        result_output_code = """
# 输出结果到标准输出，用于解析
print("INFERENCE_RESULT_START")
for result in output_list:
    print(result)
print("INFERENCE_RESULT_END")
        """
        
    elif isinstance(engine, SglangEngine):
        # SglangEngine代码生成
        model_loading_code = engine.load_model(model_path)
        sampling_params_code = engine.init_sampling_params(
            temperature, top_p, repetition_penalty, max_tokens
        )
        prompt_code = engine.init_prompt([prompts])
        output_code = engine.get_output_code("prompts", "sampling_params")
        
        # 添加结果输出代码
        result_output_code = """
# 输出结果到标准输出，用于解析
print("INFERENCE_RESULT_START")
for prompt, output in zip(prompts, outputs):
    print(output['text'])
print("INFERENCE_RESULT_END")
        """
    else:
        raise ValueError(f"不支持的engine类型: {type(engine)}")
    
    # 组合完整代码
    complete_code = (
        import_code + "\n" +
        model_loading_code + "\n" +
        sampling_params_code + "\n" +
        prompt_code + "\n" +
        output_code + "\n" +
        result_output_code
    )
    
    return complete_code


def parse_inference_output(stdout):
    """
    解析子进程的标准输出，提取推理结果
    """
    lines = stdout.strip().split('\n')
    
    # 查找结果标记
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if "INFERENCE_RESULT_START" in line:
            start_idx = i + 1
        elif "INFERENCE_RESULT_END" in line:
            end_idx = i
            break
    
    if start_idx is not None and end_idx is not None:
        result_lines = lines[start_idx:end_idx]
        return '\n'.join(result_lines).strip()
    else:
        # 如果没有找到标记，尝试从输出中提取最后的生成文本
        for line in reversed(lines):
            if line.strip() and not line.startswith("Generated text:"):
                return line.strip()
        return "未找到推理结果"


def infer_with_config(engine: Engine, prompts: str, config_name: str = "qwen_small", **kwargs):
    """
    使用配置名称进行推理的便捷函数
    
    Args:
        engine: Engine实例
        prompts: 输入提示词
        config_name: 配置名称
        **kwargs: 覆盖配置的参数
    
    Returns:
        str: 推理结果
    """
    return infer(engine, prompts, config_name, **kwargs)


if __name__ == "__main__":
    vllm_engine = VllmEngine()
    
    # 测试使用配置名称推理
    print("使用配置名称推理:")
    result1 = infer(
        engine=vllm_engine, 
        prompts="你好，你是谁？", 
        model="qwen_small"
    )
    print(f"结果1: {result1}")
    
    # 测试使用直接路径推理
    print("\n使用直接路径推理:")
    result2 = infer(
        engine=vllm_engine, 
        prompts="你好，你是谁？", 
        model="Qwen/Qwen3-1.7B",
        temperature=0.7,
        max_tokens=100
    )
    print(f"结果2: {result2}")
    
    # 测试使用配置对象推理
    print("\n使用配置对象推理:")
    from inference_config import load_inference_config
    config = load_inference_config("creative_mode")
    result3 = infer(
        engine=vllm_engine,
        prompts="写一首关于春天的短诗",
        model=config
    )
    print(f"结果3: {result3}")

