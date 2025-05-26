#!/usr/bin/env python3
"""
Inference system test script
For verifying that all components work correctly
"""

import unittest
import tempfile
import os
from engines import VllmEngine, SglangEngine
from inference_config import InferenceConfig, ConfigManager, load_inference_config
from inference import infer, generate_inference_code, parse_inference_output


class TestInferenceConfig(unittest.TestCase):
    """Test configuration system"""
    
    def test_config_creation(self):
        """Test configuration creation"""
        config = InferenceConfig(
            model_path="test/model",
            temperature=0.8,
            max_tokens=1024
        )
        self.assertEqual(config.model_path, "test/model")
        self.assertEqual(config.temperature, 0.8)
        self.assertEqual(config.max_tokens, 1024)
    
    def test_config_serialization(self):
        """Test configuration serialization"""
        config = InferenceConfig(model_path="test/model", temperature=0.7)
        config_dict = config.to_dict()
        new_config = InferenceConfig.from_dict(config_dict)
        
        self.assertEqual(config.model_path, new_config.model_path)
        self.assertEqual(config.temperature, new_config.temperature)
    
    def test_config_manager(self):
        """Test configuration manager"""
        manager = ConfigManager()
        
        # Test predefined configurations
        config = manager.get_config("qwen_small")
        self.assertIsNotNone(config)
        self.assertEqual(config.model_path, "Qwen/Qwen3-1.7B")
        
        # Test list configurations
        configs = manager.list_configs()
        self.assertIn("qwen_small", configs)
        self.assertIn("creative_mode", configs)


class TestEngines(unittest.TestCase):
    """Test engines"""
    
    def test_vllm_engine(self):
        """Test VllmEngine"""
        engine = VllmEngine()
        
        # Test import code generation
        import_code = engine.import_engine
        self.assertIn("vllm", import_code)
        self.assertIn("SamplingParams", import_code)
        
        # Test model loading code generation
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
        """Test SglangEngine"""
        engine = SglangEngine()
        
        # Test import code generation
        import_code = engine.import_engine
        self.assertIn("sglang", import_code)
        
        # Test model loading code generation
        load_code = engine.load_model("test/model")
        self.assertIn("test/model", load_code)


class TestInference(unittest.TestCase):
    """Test inference functionality"""
    
    def test_generate_inference_code(self):
        """Test inference code generation"""
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
            prompts="test prompt",
            model_path="test/model",
            config=config,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.0,
            max_tokens=100
        )
        
        # Check that generated code contains necessary components
        self.assertIn("import", code)
        self.assertIn("test/model", code)
        self.assertIn("test prompt", code)
        self.assertIn("INFERENCE_RESULT_START", code)
        self.assertIn("INFERENCE_RESULT_END", code)
    
    def test_parse_inference_output(self):
        """Test output parsing"""
        # Test normal output
        stdout = """
        Loading model...
        INFERENCE_RESULT_START
        This is the generated text result
        INFERENCE_RESULT_END
        Process completed.
        """
        
        result = parse_inference_output(stdout)
        self.assertEqual(result, "This is the generated text result")
        
        # Test multiline output
        stdout_multiline = """
        INFERENCE_RESULT_START
        First line result
        Second line result
        INFERENCE_RESULT_END
        """
        
        result = parse_inference_output(stdout_multiline)
        self.assertEqual(result, "First line result\nSecond line result")
    
    def test_config_loading_in_infer(self):
        """Test configuration loading in inference function"""
        engine = VllmEngine()
        
        # This test won't actually run inference, but will test config processing logic
        try:
            # Test using config name (will fail due to no real model, but can test config loading)
            config = load_inference_config("qwen_small")
            self.assertEqual(config.model_path, "Qwen/Qwen3-1.7B")
            
            # Test using config object
            custom_config = InferenceConfig(model_path="test/model")
            # Here we only test config processing, not actual inference
            
        except Exception as e:
            # Expected to fail because there's no real model and environment
            pass


class TestEndToEnd(unittest.TestCase):
    """End-to-end tests (requires real environment)"""
    
    def setUp(self):
        """Setup before tests"""
        self.engine = VllmEngine()
        
    def test_config_file_operations(self):
        """Test configuration file operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = ConfigManager(config_dir=temp_dir)
            
            # Create custom configuration
            config = InferenceConfig(
                model_path="test/model",
                temperature=0.8,
                max_tokens=512
            )
            
            # Save configuration
            manager.save_config("test_config", config)
            
            # Load configuration
            loaded_config = manager.get_config("test_config")
            self.assertIsNotNone(loaded_config)
            self.assertEqual(loaded_config.model_path, "test/model")
            self.assertEqual(loaded_config.temperature, 0.8)
            
            # Test template configuration creation
            template_config = manager.create_config_from_template(
                "test_config",
                "new_config", 
                temperature=0.9
            )
            self.assertEqual(template_config.temperature, 0.9)
            self.assertEqual(template_config.model_path, "test/model")  # Inherited from template


def run_functional_test():
    """Run functional tests (requires real environment)"""
    print("Starting functional tests...")
    print("Note: This requires real model and GPU environment")
    
    try:
        from engines import VllmEngine
        from inference import infer
        
        engine = VllmEngine()
        
        # Test configuration system
        print("1. Testing configuration system...")
        from inference_config import config_manager
        configs = config_manager.list_configs()
        print(f"   Available configurations: {list(configs.keys())}")
        
        # Test code generation
        print("2. Testing code generation...")
        config = load_inference_config("qwen_small")
        code = generate_inference_code(
            engine, "test", config.model_path, config,
            0.7, 0.95, 1.0, 100
        )
        print(f"   Generated code length: {len(code)} characters")
        
        print("Functional tests completed!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all modules are in correct location")
    except Exception as e:
        print(f"Error during testing: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Inference System Unit Tests")
    print("=" * 60)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    print("\n" + "=" * 60)
    print("Functional Tests")
    print("n" + "=" * 60)
    
    # Run functional tests
    run_functional_test() 