"""
推理配置文件
用于管理不同模型的推理参数和设置
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import os


@dataclass
class InferenceConfig:
    """推理配置类"""
    model_path: str
    temperature: float = 0.6
    top_p: float = 0.95
    repetition_penalty: float = 1.0
    max_tokens: int = 4096
    dtype: str = "float16"
    tensor_parallel_size: int = 1
    gpu_memory_utilization: float = 0.7
    enable_chunked_prefill: bool = False
    timeout: int = 300  # 子进程超时时间（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
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
        """从字典创建配置对象"""
        return cls(**config_dict)
    
    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'InferenceConfig':
        """从文件加载配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "./configs"):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)
        self._predefined_configs = self._create_predefined_configs()
    
    def _create_predefined_configs(self) -> Dict[str, InferenceConfig]:
        """创建预定义的配置"""
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
        """获取配置"""
        # 首先检查预定义配置
        if config_name in self._predefined_configs:
            return self._predefined_configs[config_name]
        
        # 然后检查文件配置
        config_file = os.path.join(self.config_dir, f"{config_name}.json")
        if os.path.exists(config_file):
            return InferenceConfig.load_from_file(config_file)
        
        return None
    
    def save_config(self, config_name: str, config: InferenceConfig):
        """保存配置"""
        config_file = os.path.join(self.config_dir, f"{config_name}.json")
        config.save_to_file(config_file)
    
    def list_configs(self) -> Dict[str, str]:
        """列出所有可用的配置"""
        configs = {}
        
        # 添加预定义配置
        for name in self._predefined_configs:
            configs[name] = "predefined"
        
        # 添加文件配置
        if os.path.exists(self.config_dir):
            for filename in os.listdir(self.config_dir):
                if filename.endswith('.json'):
                    name = filename[:-5]  # 移除.json后缀
                    configs[name] = "file"
        
        return configs
    
    def create_config_from_template(self, template_name: str, new_name: str, **overrides) -> InferenceConfig:
        """基于模板创建新配置"""
        template_config = self.get_config(template_name)
        if template_config is None:
            raise ValueError(f"模板配置 '{template_name}' 不存在")
        
        # 创建新配置，应用覆盖参数
        config_dict = template_config.to_dict()
        config_dict.update(overrides)
        
        new_config = InferenceConfig.from_dict(config_dict)
        self.save_config(new_name, new_config)
        
        return new_config


# 全局配置管理器实例
config_manager = ConfigManager()


def load_inference_config(config_name: str = "qwen_small") -> InferenceConfig:
    """加载推理配置的便捷函数"""
    config = config_manager.get_config(config_name)
    if config is None:
        print(f"警告: 配置 '{config_name}' 不存在，使用默认配置")
        return config_manager.get_config("qwen_small")
    return config


if __name__ == "__main__":
    # 演示配置管理器的使用
    print("可用的配置:")
    configs = config_manager.list_configs()
    for name, source in configs.items():
        config = config_manager.get_config(name)
        print(f"  {name} ({source}): {config.model_path}, temp={config.temperature}")
    
    print("\n创建自定义配置:")
    custom_config = config_manager.create_config_from_template(
        "qwen_small", 
        "my_custom_config",
        temperature=0.8,
        max_tokens=1024
    )
    print(f"自定义配置: {custom_config.to_dict()}")
    
    print("\n配置文件已保存到:", config_manager.config_dir) 