from transformers import AutoTokenizer
from vllm import LLM, SamplingParams


class Model:
    """
    A class for managing the LLM model.
    """

    def __init__(self, model_path, temperature=0.7, top_p=0.8, repetition_penalty=1.05, max_tokens=512):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.sampling_params = SamplingParams(temperature=temperature, top_p=top_p, repetition_penalty=repetition_penalty,
                                              max_tokens=max_tokens)
        self.native_model = LLM(model=model_path, dtype="half")

    def get_answer(self, prompt):
        message = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]

        text = self.tokenizer.apply_chat_template(message, tokenize=False, add_genereation_prompt=True)

        outputs = self.native_model.generate([text], self.sampling_params)

        return outputs
