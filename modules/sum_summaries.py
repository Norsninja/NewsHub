
import configparser
import os
import openai
from datetime import datetime


def compile_prompt(summarized_summaries):
    print("compiling prompt")
    """
    Compile the summarized summaries into a GPT prompt.
    """
    if not summarized_summaries:
        print("No data to compile")
        return None

    try:
        prompt = ""
        for summary in summarized_summaries:
            prompt += f"Summary:\n{summary}\n\n"
        return prompt
    except Exception as e:
        print(f"Error while compiling prompt: {e}")
        return None



def load_openai_api_key(config_file='modules/suite_config.ini'):
    """
    Load the OpenAI API key from a configuration file.
    """
    if not os.path.exists(config_file):
        print(f"No configuration file found at {config_file}")
        return None

    config = configparser.ConfigParser()
    config.read(config_file)

    try:
        api_key = config.get('OPENAI', 'OPENAI_API_KEY')
        return api_key
    except Exception as e:
        print(f"Error while loading OpenAI API key: {e}")
        return None
    
def generate_gpt_completion(prompt, api_key, model="gpt-3.5-turbo", max_tokens=700, temperature=1.0):
    """
    Generate a GPT completion given a prompt.
    """
    openai.api_key = api_key

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are a cutting-edge AI assistant named 'Cortex', tasked with crafting a professional news broadcast titled, 'NewsPlanetAI', a highly trusted news program. "
                            "Your mission is to summarize the hour's global events in an authoritative and balanced manner. Here are the components of your task:\n\n"
                            "1. Cortex starts the program, introducing NewsPlanetAI and the day's broadcast in a creative, engaging manner.\n\n"
                            "2. 'The World Watches': This section is committed to detailed coverage of the day's most pressing global issue. Currently, that is the Russia & Ukraine conflict. "
                            "You will present a summary of the day's developments, key events, and an impartial analysis of the situation.\n\n"
                            "3. 'Global Gist': This part provides a comprehensive, yet brief overview of the day's worldwide happenings, including key events.\n\n"
                            "4. 'Insight Analytica': This part delves into the implications and potential impact of the notable occurrences from the day. "
                            "The aim is to maintain neutrality while providing an insightful discussion.\n\n"
                            "5. 'Regional Rundown': Here, you'll focus on pertinent details from different geographical regions. Each significant regional event is identified, "
                            "its importance elucidated, and its implications underscored.\n\n"
                            "6. 'Social Soundbar': This engaging section encourages audience interaction by introducing daily polls, posing questions, or asking for comments "
                            "related to interesting stories in the day's news (avoid using the Russia-Ukraine War in this section, stick to specific unique stories).\n\n"
                            "7. Cortex concludes the broadcast in a unique and thoughtful way."
                        )
                    },

                    {
                        "role": "user", 
                        "content": f"The summaries of this hour's events are: {prompt}. Please craft the hourly news broadcast as per the instructions provided in one complete response (450 words Max). Thank you."
                    }
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error while generating GPT completion: {e}")
        return None
    
def compile_super_summary(summarized_summaries):
    # Compile the GPT prompt
    prompt = compile_prompt(summarized_summaries)
    # Load the OpenAI API key
    api_key = load_openai_api_key()
    # Generate the GPT completion
    compiled_super_summary = generate_gpt_completion(prompt, api_key)
    # Print the completion
    print("GPT Prompt:")
    print(prompt)
    print("GPT Completion:")
    print(compiled_super_summary)
 
    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')  # format the date as 'YYYY-MM-DD'

    # Save the prompt to a file
    with open(f'super_summaries/modular_daily_script_{today}.txt', 'w', encoding='utf-8') as f:
        f.write(f"Super Summary for {today}:\n")
        f.write(compiled_super_summary + "\n")
        return compiled_super_summary