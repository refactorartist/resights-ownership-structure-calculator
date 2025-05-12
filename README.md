# Ownership Structure Calculator

The Ownership Structure Calculator is a tool designed to calculate and analyze complex ownership relationships between companies and individuals based on provided data.

## Installation

### Prerequisites

-   [Devbox](https://www.jetify.com/devbox/) - A command-line tool for creating isolated development environments.
-   Git

### Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/refactorartist/resights-ownership-structure-calculator.git
    cd resights-ownership-structure-calculator
    ```

2.  **Start the Devbox environment:** This sets up the necessary tools and environment variables.
    ```bash
    devbox shell
    ```
    *(You'll need to run subsequent commands within this shell)*

3.  **Install dependencies:** Use Rye to install the project's Python dependencies.
    ```bash
    rye sync
    ```

4.  **Run Tests (Optional):** Verify the installation and code integrity.
    ```bash
    rye test -- -vv
    ```

## Usage

All commands should be run inside the `devbox shell`.

### Validate Input Data

Before performing calculations, you can validate the format of your JSON data file:

```bash
rye run cli validate file data/raw/CasaAS.json
```

### Ownership Structure Commands

The tool provides several commands for analyzing ownership structures:

1. **Calculate Ownership Path**
   ```bash
   # Calculate ownership path between two companies
   rye run cli ownership calculate data/raw/CasaAS.json "DANSKE BANK A/S" --target "CASA A/S"
   
   # Calculate ownership path from a company to the focus company
   rye run cli ownership calculate data/raw/CasaAS.json "CASA A/S"
   ```

2. **List All Owners**
   ```bash
   # List all owners of a specific company
   rye run cli ownership list-all data/raw/CasaAS.json --target "CASA A/S"
   
   # List all owners of the focus company
   rye run cli ownership list-all data/raw/CasaAS.json
   ```

3. **List Direct Owners**
   ```bash
   # List direct owners of a specific company
   rye run cli ownership list-owners data/raw/CasaAS.json --target "CASA A/S"
   
   # List direct owners of the focus company
   rye run cli ownership list-owners data/raw/CasaAS.json
   ```

4. **List Owned Companies**
   ```bash
   # List companies owned by a specific company
   rye run cli ownership list-owned data/raw/CasaAS.json --target "CASA A/S"
   
   # List companies owned by the focus company
   rye run cli ownership list-owned data/raw/CasaAS.json
   ```

### Quick Examples

1. **Validate and Analyze CASA A/S Ownership**
   ```bash
   # First validate the data file
   rye run cli validate file data/raw/CasaAS.json
   
   # Then analyze the ownership structure
   rye run cli ownership calculate data/raw/CasaAS.json "DANSKE BANK A/S"
   ```

2. **Find All Owners of DANSKE BANK A/S**
   ```bash
   rye run cli ownership list-all data/raw/CasaAS.json --target "DANSKE BANK A/S"
   ```

3. **Check Direct Ownership of CASA A/S**
   ```bash
   rye run cli ownership list-owners data/raw/CasaAS.json --target "CASA A/S"
   ```

4. **Find Companies Owned by CASA A/S**
   ```bash
   rye run cli ownership list-owned data/raw/CasaAS.json --target "CASA A/S"
   ```

