#!/bin/bash

# Create directories
mkdir -p results/{step-one,step-two,step-three,step-four,step-five,finished}

# Run the initial stages of the pipeline
python src/name_replacement.py
python src/citation_removal.py
python src/coref_resolution.py
python src/triplet_extraction.py

# Run error checking
python src/csv_processing.py error_check

echo "Error checking complete. Files in 'results/step-five' need manual inspection."
echo "Open each 'checked_*.csv' file, fix errors, and save changes."
echo "Press ENTER once you've completed the manual checks..."
read

# Continue processing after manual checks
python src/csv_processing.py final_process --input_dir results/step-five --output_dir results/finished
python src/csv_processing.py concatenate --input_dir results/finished --output_file results/final_combined_output.csv
python src/csv_processing.py gexf

echo "Final CSV processing and concatenation done. Output in 'results/finished' directory and GEXF generated."