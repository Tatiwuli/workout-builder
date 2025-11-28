#import the prompts 
from llmlingua import PromptCompressor
from ..app.agents.agents_prompts import exercise_selector_prompts




#Apply the ll mlingua

def compress(system_prompt, user_prompt):

    prompt_compressor = PromptCompressor()

    compressed_prompt = prompt_compressor.structured_compress_prompt(
        system_prompt,
        instruction="",
        question= user_prompt,
        rate=0.5,
    )
    print(compressed_prompt['compressed_prompt'])


compress(exercise_selector_prompts.system_prompt, exercise_selector_prompts.user_prompt)