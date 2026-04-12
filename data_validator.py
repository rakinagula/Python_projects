"""Config-driven data quality validation for database tables"""
import json
import re
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ValidationRule:
    """Single validation rule from configuration"""
    def __init__(self, rule_dict: Dict[str, Any]):
        self.field_name = rule_dict.get('field_name')
        self.rule_type = rule_dict.get('rule_type')
        self.rule_config = rule_dict.get('rule_config', {})
        self.enabled = rule_dict.get('enabled', True)
        self.description = rule_dict.get('description', '')
    def is_valid(self) -> bool:
        return bool(self.field_name and self.rule_type)


class ValidationResult:
    """Stores results of a validation check"""
    def __init__(self, field_name: str, rule_type: str, passed: bool, message: str, 
                 failed_count: int = 0, total_count: int = 0):
        self.field_name = field_name
        self.rule_type = rule_type
        self.passed = passed
        self.message = message
        self.failed_count = failed_count
        self.total_count = total_count
        self.timestamp = datetime.now()
    def to_dict(self) -> Dict[str, Any]:
        return {'field_name': self.field_name, 'rule_type': self.rule_type,
                'passed': self.passed, 'message': self.message,
                'failed_count': self.failed_count, 'total_count': self.total_count,
                'timestamp': self.timestamp.isoformat()}


class TableValidator:
    """Validates data quality in a table based on configured rules"""
    def __init__(self, connection, table_name: str, rules: List[ValidationRule]):
        self.connection = connection
        self.table_name = table_name
        self.rules = [r for r in rules if r.enabled]
        self.results = []
    def get_row_count(self) -> int:
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting row count for {self.table_name}: {e}")
            return 0
    def get_column_data(self, column_name: str) -> List[Any]:
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT {column_name} FROM {self.table_name}")
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching column {column_name}: {e}")
            return []
    def validate_null_check(self, rule: ValidationRule) -> ValidationResult:
        data = self.get_column_data(rule.field_name)
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'null_check', False, "No data found", 0, 0)
        null_count = sum(1 for v in data if v is None)
        null_percentage = (null_count / total) * 100 if total > 0 else 0
        config = rule.rule_config
        if not config.get('allow_null', True) and null_count > 0:
            return ValidationResult(rule.field_name, 'null_check', False, 
                                  f"Nulls not allowed, found {null_count}", null_count, total)
        max_null_pct = config.get('max_null_percentage', 100)
        if null_percentage > max_null_pct:
            return ValidationResult(rule.field_name, 'null_check', False,
                                  f"Null% {null_percentage:.1f}% > {max_null_pct}%", null_count, total)
        return ValidationResult(rule.field_name, 'null_check', True,
                              f"Null: {null_count}/{total} ({null_percentage:.1f}%)", null_count, total)
    def validate_range_check(self, rule: ValidationRule) -> ValidationResult:
        data = [v for v in self.get_column_data(rule.field_name) if v is not None]
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'range_check', True, "No data to validate", 0, 0)
        config = rule.rule_config
        min_val = config.get('min_value')
        max_val = config.get('max_value')
        failed = sum(1 for v in data if (min_val and float(v) < float(min_val)) or 
                                        (max_val and float(v) > float(max_val)))
        return ValidationResult(rule.field_name, 'range_check', failed == 0,
                              f"Range [{min_val},{max_val}]: {total-failed}/{total} passed", failed, total)
    def validate_allowed_values(self, rule: ValidationRule) -> ValidationResult:
        data = [v for v in self.get_column_data(rule.field_name) if v is not None]
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'allowed_values', True, "No data to validate", 0, 0)
        allowed = set(rule.rule_config.get('values', []))
        failed = sum(1 for v in data if v not in allowed)
        return ValidationResult(rule.field_name, 'allowed_values', failed == 0,
                              f"Allowed values: {total-failed}/{total} valid", failed, total)
    def validate_pattern(self, rule: ValidationRule) -> ValidationResult:
        pattern_str = rule.rule_config.get('pattern')
        if not pattern_str:
            return ValidationResult(rule.field_name, 'pattern_check', False, "No pattern specified", 0, 0)
        data = [str(v) for v in self.get_column_data(rule.field_name) if v is not None]
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'pattern_check', True, "No data to validate", 0, 0)
        try:
            regex = re.compile(pattern_str)
            failed = sum(1 for v in data if not regex.match(v))
        except re.error as e:
            return ValidationResult(rule.field_name, 'pattern_check', False, f"Invalid regex: {e}", 0, 0)
        return ValidationResult(rule.field_name, 'pattern_check', failed == 0,
                              f"Pattern: {total-failed}/{total} matched", failed, total)
    def validate_uniqueness(self, rule: ValidationRule) -> ValidationResult:
        data = self.get_column_data(rule.field_name)
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'uniqueness_check', True, "No data to validate", 0, 0)
        allow_null_dupes = rule.rule_config.get('allow_null_duplicates', True)
        data_check = data if allow_null_dupes else [v for v in data if v is not None]
        unique = len(set(data_check))
        failed = total - unique
        return ValidationResult(rule.field_name, 'uniqueness_check', failed == 0,
                              f"Unique: {unique}/{total}", failed, total)
    def validate_data_type(self, rule: ValidationRule) -> ValidationResult:
        exp_type = rule.rule_config.get('expected_type')
        if not exp_type:
            return ValidationResult(rule.field_name, 'datatype_check', False, "No type specified", 0, 0)
        data = [v for v in self.get_column_data(rule.field_name) if v is not None]
        total = len(data)
        if total == 0:
            return ValidationResult(rule.field_name, 'datatype_check', True, "No data to validate", 0, 0)
        failed = sum(1 for v in data if not self._check_type(v, exp_type))
        return ValidationResult(rule.field_name, 'datatype_check', failed == 0,
                              f"Type {exp_type}: {total-failed}/{total} valid", failed, total)
    @staticmethod
    def _check_type(value: Any, exp_type: str) -> bool:
        try:
            exp_type_lower = exp_type.lower()
            if exp_type_lower in ['string', 'str', 'varchar']:
                return isinstance(value, str)
            elif exp_type_lower in ['integer', 'int']:
                int(value)
                return True
            elif exp_type_lower in ['float', 'decimal', 'double']:
                float(value)
                return True
            elif exp_type_lower in ['date', 'timestamp', 'datetime']:
                return isinstance(value, (date, datetime)) or str(value)
            return True
        except (ValueError, TypeError):
            return False
    def run_all_validations(self) -> List[ValidationResult]:
        self.results = []
        for rule in self.rules:
            if not rule.is_valid():
                logger.warning(f"Invalid rule: {rule.field_name}")
                continue
            try:
                handlers = {
                    'null_check': self.validate_null_check,
                    'range_check': self.validate_range_check,
                    'allowed_values': self.validate_allowed_values,
                    'pattern_check': self.validate_pattern,
                    'uniqueness_check': self.validate_uniqueness,
                    'datatype_check': self.validate_data_type,
                }
                handler = handlers.get(rule.rule_type)
                if handler:
                    self.results.append(handler(rule))
                else:
                    logger.warning(f"Unknown rule type: {rule.rule_type}")
            except Exception as e:
                logger.error(f"Error validating {self.table_name}.{rule.field_name}: {e}")
                self.results.append(ValidationResult(rule.field_name, rule.rule_type, False,
                                                    f"Validation error: {e}", 0, 0))
        return self.results


class DataValidationManager:
    """Manages data validation for multiple tables with parallelization"""
    def __init__(self, config_file: str, connection):
        self.config_file = config_file
        self.connection = connection
        self.config = self._load_config()
        self.all_results = []
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            logger.info(f"Loaded config: {self.config_file}")
            return config
        except FileNotFoundError:
            logger.error(f"Config not found: {self.config_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return {}
    def _get_rules_for_table(self, table_name: str) -> List[ValidationRule]:
        for table in self.config.get('validation_tables', []):
            if table.get('table_name') == table_name:
                return [ValidationRule(r) for r in table.get('validation_rules', [])]
        return []
    def validate_single_table(self, table_name: str) -> Tuple[str, List[ValidationResult]]:
        logger.info(f"Validating: {table_name}")
        rules = self._get_rules_for_table(table_name)
        if not rules:
            logger.warning(f"No rules for: {table_name}")
            return table_name, []
        validator = TableValidator(self.connection, table_name, rules)
        results = validator.run_all_validations()
        logger.info(f"Done: {table_name}")
        return table_name, results
    def validate_all_tables(self, use_parallel: bool = False, 
                           max_workers: int = 4) -> Dict[str, List[ValidationResult]]:
        tables_config = self.config.get('validation_tables', [])
        table_names = [t.get('table_name') for t in tables_config if t.get('table_name')]
        if not table_names:
            logger.warning("No tables to validate")
            return {}
        results_dict = {}
        if use_parallel and len(table_names) > 1:
            logger.info(f"Parallel validation: {len(table_names)} tables")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.validate_single_table, t): t for t in table_names}
                for future in as_completed(futures):
                    tname, results = future.result()
                    results_dict[tname] = results
                    self.all_results.extend(results)
        else:
            logger.info(f"Sequential validation: {len(table_names)} tables")
            for tname in table_names:
                _, results = self.validate_single_table(tname)
                results_dict[tname] = results
                self.all_results.extend(results)
        return results_dict
    def generate_report(self) -> Dict[str, Any]:
        total = len(self.all_results)
        passed = sum(1 for r in self.all_results if r.passed)
        failed = total - passed
        return {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'config_file': self.config_file,
                'total_checks': total,
                'passed_checks': passed,
                'failed_checks': failed,
                'pass_percentage': (passed / total * 100) if total > 0 else 0
            },
            'detailed_results': [r.to_dict() for r in self.all_results],
            'failed_validations': [r.to_dict() for r in self.all_results if not r.passed]
        }
    def save_report_to_file(self, output_file: str) -> None:
        try:
            with open(output_file, 'w') as f:
                json.dump(self.generate_report(), f, indent=2)
            logger.info(f"Report saved: {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    def print_summary(self) -> None:
        report = self.generate_report()
        s = report['summary']
        print(f"\n{'='*60}\nDATA VALIDATION REPORT\n{'='*60}")
        print(f"Timestamp: {s['timestamp']}\nConfig: {s['config_file']}")
        print(f"\nTotal: {s['total_checks']}, Passed: {s['passed_checks']}, "
              f"Failed: {s['failed_checks']}, Rate: {s['pass_percentage']:.1f}%")
        if report['failed_validations']:
            print("\nFailed:")
            for f in report['failed_validations'][:10]:
                print(f"  - {f['field_name']} ({f['rule_type']}): {f['message']}")
        print(f"{'='*60}\n")
