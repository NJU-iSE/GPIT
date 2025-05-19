"""
@SHAOYU: in this file, I need to implement template code generation for inference engines.
"""
import textwrap
from abc import abstractmethod, ABCMeta
from typing import List
from pathlib import Path



class Engine(metaclass=ABCMeta):  # FIXME@SHAOYU: need to further investigate the ABCMeatClass
    def __init__(self):  # TODO@SHAOYU: add some necessary parameters for engines. In this way, we can modify the method from static into dynamic
        pass

    @property
    def import_engine(self):
        raise NotImplementedError

    @abstractmethod
    def load_model(self, model_path):
        raise NotImplementedError


class SglangEngine(Engine):
    def __init__(self):
        super().__init__()

    @property
    def import_engine(self):
        import_strings = \
        """
        import asyncio
        import io
        import os
        
        from PIL import Image
        import requests
        import sglang as sgl
        
        from sglang.srt.conversation import chat_templates
        from sglang.test.test_utils import is_in_ci
        from sglang.utils import async_stream_and_merge, stream_and_merge
        """
        return import_strings

    def load_model(self, model_path):
        load_strings = \
        f"""
        llm = sgl.Engine(model_path="{model_path}")
        """
        return load_strings

    def init_sampling_params(self, temperature, top_p, repetition_penalty, max_tokens):
        sampling_params_code = \
        f"""
        sampling_params = sgl.SamplingParams(temperature={temperature}, top_p={top_p}, repetition_penalty={repetition_penalty}, max_tokens={max_tokens})
        """
        return sampling_params_code

    def init_prompt(self, prompts):
        prompts_code = \
        f"""
        prompts = {prompts}
        """
        return prompts_code

    def get_output_code(self, prompts, sampling_params):
        output_code = \
        f"""
        outputs = llm.generate({prompts}, {sampling_params})
        for prompt, output in zip(prompts, outputs):
            print("===============================")
            print(f"Prompt: {{prompt}}\\nGenerated text: {{output['text']}}")
        """
        return output_code


class VllmEngine(Engine):
    def __init__(self):
        super().__init__()

    @property
    def import_engine(self):
        import_strings = textwrap.dedent(
        """
        from transformers import AutoTokenizer
        from vllm import LLM, SamplingParams
        """
        )
        return import_strings

    def load_model(self, model_path, dtype, tensor_parallel_size, gpu_memory_utilization, enable_chunked_prefill):
        load_strings = textwrap.dedent(
        f"""
        tokenizer = AutoTokenizer.from_pretrained("{model_path}")
        llm = LLM(model="{model_path}", dtype="{dtype}", tensor_parallel_size={tensor_parallel_size}, gpu_memory_utilization={gpu_memory_utilization}, enable_chunked_prefill={enable_chunked_prefill})
        """
        )
        return load_strings

    def init_sampling_params(self, temperature, top_p, repetition_penalty, max_tokens):
        sampling_params_code = textwrap.dedent(
        f"""
        sampling_params = SamplingParams(temperature={temperature}, top_p={top_p}, repetition_penalty={repetition_penalty}, max_tokens={max_tokens})
        """
        )
        return sampling_params_code

    def init_prompt(self, prompt: str):
        text_code = textwrap.dedent(
        f"""
        prompts = "{prompt}"
        messages = [
            {{"role": "user", "content": prompts}}
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        """
        )
        return text_code

    def get_output(self, num):
        output_code = textwrap.dedent(
        f"""
        outputs = llm.generate([text], sampling_params)
        output_list = []
        for i in range(len(outputs)):
            output = outputs[i]
            prompt = output.prompt
            generated_text = output.outputs[0].text
            output_list.append(generated_text)
            if i + 1 == {num}:
                break
        """
        )
        return output_code



if __name__ == "__main__":
    vllm_engine = VllmEngine()
    import_code = vllm_engine.import_engine
    # dtype uses `float32`, refer to https://github.com/vllm-project/vllm/issues/17578#issuecomment-2849401877
    model_loading_code = vllm_engine.load_model(model_path="Qwen/Qwen3-1.7B", dtype="float16", tensor_parallel_size=4, gpu_memory_utilization=0.7, enable_chunked_prefill=False)
    sampling_params_code = vllm_engine.init_sampling_params(temperature=0.6, top_p=0.95, repetition_penalty=1.0, max_tokens=4096)
    prompt_code = vllm_engine.init_prompt("hello, who you are?")
    output_code = vllm_engine.get_output(num=1)
    complete_code = import_code + model_loading_code + prompt_code + sampling_params_code + output_code
    Path("./atmp.py").write_text(complete_code)



