from quicksilver.prompt import Prompt
from quicksilver.repository import Prompts
from quicksilver.utils.lambdafn import api_handler


@api_handler(model=Prompt)
def save_prompt(prompt):
    prompt = Prompts.save(prompt)
    return prompt
