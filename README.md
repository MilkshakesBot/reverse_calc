# Schedule 1 Reverse Recipe Generator

A Python tool that programmatically generates all possible combinations of recipes listed in _Schedule 1_, then prints them to a file.

## 📜 Project Status

- **Current Status:** The tool is functional, but not yet optimized for performance.
- **Known Issues:**

  - The code does not currently deduplicate recipes that result in the same effects.
  - The script may take a long time to run, especially with large ingredient sets.
  - The tool consumes significant memory and CPU resources.

- **Planned Improvements:**

  - Implement deduplication of recipes with the same effect.

    - Retain only the most profitable and/or cost-effective version of duplicate-effect recipes.

  - Optimize the code to reduce runtime and memory usage.

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
git clone https://github.com/yourusername/schedule1-reverse-generator.git
cd schedule1-reverse-generator
```

2. Run the script:

```bash
python generate_recipes.py
```

3. Find the output files in the project directory (e.g., `CE_part1.csv`, `MH_part1.csv`).

## 📁 Output

The tool generates files typically named:

```
<shortened_name>_part1.csv
```

Each line represents a unique recipe configuration based on the Schedule 1 data.

> **Note:** With 8 ingredients, the output can exceed **100 GB** in size and generate over **1 million recipes** before deduplication. Adding more ingredients causes exponential growth in file size and combination count. Ensure sufficient disk space and memory capacity.

## 📄 License

This project is licensed under the [GNU General Public License v3.0](https://github.com/MilkshakesBot/reverse_calc/blob/main/LICENSE).

## 🡋 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss your proposed changes.
