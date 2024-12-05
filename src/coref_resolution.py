import coreferee, spacy
import spacy_transformers
import os

# Load the Spacy language model and add the Coreferee pipeline component
nlp = spacy.load('en_core_web_trf')
nlp.add_pipe('coreferee')

# Define the input folder containing text files and the output folder for the resolved texts
input_folder = "results/step-two"  # Replace with the path to your input folder
output_folder = "results/step-three"  # Replace with the path to your output folder

# Create output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over all text files in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        # Construct the full file paths
        input_file_path = os.path.join(input_folder, filename)
        output_file_path = os.path.join(output_folder, filename)

        # Read the content of the text file
        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Process the text with Spacy and Coreferee
        coref_doc = nlp(text)

        # Perform entity co-resolution
        resolved_text = ""
        for token in coref_doc:
            repres = coref_doc._.coref_chains.resolve(token)
            if repres:
                resolved_text += " " + " and ".join([t.text for t in repres])
            else:
                resolved_text += " " + token.text

        # Write the resolved text to the output file
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(resolved_text.strip())  # Remove leading space