"""
Quick Start Demo - Shows how to use the framework programmatically
"""

from config_generator import ConfigurationGenerator
from synthetic_data_generator import SyntheticDataGenerator
from utils import save_json, load_json
import json


def demo_step_by_step():
    """Demonstrate framework usage step by step"""
    
    print("\n" + "="*70)
    print("INFORMATICA FRAMEWORK - STEP BY STEP DEMO")
    print("="*70 + "\n")
    
    # Step 1: Parse XML and generate configuration
    print("STEP 1: Parse XML file and generate configuration")
    print("-" * 70)
    
    xml_file = "example_workflow.xml"
    generator = ConfigurationGenerator(xml_file)
    config = generator.generate_config()
    
    # Show configuration structure
    print(f"\nGenerated Config Keys: {list(config.keys())}")
    print(f"Schema Version: {config['schema']['version']}")
    print(f"Workflow Name: {config['schema']['name']}")
    print(f"Total Fields: {config['schema']['total_fields']}")
    print(f"Total Transformations: {config['transformations']['total_transformations']}")
    
    # Save configuration
    config_file = "output/demo_config.json"
    save_json(config, config_file)
    print(f"\n✓ Configuration saved to: {config_file}")
    
    # Step 2: Generate synthetic data
    print("\n" + "="*70)
    print("STEP 2: Generate synthetic data from configuration")
    print("-" * 70)
    
    data_generator = SyntheticDataGenerator(config_file, seed=42)
    synthetic_data = data_generator.generate_data(row_count=20)
    
    # Show sample data
    print(f"\nGenerated {len(synthetic_data)} rows of synthetic data")
    print("\nFirst 2 rows:")
    for idx, row in enumerate(synthetic_data[:2]):
        print(f"\nRow {idx + 1}:")
        for key, value in list(row.items())[:5]:  # Show first 5 fields
            print(f"  {key}: {value}")
        print(f"  ... ({len(row)} total fields)")
    
    # Save synthetic data
    data_file = "output/demo_synthetic_data.json"
    save_json(synthetic_data, data_file)
    print(f"\n✓ Synthetic data saved to: {data_file}")
    
    # Step 3: Get data summary
    print("\n" + "="*70)
    print("STEP 3: Data Quality Summary")
    print("-" * 70)
    
    summary = data_generator.get_data_summary(synthetic_data)
    print(f"\nTotal Rows: {summary['total_rows']}")
    print(f"Total Fields: {summary['total_fields']}")
    
    print("\nField Summaries:")
    for field_summary in summary['field_summaries'][:5]:  # Show first 5 fields
        print(f"\n  {field_summary['field_name']}:")
        print(f"    - Datatype: {field_summary['datatype']}")
        print(f"    - Non-null values: {field_summary['total_values']}")
        print(f"    - Null count: {field_summary['null_count']}")
        print(f"    - Null %: {field_summary['null_percentage']}%")
    
    print("\n" + "="*70)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")


def demo_csv_export():
    """Demonstrate CSV export functionality"""
    
    print("\n" + "="*70)
    print("CSV EXPORT DEMO")
    print("="*70 + "\n")
    
    xml_file = "example_workflow.xml"
    generator = ConfigurationGenerator(xml_file)
    config = generator.generate_config()
    
    config_file = "output/demo_config.json"
    save_json(config, config_file)
    
    # Generate CSV data
    data_generator = SyntheticDataGenerator(config_file, seed=42)
    csv_data = data_generator.generate_data_csv(row_count=10)
    
    # Save CSV
    csv_file = "output/demo_synthetic_data.csv"
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(csv_data)
    
    print(f"✓ CSV data saved to: {csv_file}")
    print("\nCSV Preview (first 3 rows):")
    rows = csv_data.split('\n')[:3]
    for row in rows:
        print(row[:80] + "..." if len(row) > 80 else row)
    
    print("\n" + "="*70 + "\n")


def demo_using_existing_config():
    """Demonstrate using existing configuration without XML parsing"""
    
    print("\n" + "="*70)
    print("USING EXISTING CONFIGURATION - NO XML PARSING")
    print("="*70 + "\n")
    
    # Custom configuration
    custom_config = {
        "schema": {
            "version": "1.0",
            "name": "SimpleExample",
            "total_fields": 4,
            "fields": [
                {
                    "field_id": "field_1",
                    "name": "id",
                    "datatype": "integer",
                    "length": 10,
                    "nullable": False
                },
                {
                    "field_id": "field_2",
                    "name": "name",
                    "datatype": "string",
                    "length": 100,
                    "nullable": False
                },
                {
                    "field_id": "field_3",
                    "name": "balance",
                    "datatype": "decimal",
                    "precision": 10,
                    "scale": 2,
                    "nullable": False
                },
                {
                    "field_id": "field_4",
                    "name": "active",
                    "datatype": "boolean",
                    "nullable": True
                }
            ]
        },
        "synthetic_data_rules": {
            "default_row_count": 50
        }
    }
    
    # Save custom config
    config_file = "output/custom_config.json"
    save_json(custom_config, config_file)
    print(f"✓ Custom configuration saved to: {config_file}")
    
    # Generate data from custom config
    data_generator = SyntheticDataGenerator(config_file, seed=99)
    synthetic_data = data_generator.generate_data(row_count=10)
    
    print(f"\nGenerated {len(synthetic_data)} rows with custom configuration")
    print("\nSample row:")
    if synthetic_data:
        for key, value in synthetic_data[0].items():
            print(f"  {key}: {value}")
    
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    print("\nChoose a demo to run:")
    print("1. Step-by-step framework demo")
    print("2. CSV export demo")
    print("3. Custom configuration demo")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    try:
        if choice == '1':
            demo_step_by_step()
        elif choice == '2':
            demo_csv_export()
        elif choice == '3':
            demo_using_existing_config()
        else:
            print("Invalid choice. Running default demo...")
            demo_step_by_step()
    except Exception as e:
        print(f"\n✗ Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
