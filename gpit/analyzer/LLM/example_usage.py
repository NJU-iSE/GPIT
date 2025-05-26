#!/usr/bin/env python3
"""
Inference function usage examples
Demonstrates how to use different engines for model inference
"""

from engines import VllmEngine, SglangEngine
from inference import infer
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_vllm_inference():
    """Example of using VllmEngine for inference"""
    logger.info("Starting VllmEngine inference example...")
    
    # Create VllmEngine instance
    vllm_engine = VllmEngine()
    
    # Define test cases
    test_cases = [
        {
            "prompts": "Hello, please introduce yourself.",
            "model": "Qwen/Qwen3-1.7B",
            "temperature": 0.7,
            "max_tokens": 100
        },
        {
            "prompts": "Please explain what artificial intelligence is.",
            "model": "Qwen/Qwen3-1.7B", 
            "temperature": 0.5,
            "max_tokens": 200
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"Executing test case {i}...")
        logger.info(f"Input: {test_case['prompts']}")
        
        start_time = time.time()
        try:
            result = infer(
                engine=vllm_engine,
                prompts=test_case["prompts"],
                model=test_case["model"],
                temperature=test_case["temperature"],
                max_tokens=test_case["max_tokens"]
            )
            
            end_time = time.time()
            logger.info(f"Inference completed, time elapsed: {end_time - start_time:.2f} seconds")
            logger.info(f"Output: {result}")
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}")
            print("-" * 50)


def example_sglang_inference():
    """Example of using SglangEngine for inference"""
    logger.info("Starting SglangEngine inference example...")
    
    # Create SglangEngine instance
    sglang_engine = SglangEngine()
    
    # Define test case
    test_case = {
        "prompts": "Write a poem about spring.",
        "model": "Qwen/Qwen3-1.7B",
        "temperature": 0.8,
        "max_tokens": 150
    }
    
    logger.info(f"Input: {test_case['prompts']}")
    
    start_time = time.time()
    try:
        result = infer(
            engine=sglang_engine,
            prompts=test_case["prompts"],
            model=test_case["model"],
            temperature=test_case["temperature"],
            max_tokens=test_case["max_tokens"]
        )
        
        end_time = time.time()
        logger.info(f"Inference completed, time elapsed: {end_time - start_time:.2f} seconds")
        logger.info(f"Output: {result}")
        
    except Exception as e:
        logger.error(f"Inference failed: {str(e)}")


def batch_inference_example():
    """Batch inference example"""
    logger.info("Starting batch inference example...")
    
    vllm_engine = VllmEngine()
    
    prompts_list = [
        "What is machine learning?",
        "Explain the basic concepts of deep learning.",
        "What are the advantages of Python?"
    ]
    
    results = []
    for prompt in prompts_list:
        try:
            result = infer(
                engine=vllm_engine,
                prompts=prompt,
                model="Qwen/Qwen3-1.7B",
                temperature=0.6,
                max_tokens=100
            )
            results.append({"prompt": prompt, "result": result, "status": "success"})
            logger.info(f"Completed inference: {prompt[:20]}...")
            
        except Exception as e:
            results.append({"prompt": prompt, "result": str(e), "status": "failed"})
            logger.error(f"Inference failed: {prompt[:20]}... - {str(e)}")
    
    # Output batch inference results
    logger.info("Batch inference results summary:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Prompt: {result['prompt']}")
        print(f"   Status: {result['status']}")
        print(f"   Result: {result['result'][:100]}..." if len(result['result']) > 100 else f"   Result: {result['result']}")


if __name__ == "__main__":
    print("=" * 60)
    print("Inference Function Usage Examples")
    print("=" * 60)
    
    # Run VllmEngine example
    try:
        example_vllm_inference()
    except Exception as e:
        logger.error(f"VllmEngine example execution failed: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Run SglangEngine example
    try:
        example_sglang_inference()
    except Exception as e:
        logger.error(f"SglangEngine example execution failed: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Run batch inference example
    try:
        batch_inference_example()
    except Exception as e:
        logger.error(f"Batch inference example execution failed: {str(e)}")
    
    print("\nInference examples completed!") 