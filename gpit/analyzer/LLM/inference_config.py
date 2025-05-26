"""
Inference configuration file
For managing inference parameters and settings for different models
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import os


@dataclass
class InferenceConfig:
    """Inference configuration class"""
    model_path: str
    temperature: float = 0.6
    top_p: float = 0.95
    repetition_penalty: float = 1.0
    max_tokens: int = 4096
    dtype: str = "float16"
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.7
    enable_chunked_prefill: bool = False
    timeout: int = 300  # Subprocess timeout in seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "model_path": self.model_path,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repetition_penalty": self.repetition_penalty,
            "max_tokens": self.max_tokens,
            "dtype": self.dtype,
            "tensor_parallel_size": self.tensor_parallel_size,
            "gpu_memory_utilization": self.gpu_memory_utilization,
            "enable_chunked_prefill": self.enable_chunked_prefill,
            "timeout": self.timeout
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'InferenceConfig':
        """Create config object from dictionary"""
        return cls(**config_dict)
    
    def save_to_file(self, filepath: str):
        """Save configuration to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'InferenceConfig':
        """Load configuration from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)


class ConfigManager:
    """Configuration manager"""
    
    def __init__(self, config_dir: str = "./configs"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        self._predefined_configs = self._create_predefined_configs()
    
    def _create_predefined_configs(self) -> Dict[str, InferenceConfig]:
        """Create predefined configurations"""
        configs = {
            "qwen_small": InferenceConfig(
                model_path="Qwen/Qwen3-1.7B",
                temperature=0.7,
                max_tokens=2048,
                tensor_parallel_size=1,
                gpu_memory_utilization=0.6
            ),
            "qwen_medium": InferenceConfig(
                model_path="Qwen/Qwen3-4B",
                temperature=0.6,
                max_tokens=4096,
                tensor_parallel_size=2,
                gpu_memory_utilization=0.8
            ),
            "qwen_large": InferenceConfig(
                model_path="Qwen/Qwen3-14B",
                temperature=0.5,
                max_tokens=8192,
                tensor_parallel_size=4,
                gpu_memory_utilization=0.9
            ),
            "creative_mode": InferenceConfig(
                model_path="Qwen/Qwen3-1.7B",
                temperature=0.9,
                top_p=0.8,
                max_tokens=1024,
                repetition_penalty=1.1
            ),
            "precise_mode": InferenceConfig(
                model_path="Qwen/Qwen3-1.7B",
                temperature=0.1,
                top_p=0.9,
                max_tokens=2048,
                repetition_penalty=1.0
            )
        }
        return configs
    
    def get_config(self, config_name: str) -> Optional[InferenceConfig]:
        """Get configuration"""
        # First check predefined configs
        if config_name in self._predefined_configs:
            return self._predefined_configs[config_name]
        
        # Then check file configs
        config_file = os.path.join(self.config_dir, f"{config_name}.json")
        if os.path.exists(config_file):
            return InferenceConfig.load_from_file(config_file)
        
        return None
    
    def save_config(self, config_name: str, config: InferenceConfig):
        """Save configuration"""
        config_file = os.path.join(self.config_dir, f"{config_name}.json")
        config.save_to_file(config_file)
    
    def list_configs(self) -> Dict[str, str]:
        """List all available configurations"""
        configs = {}
        
        # Add predefined configs
        for name in self._predefined_configs:
            configs[name] = "predefined"
        
        # Add file configs
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]  # Remove .json suffix
                    configs[name] = "file"
        
        return configs
    
    def create_config_from_template(self, template_name: str, new_name: str, **overrides) -> InferenceConfig:
        """Create new configuration based on template"""
        template_config = self.get_config(template_name)
        if template_config is None:
            raise ValueError(f"Template configuration '{template_name}' does not exist")
        
        # Create new config with override parameters
        config_dict = template_config.to_dict()
        config_dict.update(overrides)
        
        new_config = InferenceConfig.from_dict(config_dict)
        self.save_config(new_name, new_config)
        
        return new_config


# Global config manager instance
config_manager = ConfigManager()


def load_inference_config(config_name: str = "qwen_small") -> InferenceConfig:
    """Convenient function to load inference configuration"""
    config = config_manager.get_config(config_name)
    if config is None:
        print(f"Warning: Configuration '{config_name}' does not exist, using default configuration")
        return config_manager.get_config("qwen_small")
    return config


if __name__ == "__main__":
    # Demonstrate config manager usage
    print("Available configurations:")
    configs = config_manager.list_configs()
    for name, source in configs.items():
        config = config_manager.get_config(name)
        print(f"  {name} ({source}): {config.model_path}, temp={config.temperature}")
    
    print("\nCreating custom configuration:")
    custom_config = config_manager.create_config_from_template(
        "qwen_small", 
        "my_custom_config",
        temperature=0.8,
        max_tokens=1024
    )
    print(f"Custom configuration: {custom_config.to_dict()}")
    
    print("\nConfiguration files saved to:", config_manager.config_dir) 