"""
@SHAOYU: in this file, I need to implement some inference engine operations.
"""

class Engine:
    def __init__(self):  # TODO@SHAOYU: add some necessary parameters for engines.
        pass

    @property
    def import_engine(self):
        raise NotImplementedError

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

    def init_prompt(self, prompts):
        get_prompts_code = \
        f"""
        prompts = {prompts}
        """
        return get_prompts_code

    def init_sampling_params(self, temperature, top_p, repetition_penalty, max_tokens):
        get_sampling_params_code = \
        f"""
        sampling_params = sgl.SamplingParams(temperature={temperature}, top_p={top_p}, repetition_penalty={repetition_penalty}, max_tokens={max_tokens})
        """
        return get_sampling_params_code

    def get_output(self, prompts, sampling_params):
        get_output_code = \
        f"""
        outputs = llm.generate({prompts}, {sampling_params})
        for prompt, output in zip(prompts, outputs):
            print("===============================")
            print(f"Prompt: {{prompt}}\\nGenerated text: {{output['text']}}")
        """
        return get_output_code


class VllmEngine(Engine):
    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    sgl_engine = SglangEngine()
    import_code = sgl_engine.import_engine
    model_loading_code = sgl_engine.load_model(model_path="Qwen/Qwen3-4B-Base")
    prompts = [
        "Hello, my name is",
        "The president of the United States is",
        "The capital of France is",
        "The future of AI is",
    ]
    prompts_code = sgl_engine.init_prompt(prompts=prompts)
    init_sampling_params_code = sgl_engine.init_sampling_params(temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=512)
    get_output_code = sgl_engine.get_output(prompts=prompts, sampling_params=init_sampling_params_code)

    complete_code = import_code + model_loading_code + prompts_code + init_sampling_params_code + get_output_code

    print(complete_code)







