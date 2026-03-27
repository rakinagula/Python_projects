# Quick Start Guide

Get up and running with the Informatica Framework in 5 minutes.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation (2 minutes)

### 1. Open Terminal in Project Directory

```bash
cd Informatica_to_Json_config_medata
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed lxml-4.9.3 faker-20.1.0
```

## Basic Usage (3 minutes)

### Option A: Using Command Line (Fastest)

Use the example workflow that comes with the project:

```bash
python main.py example_workflow.xml
```

**What happens:**
1. XML file is parsed
2. JSON configuration is generated → `output/example_workflow_config.json`
3. Synthetic data is generated → `output/example_workflow_synthetic_data.json`

**Output folders created:**
- `output/` - Contains all generated files

### Option B: Using Your Own XML File

```bash
python main.py your_workflow.xml
```

Create the workflow XML file with structure like `example_workflow.xml`.

### Option C: Generate More Rows

```bash
python main.py example_workflow.xml -r 500
```

Generates 500 rows instead of default 100.

## Understanding the Output

### Configuration File (`*_config.json`)

Contains workflow structure and field definitions:

```json
{
  "schema": {
    "version": "1.0",
    "name": "CustomerDataWorkflow",
    "total_fields": 10,
    "fields": [
      {
        "field_id": "field_1",
        "name": "customer_id",
        "datatype": "biginteger",
        "length": 20,
        "nullable": false
      }
    ]
  }
}
```

### Synthetic Data File (`*_synthetic_data.json`)

Contains generated test data:

```json
[
  {
    "customer_id": 5234891023487,
    "first_name": "John",
    "email": "john.smith@example.com"
  }
]
```

## Common Tasks

### Generate 1000 rows of test data

```bash
python main.py workflow.xml -r 1000 -o output
```

### Save to specific output folder

```bash
python main.py workflow.xml -o /path/to/output
```

### View Help

```bash
python main.py --help
```

## Programmatic Usage (For Developers)

Use the framework directly in your Python code:

```python
from config_generator import ConfigurationGenerator
from synthetic_data_generator import SyntheticDataGenerator

# Step 1: Generate configuration from XML
config_gen = ConfigurationGenerator("workflow.xml")
config = config_gen.generate_config()

# Step 2: Generate synthetic data
data_gen = SyntheticDataGenerator(config_path)
data = data_gen.generate_data(row_count=100)

# Access the data
print(f"Generated {len(data)} rows")
```

## Try the Demo

Interactive demo showing all features:

```bash
python demo.py
```

Choose from:
1. Step-by-step framework demo
2. CSV export demo
3. Custom configuration demo

## Your XMLFile Structure

Informatica XML should look like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Workflow name="YourWorkflowName">
    <Field name="field1" datatype="string" length="50" nullable="false"/>
    <Field name="field2" datatype="integer" nullable="true"/>
    <Field name="field3" datatype="decimal" precision="10" scale="2"/>
</Workflow>
```

### Supported Data Types

- **string** - Text data (max length 9999 chars)
- **integer** - Whole numbers (-2.1B to 2.1B)
- **biginteger** - Large whole numbers
- **decimal** - Precise decimal numbers
- **double** - Floating point numbers
- **date** - Calendar dates
- **timestamp** - Date and time
- **boolean** - True/False values
- **blob** - Binary data (represented as hex)

### Field Attributes

```xml
<Field 
  name="field_name"           <!-- Required: Field name -->
  datatype="string"           <!-- Required: Data type -->
  length="50"                 <!-- Optional: String length -->
  precision="10"              <!-- Optional: Total digits -->
  scale="2"                   <!-- Optional: Decimal places -->
  nullable="true"             <!-- Optional: Allow nulls -->
  description="Field docs"    <!-- Optional: Description -->
/>
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `FileNotFoundError` | Check XML file path and ensure it exists |
| `XMLSyntaxError` | Validate XML file syntax |
| No output folder | Framework creates it automatically |
| Wrong data generated | Check datatype names match supported types |

## Next Steps

1. **Process Your Workflow**: Use your own Informatica XML file
2. **Customize Fields**: Edit XML to add/remove fields as needed
3. **Programmatic Usage**: Integrate into your Python projects
4. **Larger Datasets**: Generate thousands of rows for testing

## Example Workflow

```bash
# 1. Create your XML file based on example_workflow.xml
# 2. Run the framework
python main.py my_workflow.xml -r 1000

# 3. Check output
ls output/

# 4. Use the generated files for testing
```

## Getting Help

For detailed information:
- See `README.md` for complete documentation
- Review `example_workflow.xml` for XML structure
- Check module docstrings in Python files
- Run `demo.py` for interactive examples

---

**Ready to get started?**

```bash
python main.py example_workflow.xml
```

That's it! Check the `output/` folder for generated files.
