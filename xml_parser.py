"""
XML Parser - Parses Informatica XML workflow/mapping files
"""

from lxml import etree
from typing import Dict, List, Any, Optional
from utils import validate_xml_file


class InformaticaXMLParser:
    """Parser for Informatica XML workflow and mapping files"""
    
    def __init__(self, xml_filepath: str):
        """
        Initialize parser with XML file.
        
        Args:
            xml_filepath: Path to Informatica XML file
        """
        if not validate_xml_file(xml_filepath):
            raise FileNotFoundError(f"Invalid XML file: {xml_filepath}")
        
        self.xml_filepath = xml_filepath
        self.tree = None
        self.root = None
        self._parse_xml()
    
    def _parse_xml(self) -> None:
        """Parse XML file and load into memory"""
        try:
            self.tree = etree.parse(self.xml_filepath)
            self.root = self.tree.getroot()
            print(f"✓ Successfully parsed XML file: {self.xml_filepath}")
        except etree.XMLSyntaxError as e:
            print(f"✗ XML parsing error: {str(e)}")
            raise
    
    def get_workflow_name(self) -> str:
        """
        Extract workflow/mapping name from XML.
        
        Returns:
            Name of the workflow/mapping
        """
        # Try different common XML attribute names
        name = self.root.get('name') or self.root.get('Name') or 'Unknown'
        return name
    
    def get_root_tag(self) -> str:
        """Get root tag of XML document"""
        return self.root.tag
    
    def extract_fields(self) -> List[Dict[str, Any]]:
        """
        Extract field/column information from XML.
        
        Returns:
            List of field dictionaries with metadata
        """
        fields = []
        
        # Common XPath patterns for finding fields in Informatica XML
        xpath_patterns = [
            './/Field',
            './/field',
            './/Column',
            './/column',
            './/Property[@NAME="FieldName"]',
            './/FIELD',
            './/*[@datatype]'  # Any element with datatype attribute
        ]
        
        found_fields = []
        for xpath in xpath_patterns:
            try:
                elements = self.root.xpath(xpath)
                if elements:
                    found_fields = elements
                    break
            except:
                continue
        
        # If no fields found with XPath, try to extract from any elements with name/type
        if not found_fields:
            found_fields = self.root.xpath('.//*[@name and @datatype]')
        
        # Process found fields
        for idx, field_elem in enumerate(found_fields):
            field_info = self._extract_field_info(field_elem, idx)
            if field_info:
                fields.append(field_info)
        
        return fields if fields else self._extract_default_fields()
    
    def _extract_field_info(self, elem: Any, index: int) -> Optional[Dict[str, Any]]:
        """
        Extract information from a field element.
        
        Args:
            elem: XML element representing a field
            index: Index of field
            
        Returns:
            Dictionary with field information or None
        """
        field_info = {
            'field_id': f"field_{index + 1}",
            'name': elem.get('name') or elem.get('Name') or f"column_{index + 1}",
            'datatype': elem.get('datatype') or elem.get('Datatype') or 'string',
            'length': elem.get('length') or elem.get('Length') or '50',
            'precision': elem.get('precision') or elem.get('Precision') or '0',
            'scale': elem.get('scale') or elem.get('Scale') or '0',
            'nullable': elem.get('nullable') or elem.get('Nullable') or 'true',
            'description': elem.get('description') or elem.get('Description') or '',
        }
        
        # Extract text content if element has it
        if elem.text and elem.text.strip():
            field_info['content'] = elem.text.strip()
        
        return field_info
    
    def _extract_default_fields(self) -> List[Dict[str, Any]]:
        """
        Extract fields from generic XML structure as fallback.
        
        Returns:
            List of field dictionaries from generic structure
        """
        fields = []
        
        # Get all child elements
        for idx, child in enumerate(self.root):
            if child.tag.lower() not in ['name', 'description', 'version']:
                field_info = {
                    'field_id': f"field_{idx + 1}",
                    'name': child.get('name') or child.tag,
                    'datatype': child.get('type') or 'string',
                    'length': child.get('length') or '50',
                    'precision': '0',
                    'scale': '0',
                    'nullable': 'true',
                    'description': child.get('description') or ''
                }
                fields.append(field_info)
        
        return fields
    
    def extract_transformations(self) -> List[Dict[str, Any]]:
        """
        Extract transformation rules from XML.
        
        Returns:
            List of transformation dictionaries
        """
        transformations = []
        
        xpath_patterns = [
            './/Transformation',
            './/transformation',
            './/TRANSFORMATION',
            './/Expression',
            './/expression',
            './/Mapping',
            './/mapping'
        ]
        
        found_elements = []
        for xpath in xpath_patterns:
            try:
                elements = self.root.xpath(xpath)
                if elements:
                    found_elements = elements
                    break
            except:
                continue
        
        for idx, elem in enumerate(found_elements):
            trans_info = {
                'transformation_id': f"transform_{idx + 1}",
                'name': elem.get('name') or elem.get('Name') or f"transformation_{idx + 1}",
                'type': elem.get('type') or elem.get('Type') or 'expression',
                'expression': elem.text or elem.get('expression') or ''
            }
            transformations.append(trans_info)
        
        return transformations
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Extract complete metadata from XML.
        
        Returns:
            Dictionary with all extracted metadata
        """
        return {
            'file_path': self.xml_filepath,
            'root_tag': self.get_root_tag(),
            'workflow_name': self.get_workflow_name(),
            'fields': self.extract_fields(),
            'transformations': self.extract_transformations(),
            'total_fields': len(self.extract_fields()),
            'total_transformations': len(self.extract_transformations())
        }
