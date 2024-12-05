import spacy
import re
import os

nlp = spacy.load("en_core_web_lg")

def remove_citations(text):
    """Removes in-text citations from text using SpaCy and regex."""
    text = re.sub(r'\([^)]*\)', '', text)  #Efficient regular expression based removal
    return text


def process_folder(input_folder, output_folder):
    """Processes all .txt files in the input folder, removing citations, and saves to output folder."""
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            try:
                with open(input_path, 'r', encoding='utf-8') as infile:
                    text = infile.read()
                cleaned_text = remove_citations(text)
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    outfile.write(cleaned_text)
                print(f"Now find under step-two -> Citation Removal Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

input_folder = "results/step-one"
output_folder = "results/step-two"
process_folder(input_folder, output_folder)
