import csv
import os
import pandas as pd
import argparse
import networkx as nx
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

# Configuration: Path to the predicates file
PREDICATES_FILE = "predicates.txt" 

def read_predicates_from_file(filepath):
    """Reads predicates from a text file, one predicate per line."""
    try:
        with open(filepath, 'r') as f:
            predicates = [line.strip() for line in f if line.strip()]  # Remove empty lines
        return predicates
    except FileNotFoundError:
        print(f"Error: Predicates file '{filepath}' not found.")
        return []  # Return an empty list if the file is not found

def error_check_predicates(input_file, output_file, valid_predicates=None):
    """
    Check CSV file for valid predicates and column count.

    Args:
    input_file (str): Path to input CSV file
    output_file (str): Path to output error-checked file
    valid_predicates (list): List of valid predicate verbs
    """
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write header
        header = next(reader)
        writer.writerow(header)

        for row in reader:
            # Mark line with ### if more than 3 columns
            if len(row) != 3:
                row.insert(0, '###')
                writer.writerow(row)
                continue

            # Check predicate validity - EXACT MATCH ONLY
            verb = row[1].strip()
            if verb not in valid_predicates:
                row.insert(0, '###')

            writer.writerow(row)

def error_process_all_files(input_dir='results/triplets', output_dir='results/check'):
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.endswith('_triplets.csv'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'checked_{filename}')

            error_check_predicates(input_path, output_path, valid_predicates=initial_list_predicates) #### remember to change to whatever list of predicates you're using!
            print(f'Processed:{output_dir}/{filename}')

def final_process_csv_files(input_folder, output_folder=None):
    # Create output folder if not specified
    if output_folder is None:
        output_folder = input_folder

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through all files in the input folder
    for filename in os.listdir(input_folder):
        # Process only CSV files
        if filename.endswith('.csv'):
            # Full input file path
            input_path = os.path.join(input_folder, filename)

            # Read the CSV file
            thing = pd.read_csv(input_path, names=['subject', 'verb', 'object'], header=0, on_bad_lines='skip')


            # Drop rows with NaN values
            thing = thing.dropna()

            # Replace spaces with underscores in the specified columns
            thing['subject'] = thing['subject'].str.replace(' ', '_')
            thing['verb'] = thing['verb'].str.replace(' ', '_')
            thing['object'] = thing['object'].str.replace(' ', '_')

            #extraneous periods or apostrophes too
            thing['subject'] = thing['subject'].str.replace(r"\b['’.]\b", "", regex=True)
            thing['object'] = thing['object'].str.replace(r"\b['’.]\b", "", regex=True)

            #remove `the`
            for col in ['subject', 'object']:  # Add more columns as needed
              thing[col] = thing[col].str.replace(r'^the_', '', regex=True)

            # Lowercase only specific columns
            # This will preserve the case of the 'verb' column
            for col in [thing.columns[0], thing.columns[-1]]:  # subject and object columns
                thing[col] = thing[col].astype(str).str.lower()

            # Remove quotation marks from the first and last columns
            for col in [thing.columns[0], thing.columns[-1]]:
                thing.loc[:, col] = thing[col].astype(str).str.strip('"')

            # Create output filename (optionally add a prefix or suffix)
            output_filename = f"processed_{filename}"
            output_path = os.path.join(output_folder, output_filename)

            # Save the processed DataFrame to a new CSV file
            thing.to_csv(output_path, index=False)

            print(f"Processed: {filename} → {output_filename}")

def concatenate_csv_files(input_folder, output_filename='combined_output.csv'):
    # List to store all dataframes
    all_dataframes = []

    # Flag to track whether headers have been processed
    first_file = True

    # Iterate through all files in the input folder
    for filename in sorted(os.listdir(input_folder)):
        # Process only CSV files
        if filename.endswith('.csv'):
            # Full input file path
            input_path = os.path.join(input_folder, filename)

            # Read the CSV file
            if first_file:
                # For the first file, read with headers
                df = pd.read_csv(input_path)
                all_dataframes.append(df)
                first_file = False
            else:
                # For subsequent files, skip the header row
                df = pd.read_csv(input_path, header=None, skiprows=1)

                # Ensure the columns match the first file
                if len(df.columns) == len(all_dataframes[0].columns):
                    df.columns = all_dataframes[0].columns
                    all_dataframes.append(df)
                else:
                    print(f"Skipping {filename}: Column mismatch")

    # Concatenate all dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    # Save the combined dataframe
    combined_df.to_csv(output_filename, index=False)

    print(f"Combined {len(all_dataframes)} files into {output_filename}")
    print(f"Total rows: {len(combined_df)}")

def csv_to_gexf(input_csv, output_gexf, source_col='source', target_col='target', weight_col=None, relationship_col='relationship'):
    """
    Convert a CSV file to a GEXF network file.

    Args:
        input_csv (str): Path to the input CSV file.
        output_gexf (str): Path to the output GEXF file.
        source_col (str, optional): Name of the source node column. Defaults to 'source'.
        target_col (str, optional): Name of the target node column. Defaults to 'target'.
        weight_col (str, optional): Name of the weight column. Defaults to None.
        relationship_col (str, optional): Name of the relationship column (used for edge labels). Defaults to 'relationship'.

    Returns:
        networkx.Graph: The created network graph.
    """
    # Read the CSV file
    try:
        df = pd.read_csv(input_csv)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

    # Validate required columns
    if source_col not in df.columns or target_col not in df.columns:
        print(f"Error: Required columns {source_col} or {target_col} not found in the CSV.")
        return None

    # Create a graph
    G = nx.from_pandas_edgelist(
        df,
        source=source_col,
        target=target_col,
        edge_attr=([weight_col] if weight_col and weight_col in df.columns else None)
    )

    # Prepare GEXF XML structure
    gexf = ET.Element('gexf', {
        'xmlns': 'http://www.gexf.net/1.2draft',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': 'http://www.gexf.net/1.2draft http://www.gexf.net/1.2draft/gexf.xsd',
        'version': '1.2'
    })

    # Meta information
    meta = ET.SubElement(gexf, 'meta')
    ET.SubElement(meta, 'creator').text = 'CSV to GEXF Converter'
    ET.SubElement(meta, 'description').text = f'Network generated from {input_csv}'

    # Graph element
    graph = ET.SubElement(gexf, 'graph', {'defaultedgetype': 'undirected'})

    # Nodes
    nodes = ET.SubElement(graph, 'nodes')
    for i, node in enumerate(G.nodes()):
        node_elem = ET.SubElement(nodes, 'node', {
            'id': str(node),
            'label': str(node)
        })

    # Edges
    edges = ET.SubElement(graph, 'edges')
    for i, (source, target, data) in enumerate(G.edges(data=True)):
        # Find the corresponding row in the original DataFrame
        matching_row = df[(df[source_col] == source) & (df[target_col] == target)]

        edge_attrs = {
            'id': str(i),
            'source': str(source),
            'target': str(target)
        }

        # Add weight if available
        if weight_col and weight_col in data:
            edge_attrs['weight'] = str(data[weight_col])

        # Add relationship label if column exists
        if relationship_col in df.columns and not matching_row.empty:
            relationship_value = matching_row[relationship_col].iloc[0]
            edge_attrs['label'] = str(relationship_value)

        ET.SubElement(edges, 'edge', edge_attrs)

    # Convert to pretty-printed XML
    rough_string = ET.tostring(gexf, 'utf-8')
    reparsed = minidom.parseString(rough_string)

    # Write to file
    with open(output_gexf, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))

    print(f"GEXF file created successfully: {output_gexf}")
    print(f"Network stats - Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    return G

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files.")
    parser.add_argument("action", choices=["error_check", "final_process", "concatenate", "gexf"], help="Action to perform")
    parser.add_argument("--input_dir", default="results/error_check", help="Input directory (default: error-check)")
    parser.add_argument("--output_dir", default="results/final_process", help="Output directory (default: final_process)")
    parser.add_argument("--output_file", default="results/combined_output.csv", help="Output filename for concatenation (default: combined_output.csv)")
    args = parser.parse_args()

    initial_list_predicates = read_predicates_from_file(PREDICATES_FILE)
    if not initial_list_predicates:
        print("Failed to read predicates. Exiting.")
        exit(1)

    if args.action == "error_check":
        error_process_all_files(args.input_dir, args.output_dir)
    elif args.action == "final_process":
        final_process_csv_files(args.input_dir, args.output_dir)
    elif args.action == "concatenate":
        concatenate_csv_files(args.input_dir, args.output_file)
    elif args.action == "gexf":
        csv_to_gexf(
            input_csv='results/final_combined_output.csv',  # Adjust as needed
            output_gexf='results/final_combined_output.gexf',  # Adjust as needed
            source_col='subject',
            target_col='object',
            relationship_col='verb'
        )