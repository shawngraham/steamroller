import subprocess
import os
import csv
import re

def load_predicates(predicates_filepath):
    """Loads predicates from a file."""
    try:
        with open(predicates_filepath, 'r', encoding='utf-8') as f:
            predicates = [line.strip() for line in f]
        return predicates
    except FileNotFoundError:
        print(f"Error: Predicates file not found at {predicates_filepath}")
        return None
    except Exception as e:
        print(f"Error reading predicates file: {e}")
        return None


def process_text_and_triplets(source_text_path, triplets_path, predicates, model1_command, model2_command): #predicates added here
    """Processes a single source text and its corresponding triplets using subprocess."""
    try:
        with open(source_text_path, 'r', encoding='utf-8') as f:
            source_text = f.read()
    except FileNotFoundError:
        print(f"Error: Source text file not found at {source_text_path}")
        return None
    except Exception as e:
        print(f"Error reading source text: {e}")
        return None

    triplets = []
    try:
        with open(triplets_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip the header row if it exists.
            for row in reader:
                triplets.append((row[0], row[1], row[2]))
    except FileNotFoundError:
        print(f"Error: Triplets file not found at {triplets_path}")
        return None
    except Exception as e:
        print(f"Error reading triplets file: {e}")
        return None


    prompt = f"""Analyze the following source text and its corresponding triplets, ensuring all triplets utilize predicates from the provided list:\n\nSource Text: {source_text}\n\nPredicates: {', '.join(predicates)}\n\nTriplets:\n"""
    for i, triplet in enumerate(triplets):
        prompt += f"Triplet {i+1}: {triplet[0]}, {triplet[1]}, {triplet[2]}\n"

    prompt += "\nAssess the accuracy and coherence of the triplets in relation to the source text and ensure each triplet utilizes at least one predicate from the provided list. Identify any missing information, inconsistencies, or inaccuracies. Suggest improvements or corrections for each triplet, making sure to incorporate appropriate predicates.\n\nProvide your analysis structured like this:\n\nTriplet 1:\nAccuracy: [Assessment of accuracy]\nInaccuracy: [Description of inaccuracies, if any]\nCorrection: [Suggested correction, if needed]\nUsed Predicates: [List of predicates used]\n\nTriplet 2:\n...\nand so on.\n\nThen, provide a set of rewritten triplets based on your analysis, in the following format:\n\nRewritten Triplets:\nTriplet 1: [rewritten_text1], [rewritten_text2], [rewritten_text3]\nTriplet 2: [rewritten_text4], [rewritten_text5], [rewritten_text6]\n..."

    # --- Model 1 ---
    try:
        model1_process = subprocess.run(model1_command + [prompt], capture_output=True, text=True, check=True)
        model1_output = model1_process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Model 1: {e}")
        print(f"Return code: {e.returncode}, Output: {e.stderr}")
        return None, None, None


    # --- Model 2 ---
    model2_prompt = f"""Review the following analysis from Model 1, the original source text, and the provided triplets:\n\nModel 1 Analysis:\n{model1_output}\n\nSource Text:\n{source_text}\n\nPredicates: {', '.join(predicates)}\n\nTriplets:\n""" #Added Model 1 output here
    for i, triplet in enumerate(triplets):
        model2_prompt += f"Triplet {i+1}: {triplet[0]}, {triplet[1]}, {triplet[2]}\n"

    model2_prompt += """\nFurther refine the analysis, providing more specific suggestions for improvement, clearly stating any remaining inconsistencies or inaccuracies, and ensuring the analysis aligns with both the source text and the triplets.  Then, provide a set of rewritten triplets based on your analysis, in the following format:

Rewritten Triplets:
Triplet 1: [rewritten_text1], [rewritten_text2], [rewritten_text3]
Triplet 2: [rewritten_text4], [rewritten_text5], [rewritten_text6]
...
"""


    try:
        model2_process = subprocess.run(model2_command + [model2_prompt], capture_output=True, text=True, check=True)
        model2_output = model2_process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Model 2: {e}")
        print(f"Return code: {e.returncode}, Output: {e.stderr}")
        return None, None


    # Extract rewritten triplets (this is a simple extraction; improve as needed)
    rewritten_triplets_match = re.search(r"Rewritten Triplets:\n(.*)", model2_output, re.DOTALL)
    rewritten_triplets = []
    if rewritten_triplets_match:
        for line in rewritten_triplets_match.group(1).strip().splitlines():
            parts = line.split(": ", 1)
            if len(parts) == 2:
                try:
                    rewritten_triplets.append( [x.strip() for x in parts[1].split(',')])

                except:
                    print(f"Error parsing triplet from Model 2 output: {parts[1]}")
    else:
        print("Could not extract rewritten triplets from Model 2's output.")
        rewritten_triplets = None



    return model1_output, model2_output, rewritten_triplets



def evaluate_triplets(model1_command, model2_command, source_texts_folder, triplets_folder, predicates_filepath, output_folder):
    predicates = load_predicates(predicates_filepath)
    if predicates is None:
        return  # Exit if predicate loading fails

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(source_texts_folder):
        if filename.endswith(".txt"):
            file_id = filename[:-4]
            source_text_path = os.path.join(source_texts_folder, filename)
            triplets_path = os.path.join(triplets_folder, f"{file_id}_triplets.csv")

            model1_result, model2_result, rewritten_triplets = process_text_and_triplets(source_text_path, triplets_path, predicates, model1_command, model2_command)

            if model1_result:
                output_filename = os.path.join(output_folder, f"{file_id}_analysis.txt")
                with open(output_filename, "w", encoding="utf-8") as outfile:
                    outfile.write(f"Model 1 Output:\n{model1_result}\n\nModel 2 Output:\n{model2_result}")
                    if rewritten_triplets:
                        outfile.write("\n\nRewritten Triplets:\n")
                        for i, triplet in enumerate(rewritten_triplets):
                            outfile.write(f"Triplet {i+1}: {', '.join(triplet)}\n")
                print(f"Analysis for {file_id} saved to {output_filename}")



if __name__ == "__main__":
    MODEL1_COMMAND = ["llm", "-m", "gpt-4o"]  # Replace with your actual command
    MODEL2_COMMAND = ["llm", "-m", "groq-llama3"]  # Replace with your actual command
    PREDICATES_FILEPATH = "predicates.txt"  # Make sure this file exists
    SOURCE_TEXTS_FOLDER = "source-texts"  # Make sure this folder exists
    TRIPLETS_FOLDER = "results/triplets"  # Make sure this folder exists
    OUTPUT_FOLDER = "triplet_analyses"  # <--- This line was missing the argument

    evaluate_triplets(MODEL1_COMMAND, MODEL2_COMMAND, SOURCE_TEXTS_FOLDER, TRIPLETS_FOLDER, PREDICATES_FILEPATH, OUTPUT_FOLDER)
