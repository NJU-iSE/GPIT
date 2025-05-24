from engines import VllmEngine, SglangEngine, Engine


def infer(engine: Engine, prompts, model):
    print(engine.import_engine)


if __name__ == "__main__":
    vllm_engine = VllmEngine()
    infer(vllm_engine, "prompt", "model")
