# Schedule 1 Reverse Recipe Generator

A Python tool that programmatically generates all possible combinations of recipes listed in _Schedule 1_, then prints them to a file.

## 📜 Project Status

- **Current Status:** The tool is functional, but not yet optimized for performance.
  - The recipe generation and deduplication processes are split into two separate scripts: `recipies.py` and `dedupe.py`.
- **Known Issues:**

  - The deduplication script (`dedupe.py`) is not fully functional and may not work as intended.
    - However for testing purposes, it can be run on a small set of ingredients to verify its functionality.
  - The code does not currently deduplicate recipes that result in the same effects all in one script.
  - The script may take a long time to run, especially with large ingredient sets.
  - The tool consumes significant memory and CPU resources.

- **Planned Improvements:**

  - Optimize the code to reduce runtime and memory usage.
  - Merge the two scripts into a single script for better usability.
    - Handle deduplication as new recipes are generated to avoid excessive file sizes.

## 🔧 Features

- Generates every valid combination of Schedule 1 recipes.
- Outputs all results to a CSV file.
- Includes calculated Price, Profit, and Cost for each recipe.
- Uses shorthand notation for drugs, interactions, and mixins to minimize file size.

## 📆 Requirements

- Python 3.7+
- No external dependencies (pure Python)

## 🚀 Usage

1. Clone the repository:

```bash
git clone https://github.com/MilkshakesBot/reverse_calc.git
cd reverse_calc
```

2. Run the script:

```bash
python recipies.py
```

```bash
python dedupe.py
```

3. Find the output files in the project directory (e.g., `CE_part1.csv`, `MH_part1.csv`).

## 📁 Output

The tool generates files typically named:

```
<shortened_name>_part1.csv
```

Each line represents a unique recipe configuration based on the Schedule 1 data.

> **Note:** With 8 ingredients, the output can exceed **100 GB** in size and generate over **500** differnt csv files per drug before deduplication. Each file has 1 million recipies. There are a total of 3 billion recipies with 8 ingredients. Adding more ingredients causes exponential growth in file size and combination count. Ensure sufficient disk space and memory capacity.

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://github.com/MilkshakesBot/reverse_calc/blob/main/LICENSE).

## 🡋 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss your proposed changes.
