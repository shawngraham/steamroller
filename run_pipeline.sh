#!/bin/bash

# Create directories
mkdir -p results/{namefixed,triplets,error_check,finished}

# Run the initial stages of the pipeline
python src/name_replacement.py
#python src/citation_removal.py
#python src/coref_resolution.py
python src/triplet_extraction.py

# Run error checking
python src/csv_processing.py error_check --input_dir results/triplets --output_dir results/error_check

echo "Error checking complete. Files in 'results/error_check' need manual inspection."
echo "Open each 'checked_*.csv' file, fix errors, and save changes."
echo "Press ENTER once you've completed the manual checks..."
read

# Continue processing after manual checks
python src/csv_processing.py final_process --input_dir results/error_check --output_dir results/final_process
python src/csv_processing.py concatenate --input_dir results/final_process --output_file results/finished/final_combined_output.csv
python src/csv_processing.py gexf 