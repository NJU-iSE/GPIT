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
    Generate templated code using engine instance, start subprocess for inference and return results
    
    Args:
        engine: Instantiated Engine object (VllmEngine or SglangEngine)
        prompts: Input prompts
        model: Model path/name or InferenceConfig object, or config name
        **kwargs: Other inference parameters that will override config parameters
    
    Returns:
        str: Generated text result from inference
    """
    
    # Process configuration parameters
    if isinstance(model, InferenceConfig):
        config = model
        model_path = config.model_path
    elif isinstance(model, str):
        if model.startswith("/") or model.startswith("./") or "/" in model:
            # If it's a path, create default config
            config = InferenceConfig(model_path=model)
            model_path = model
        else:
            # If it's a config name, load config
            config = load_inference_config(model)
            model_path = config.model_path
    else:
        raise ValueError("model parameter must be a string (path or config name) or InferenceConfig object")
    
    # Override config parameters with kwargs
    temperature = kwargs.get('temperature', config.temperature)
    top_p = kwargs.get('top_p', config.top_p)
    repetition_penalty = kwargs.get('repetition_penalty', config.repetition_penalty)
    max_tokens = kwargs.get('max_tokens', config.max_tokens)
    timeout = kwargs.get('timeout', config.timeout)
    
    # Generate complete inference code
    complete_code = generate_inference_code(
        engine, prompts, model_path, config,
        temperature, top_p, repetition_penalty, max_tokens
    )
    
    # Create temporary file and write code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(complete_code)
        temp_file_path = temp_file.name
    
    try:
        # Start subprocess to execute code
        result = subprocess.run(
            ['python', temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Inference process error: {result.stderr}")
        
        # Parse output results
        output = parse_inference_output(result.stdout)
        return output
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)


def generate_inference_code(engine, prompts, model_path, config, temperature, top_p, repetition_penalty, max_tokens):
    """
    Generate complete inference code based on engine type
    """
    import_code = engine.import_engine
    
    if isinstance(engine, VllmEngine):
        # VllmEngine code generation - use parameters from config
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
        
        # Add result output code
        result_output_code = """
# Output results to stdout for parsing
print("INFERENCE_RESULT_START")
for result in output_list:
    print(result)
print("INFERENCE_RESULT_END")
        """
        
    elif isinstance(engine, SglangEngine):
        # SglangEngine code generation
        model_loading_code = engine.load_model(model_path)
        sampling_params_code = engine.init_sampling_params(
            temperature, top_p, repetition_penalty, max_tokens
        )
        prompt_code = engine.init_prompt([prompts])
        output_code = engine.get_output_code("prompts", "sampling_params")
        
        # Add result output code
        result_output_code = """
# Output results to stdout for parsing
print("INFERENCE_RESULT_START")
for prompt, output in zip(prompts, outputs):
    print(output['text'])
print("INFERENCE_RESULT_END")
        """
    else:
        raise ValueError(f"Unsupported engine type: {type(engine)}")
    
    # Combine complete code
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
    Parse subprocess stdout and extract inference results
    """
    lines = stdout.strip().split('\n')
    
    # Find result markers
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
        # If markers not found, try to extract last generated text from output
        for line in reversed(lines):
            if line.strip() and not line.startswith("Generated text:"):
                return line.strip()
        return "Inference result not found"


def infer_with_config(engine: Engine, prompts: str, config_name: str = "qwen_small", **kwargs):
    """
    Convenient function for inference using config name
    
    Args:
        engine: Engine instance
        prompts: Input prompts
        config_name: Configuration name
        **kwargs: Parameters to override config
    
    Returns:
        str: Inference result
    """
    return infer(engine, prompts, config_name, **kwargs)


if __name__ == "__main__":
    vllm_engine = VllmEngine()
    
    # Test inference using config name
    print("Testing inference with config name:")
    result1 = infer(
        engine=vllm_engine, 
        prompts="Hello, who are you?", 
        model="qwen_small"
    )
    print(f"Result 1: {result1}")
    
    # Test inference using direct path
    print("\nTesting inference with direct path:")
    result2 = infer(
        engine=vllm_engine, 
        prompts="Hello, who are you?", 
        model="Qwen/Qwen3-1.7B",
        temperature=0.7,
        max_tokens=100
    )
    print(f"Result 2: {result2}")
    
    # Test inference using config object
    print("\nTesting inference with config object:")
    from inference_config import load_inference_config
    config = load_inference_config("creative_mode")
    result3 = infer(
        engine=vllm_engine,
        prompts="Write a short poem about spring",
        model=config
    )
    print(f"Result 3: {result3}")

