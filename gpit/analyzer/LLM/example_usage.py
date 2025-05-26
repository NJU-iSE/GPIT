#!/usr/bin/env python3
"""
推理函数使用示例
演示如何使用不同的engine进行模型推理
"""

from engines import VllmEngine, SglangEngine
from inference import infer
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def example_vllm_inference():
    """使用VllmEngine进行推理的示例"""
    logger.info("开始VllmEngine推理示例...")
    
    # 创建VllmEngine实例
    vllm_engine = VllmEngine()
    
    # 定义测试用例
    test_cases = [
        {
            "prompts": "你好，请介绍一下你自己。",
            "model": "Qwen/Qwen3-1.7B",
            "temperature": 0.7,
            "max_tokens": 100
        },
        {
            "prompts": "请解释什么是人工智能。",
            "model": "Qwen/Qwen3-1.7B", 
            "temperature": 0.5,
            "max_tokens": 200
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"执行测试用例 {i}...")
        logger.info(f"输入: {test_case['prompts']}")
        
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
            logger.info(f"推理完成，耗时: {end_time - start_time:.2f}秒")
            logger.info(f"输出: {result}")
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"推理失败: {str(e)}")
            print("-" * 50)


def example_sglang_inference():
    """使用SglangEngine进行推理的示例"""
    logger.info("开始SglangEngine推理示例...")
    
    # 创建SglangEngine实例
    sglang_engine = SglangEngine()
    
    # 定义测试用例
    test_case = {
        "prompts": "写一首关于春天的诗。",
        "model": "Qwen/Qwen3-1.7B",
        "temperature": 0.8,
        "max_tokens": 150
    }
    
    logger.info(f"输入: {test_case['prompts']}")
    
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
        logger.info(f"推理完成，耗时: {end_time - start_time:.2f}秒")
        logger.info(f"输出: {result}")
        
    except Exception as e:
        logger.error(f"推理失败: {str(e)}")


def batch_inference_example():
    """批量推理示例"""
    logger.info("开始批量推理示例...")
    
    vllm_engine = VllmEngine()
    
    prompts_list = [
        "什么是机器学习？",
        "解释深度学习的基本概念。",
        "Python有哪些优势？"
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
            logger.info(f"完成推理: {prompt[:20]}...")
            
        except Exception as e:
            results.append({"prompt": prompt, "result": str(e), "status": "failed"})
            logger.error(f"推理失败: {prompt[:20]}... - {str(e)}")
    
    # 输出批量推理结果
    logger.info("批量推理结果汇总:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. 提示词: {result['prompt']}")
        print(f"   状态: {result['status']}")
        print(f"   结果: {result['result'][:100]}..." if len(result['result']) > 100 else f"   结果: {result['result']}")


if __name__ == "__main__":
    print("=" * 60)
    print("推理函数使用示例")
    print("=" * 60)
    
    # 运行VllmEngine示例
    try:
        example_vllm_inference()
    except Exception as e:
        logger.error(f"VllmEngine示例执行失败: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # 运行SglangEngine示例
    try:
        example_sglang_inference()
    except Exception as e:
        logger.error(f"SglangEngine示例执行失败: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # 运行批量推理示例
    try:
        batch_inference_example()
    except Exception as e:
        logger.error(f"批量推理示例执行失败: {str(e)}")
    
    print("\n推理示例完成!") 