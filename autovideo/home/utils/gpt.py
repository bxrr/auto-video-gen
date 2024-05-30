import re
import os
import g4f
import json

from g4f.client import Client
from dotenv import load_dotenv
from typing import Tuple, List


load_dotenv("../../../.env")


def generate_response(prompt: str) -> str:
    client = Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    ).choices[0].message.content

    return response


def generate_script(video_subject: str, paragraph_number: int, language: str) -> str:
    prompt = f"""
        Generate a script for a video, depending on the subject of the video.

        The script is to be returned as a string with the specified number of paragraphs.

        Here is an example of a string:
        "This is an example string."

        Do not under any circumstance reference this prompt in your response.

        Get straight to the point, don't start with unnecessary things like, "welcome to this video".

        Obviously, the script should be related to the subject of the video.

        YOU MUST NOT INCLUDE ANY TYPE OF MARKDOWN OR FORMATTING IN THE SCRIPT, NEVER USE A TITLE.
        YOU MUST WRITE THE SCRIPT IN THE LANGUAGE SPECIFIED IN [LANGUAGE].
        ONLY RETURN THE RAW CONTENT OF THE SCRIPT. DO NOT INCLUDE "VOICEOVER", "NARRATOR" OR SIMILAR INDICATORS OF WHAT SHOULD BE SPOKEN AT THE BEGINNING OF EACH PARAGRAPH OR LINE. YOU MUST NOT MENTION THE PROMPT, OR ANYTHING ABOUT THE SCRIPT ITSELF. ALSO, NEVER TALK ABOUT THE AMOUNT OF PARAGRAPHS OR LINES. JUST WRITE THE SCRIPT.

        Subject: {video_subject}
        Number of paragraphs: {paragraph_number}
        Language: {language}
    """

    # Generate script
    response = generate_response(prompt)

    print(response)

    # Return the generated script
    if response:
        # Clean the script
        # Remove asterisks, hashes
        response = response.replace("*", "")
        response = response.replace("#", "")

        # Remove markdown syntax
        response = re.sub(r"\[.*\]", "", response)
        response = re.sub(r"\(.*\)", "", response)

        # Split the script into paragraphs
        paragraphs = response.split("\n\n")

        # Select the specified number of paragraphs
        selected_paragraphs = paragraphs[:paragraph_number]

        # Join the selected paragraphs into a single string
        final_script = "\n\n".join(selected_paragraphs)

        # Print to console the number of paragraphs used
        print(f"Number of paragraphs used: {len(selected_paragraphs)}")

        return final_script
    else:
        print("GPT returned an empty response.")
        return None


def get_keywords(vidoe_subject:str, amt:int, script:str)->List[str]: 
  """
  Generate a JSON-Array of search terms for stock videos,
  depending on the subject of a video.

  Args:
      video_subject (str): The subject of the video.
      amount (int): The amount of search terms to generate.
      script (str): The script of the video.
      ai_model (str): The AI model to use for generation.

  Returns:
      List[str]: The search terms for the video subject.
  """

  # Build prompt
  prompt = f"""
  Generate {amount} search terms for stock videos,
  depending on the subject of a video.
  Subject: {video_subject}

  The search terms are to be returned as
  a JSON-Array of strings.

  Each search term should consist of 1-3 words,
  always add the main subject of the video.
    
  YOU MUST ONLY RETURN THE JSON-ARRAY OF STRINGS.
  YOU MUST NOT RETURN ANYTHING ELSE. 
  YOU MUST NOT RETURN THE SCRIPT.
    
  The search terms must be related to the subject of the video.
  Here is an example of a JSON-Array of strings:
  ["search term 1", "search term 2", "search term 3"]

  For context, here is the full text:
  {script}
  """

  # Generate search terms
  response = generate_response(prompt, ai_model)
  print(response)

  # Parse response into a list of search terms
  search_terms = []
  try:
    search_terms = json.loads(response)
    if not isinstance(search_terms, list) or not all(isinstance(term, str) for term in search_terms):
      raise ValueError("Response is not a list of strings.")
  except (json.JSONDecodeError, ValueError):
    # Get everything between the first and last square brackets
    response = response[response.find("[") + 1:response.rfind("]")]

    print(colored("[*] GPT returned an unformatted response. Attempting to clean...", "yellow"))

    # Attempt to extract list-like string and convert to list
    match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
    print(match.group())
    if match:
      try:
        search_terms = json.loads(match.group())
      except json.JSONDecodeError:
        print(colored("[-] Could not parse response.", "red"))
        return []
    
  
  # Let user know
  print(f"\nGenerated {len(search_terms)} search terms: {', '.join(search_terms)}")

  # Return search terms
  return search_terms

def generate_metadata(video_subject: str, script: str, ai_model: str) -> Tuple[str, str, List[str]]:  
  """  
  Generate metadata for a YouTube video, including the title, description, and keywords.  
  
  Args:  
      video_subject (str): The subject of the video.  
      script (str): The script of the video.  
      ai_model (str): The AI model to use for generation.  
  
  Returns:  
      Tuple[str, str, List[str]]: The title, description, and keywords for the video.  
  """  
  
  # Build prompt for title  
  title_prompt = f"""  
  Generate a catchy and SEO-friendly title for a YouTube shorts video about {video_subject}.  
  """  
  
  # Generate title  
  title = generate_response(title_prompt, ai_model).strip()  
    
  # Build prompt for description  
  description_prompt = f"""  
  Write a brief and engaging description for a YouTube shorts video about {video_subject}.  
  The video is based on the following script:  
  {script}  
  """  
  
  # Generate description  
  description = generate_response(description_prompt, ai_model).strip()  
  
  # Generate keywords  
  keywords = get_search_terms(video_subject, 6, script, ai_model)  

  return title, description, keywords  
