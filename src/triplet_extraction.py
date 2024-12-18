import os
import llm
import re

# Ensure results directory exists
os.makedirs("results", exist_ok=True)

PREDICATES_FILE = "predicates.txt"
DEFINITIONS_FILE ="definitions.txt"


def read_predicates_from_file(filepath):
    """Reads predicates from a text file, one predicate per line."""
    try:
        with open(filepath, 'r') as f:
            predicates = [line.strip() for line in f if line.strip()]
        return predicates
    except FileNotFoundError:
        print(f"Error: Predicates file '{filepath}' not found.")
        return []

def read_definitions_from_file(filepath):
    """Reads definitions from a text file, one definition per line."""
    try:
        with open(filepath, 'r') as f:
            definitions = [line.strip() for line in f if line.strip()]
        return definitions
    except FileNotFoundError:
        print(f"Error: Predicates file '{filepath}' not found.")
        return []


# Get the LLM model

model = llm.get_model("themodel")


# Path to the ready-to-go folder

input_folder = "results/namefixed" #skipping citation, coreferee

# Read predicates from file
initial_list_predicates = read_predicates_from_file(PREDICATES_FILE)
if not initial_list_predicates:
    print("Failed to read predicates. Exiting.")
    exit(1)

initial_list_definitions = read_definitions_from_file(PREDICATES_FILE)
if not initial_list_definitions:
    print("Failed to read definitions. Exiting.")
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
        output_path = os.path.join("results/triplets", output_filename)

        # Convert the predicates list to a comma-separated string
        predicates_str = ", ".join(initial_list_predicates)  ### change predicates here
        definitions_str = ", ".join(initial_list_definitions)


        # Open the output file to write results
        with open(output_path, "w") as output_file:
            # Write CSV header
            output_file.write("subject,verb,object\n")

            # Iterate through each paragraph
            for paragraph_index, paragraph in enumerate(paragraphs, 1):
                prompt = paragraph + f"""
    Analyze the provided text and extract subject-verb-object triplets that accurately represent its core meaning.  Your output MUST adhere to the following STRICT rules:

    1. **Errors will be punished:** You have 30 tokens. Every time you make a mistake, you are electrocuted and you lose a token. Each loss of a token adds ten seconds of electrocution.
    2. **Predicate Constraint:** The verb in each triplet MUST be one of the following verbs: {predicates_str}.  No other verbs are allowed. This list of definitions explains how you should understand each verb: {definitions_str}
    3. **Named Entity Subjects and Objects:**  Use only explicitly named entities (people, organizations, locations, objects) found within the text as subjects and objects.  Pronouns or implied entities are NOT permitted.
    4. **Prepositions:** Pay attention to grammatical sense, such that prepositions are correctly used.
    5. **Empty input paragraphs:** If the input is empty, return nothing and make no comment.
    6. **CSV Format:** Output the triplets as a comma-separated value (CSV) string with columns 'subject','verb','object'.
    7. **Each row MUST contain a subject, predicate, and object.  
    7. **Row Endings:** Each row of new data has a newline character at the end.
    8. **Return just the response:** Do not include any headers or other explanatory text.


    Text:
    {paragraph}

    Triplets (CSV):"""


                # Send the prompt to the LLM and get the response
                try:
                    response = model.prompt(prompt)#, temperature=0) # alter this if your model via llm allows you to set temperature. smol doesn't
                    #for chunk in response:
                    #    print(chunk, end="")
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

print("Extraction complete. Results saved in 'results/triplets' folder.")



