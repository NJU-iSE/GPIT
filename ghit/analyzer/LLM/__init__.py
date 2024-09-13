from models import Model

qwen_model = Model(model_path="Qwen/Qwen2-7B-Instruct")


outputs = qwen_model.get_answer("who you r ?")

for output in outputs:
    print(output.outputs[0].text)
