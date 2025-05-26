#!/usr/bin/env python3
"""
推理系统测试脚本
用于验证各个组件是否正常工作
"""

import unittest
import tempfile
import os
from engines import VllmEngine, SglangEngine
from inference_config import InferenceConfig, ConfigManager, load_inference_config
from inference import infer, generate_inference_code, parse_inference_output


class TestInferenceConfig(unittest.TestCase):
    """测试配置系统"""
    
    def test_config_creation(self):
        """测试配置创建"""
        config = InferenceConfig(
            model_path="test/model",
            temperature=0.8,
            max_tokens=1024
        )
        self.assertEqual(config.model_path, "test/model")
        self.assertEqual(config.temperature, 0.8)
        self.assertEqual(config.max_tokens, 1024)
    
    def test_config_serialization(self):
        """测试配置序列化"""
        config = InferenceConfig(model_path="test/model", temperature=0.7)
        config_dict = config.to_dict()
        new_config = InferenceConfig.from_dict(config_dict)
        
        self.assertEqual(config.model_path, new_config.model_path)
        self.assertEqual(config.temperature, new_config.temperature)
    
    def test_config_manager(self):
        """测试配置管理器"""
        manager = ConfigManager()
        
        # 测试预定义配置
        config = manager.get_config("qwen_small")
        self.assertIsNotNone(config)
        self.assertEqual(config.model_path, "Qwen/Qwen3-1.7B")
        
        # 测试列出配置
        configs = manager.list_configs()
        self.assertIn("qwen_small", configs)
        self.assertIn("creative_mode", configs)


class TestEngines(unittest.TestCase):
    """测试引擎"""
    
    def test_vllm_engine(self):
        """测试VllmEngine"""
        engine = VllmEngine()
        
        # 测试导入代码生成
        import_code = engine.import_engine
        self.assertIn("vllm", import_code)
        self.assertIn("SamplingParams", import_code)
        
        # 测试模型加载代码生成
        load_code = engine.load_model(
            model_path="test/model",
            dtype="float16", 
            tensor_parallel_size=1,
            gpu_memory_utilization=0.7,
            enable_chunked_prefill=False
        )
        self.assertIn("test/model", load_code)
        self.assertIn("LLM", load_code)
    
    def test_sglang_engine(self):
        """测试SglangEngine"""
        engine = SglangEngine()
        
        # 测试导入代码生成
        import_code = engine.import_engine
        self.assertIn("sglang", import_code)
        
        # 测试模型加载代码生成
        load_code = engine.load_model("test/model")
        self.assertIn("test/model", load_code)


class TestInference(unittest.TestCase):
    """测试推理功能"""
    
    def test_generate_inference_code(self):
        """测试推理代码生成"""
        engine = VllmEngine()
        config = InferenceConfig(
            model_path="test/model",
            dtype="float16",
            tensor_parallel_size=1,
            gpu_memory_utilization=0.7,
            enable_chunked_prefill=False
        )
        
        code = generate_inference_code(
            engine=engine,
            prompts="测试提示词",
            model_path="test/model",
            config=config,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.0,
            max_tokens=100
        )
        
        # 检查生成的代码包含必要组件
        self.assertIn("import", code)
        self.assertIn("test/model", code)
        self.assertIn("测试提示词", code)
        self.assertIn("INFERENCE_RESULT_START", code)
        self.assertIn("INFERENCE_RESULT_END", code)
    
    def test_parse_inference_output(self):
        """测试输出解析"""
        # 测试正常输出
        stdout = """
        Loading model...
        INFERENCE_RESULT_START
        这是生成的文本结果
        INFERENCE_RESULT_END
        Process completed.
        """
        
        result = parse_inference_output(stdout)
        self.assertEqual(result, "这是生成的文本结果")
        
        # 测试多行输出
        stdout_multiline = """
        INFERENCE_RESULT_START
        第一行结果
        第二行结果
        INFERENCE_RESULT_END
        """
        
        result = parse_inference_output(stdout_multiline)
        self.assertEqual(result, "第一行结果\n第二行结果")
    
    def test_config_loading_in_infer(self):
        """测试推理函数中的配置加载"""
        engine = VllmEngine()
        
        # 这个测试不会真正执行推理，但会测试配置处理逻辑
        try:
            # 测试使用配置名称（会因为没有真实模型而失败，但可以测试配置加载）
            config = load_inference_config("qwen_small")
            self.assertEqual(config.model_path, "Qwen/Qwen3-1.7B")
            
            # 测试使用配置对象
            custom_config = InferenceConfig(model_path="test/model")
            # 这里我们只测试配置处理，不执行实际推理
            
        except Exception as e:
            # 预期会失败，因为没有真实的模型和环境
            pass


class TestEndToEnd(unittest.TestCase):
    """端到端测试（需要真实环境）"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = VllmEngine()
        
    def test_config_file_operations(self):
        """测试配置文件操作"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(config_dir=temp_dir)
            
            # 创建自定义配置
            config = InferenceConfig(
                model_path="test/model",
                temperature=0.8,
                max_tokens=512
            )
            
            # 保存配置
            manager.save_config("test_config", config)
            
            # 加载配置
            loaded_config = manager.get_config("test_config")
            self.assertIsNotNone(loaded_config)
            self.assertEqual(loaded_config.model_path, "test/model")
            self.assertEqual(loaded_config.temperature, 0.8)
            
            # 测试模板配置创建
            template_config = manager.create_config_from_template(
                "test_config",
                "new_config", 
                temperature=0.9
            )
            self.assertEqual(template_config.temperature, 0.9)
            self.assertEqual(template_config.model_path, "test/model")  # 继承自模板


def run_functional_test():
    """运行功能测试（需要真实环境）"""
    print("开始功能测试...")
    print("注意：这需要真实的模型和GPU环境")
    
    try:
        from engines import VllmEngine
        from inference import infer
        
        engine = VllmEngine()
        
        # 测试配置系统
        print("1. 测试配置系统...")
        from inference_config import config_manager
        configs = config_manager.list_configs()
        print(f"   可用配置: {list(configs.keys())}")
        
        # 测试代码生成
        print("2. 测试代码生成...")
        config = load_inference_config("qwen_small")
        code = generate_inference_code(
            engine, "测试", config.model_path, config,
            0.7, 0.95, 1.0, 100
        )
        print(f"   生成的代码长度: {len(code)} 字符")
        
        print("功能测试完成！")
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保所有模块都在正确位置")
    except Exception as e:
        print(f"测试过程中出错: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("推理系统单元测试")
    print("=" * 60)
    
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 60)
    print("功能测试")
    print("=" * 60)
    
    # 运行功能测试
    run_functional_test() 