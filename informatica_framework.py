"""
Informatica Metadata to JSON Configuration Framework
Purpose: Parse Informatica mappings and generate standardized JSON output for synthetic data generation
Author: Framework Developer
Version: 1.0.0
"""

import json
import xml.etree.ElementTree as ET
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logger(log_file: str = "informatica_framework.log") -> logging.Logger:
    """Initialize logging configuration"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_path = log_dir / log_file
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


logger = setup_logger()


# ============================================================================
# DATA CLASSES FOR TYPE SAFETY
# ============================================================================

@dataclass
class ColumnMetadata:
    """Represents column metadata extracted from Informatica mapping"""
    column_name: str
    data_type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    description: str = ""
    transformation: Optional[str] = None
    source_table: str = ""
    target_table: str = ""


@dataclass
class MappingMetadata:
    """Represents complete mapping metadata"""
    mapping_name: str
    mapping_id: str
    source_table: str
    target_table: str
    created_date: str
    modified_date: str
    description: str
    columns: List[ColumnMetadata]
    transformations: List[Dict[str, Any]]


# ============================================================================
# METADATA EXTRACTOR CLASS
# ============================================================================

class InformaticaMetadataExtractor:
    """Extract metadata from Informatica mapping files"""
    
    def __init__(self):
        self.logger = logger
        self.logger.info("Initialized InformaticaMetadataExtractor")
    
    def extract_from_dict(self, mapping_data: Dict[str, Any]) -> MappingMetadata:
        """
        Extract metadata from dictionary representation of Informatica mapping
        
        Args:
            mapping_data: Dictionary containing mapping information
            
        Returns:
            MappingMetadata object
        """
        try:
            self.logger.info(f"Extracting metadata from mapping: {mapping_data.get('mapping_name')}")
            
            # Extract basic mapping information
            mapping_name = mapping_data.get('mapping_name', 'Unknown')
            mapping_id = mapping_data.get('mapping_id', 'N/A')
            source_table = mapping_data.get('source_table', '')
            target_table = mapping_data.get('target_table', '')
            created_date = mapping_data.get('created_date', datetime.now().isoformat())
            modified_date = mapping_data.get('modified_date', datetime.now().isoformat())
            description = mapping_data.get('description', '')
            
            # Extract columns
            columns = []
            for col_data in mapping_data.get('columns', []):
                column = ColumnMetadata(
                    column_name=col_data.get('column_name', ''),
                    data_type=col_data.get('data_type', 'VARCHAR'),
                    length=col_data.get('length'),
                    precision=col_data.get('precision'),
                    scale=col_data.get('scale'),
                    nullable=col_data.get('nullable', True),
                    description=col_data.get('description', ''),
                    transformation=col_data.get('transformation'),
                    source_table=col_data.get('source_table', source_table),
                    target_table=col_data.get('target_table', target_table)
                )
                columns.append(column)
            
            # Extract transformations
            transformations = mapping_data.get('transformations', [])
            
            metadata = MappingMetadata(
                mapping_name=mapping_name,
                mapping_id=mapping_id,
                source_table=source_table,
                target_table=target_table,
                created_date=created_date,
                modified_date=modified_date,
                description=description,
                columns=columns,
                transformations=transformations
            )
            
            self.logger.info(f"Successfully extracted metadata for {len(columns)} columns")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata: {str(e)}", exc_info=True)
            raise


# ============================================================================
# CONFIGURATION BUILDER CLASS
# ============================================================================

class ConfigurationBuilder:
    """Build standardized configuration from extracted metadata"""
    
    def __init__(self):
        self.logger = logger
        self.logger.info("Initialized ConfigurationBuilder")
    
    def build_column_config(self, column: ColumnMetadata) -> Dict[str, Any]:
        """
        Build configuration for a single column
        
        Args:
            column: ColumnMetadata object
            
        Returns:
            Dictionary with column configuration
        """
        config = {
            "columnName": column.column_name,
            "dataType": column.data_type,
            "properties": {
                "nullable": column.nullable,
                "description": column.description
            },
            "generationConfig": {
                "strategy": self._determine_strategy(column.data_type),
                "parameters": self._get_generation_parameters(column)
            }
        }
        
        # Add size information if applicable
        if column.length:
            config["properties"]["length"] = column.length
        
        if column.precision:
            config["properties"]["precision"] = column.precision
        
        if column.scale:
            config["properties"]["scale"] = column.scale
        
        # Add transformation if exists
        if column.transformation:
            config["transformation"] = column.transformation
        
        return config
    
    def _determine_strategy(self, data_type: str) -> str:
        """Determine synthetic data generation strategy based on data type"""
        data_type_upper = data_type.upper()
        
        strategies = {
            'INT': 'NUMERIC',
            'INTEGER': 'NUMERIC',
            'BIGINT': 'NUMERIC',
            'DECIMAL': 'NUMERIC',
            'FLOAT': 'NUMERIC',
            'DOUBLE': 'NUMERIC',
            'VARCHAR': 'STRING',
            'CHAR': 'STRING',
            'TEXT': 'STRING',
            'DATE': 'DATE',
            'DATETIME': 'DATETIME',
            'TIMESTAMP': 'DATETIME',
            'BOOLEAN': 'BOOLEAN',
            'BIT': 'BOOLEAN'
        }
        
        return strategies.get(data_type_upper, 'STRING')
    
    def _get_generation_parameters(self, column: ColumnMetadata) -> Dict[str, Any]:
        """Get generation parameters based on column properties"""
        params = {}
        
        data_type_upper = column.data_type.upper()
        
        if 'INT' in data_type_upper or 'DECIMAL' in data_type_upper or 'FLOAT' in data_type_upper:
            params['minValue'] = 0
            params['maxValue'] = 1000
        
        elif 'VARCHAR' in data_type_upper or 'CHAR' in data_type_upper:
            params['maxLength'] = column.length if column.length else 50
            params['pattern'] = 'ALPHANUMERIC'
        
        elif 'DATE' in data_type_upper:
            params['format'] = 'yyyy-MM-dd'
            params['startDate'] = '2020-01-01'
            params['endDate'] = '2025-12-31'
        
        return params
    
    def build_transformation_config(self, transformation: Dict[str, Any]) -> Dict[str, Any]:
        """Build configuration for transformations"""
        return {
            "transformationName": transformation.get('name', 'transformation'),
            "transformationType": transformation.get('type', 'UNKNOWN'),
            "transformationLogic": transformation.get('logic', ''),
            "inputMappings": transformation.get('inputs', []),
            "outputMappings": transformation.get('outputs', [])
        }


# ============================================================================
# JSON CONFIGURATION GENERATOR CLASS
# ============================================================================

class JSONConfigurationGenerator:
    """Generate standardized JSON configuration"""
    
    def __init__(self):
        self.logger = logger
        self.config_builder = ConfigurationBuilder()
        self.logger.info("Initialized JSONConfigurationGenerator")
    
    def generate(self, metadata: MappingMetadata) -> Dict[str, Any]:
        """
        Generate complete JSON configuration from metadata
        
        Args:
            metadata: MappingMetadata object
            
        Returns:
            Dictionary representing complete JSON configuration
        """
        try:
            self.logger.info(f"Generating JSON configuration for mapping: {metadata.mapping_name}")
            
            # Build column configurations
            columns_config = []
            for column in metadata.columns:
                col_config = self.config_builder.build_column_config(column)
                columns_config.append(col_config)
            
            # Build transformation configurations
            transformations_config = []
            for transformation in metadata.transformations:
                trans_config = self.config_builder.build_transformation_config(transformation)
                transformations_config.append(trans_config)
            
            # Build complete configuration
            configuration = {
                "metadata": {
                    "framework": "Informatica Metadata to JSON Configuration Framework",
                    "version": "1.0.0",
                    "generatedDate": datetime.now().isoformat(),
                    "generatedBy": "InformaticaFramework"
                },
                "mapping": {
                    "id": metadata.mapping_id,
                    "name": metadata.mapping_name,
                    "description": metadata.description,
                    "source": {
                        "tableName": metadata.source_table,
                        "type": "relational"
                    },
                    "target": {
                        "tableName": metadata.target_table,
                        "type": "relational"
                    },
                    "createdDate": metadata.created_date,
                    "modifiedDate": metadata.modified_date
                },
                "syntheticDataGeneration": {
                    "totalColumns": len(metadata.columns),
                    "columns": columns_config,
                    "transformations": transformations_config,
                    "generationStrategy": "RULE_BASED"
                }
            }
            
            self.logger.info(f"Successfully generated configuration with {len(columns_config)} columns")
            return configuration
            
        except Exception as e:
            self.logger.error(f"Error generating JSON configuration: {str(e)}", exc_info=True)
            raise
    
    def save_to_file(self, configuration: Dict[str, Any], output_path: str) -> bool:
        """
        Save configuration to JSON file
        
        Args:
            configuration: Configuration dictionary
            output_path: Path to save JSON file
            
        Returns:
            Boolean indicating success
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(configuration, f, indent=2)
            
            self.logger.info(f"Configuration saved successfully to: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration to file: {str(e)}", exc_info=True)
            return False


# ============================================================================
# MAIN FRAMEWORK CLASS
# ============================================================================

class InformaticaFramework:
    """Main framework orchestrator"""
    
    def __init__(self):
        self.logger = logger
        self.extractor = InformaticaMetadataExtractor()
        self.generator = JSONConfigurationGenerator()
        self.logger.info("Initialized InformaticaFramework")
    def parse_xml_mapping(self, xml_path: str) -> Dict[str, Any]:
        """
        Parse Informatica mapping/workflow XML file and convert to dictionary
        Args:
            xml_path: Path to XML file
        Returns:
            Dictionary containing mapping data
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            mapping_data = {}
            # Example parsing logic (adjust tags as per Informatica XML structure)
            mapping_data['mapping_name'] = root.attrib.get('NAME', 'Unknown')
            mapping_data['mapping_id'] = root.attrib.get('ID', 'N/A')
            mapping_data['description'] = root.attrib.get('DESCRIPTION', '')
            mapping_data['source_table'] = ''
            mapping_data['target_table'] = ''
            mapping_data['created_date'] = root.attrib.get('CREATED', '')
            mapping_data['modified_date'] = root.attrib.get('MODIFIED', '')
            # Parse columns
            columns = []
            for col_elem in root.findall('.//FIELD'):  # Adjust tag as per XML
                column = {
                    'column_name': col_elem.attrib.get('NAME', ''),
                    'data_type': col_elem.attrib.get('DATATYPE', 'VARCHAR'),
                    'length': int(col_elem.attrib.get('LENGTH', '0')) if col_elem.attrib.get('LENGTH') else None,
                    'precision': int(col_elem.attrib.get('PRECISION', '0')) if col_elem.attrib.get('PRECISION') else None,
                    'scale': int(col_elem.attrib.get('SCALE', '0')) if col_elem.attrib.get('SCALE') else None,
                    'nullable': col_elem.attrib.get('NULLABLE', 'YES') == 'YES',
                    'description': col_elem.attrib.get('DESCRIPTION', ''),
                    'transformation': col_elem.attrib.get('TRANSFORMATION', None),
                    'source_table': col_elem.attrib.get('SOURCE', ''),
                    'target_table': col_elem.attrib.get('TARGET', '')
                }
                columns.append(column)
            mapping_data['columns'] = columns
            # Parse transformations
            transformations = []
            for trans_elem in root.findall('.//TRANSFORMATION'):  # Adjust tag as per XML
                transformation = {
                    'name': trans_elem.attrib.get('NAME', ''),
                    'type': trans_elem.attrib.get('TYPE', ''),
                    'logic': trans_elem.attrib.get('LOGIC', ''),
                    'inputs': [inp.attrib.get('NAME', '') for inp in trans_elem.findall('.//INPUT')],
                    'outputs': [out.attrib.get('NAME', '') for out in trans_elem.findall('.//OUTPUT')]
                }
                transformations.append(transformation)
            mapping_data['transformations'] = transformations
            self.logger.info(f"Parsed XML mapping: {mapping_data['mapping_name']}")
            return mapping_data
        except Exception as e:
            self.logger.error(f"Error parsing XML mapping: {str(e)}", exc_info=True)
            raise
    
    def process_mapping(self, mapping_data: Dict[str, Any], output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process Informatica mapping and generate JSON configuration
        
        Args:
            mapping_data: Dictionary containing mapping data
            output_path: Optional path to save configuration
            
        Returns:
            Generated configuration dictionary
        """
        try:
            self.logger.info("=" * 80)
            self.logger.info("Starting mapping processing")
            self.logger.info("=" * 80)
            
            # Extract metadata
            metadata = self.extractor.extract_from_dict(mapping_data)
            
            # Generate configuration
            configuration = self.generator.generate(metadata)
            
            # Save to file if path provided
            if output_path:
                self.generator.save_to_file(configuration, output_path)
            
            self.logger.info("=" * 80)
            self.logger.info("Mapping processing completed successfully")
            self.logger.info("=" * 80)
            
            return configuration
            
        except Exception as e:
            self.logger.error(f"Error processing mapping: {str(e)}", exc_info=True)
            raise
    
    def process_multiple_mappings(self, mappings_list: List[Dict[str, Any]], output_dir: str) -> List[Dict[str, Any]]:
        """
        Process multiple Informatica mappings
        
        Args:
            mappings_list: List of mapping dictionaries
            output_dir: Directory to save all configurations
            
        Returns:
            List of generated configurations
        """
        configurations = []
        
        for idx, mapping in enumerate(mappings_list, 1):
            try:
                self.logger.info(f"Processing mapping {idx} of {len(mappings_list)}")
                output_file = os.path.join(output_dir, f"{mapping.get('mapping_name', f'mapping_{idx}')}_config.json")
                config = self.process_mapping(mapping, output_file)
                configurations.append(config)
            except Exception as e:
                self.logger.error(f"Failed to process mapping {idx}: {str(e)}")
                continue
        
        self.logger.info(f"Successfully processed {len(configurations)} out of {len(mappings_list)} mappings")
        return configurations


# ============================================================================
# SAMPLE DATA AND MAIN EXECUTION
# ============================================================================

def create_sample_mapping_data() -> Dict[str, Any]:
    """Create sample mapping data for demonstration"""
    return {
        'mapping_name': 'CUSTOMER_ETL_MAPPING',
        'mapping_id': 'MAP_001',
        'source_table': 'SOURCE.CUSTOMER',
        'target_table': 'TARGET.CUSTOMER_STAGING',
        'created_date': '2025-01-15T10:30:00',
        'modified_date': '2026-03-12T14:45:00',
        'description': 'ETL mapping for customer data transformation',
        'columns': [
            {
                'column_name': 'CUSTOMER_ID',
                'data_type': 'BIGINT',
                'length': 20,
                'nullable': False,
                'description': 'Unique customer identifier',
                'source_table': 'SOURCE.CUSTOMER',
                'target_table': 'TARGET.CUSTOMER_STAGING'
            },
            {
                'column_name': 'CUSTOMER_NAME',
                'data_type': 'VARCHAR',
                'length': 100,
                'nullable': False,
                'description': 'Customer full name',
                'transformation': 'UPPER(TRIM(NAME))'
            },
            {
                'column_name': 'EMAIL',
                'data_type': 'VARCHAR',
                'length': 150,
                'nullable': True,
                'description': 'Customer email address'
            },
            {
                'column_name': 'PHONE',
                'data_type': 'VARCHAR',
                'length': 20,
                'nullable': True,
                'description': 'Customer phone number'
            },
            {
                'column_name': 'ACCOUNT_BALANCE',
                'data_type': 'DECIMAL',
                'precision': 15,
                'scale': 2,
                'nullable': False,
                'description': 'Current account balance',
                'transformation': 'ROUND(BALANCE, 2)'
            },
            {
                'column_name': 'REGISTRATION_DATE',
                'data_type': 'DATE',
                'nullable': False,
                'description': 'Customer registration date'
            },
            {
                'column_name': 'IS_ACTIVE',
                'data_type': 'BOOLEAN',
                'nullable': False,
                'description': 'Flag indicating if customer is active'
            }
        ],
        'transformations': [
            {
                'name': 'CUSTOMER_VALIDATION',
                'type': 'ROUTER',
                'logic': 'Route on CUSTOMER_ID IS NOT NULL and EMAIL IS NOT NULL',
                'inputs': ['CUSTOMER_ID', 'EMAIL'],
                'outputs': ['VALID_CUSTOMERS', 'INVALID_CUSTOMERS']
            },
            {
                'name': 'NAME_TRANSFORMATION',
                'type': 'EXPRESSION',
                'logic': 'UPPER(TRIM(CUSTOMER_NAME))',
                'inputs': ['CUSTOMER_NAME'],
                'outputs': ['TRANSFORMED_NAME']
            }
        ]
    }


def main():
    """Main execution function"""
    try:
        logger.info("Starting Informatica Framework Application")
        framework = InformaticaFramework()
        # Example: Use XML input if provided
        import sys
        if len(sys.argv) > 1 and sys.argv[1].endswith('.xml'):
            xml_path = sys.argv[1]
            mapping_data = framework.parse_xml_mapping(xml_path)
            output_file = f"output/{mapping_data.get('mapping_name', 'mapping')}_config.json"
        else:
            mapping_data = create_sample_mapping_data()
            output_file = "output/customer_etl_config.json"
        configuration = framework.process_mapping(mapping_data, output_file)
        print("\n" + "=" * 80)
        print("GENERATED CONFIGURATION")
        print("=" * 80)
        print(json.dumps(configuration, indent=2))
        print("=" * 80 + "\n")
        logger.info("Framework execution completed successfully")
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
