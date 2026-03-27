"""
Main module - Orchestrates XML parsing, configuration generation, and synthetic data generation
"""

import argparse
import sys
import os
from typing import Dict
from utils import save_json, get_output_filename, print_summary
from config_generator import ConfigurationGenerator
from synthetic_data_generator import SyntheticDataGenerator


class InformaticaFramework:
    """Main framework for processing Informatica workflows"""
    
    def __init__(self, xml_file: str, output_dir: str = 'output'):
        """
        Initialize framework.
        
        Args:
            xml_file: Path to Informatica XML file
            output_dir: Directory for output files
        """
        self.xml_file = xml_file
        self.output_dir = output_dir
        self.config = None
        self.synthetic_data = None
    
    def process_step1_generate_config(self) -> str:
        """
        Step 1: Parse XML and generate standardized JSON configuration.
        
        Returns:
            Path to generated configuration file
        """
        print("\n" + "="*60)
        print("STEP 1: Parse XML and Generate Configuration")
        print("="*60)
        
        try:
            # Generate configuration from XML
            generator = ConfigurationGenerator(self.xml_file)
            self.config = generator.generate_config()
            
            # Save configuration
            config_filename = get_output_filename(self.xml_file, 'config')
            config_filepath = os.path.join(self.output_dir, config_filename)
            save_json(self.config, config_filepath)
            
            # Print summary
            schema = self.config.get('schema', {})
            summary = {
                'Workflow Name': schema.get('name'),
                'Total Fields': schema.get('total_fields'),
                'Output File': config_filepath
            }
            print_summary("Configuration Generation Summary", summary)
            
            return config_filepath
            
        except Exception as e:
            print(f"✗ Error in Step 1: {str(e)}")
            raise
    
    def process_step2_generate_synthetic_data(self, config_filepath: str, row_count: int = 100) -> str:
        """
        Step 2: Generate synthetic data based on configuration.
        
        Args:
            config_filepath: Path to generated configuration file
            row_count: Number of rows to generate
            
        Returns:
            Path to generated data file
        """
        print("\n" + "="*60)
        print("STEP 2: Generate Synthetic Data")
        print("="*60)
        
        try:
            # Generate synthetic data
            data_generator = SyntheticDataGenerator(config_filepath)
            self.synthetic_data = data_generator.generate_data(row_count)
            
            # Save data
            data_filename = get_output_filename(self.xml_file, 'data')
            data_filepath = os.path.join(self.output_dir, data_filename)
            save_json(self.synthetic_data, data_filepath)
            
            # Get and print summary
            summary_stats = data_generator.get_data_summary(self.synthetic_data)
            summary = {
                'Total Rows Generated': summary_stats['total_rows'],
                'Total Fields': summary_stats['total_fields'],
                'Output File': data_filepath
            }
            print_summary("Synthetic Data Generation Summary", summary)
            
            return data_filepath
            
        except Exception as e:
            print(f"✗ Error in Step 2: {str(e)}")
            raise
    
    def process_complete_workflow(self, row_count: int = 100) -> Dict[str, str]:
        """
        Execute complete workflow: XML parsing -> Config generation -> Data generation.
        
        Args:
            row_count: Number of rows to generate
            
        Returns:
            Dictionary with paths to generated files
        """
        print("\n" + "="*70)
        print("INFORMATICA XML TO JSON CONFIGURATION AND SYNTHETIC DATA GENERATOR")
        print("="*70)
        
        results = {}
        
        try:
            # Step 1
            config_file = self.process_step1_generate_config()
            results['config_file'] = config_file
            
            # Step 2
            data_file = self.process_step2_generate_synthetic_data(config_file, row_count)
            results['data_file'] = data_file
            
            # Final summary
            print("\n" + "="*70)
            print("WORKFLOW COMPLETED SUCCESSFULLY")
            print("="*70)
            print(f"Input XML File: {self.xml_file}")
            print(f"Configuration File: {results['config_file']}")
            print(f"Synthetic Data File: {results['data_file']}")
            print(f"Rows Generated: {row_count}")
            print("="*70 + "\n")
            
            return results
            
        except Exception as e:
            print(f"\n✗ Workflow failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Informatica XML to JSON Configuration and Synthetic Data Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py workflow.xml
  python main.py workflow.xml -o output_folder -r 500
  python main.py mapping.xml --rows 1000
        '''
    )
    
    parser.add_argument('xml_file', help='Path to Informatica XML file')
    parser.add_argument('-o', '--output', default='output', help='Output directory (default: output)')
    parser.add_argument('-r', '--rows', type=int, default=100, help='Number of rows to generate (default: 100)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.xml_file):
        print(f"✗ XML file not found: {args.xml_file}")
        sys.exit(1)
    
    # Run framework
    try:
        framework = InformaticaFramework(args.xml_file, args.output)
        results = framework.process_complete_workflow(args.rows)
        sys.exit(0)
    except Exception as e:
        print(f"✗ Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
