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
# XML TYPE DETECTION AND VALIDATION
# ============================================================================

class InformaticaXMLType:
    """Enumeration for Informatica XML types"""
    MAPPING = "MAPPING"
    WORKFLOW = "WORKFLOW"
    APPLICATION = "APPLICATION"
    UNKNOWN = "UNKNOWN"


class InformaticaXMLValidator:
    """Validate Informatica XML structure"""
    
    def __init__(self):
        self.logger = logger
    
    def validate_xml_structure(self, root: ET.Element) -> Dict[str, Any]:
        """
        Validate XML structure against Informatica DTD patterns
        
        Args:
            root: XML root element
            
        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "detected_type": InformaticaXMLType.UNKNOWN
        }
        
        try:
            # Check root element
            if root.tag != "POWERMART":
                validation_result["errors"].append("Root element must be 'POWERMART'")
                validation_result["is_valid"] = False
            else:
                self.logger.debug("Root element 'POWERMART' validation passed")
            
            # Check required attributes
            if not root.attrib.get("CREATION_DATE"):
                validation_result["warnings"].append("Missing CREATION_DATE attribute in POWERMART")
            
            # Check for REPOSITORY
            repository = root.find("REPOSITORY")
            if repository is None:
                validation_result["errors"].append("Missing REPOSITORY element")
                validation_result["is_valid"] = False
            else:
                self.logger.debug("REPOSITORY element found")
                
                # Check for FOLDER
                folders = repository.findall("FOLDER")
                if not folders:
                    validation_result["warnings"].append("No FOLDER elements found in REPOSITORY")
                
                # Detect XML type by analyzing contents
                detected_type = self._detect_xml_type(repository)
                validation_result["detected_type"] = detected_type
            
            return validation_result
            
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Validation error: {str(e)}")
            self.logger.error(f"Error during XML validation: {str(e)}", exc_info=True)
            return validation_result
    
    def _detect_xml_type(self, repository: ET.Element) -> str:
        """
        Detect the Informatica XML type
        
        Args:
            repository: REPOSITORY element
            
        Returns:
            Type of XML (MAPPING, WORKFLOW, or APPLICATION)
        """
        folder = repository.find("FOLDER")
        if folder is None:
            return InformaticaXMLType.APPLICATION
        
        # Check for workflow-specific elements
        if folder.find(".//WORKFLOW") is not None or folder.find(".//SESSION") is not None:
            return InformaticaXMLType.WORKFLOW
        
        # Check for mapping-specific elements
        if folder.find(".//MAPPING") is not None:
            return InformaticaXMLType.MAPPING
        
        # Default to APPLICATION if repository has multiple folders
        folders = repository.findall("FOLDER")
        if len(folders) > 1:
            return InformaticaXMLType.APPLICATION
        
        # Determine based on child elements
        for folder in folders:
            element_count = len(folder)
            mappings = len(folder.findall(".//MAPPING"))
            workflows = len(folder.findall(".//WORKFLOW"))
            
            if workflows > 0 and mappings == 0:
                return InformaticaXMLType.WORKFLOW
            elif mappings > 0:
                return InformaticaXMLType.MAPPING
        
        return InformaticaXMLType.UNKNOWN


# ============================================================================
# TYPE-SPECIFIC XML PARSERS
# ============================================================================

class InformaticaMappingXMLParser:
    """Parse Informatica Mapping XML files"""
    
    def __init__(self):
        self.logger = logger
    
    def parse(self, root: ET.Element) -> Dict[str, Any]:
        """Parse mapping XML and extract data"""
        mapping_data = {
            'xml_type': InformaticaXMLType.MAPPING,
            'mapping_name': 'Unknown',
            'mapping_id': 'N/A',
            'description': '',
            'source_table': '',
            'target_table': '',
            'created_date': '',
            'modified_date': '',
            'sources': [],
            'targets': [],
            'columns': [],
            'transformations': [],
            'instances': [],
            'connectors': []
        }
        
        try:
            powermart_attrs = root.attrib
            mapping_data['created_date'] = powermart_attrs.get('CREATION_DATE', '')
            mapping_data['modified_date'] = powermart_attrs.get('CREATION_DATE', '')
            
            # Find repository and folder
            repository = root.find('REPOSITORY')
            if repository is None:
                self.logger.warning("No REPOSITORY found in XML")
                return mapping_data
            
            folder = repository.find('FOLDER')
            if folder is None:
                self.logger.warning("No FOLDER found in REPOSITORY")
                return mapping_data
            
            # Parse sources
            sources = folder.findall('SOURCE')
            for source in sources:
                source_data = self._parse_source(source)
                mapping_data['sources'].append(source_data)
                mapping_data['source_table'] = source_data['name']
            
            # Parse targets
            targets = folder.findall('TARGET')
            for target in targets:
                target_data = self._parse_target(target)
                mapping_data['targets'].append(target_data)
                mapping_data['target_table'] = target_data['name']
            
            # Parse mappings
            mappings = folder.findall('MAPPING')
            if mappings:
                mapping = mappings[0]  # Get first mapping
                mapping_data['mapping_name'] = mapping.attrib.get('NAME', 'Unknown')
                mapping_data['mapping_id'] = mapping.attrib.get('NAME', 'N/A')
                mapping_data['description'] = mapping.attrib.get('DESCRIPTION', '')
                
                # Parse transformations
                transformations = mapping.findall('.//TRANSFORMATION')
                for trans in transformations:
                    trans_data = self._parse_transformation(trans)
                    mapping_data['transformations'].append(trans_data)
                
                # Parse instances
                instances = mapping.findall('.//INSTANCE')
                for inst in instances:
                    inst_data = self._parse_instance(inst)
                    mapping_data['instances'].append(inst_data)
                
                # Parse connectors
                connectors = mapping.findall('.//CONNECTOR')
                for conn in connectors:
                    conn_data = self._parse_connector(conn)
                    mapping_data['connectors'].append(conn_data)
            
            # Extract columns from sources and transformations
            mapping_data['columns'] = self._extract_columns(sources, targets, mappings)
            
            self.logger.info(f"Parsed mapping XML: {mapping_data['mapping_name']}")
            return mapping_data
            
        except Exception as e:
            self.logger.error(f"Error parsing mapping XML: {str(e)}", exc_info=True)
            raise
    
    def _parse_source(self, source: ET.Element) -> Dict[str, Any]:
        """Parse SOURCE element"""
        source_data = {
            'name': source.attrib.get('NAME', ''),
            'database_type': source.attrib.get('DATABASETYPE', ''),
            'description': source.attrib.get('DESCRIPTION', ''),
            'fields': []
        }
        
        fields = source.findall('SOURCEFIELD')
        for field in fields:
            field_data = {
                'name': field.attrib.get('NAME', ''),
                'datatype': field.attrib.get('DATATYPE', ''),
                'length': field.attrib.get('LENGTH'),
                'precision': field.attrib.get('PRECISION'),
                'scale': field.attrib.get('SCALE'),
                'nullable': field.attrib.get('NULLABLE', 'YES') == 'YES'
            }
            source_data['fields'].append(field_data)
        
        return source_data
    
    def _parse_target(self, target: ET.Element) -> Dict[str, Any]:
        """Parse TARGET element"""
        target_data = {
            'name': target.attrib.get('NAME', ''),
            'database_type': target.attrib.get('DATABASETYPE', ''),
            'description': target.attrib.get('DESCRIPTION', ''),
            'fields': []
        }
        
        fields = target.findall('TARGETFIELD')
        for field in fields:
            field_data = {
                'name': field.attrib.get('NAME', ''),
                'datatype': field.attrib.get('DATATYPE', ''),
                'precision': field.attrib.get('PRECISION'),
                'scale': field.attrib.get('SCALE'),
                'nullable': field.attrib.get('NULLABLE', 'YES') == 'YES'
            }
            target_data['fields'].append(field_data)
        
        return target_data
    
    def _parse_transformation(self, trans: ET.Element) -> Dict[str, Any]:
        """Parse TRANSFORMATION element"""
        trans_data = {
            'name': trans.attrib.get('NAME', ''),
            'type': trans.attrib.get('TYPE', ''),
            'description': trans.attrib.get('DESCRIPTION', ''),
            'fields': [],
            'attributes': []
        }
        
        # Parse transformation fields
        fields = trans.findall('TRANSFORMFIELD')
        for field in fields:
            field_data = {
                'name': field.attrib.get('NAME', ''),
                'datatype': field.attrib.get('DATATYPE', ''),
                'porttype': field.attrib.get('PORTTYPE', ''),
                'precision': field.attrib.get('PRECISION'),
                'scale': field.attrib.get('SCALE')
            }
            trans_data['fields'].append(field_data)
        
        # Parse table attributes
        attributes = trans.findall('TABLEATTRIBUTE')
        for attr in attributes:
            attr_data = {
                'name': attr.attrib.get('NAME', ''),
                'value': attr.attrib.get('VALUE', '')
            }
            trans_data['attributes'].append(attr_data)
        
        return trans_data
    
    def _parse_instance(self, inst: ET.Element) -> Dict[str, Any]:
        """Parse INSTANCE element"""
        return {
            'name': inst.attrib.get('NAME', ''),
            'type': inst.attrib.get('TYPE', ''),
            'transformation_name': inst.attrib.get('TRANSFORMATION_NAME', ''),
            'transformation_type': inst.attrib.get('TRANSFORMATION_TYPE', '')
        }
    
    def _parse_connector(self, conn: ET.Element) -> Dict[str, Any]:
        """Parse CONNECTOR element"""
        return {
            'from_instance': conn.attrib.get('FROMINSTANCE', ''),
            'from_field': conn.attrib.get('FROMFIELD', ''),
            'to_instance': conn.attrib.get('TOINSTANCE', ''),
            'to_field': conn.attrib.get('TOFIELD', '')
        }
    
    def _extract_columns(self, sources: List[ET.Element], targets: List[ET.Element], 
                        mappings: List[ET.Element]) -> List[Dict[str, Any]]:
        """Extract columns from sources and targets"""
        columns = []
        
        # Extract from sources
        for source in sources:
            fields = source.findall('SOURCEFIELD')
            for field in fields:
                column = {
                    'column_name': field.attrib.get('NAME', ''),
                    'data_type': field.attrib.get('DATATYPE', 'VARCHAR'),
                    'length': self._safe_int(field.attrib.get('LENGTH')),
                    'precision': self._safe_int(field.attrib.get('PRECISION')),
                    'scale': self._safe_int(field.attrib.get('SCALE')),
                    'nullable': field.attrib.get('NULLABLE', 'YES') == 'YES',
                    'description': field.attrib.get('DESCRIPTION', ''),
                    'transformation': None,
                    'source_table': source.attrib.get('NAME', ''),
                    'target_table': targets[0].attrib.get('NAME', '') if targets else ''
                }
                if column['column_name']:  # Only add if name exists
                    columns.append(column)
        
        return columns
    
    @staticmethod
    def _safe_int(value: Optional[str]) -> Optional[int]:
        """Safely convert string to int"""
        if value:
            try:
                return int(value)
            except ValueError:
                return None
        return None


class InformaticaWorkflowXMLParser:
    """Parse Informatica Workflow XML files"""
    
    def __init__(self):
        self.logger = logger
    
    def parse(self, root: ET.Element) -> Dict[str, Any]:
        """Parse workflow XML and extract data"""
        workflow_data = {
            'xml_type': InformaticaXMLType.WORKFLOW,
            'workflow_name': 'Unknown',
            'workflow_id': 'N/A',
            'description': '',
            'created_date': '',
            'sessions': [],
            'tasks': [],
            'mappings_used': []
        }
        
        try:
            powermart_attrs = root.attrib
            workflow_data['created_date'] = powermart_attrs.get('CREATION_DATE', '')
            
            # Find repository and folder
            repository = root.find('REPOSITORY')
            if repository is None:
                self.logger.warning("No REPOSITORY found in workflow XML")
                return workflow_data
            
            folder = repository.find('FOLDER')
            if folder is None:
                self.logger.warning("No FOLDER found in REPOSITORY")
                return workflow_data
            
            # Parse workflows
            workflows = folder.findall('WORKFLOW')
            if workflows:
                workflow = workflows[0]
                workflow_data['workflow_name'] = workflow.attrib.get('NAME', 'Unknown')
                workflow_data['workflow_id'] = workflow.attrib.get('NAME', 'N/A')
                workflow_data['description'] = workflow.attrib.get('DESCRIPTION', '')
            
            # Parse sessions
            sessions = folder.findall('.//SESSION')
            for session in sessions:
                session_data = {
                    'name': session.attrib.get('NAME', ''),
                    'mapping_name': session.attrib.get('MAPPINGNAME', ''),
                    'description': session.attrib.get('DESCRIPTION', '')
                }
                workflow_data['sessions'].append(session_data)
                workflow_data['mappings_used'].append(session_data['mapping_name'])
            
            self.logger.info(f"Parsed workflow XML: {workflow_data['workflow_name']}")
            return workflow_data
            
        except Exception as e:
            self.logger.error(f"Error parsing workflow XML: {str(e)}", exc_info=True)
            raise


class InformaticaApplicationXMLParser:
    """Parse Informatica Application (Repository) XML files"""
    
    def __init__(self):
        self.logger = logger
    
    def parse(self, root: ET.Element) -> Dict[str, Any]:
        """Parse application XML and extract data"""
        app_data = {
            'xml_type': InformaticaXMLType.APPLICATION,
            'repository_name': 'Unknown',
            'repository_version': '',
            'created_date': '',
            'folders': [],
            'total_mappings': 0,
            'total_workflows': 0,
            'total_sources': 0,
            'total_targets': 0
        }
        
        try:
            powermart_attrs = root.attrib
            app_data['created_date'] = powermart_attrs.get('CREATION_DATE', '')
            
            # Find repository
            repository = root.find('REPOSITORY')
            if repository is None:
                self.logger.warning("No REPOSITORY found in application XML")
                return app_data
            
            app_data['repository_name'] = repository.attrib.get('NAME', 'Unknown')
            app_data['repository_version'] = repository.attrib.get('VERSION', '')
            
            # Parse folders and count elements
            folders = repository.findall('FOLDER')
            for folder in folders:
                folder_data = {
                    'name': folder.attrib.get('NAME', ''),
                    'description': folder.attrib.get('DESCRIPTION', ''),
                    'owner': folder.attrib.get('OWNER', ''),
                    'mappings': len(folder.findall('.//MAPPING')),
                    'workflows': len(folder.findall('.//WORKFLOW')),
                    'sources': len(folder.findall('SOURCE')),
                    'targets': len(folder.findall('TARGET'))
                }
                app_data['folders'].append(folder_data)
                app_data['total_mappings'] += folder_data['mappings']
                app_data['total_workflows'] += folder_data['workflows']
                app_data['total_sources'] += folder_data['sources']
                app_data['total_targets'] += folder_data['targets']
            
            self.logger.info(f"Parsed application XML: {app_data['repository_name']}")
            return app_data
            
        except Exception as e:
            self.logger.error(f"Error parsing application XML: {str(e)}", exc_info=True)
            raise


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
