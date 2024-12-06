# you need to $pip install tibert transformers
# and you need a huggingface token in your environment HF_TOKEN
# this works just often enough to seem to be worth it, but it fails in spectacular ways occasionally.
# I'm just lodging it here for the day when I decide to give it another try.
# ah computers.

import os
import shutil
from tibert import BertForCoreferenceResolution, predict_coref_simple
from transformers import BertTokenizerFast

# Load model and tokenizer
coref_model = BertForCoreferenceResolution.from_pretrained(
    "compnet-renard/bert-base-cased-literary-coref"
)
tokenizer = BertTokenizerFast.from_pretrained("bert-base-cased")

PRONOUNS = {
    "he", "she", "it", "they", "them", "him", "her", "you", "we", "us",
    "i", "me", "mine", "yours", "ours", "his", "hers", "its", "their", "theirs",
    "myself", "yourself", "himself", "herself", "itself", "ourselves", "yourselves", "themselves"
}

def is_pronoun(mention_tokens):
    """
    Check if a mention is a pronoun.
    """
    return len(mention_tokens) == 1 and mention_tokens[0].lower() in PRONOUNS


def rewrite_text_with_coreferences(text, model, tokenizer):
    """
    Rewrite text by replacing pronouns with their most informative mentions.

    Args:
        text (str): Input text to resolve coreferences
        model: Tibert coreference resolution model
        tokenizer: Corresponding tokenizer

    Returns:
        str: Text with coreferences resolved
    """
    # Perform coreference resolution
    coref_doc = predict_coref_simple(text, model, tokenizer)

    # Find the replacement mapping
    replacements = {}
    for chain in coref_doc.coref_chains:
        if len(chain) > 1:
            # Select the most informative mention as the representative
            representative = select_representative_mention(chain)
            rep_text = ' '.join(representative.tokens)

            # Map other mentions to this representative
            for mention in chain:
                original = ' '.join(mention.tokens)
                if original != rep_text:  # Avoid self-replacement
                    replacements[original] = rep_text

    # Perform replacements
    for original, replacement in replacements.items():
        # Use a more robust method to replace to handle overlapping mentions
        text = re.sub(rf'\b{re.escape(original)}\b', replacement, text)

    return text


# Helper function for mention selection
import re

def is_proper_noun(mention_tokens):
    """
    Heuristic to determine if a mention is a proper noun.
    Assumes proper nouns are capitalized.
    """
    # Check if the first token is capitalized (not at sentence start)
    return all(token[0].isupper() for token in mention_tokens)

def select_representative_mention(chain):
    """
    Select the most informative mention in the chain.
    Prioritize by length, proper noun status, and being non-pronoun.
    """
    return max(
        chain,
        key=lambda m: (len(m.tokens), is_proper_noun(m.tokens), not is_pronoun(m.tokens))
    )



def rewrite_texts_in_folder(input_folder, output_folder, model, tokenizer):
    """
    Rewrite all text files in an input folder to an output folder.

    Args:
        input_folder (str): Path to folder containing input text files
        output_folder (str): Path to folder for rewritten text files
        model: Tibert coreference resolution model
        tokenizer: Corresponding tokenizer
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through files in input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            # Full file paths
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Read input file
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # Rewrite text with coreferences
            rewritten_text = rewrite_text_with_coreferences(text, coref_model, tokenizer)

            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(rewritten_text)

            print(f"Processed: {filename}")

# Example usage, make sure you have the output folder created
input_folder = 'results/namefixed'
output_folder = 'results/coref-results'

rewrite_texts_in_folder(input_folder, output_folder, coref_model, tokenizer)
