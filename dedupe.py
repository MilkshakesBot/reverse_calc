import os
import csv
import multiprocessing
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

# Helper function to generate a key from the 'Effects' column by sorting the effects


def get_effect_key(row):
    return tuple(sorted(effect.strip() for effect in row['Effects'].split(',')))

# Process a chunk of files, extracting the highest profit for each unique effect combination


def process_file_chunk(file_chunk, input_dir):
    local_map = {}  # Dictionary to store the best profit for each effect combination
    for filename in file_chunk:
        if not filename.endswith('.csv'):  # Skip non-CSV files
            continue
        with open(os.path.join(input_dir, filename), newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)  # Read each file as a CSV with headers
            for row in reader:
                try:
                    # Get a unique key for the 'Effects' column
                    key = get_effect_key(row)
                    profit = float(row['Profit'])  # Extract profit as a float
                    # If this effect key is not seen before or the profit is higher, update the local map
                    if key not in local_map or profit > local_map[key]:
                        local_map[key] = profit
                except Exception as e:
                    print(f"Error processing row: {row}, Error: {e}")
                    continue
    return local_map

# Merge multiple partial result maps into one, keeping the highest profit for each effect combination


def merge_maps(maps):
    merged = {}
    for partial in maps:
        for key, profit in partial.items():
            # If this effect combination is not seen or the profit is higher, update merged map
            if key not in merged or profit > merged[key]:
                merged[key] = profit
    return merged

# Write the best recipes (highest profit) for each unique effect combination to the output file


def write_best_recipes_to_file(output_file, input_dir, effect_max_profit, prefix):
    # Track which effect combinations have been written to avoid duplicates
    written_keys = set()
    with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
        writer = None
        for filename in os.listdir(input_dir):
            if not filename.endswith('.csv'):  # Skip non-CSV files
                continue
            with open(os.path.join(input_dir, filename), newline='', encoding='utf-8') as f:
                # Read each file as a CSV with headers
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Get a unique key for the 'Effects' column
                        key = get_effect_key(row)
                        # Extract profit as a float
                        profit = float(row['Profit'])
                        # If the profit matches the best profit for this effect and not written yet, write the row
                        if profit == effect_max_profit.get(key) and key not in written_keys:
                            if not writer:  # Initialize the CSV writer if it hasn't been done
                                writer = csv.DictWriter(
                                    out_f, fieldnames=reader.fieldnames)
                                writer.writeheader()  # Write headers once
                            writer.writerow(row)  # Write the row
                            # Mark the effect combination as written
                            written_keys.add(key)
                    except Exception as e:
                        print(f"Error processing row: {row}, Error: {e}")
                        continue

# Utility function to split a list into chunks of size n


def chunk_list(lst, n):
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))

# Group files by their prefix (assumes filenames are structured with prefixes)


def group_files_by_prefix(files):
    # Default dictionary to group files by prefix
    grouped_files = defaultdict(list)
    for filename in files:
        # Extract prefix before the first underscore
        prefix = filename.split('_')[0]
        grouped_files[prefix].append(filename)  # Group the files by prefix
    return grouped_files

# Process the grouped files, using multiprocessing for scanning and threading for writing results


def process_grouped_files(grouped_files, input_dir, output_dir, num_workers):
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with ThreadPoolExecutor() as executor:
        futures = []  # List to hold futures for concurrent tasks
        for prefix, files in grouped_files.items():
            print(f"Processing group: {prefix} with {len(files)} files...")
            # Split files into chunks
            file_chunks = list(chunk_list(files, num_workers))

            print(
                f"Pass 1: Using {num_workers} processes to scan {len(files)} files...")

            with multiprocessing.Pool(processes=num_workers) as pool:
                # Use multiprocessing to process chunks of files
                partial_maps = pool.starmap(
                    process_file_chunk, [(chunk, input_dir) for chunk in file_chunks])

            print("Merging results from workers...")
            # Merge the results from all workers
            effect_max_profit = merge_maps(partial_maps)

            print(f"Found {len(effect_max_profit)} unique effect sets.")

            output_file = os.path.join(
                # Output file for this group
                output_dir, f'{prefix}_deduplicated.csv')
            print(f"Pass 2: Writing final deduplicated CSV for {prefix}...")

            # Submit the write task to the executor (this will run in a separate thread)
            futures.append(executor.submit(
                write_best_recipes_to_file, output_file, input_dir, effect_max_profit, prefix))

        for future in futures:
            future.result()  # Wait for all write tasks to finish

    print("Finished writing all deduplicated CSVs.")

# Main entry point for the script


def main():
    input_dir = 'drug_outputs_csv'  # Directory containing input CSV files
    output_dir = 'drug_deduped_csv'  # Directory to store the output CSV files
    # Number of workers based on available CPU cores
    num_workers = multiprocessing.cpu_count()

    files = [f for f in os.listdir(input_dir) if f.endswith(
        '.csv')]  # List CSV files in input directory
    grouped_files = group_files_by_prefix(files)  # Group files by their prefix

    # Process the grouped files using multiprocessing and threading
    process_grouped_files(grouped_files, input_dir, output_dir, num_workers)

    print("Done.")  # Indicate the script has finished


# Run the main function when the script is executed
if __name__ == "__main__":
    main()
