import os
import re
import spacy
from typing import List, Dict

def extract_full_names(text: str) -> Dict[str, str]:
    """
    Extract full names from the text by looking for patterns of firstname lastname.

    Args:
        text (str): Input text to extract names from

    Returns:
        Dict[str, str]: A dictionary mapping surnames to full names
    """
    # Load SpaCy model
    nlp = spacy.load("en_core_web_lg")

    # Process the text
    doc = nlp(text)

    # Dictionary to store full names
    full_names = {}

    # Track previously seen firstname-lastname combinations
    name_mentions = []

    # First pass: identify full names from named entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name_parts = ent.text.split()
            if len(name_parts) > 1:
                full_name = ent.text
                surname = name_parts[-1]

                # Ensure uniqueness and completeness
                if surname not in full_names or len(full_name.split()) > len(full_names[surname].split()):
                    full_names[surname] = full_name

    # Second pass: look for firstname lastname patterns not caught by NER
    for i in range(len(doc) - 1):
        # Look for sequences of capitalized tokens that could be names
        if (doc[i].is_title and doc[i+1].is_title and
            doc[i].text not in ['A', 'An', 'The'] and
            doc[i+1].text not in ['A', 'An', 'The']):

            full_name = f"{doc[i].text} {doc[i+1].text}"
            surname = doc[i+1].text

            # Add to full names if not already present or is more complete
            if surname not in full_names or len(full_name.split()) > len(full_names[surname].split()):
                full_names[surname] = full_name

    return full_names

def replace_surnames(text: str) -> str:
    """
    Replace standalone surnames with their full names.

    Args:
        text (str): Input text to process

    Returns:
        str: Processed text with surnames replaced
    """
    # Load SpaCy model
    nlp = spacy.load("en_core_web_lg")

    # Extract full names
    full_names = extract_full_names(text)

    # Process the text
    doc = nlp(text)

    # Create a list to track modifications
    modified_tokens = []

    # Track whether we've already replaced a name to avoid duplicates
    replaced_indices = set()

    # Iterate through tokens
    for i, token in enumerate(doc):
        # Check if the token is a standalone surname to replace
        should_replace = (
            token.text in full_names and
            i not in replaced_indices and
            # Ensure it's a true standalone word
            ((i == 0 or not doc[i-1].text.lower() in full_names[token.text].lower().split()) and
             (i == len(doc)-1 or not doc[i+1].text.lower() in full_names[token.text].lower().split())) and
            # Avoid replacing within multi-word names or references
            not any(full_name.startswith(token.text) for full_name in full_names.values())
        )

        if should_replace:
            # Replace with full name
            modified_tokens.append(full_names[token.text])
            replaced_indices.add(i)
        else:
            # Keep original token
            modified_tokens.append(token.text)

    # Reconstruct the text
    modified_text = ' '.join(modified_tokens)

    return modified_text

def main():
    # Ensure output folder exists
    input_folder = "source-texts"
    #output_folder = "results/step-one" # when we want to do citation_removal.py next
    output_folder = "results/step-two"
    
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Process each text file
    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            # Construct the full file paths
            input_file_path = os.path.join(input_folder, filename)
            output_file_path = os.path.join(output_folder, filename)

            # Read the content of the text file
            try:
                with open(input_file_path, 'r', encoding='utf-8') as file:
                    text = file.read()

                # Replace surnames and write to output file
                with open(output_file_path, 'w', encoding='utf-8') as file:
                    file.write(replace_surnames(text))

                print(f"Now find under step-one -> Name Replacement Processed: {filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()