"""
Synthetic Data Generator - Generates synthetic test data based on JSON configuration
"""

import random
import string
from typing import Dict, List, Any
from datetime import datetime, timedelta
from faker import Faker
from utils import load_json


class SyntheticDataGenerator:
    """Generates synthetic data based on standardized configuration"""
    
    def __init__(self, config_filepath: str, seed: int = 42):
        """
        Initialize synthetic data generator.
        
        Args:
            config_filepath: Path to JSON configuration file
            seed: Random seed for reproducibility
        """
        self.config = load_json(config_filepath)
        self.seed = seed
        random.seed(seed)
        self.fake = Faker()
        Faker.seed(seed)
    
    def generate_data(self, row_count: int = None) -> List[Dict[str, Any]]:
        """
        Generate synthetic data based on configuration.
        
        Args:
            row_count: Number of rows to generate (uses config default if None)
            
        Returns:
            List of dictionaries with synthetic data
        """
        if row_count is None:
            row_count = self.config.get('synthetic_data_rules', {}).get('default_row_count', 100)
        
        print(f"Generating {row_count} rows of synthetic data...")
        
        data = []
        schema_fields = self.config.get('schema', {}).get('fields', [])
        
        for row_num in range(row_count):
            row = {}
            for field in schema_fields:
                field_name = field.get('name')
                datatype = field.get('datatype', 'string')
                nullable = field.get('nullable', True)
                
                # Generate null value with probability
                null_probability = 0.05 if nullable else 0.0
                if random.random() < null_probability:
                    row[field_name] = None
                else:
                    row[field_name] = self._generate_value(field)
            
            data.append(row)
            
            # Progress indicator
            if (row_num + 1) % max(1, row_count // 10) == 0:
                print(f"  Progress: {row_num + 1}/{row_count} rows generated")
        
        print(f"✓ Generated {row_count} rows of synthetic data")
        return data
    
    def _generate_value(self, field: Dict[str, Any]) -> Any:
        """
        Generate appropriate value for field based on datatype.
        
        Args:
            field: Field configuration dictionary
            
        Returns:
            Generated value
        """
        datatype = field.get('datatype', 'string').lower()
        length = field.get('length', 50)
        precision = field.get('precision', 10)
        scale = field.get('scale', 2)
        
        if datatype in ['string', 'varchar', 'char']:
            return self._generate_string(length)
        elif datatype in ['integer', 'int']:
            return self._generate_integer()
        elif datatype == 'biginteger':
            return self._generate_biginteger()
        elif datatype in ['decimal', 'numeric']:
            return self._generate_decimal(precision, scale)
        elif datatype in ['double', 'float']:
            return self._generate_double()
        elif datatype in ['date']:
            return self._generate_date()
        elif datatype in ['timestamp', 'datetime']:
            return self._generate_timestamp()
        elif datatype == 'boolean':
            return self._generate_boolean()
        elif datatype == 'blob':
            return self._generate_hex(32)
        else:
            return self._generate_string(length)
    
    def _generate_string(self, length: int) -> str:
        """Generate random string with Faker"""
        # Use appropriate faker methods based on context
        strategies = [
            self.fake.word,
            self.fake.words,
            self.fake.sentence,
            self.fake.name,
            self.fake.email,
            self.fake.address,
            self.fake.company
        ]
        
        value = random.choice(strategies)()
        
        # Ensure length constraint
        if isinstance(value, list):
            value = ' '.join(value)
        
        value = str(value)[:length]
        return value if value else 'N/A'
    
    def _generate_integer(self) -> int:
        """Generate random integer"""
        return random.randint(-2147483648, 2147483647)
    
    def _generate_biginteger(self) -> int:
        """Generate random big integer"""
        return random.randint(-9223372036854775808, 9223372036854775807)
    
    def _generate_decimal(self, precision: int, scale: int) -> float:
        """
        Generate random decimal number.
        
        Args:
            precision: Total number of digits
            scale: Number of decimal places
            
        Returns:
            Random decimal number
        """
        if precision <= 0:
            precision = 10
        if scale < 0:
            scale = 0
        
        integer_part = 10 ** (precision - scale - 1)
        value = random.uniform(-integer_part, integer_part)
        
        return round(value, scale)
    
    def _generate_double(self) -> float:
        """Generate random double value"""
        return random.uniform(-1e10, 1e10)
    
    def _generate_date(self) -> str:
        """Generate random date as ISO string"""
        random_date = self.fake.date_object()
        return random_date.isoformat()
    
    def _generate_timestamp(self) -> str:
        """Generate random timestamp as ISO string"""
        random_datetime = self.fake.date_time()
        return random_datetime.isoformat()
    
    def _generate_boolean(self) -> bool:
        """Generate random boolean"""
        return random.choice([True, False])
    
    def _generate_hex(self, length: int) -> str:
        """Generate random hexadecimal string"""
        return ''.join(random.choices(string.hexdigits[:16], k=length))
    
    def generate_data_csv(self, row_count: int = None) -> str:
        """
        Generate synthetic data in CSV format.
        
        Args:
            row_count: Number of rows to generate
            
        Returns:
            CSV formatted string
        """
        data = self.generate_data(row_count)
        
        if not data:
            return ""
        
        schema_fields = self.config.get('schema', {}).get('fields', [])
        
        # Create header
        headers = [field.get('name') for field in schema_fields]
        csv_lines = [','.join(headers)]
        
        # Add data rows
        for row in data:
            values = [str(row.get(header, '')).replace(',', ' ') for header in headers]
            csv_lines.append(','.join(values))
        
        return '\n'.join(csv_lines)
    
    def get_data_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics about generated data.
        
        Args:
            data: Generated data
            
        Returns:
            Dictionary with summary statistics
        """
        schema_fields = self.config.get('schema', {}).get('fields', [])
        summary = {
            'total_rows': len(data),
            'total_fields': len(schema_fields),
            'field_summaries': []
        }
        
        for field in schema_fields:
            field_name = field.get('name')
            datatype = field.get('datatype')
            
            values = [row.get(field_name) for row in data if row.get(field_name) is not None]
            
            field_summary = {
                'field_name': field_name,
                'datatype': datatype,
                'total_values': len(values),
                'null_count': len(data) - len(values),
                'null_percentage': round((len(data) - len(values)) / len(data) * 100, 2) if data else 0
            }
            
            # Add type-specific statistics
            if datatype in ['integer', 'biginteger', 'decimal', 'double']:
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    field_summary['min'] = min(numeric_values)
                    field_summary['max'] = max(numeric_values)
                    field_summary['avg'] = sum(numeric_values) / len(numeric_values)
            
            summary['field_summaries'].append(field_summary)
        
        return summary
