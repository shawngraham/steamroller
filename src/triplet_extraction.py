import os
import llm
import re

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

PREDICATES_FILE = "predicates.txt"


def read_predicates_from_file(filepath):
    """Reads predicates from a text file, one predicate per line."""
    try:
        with open(filepath, 'r') as f:
            predicates = [line.strip() for line in f if line.strip()]
        return predicates
    except FileNotFoundError:
        print(f"Error: Predicates file '{filepath}' not found.")
        return []

# Get the LLM model

model = llm.get_model("themodel")
#model = llm.get_model("gemini-1.5-flash-001")


# Path to the ready-to-go folder
input_folder = "results/step-three"

# Read predicates from file
initial_list_predicates = read_predicates_from_file(PREDICATES_FILE)
if not initial_list_predicates:
    print("Failed to read predicates. Exiting.")
    exit(1)

# Iterate through all text files in the ready-to-go folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        # Full path to the input file
        input_path = os.path.join(input_folder, filename)

        # Read the text content
        with open(input_path, "r") as file:
            text_content = file.read()

        # Split the text content into paragraphs using regular expressions
        # This is so that everything fits inside the context window
        paragraphs = re.split(r'\n\s*\n', text_content)

        # Prepare output file path in results folder
        output_filename = filename.replace(".txt", "_triplets.csv")
        output_path = os.path.join("results/step-four", output_filename)

        # Convert the predicates list to a comma-separated string
        predicates_str = ", ".join(initial_list_predicates)  ### change predicates here

        # Open the output file to write results
        with open(output_path, "w") as output_file:
            # Write CSV header
            output_file.write("subject,verb,object\n")

            # Iterate through each paragraph
            for paragraph_index, paragraph in enumerate(paragraphs, 1):
                prompt = paragraph + f"""\n\n Extract subject,verb,object triplets that capture the nuance of the text.
                Your output will be in csv format with columns 'subject','verb','object'.
                STRICT RULES FOR ENTITY EXTRACTION:
                - Use only substantive, named entities from the main text.
                - Use the full name of any organizations or museums.
                - The 'subject' must be a singular thing.
                - The 'object' must be a singular thing. Use multiple lines for multiple objects.
                - The target predicates are {predicates_str}.
                - ONLY USE THE TARGET PREDICATES. This is mission critical and you will be punished if you do not!
                - RETURN ONLY THE LIST OF TRIPLETS.
                - If no text is provided, return [null],[null],[null]"""


                # Send the prompt to the LLM and get the response
                try:
                    response = model.prompt(prompt, temperature=0)

                    # Combine response chunks
                    full_response = ''.join(chunk for chunk in response)

                    # Print the response for the current paragraph to console
                    print(f"Paragraph {paragraph_index} from {filename}:")
                    print(full_response)
                    print("\n---\n")

                    # Write the response to the output file
                    output_file.write(full_response)
                except Exception as e:
                    print(f"Error processing paragraph {paragraph_index} in {filename}: {e}")

print("Extraction complete. Results saved in 'step-four' folder.")



