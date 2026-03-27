"""
Configuration Generator - Generates standardized JSON configuration from parsed XML metadata
"""

from typing import Dict, List, Any
from datetime import datetime
from xml_parser import InformaticaXMLParser


class ConfigurationGenerator:
    """Generates standardized JSON configuration from Informatica metadata"""
    
    def __init__(self, xml_filepath: str):
        """
        Initialize configuration generator.
        
        Args:
            xml_filepath: Path to Informatica XML file
        """
        self.parser = InformaticaXMLParser(xml_filepath)
        self.metadata = self.parser.get_metadata()
    
    def generate_config(self) -> Dict[str, Any]:
        """
        Generate standardized configuration from metadata.
        
        Returns:
            Dictionary with standardized configuration
        """
        config = {
            'schema': self._generate_schema(),
            'transformations': self._generate_transformations(),
            'metadata': self._generate_metadata(),
            'synthetic_data_rules': self._generate_data_rules()
        }
        return config
    
    def _generate_schema(self) -> Dict[str, Any]:
        """
        Generate schema configuration from fields.
        
        Returns:
            Schema configuration dictionary
        """
        schema = {
            'version': '1.0',
            'name': self.metadata['workflow_name'],
            'description': f"Schema for {self.metadata['workflow_name']}",
            'total_fields': self.metadata['total_fields'],
            'fields': []
        }
        
        for field in self.metadata['fields']:
            field_config = self._build_field_config(field)
            schema['fields'].append(field_config)
        
        return schema
    
    def _build_field_config(self, field: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build configuration for individual field.
        
        Args:
            field: Field metadata from parser
            
        Returns:
            Field configuration dictionary
        """
        datatype = field.get('datatype', 'string').lower()
        
        field_config = {
            'field_id': field.get('field_id'),
            'name': field.get('name'),
            'datatype': datatype,
            'length': self._parse_length(field.get('length', '50')),
            'precision': self._parse_precision(field.get('precision', '0')),
            'scale': self._parse_scale(field.get('scale', '0')),
            'nullable': field.get('nullable', 'true').lower() == 'true',
            'description': field.get('description', ''),
            'sample_value': self._generate_sample_value(datatype)
        }
        
        return field_config
    
    def _parse_length(self, length: Any) -> int:
        """Parse and validate length value"""
        try:
            val = int(str(length).strip())
            return max(1, min(val, 9999))  # Constrain between 1 and 9999
        except (ValueError, TypeError):
            return 50  # Default
    
    def _parse_precision(self, precision: Any) -> int:
        """Parse and validate precision value"""
        try:
            val = int(str(precision).strip())
            return max(0, val)
        except (ValueError, TypeError):
            return 0
    
    def _parse_scale(self, scale: Any) -> int:
        """Parse and validate scale value"""
        try:
            val = int(str(scale).strip())
            return max(0, val)
        except (ValueError, TypeError):
            return 0
    
    def _generate_sample_value(self, datatype: str) -> Any:
        """
        Generate sample value for field based on datatype.
        
        Args:
            datatype: Data type string
            
        Returns:
            Sample value for the datatype
        """
        samples = {
            'string': 'sample_text',
            'varchar': 'sample_text',
            'integer': 123,
            'biginteger': 9223372036854775807,
            'decimal': 123.45,
            'double': 123.45,
            'date': '2024-01-01',
            'timestamp': '2024-01-01 12:00:00',
            'datetime': '2024-01-01 12:00:00',
            'boolean': True,
            'blob': 'binary_data'
        }
        return samples.get(datatype.lower(), 'sample_value')
    
    def _generate_transformations(self) -> Dict[str, Any]:
        """
        Generate transformations configuration.
        
        Returns:
            Transformations configuration dictionary
        """
        transformations = {
            'total_transformations': self.metadata['total_transformations'],
            'rules': []
        }
        
        for trans in self.metadata['transformations']:
            trans_config = {
                'transformation_id': trans.get('transformation_id'),
                'name': trans.get('name'),
                'type': trans.get('type'),
                'expression': trans.get('expression'),
                'enabled': True
            }
            transformations['rules'].append(trans_config)
        
        return transformations
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """
        Generate metadata information.
        
        Returns:
            Metadata dictionary
        """
        return {
            'source_file': self.metadata['file_path'],
            'workflow_name': self.metadata['workflow_name'],
            'root_tag': self.metadata['root_tag'],
            'generated_at': datetime.now().isoformat(),
            'generator_version': '1.0'
        }
    
    def _generate_data_rules(self) -> Dict[str, Any]:
        """
        Generate rules for synthetic data generation.
        
        Returns:
            Data rules configuration dictionary
        """
        data_rules = {
            'description': 'Rules for generating synthetic data',
            'default_row_count': 100,
            'seed': 42,  # For reproducible data
            'field_rules': []
        }
        
        for field in self.metadata['fields']:
            rule = {
                'field_name': field.get('name'),
                'datatype': field.get('datatype', 'string').lower(),
                'nullable': field.get('nullable', 'true').lower() == 'true',
                'null_probability': 0.0 if field.get('nullable') == 'false' else 0.05,
                'generation_strategy': self._get_generation_strategy(
                    field.get('datatype', 'string').lower()
                )
            }
            data_rules['field_rules'].append(rule)
        
        return data_rules
    
    def _get_generation_strategy(self, datatype: str) -> str:
        """
        Get appropriate generation strategy for datatype.
        
        Args:
            datatype: Data type string
            
        Returns:
            Generation strategy name
        """
        strategies = {
            'string': 'random_text',
            'varchar': 'random_text',
            'integer': 'random_integer',
            'biginteger': 'random_biginteger',
            'decimal': 'random_decimal',
            'double': 'random_double',
            'date': 'random_date',
            'timestamp': 'random_timestamp',
            'datetime': 'random_datetime',
            'boolean': 'random_boolean',
            'blob': 'random_hex'
        }
        return strategies.get(datatype.lower(), 'random_text')
