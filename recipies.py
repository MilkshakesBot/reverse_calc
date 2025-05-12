from concurrent.futures import ProcessPoolExecutor
import itertools
import json
import os
import csv
import time
from datetime import datetime

# Configuration constants
MAX_MIXIN_LENGTH = 4  # Maximum number of mixins to combine
CHUNK_SIZE = 500000  # Number of permutations per processing chunk
OUTPUT_DIR = "drug_outputs_csv"  # Output directory for CSV files
# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load JSON data files
with open("interactions.json") as f:
    interactions = json.load(f)

with open("mixins.json") as f:
    mixins = json.load(f)

with open("drugs.json") as f:
    drugs = json.load(f)

with open("multipliers.json") as f:
    effect_multipliers = json.load(f)

# Create a list of (ingredient, effect) tuples from the mixins
mixin_effects = [(m["Ingredient"], m["Effect"]) for m in mixins]

# Helper function to log messages with timestamps


def log(msg: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

# Applies effect replacements based on interactions rules


def apply_replacements(effects, ingredient_name):
    # Get replacement rules for the ingredient
    replacements = interactions.get(
        ingredient_name, {}).get("replacements", {})
    updated_effects = set(effects)

    for eff in list(updated_effects):
        repl = replacements.get(eff)
        if isinstance(repl, dict):
            # If the replacement has a condition and it's met, replace the effect
            if repl.get("condition") in updated_effects:
                updated_effects.remove(eff)
                updated_effects.add(repl["replacement"])
        elif repl:
            # If it's a direct replacement, apply it
            updated_effects.remove(eff)
            updated_effects.add(repl)

    return updated_effects

# Generator that yields chunks of mixin permutations up to CHUNK_SIZE


def generate_permutation_chunks():
    for r in range(1, MAX_MIXIN_LENGTH + 1):
        perms = itertools.permutations(mixin_effects, r)
        chunk = []
        for p in perms:
            chunk.append(p)
            if len(chunk) >= CHUNK_SIZE:
                yield chunk
                chunk = []
        if chunk:
            yield chunk

# Process a single chunk of permutations for a given drug


def process_permutation_chunk(drug, chunk):
    # Parse base effects and base price from the drug
    base_effects = set(drug["Effect"]) if drug["Effect"] != "None" else set()
    base_price = drug["Base Price"]
    rows = []

    # Iterate through each permutation of mixins
    for perm in chunk:
        current_effects = set(base_effects)
        mixin_names = []
        total_mixin_cost = 0  # Track total cost of all mixins used

        for mixin_name, mixin_effect in perm:
            mixin_names.append(mixin_name)
            current_effects = apply_replacements(current_effects, mixin_name)
            current_effects.add(mixin_effect)

            # Add the price of the current mixin to the total
            mixin_price = next(m["Price"]
                               for m in mixins if m["Ingredient"] == mixin_name)
            total_mixin_cost += mixin_price

        total_multiplier = 0
        multipliers_details = []

        # Calculate the total multiplier from all current effects
        for effect in current_effects:
            multiplier = effect_multipliers.get(
                effect, {}).get("Multiplier", 0)
            if multiplier > 0:
                total_multiplier += multiplier
                multipliers_details.append((effect, multiplier))

        # Compute final drug price based on base price and multiplier
        final_price = int(round(base_price * (1 + total_multiplier)))
        profit = final_price - total_mixin_cost  # Net profit calculation

        # Append a row with data about the combination
        rows.append([
            "".join(sorted(mixin_names)),                  # No commas, sorted
            # No commas, deduplicated and sorted
            "".join(sorted(set(current_effects))),
            final_price,
            profit,
            total_mixin_cost
        ])

    return rows


def process_drug_parallel(drug):
    log(f"==> Starting {drug['Product']}")
    start = time.time()

    chunk_counter = 0
    file_counter = 1
    current_rows = []

    output_base = os.path.join(
        OUTPUT_DIR, f"{drug['Product'].replace(' ', '_')}_part")

    # Writes a batch of rows to a CSV file
    def write_chunk(rows, index):
        file_path = f"{output_base}{index}.csv"
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Mixins", "Effects", "Price", "Profit", "Cost"])
            writer.writerows(rows)
        log(f"Wrote {len(rows):,} rows to {file_path}")

    # Iterate through permutation chunks and process them
    for chunk in generate_permutation_chunks():
        rows = process_permutation_chunk(drug, chunk)
        for row in rows:
            current_rows.append(row)
            chunk_counter += 1
            # Once enough rows are collected, write to file
            if chunk_counter >= 1_000_000:
                write_chunk(current_rows, file_counter)
                file_counter += 1
                current_rows = []
                chunk_counter = 0

    # Write any remaining rows
    if current_rows:
        write_chunk(current_rows, file_counter)

    log(f"<== Finished {drug['Product']} in {time.time() - start:.2f}s")

# Entry point for the script


def main():
    # Use ProcessPoolExecutor to parallelize over the drugs
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        # Process all drugs in parallel
        executor.map(process_drug_parallel, drugs)


if __name__ == "__main__":
    main()
