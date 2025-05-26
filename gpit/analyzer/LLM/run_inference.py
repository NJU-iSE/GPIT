#!/usr/bin/env python3
"""
Inference system startup script
Provides command line interface to use the inference system
"""

import argparse
import sys
import time
from engines import VllmEngine, SglangEngine
from inference import infer
from inference_config import config_manager, load_inference_config


def main():
    parser = argparse.ArgumentParser(
        description="Large Language Model Inference System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Use predefined config
  python run_inference.py -e vllm -m qwen_small -p "Hello, who are you?"
  
  # Use custom parameters
  python run_inference.py -e vllm -m "Qwen/Qwen3-1.7B" -p "Explain machine learning" --temperature 0.8 --max-tokens 200
  
  # List available configs
  python run_inference.py --list-configs
  
  # Interactive mode
  python run_inference.py -e vllm -m qwen_small --interactive
        """
    )
    
    parser.add_argument('-e', '--engine', 
                       choices=['vllm', 'sglang'], 
                       default='vllm',
                       help='Inference engine type (default: vllm)')
    
    parser.add_argument('-m', '--model',
                       help='Model path or configuration name')
    
    parser.add_argument('-p', '--prompt',
                       help='Input prompt')
    
    parser.add_argument('--temperature', type=float,
                       help='Sampling temperature (0.0-2.0)')
    
    parser.add_argument('--top-p', type=float,
                       help='Nucleus sampling parameter (0.0-1.0)')
    
    parser.add_argument('--max-tokens', type=int,
                       help='Maximum generation length')
    
    parser.add_argument('--repetition-penalty', type=float,
                       help='Repetition penalty (1.0 for no penalty)')
    
    parser.add_argument('--timeout', type=int,
                       help='Inference timeout in seconds')
    
    parser.add_argument('--list-configs', action='store_true',
                       help='List all available configurations')
    
    parser.add_argument('--interactive', action='store_true',
                       help='Enter interactive mode')
    
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # List configurations
    if args.list_configs:
        print("Available inference configurations:")
        configs = config_manager.list_configs()
        for name, source in configs.items():
            config = config_manager.get_config(name)
            print(f"  {name:15} ({source:10}): {config.model_path}")
            if args.verbose:
                print(f"    - Temperature: {config.temperature}")
                print(f"    - Max length: {config.max_tokens}")
                print(f"    - GPU parallel: {config.tensor_parallel_size}")
        return
    
    # Check required parameters
    if not args.model:
        print("Error: Must specify model (-m/--model)")
        sys.exit(1)
    
    # Create engine
    if args.engine == 'vllm':
        engine = VllmEngine()
    elif args.engine == 'sglang':
        engine = SglangEngine()
    else:
        print(f"Error: Unsupported engine type {args.engine}")
        sys.exit(1)
    
    print(f"Using {args.engine.upper()} engine, model: {args.model}")
    
    # Prepare inference parameters
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
    
    # Interactive mode
    if args.interactive:
        print("\nEntering interactive mode (type 'quit' or 'exit' to exit)")
        print("-" * 50)
        
        while True:
            try:
                prompt = input("\nPlease enter your question: ").strip()
                
                if prompt.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if not prompt:
                    continue
                
                print(f"\nInferring... (engine: {args.engine})")
                start_time = time.time()
                
                result = infer(
                    engine=engine,
                    prompts=prompt,
                    model=args.model,
                    **kwargs
                )
                
                end_time = time.time()
                
                print(f"\nAnswer (time elapsed: {end_time - start_time:.2f} seconds):")
                print("-" * 30)
                print(result)
                print("-" * 30)
                
            except KeyboardInterrupt:
                print("\n\nUser interrupted, exiting...")
                break
            except Exception as e:
                print(f"\nError: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    
    # Single inference mode
    else:
        if not args.prompt:
            print("Error: Must specify prompt (-p/--prompt)")
            sys.exit(1)
        
        print(f"Prompt: {args.prompt}")
        if kwargs:
            print(f"Parameters: {kwargs}")
        
        try:
            print("\nInferring...")
            start_time = time.time()
            
            result = infer(
                engine=engine,
                prompts=args.prompt,
                model=args.model,
                **kwargs
            )
            
            end_time = time.time()
            
            print(f"\nInference result (time elapsed: {end_time - start_time:.2f} seconds):")
            print("=" * 50)
            print(result)
            print("=" * 50)
            
        except Exception as e:
            print(f"Inference failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main() 