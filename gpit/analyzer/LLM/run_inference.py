#!/usr/bin/env python3
"""
推理系统启动脚本
提供命令行界面来使用推理系统
"""

import argparse
import sys
import time
from engines import VllmEngine, SglangEngine
from inference import infer
from inference_config import config_manager, load_inference_config


def main():
    parser = argparse.ArgumentParser(
        description="大语言模型推理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用预定义配置
  python run_inference.py -e vllm -m qwen_small -p "你好，你是谁？"
  
  # 使用自定义参数
  python run_inference.py -e vllm -m "Qwen/Qwen3-1.7B" -p "解释机器学习" --temperature 0.8 --max-tokens 200
  
  # 列出可用配置
  python run_inference.py --list-configs
  
  # 交互模式
  python run_inference.py -e vllm -m qwen_small --interactive
        """
    )
    
    parser.add_argument('-e', '--engine', 
                       choices=['vllm', 'sglang'], 
                       default='vllm',
                       help='推理引擎类型 (默认: vllm)')
    
    parser.add_argument('-m', '--model',
                       help='模型路径或配置名称')
    
    parser.add_argument('-p', '--prompt',
                       help='输入提示词')
    
    parser.add_argument('--temperature', type=float,
                       help='采样温度 (0.0-2.0)')
    
    parser.add_argument('--top-p', type=float,
                       help='核采样参数 (0.0-1.0)')
    
    parser.add_argument('--max-tokens', type=int,
                       help='最大生成长度')
    
    parser.add_argument('--repetition-penalty', type=float,
                       help='重复惩罚 (1.0为无惩罚)')
    
    parser.add_argument('--timeout', type=int,
                       help='推理超时时间(秒)')
    
    parser.add_argument('--list-configs', action='store_true',
                       help='列出所有可用配置')
    
    parser.add_argument('--interactive', action='store_true',
                       help='进入交互模式')
    
    parser.add_argument('--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 列出配置
    if args.list_configs:
        print("可用的推理配置:")
        configs = config_manager.list_configs()
        for name, source in configs.items():
            config = config_manager.get_config(name)
            print(f"  {name:15} ({source:10}): {config.model_path}")
            if args.verbose:
                print(f"    - 温度: {config.temperature}")
                print(f"    - 最大长度: {config.max_tokens}")
                print(f"    - GPU并行: {config.tensor_parallel_size}")
        return
    
    # 检查必要参数
    if not args.model:
        print("错误: 必须指定模型 (-m/--model)")
        sys.exit(1)
    
    # 创建引擎
    if args.engine == 'vllm':
        engine = VllmEngine()
    elif args.engine == 'sglang':
        engine = SglangEngine()
    else:
        print(f"错误: 不支持的引擎类型 {args.engine}")
        sys.exit(1)
    
    print(f"使用 {args.engine.upper()} 引擎，模型: {args.model}")
    
    # 准备推理参数
    kwargs = {}
    if args.temperature is not None:
        kwargs['temperature'] = args.temperature
    if args.top_p is not None:
        kwargs['top_p'] = args.top_p
    if args.max_tokens is not None:
        kwargs['max_tokens'] = args.max_tokens
    if args.repetition_penalty is not None:
        kwargs['repetition_penalty'] = args.repetition_penalty
    if args.timeout is not None:
        kwargs['timeout'] = args.timeout
    
    # 交互模式
    if args.interactive:
        print("\n进入交互模式 (输入 'quit' 或 'exit' 退出)")
        print("-" * 50)
        
        while True:
            try:
                prompt = input("\n请输入您的问题: ").strip()
                
                if prompt.lower() in ['quit', 'exit', '退出']:
                    print("再见！")
                    break
                
                if not prompt:
                    continue
                
                print(f"\n正在推理... (引擎: {args.engine})")
                start_time = time.time()
                
                result = infer(
                    engine=engine,
                    prompts=prompt,
                    model=args.model,
                    **kwargs
                )
                
                end_time = time.time()
                
                print(f"\n回答 (耗时: {end_time - start_time:.2f}秒):")
                print("-" * 30)
                print(result)
                print("-" * 30)
                
            except KeyboardInterrupt:
                print("\n\n用户中断，退出...")
                break
            except Exception as e:
                print(f"\n错误: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    
    # 单次推理模式
    else:
        if not args.prompt:
            print("错误: 必须指定提示词 (-p/--prompt)")
            sys.exit(1)
        
        print(f"提示词: {args.prompt}")
        if kwargs:
            print(f"参数: {kwargs}")
        
        try:
            print("\n正在推理...")
            start_time = time.time()
            
            result = infer(
                engine=engine,
                prompts=args.prompt,
                model=args.model,
                **kwargs
            )
            
            end_time = time.time()
            
            print(f"\n推理结果 (耗时: {end_time - start_time:.2f}秒):")
            print("=" * 50)
            print(result)
            print("=" * 50)
            
        except Exception as e:
            print(f"推理失败: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main() 