import subprocess
import os
import csv

def process_text_and_triplets(source_text_path, triplets_path, model1_command, model2_command):
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


    prompt = f"Analyze the following source text and its corresponding triplets:\n\nSource Text: {source_text}\n\nTriplets:\n"
    for i, triplet in enumerate(triplets):
        prompt += f"Triplet {i+1}: {triplet[0]}, {triplet[1]}, {triplet[2]}\n"

    prompt += "\nAssess the accuracy and coherence of the triplets in relation to the source text. Identify any missing information, inconsistencies, or inaccuracies. Suggest improvements or corrections for each triplet.\n\nProvide your analysis structured like this:\n\nTriplet 1:\nAccuracy: [Assessment of accuracy]\nInaccuracy: [Description of inaccuracies, if any]\nCorrection: [Suggested correction, if needed]\n\nTriplet 2:\n...\nand so on."


    # --- Model 1 ---
    try:
        model1_process = subprocess.run(model1_command + [prompt], capture_output=True, text=True, check=True)
        model1_output = model1_process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Model 1: {e}")
        print(f"Return code: {e.returncode}, Output: {e.stderr}")
        return None

    # --- Model 2 ---
    model2_prompt = f"Review the following analysis:\n\n{model1_output}\n\nFurther refine the analysis, providing more specific suggestions for improvement and clearly stating any remaining inconsistencies or inaccuracies. Finally, return the list of BEST TRIPLETS."
    try:
        model2_process = subprocess.run(model2_command + [model2_prompt], capture_output=True, text=True, check=True)
        model2_output = model2_process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running Model 2: {e}")
        print(f"Return code: {e.returncode}, Output: {e.stderr}")
        return None

    return model2_output



def evaluate_triplets(model1_command, model2_command, source_texts_folder, triplets_folder, output_folder):
    """Evaluates triplets for all source texts."""
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(source_texts_folder):
        if filename.endswith(".txt"):
            file_id = filename[:-4] # Extract ID (e.g., '1' from '1.txt')
            source_text_path = os.path.join(source_texts_folder, filename)
            triplets_path = os.path.join(triplets_folder, f"{file_id}_triplets.csv")

            analysis = process_text_and_triplets(source_text_path, triplets_path, model1_command, model2_command)

            if analysis:
                output_filename = os.path.join(output_folder, f"{file_id}_analysis.txt")
                with open(output_filename, "w", encoding="utf-8") as outfile:
                    outfile.write(analysis)
                print(f"Analysis for {file_id} saved to {output_filename}")


# Example usage (assuming your LLM wrapper takes a list of arguments):
if __name__ == "__main__":
    MODEL1_COMMAND = ["llm", "-m", "gpt-4o"]  
    MODEL2_COMMAND = ["llm", "-m", "groq-llama3"]  
    SOURCE_TEXTS_FOLDER = "source-texts"
    TRIPLETS_FOLDER = "results/triplets"
    OUTPUT_FOLDER = "triplet_analyses"

    evaluate_triplets(MODEL1_COMMAND, MODEL2_COMMAND, SOURCE_TEXTS_FOLDER, TRIPLETS_FOLDER, OUTPUT_FOLDER)
