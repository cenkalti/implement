import os
import logging
import importlib

import yapf
import openai

from implement import source

MODEL = os.environ.get("IMPLEMENT_OPENAI_MODEL", "gpt-4o")

logger = logging.getLogger(__name__)
log_level = os.environ.get("IMPLEMENT_LOG_LEVEL")
if log_level:
    logger.setLevel(log_level)
    logger.addHandler(logging.StreamHandler())


if os.environ.get("IMPLEMENT_CLEAN", None):
    for file in os.listdir("functions"):
        if file.endswith(".py"):
            os.remove(os.path.join("functions", file))
            logger.info(f"Removed {file} from functions directory.")
    logger.info("Cleaned functions directory.")


client = openai.Client()


def implement():
    """Decorator to implement a function using OpenAI's GPT-4o model."""
    def wrapper(f: callable):
        return ImplementedFunction(f)
    return wrapper


class ImplementedFunction:
    def __init__(self, f: callable):
        self.f = f
        self.path = os.path.join("functions", f"{f.__name__}.py")
        if os.path.exists(self.path):
            logger.info(f"Function {f.__name__} is already implemented.")
            return
        script = generate_python_script(f)
        script, _ = yapf.yapf_api.FormatCode(script)
        os.makedirs("functions", exist_ok=True)
        with open(self.path, "w") as f:
            f.write(script)

    def __call__(self, *args, **kwargs):
        logger.info(f"Calling {self.f.__name__} with arguments: {args}, {kwargs}")
        module = importlib.import_module(f"functions.{self.f.__name__}")
        function = getattr(module, self.f.__name__)
        return function(*args, **kwargs)


def generate_python_script(f: callable) -> str:
    source_code = source.extract(f)
    logger.info(f"Generating Python script for function: {f.__name__}")
    logger.debug(f"Function source code:\n{source_code}")
    messages = [
        {
            "role": "system",
            "content": " ".join([
                "You are Python programmer.",
                "Implement the given function.",
                "Do not write type annotations.",
                "Answer only with code.",
                "Do not wrap your answer as code block.",
            ]),
        },
        {
            "role": "user",
            "content": source_code,
            "temperature": 0,
        },
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        seed=6,
    )
    response_message = response.choices[0].message
    logger.info(f"Generated Python script for function: {f.__name__}")
    logger.debug(f"Python script:\n{response_message.content}\n")
    return response_message.content
