"""
Comprehensive test of all data validation features
"""

import sqlite3
import json
from pathlib import Path
from data_validator import DataValidationManager

def create_comprehensive_test_db():
    """Create a comprehensive test database"""
    db_file = 'comprehensive_test.db'
    if Path(db_file).exists():
        Path(db_file).unlink()
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Create comprehensive test tables
    cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT,
            age INTEGER,
            status TEXT
        )
    ''')
    
    users_data = [
        (1, 'alice', 'alice@example.com', 28, 'active'),
        (2, 'bob', 'bob@example.com', 35, 'active'),
        (3, 'charlie', 'invalid-email', 150, 'inactive'),
        (4, 'diana', None, 22, 'active'),
        (5, 'eve', 'eve@example.com', 45, 'suspended'),
    ]
    cursor.executemany('INSERT INTO users VALUES (?, ?, ?, ?, ?)', users_data)
    
    cursor.execute('''
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT,
            price DECIMAL,
            quantity INTEGER,
            category TEXT
        )
    ''')
    
    products_data = [
        (1, 'Laptop', 999.99, 10, 'Electronics'),
        (2, 'Mouse', 29.99, 100, 'Electronics'),
        (3, 'Desk', -50.00, 5, 'Furniture'),  # Invalid price
        (4, 'Chair', 149.99, 20, 'Furniture'),
        (5, 'Monitor', 299.99, None, 'Electronics'),  # Null quantity
    ]
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)', products_data)
    
    conn.commit()
    conn.close()
    return db_file

def create_test_config():
    """Create comprehensive test configuration"""
    config = {
        "validation_config": {
            "version": "1.0",
            "description": "Comprehensive validation test"
        },
        "database_connection": {
            "db_type": "sqlite",
            "database": "comprehensive_test.db"
        },
        "validation_tables": [
            {
                "table_name": "users",
                "enabled": True,
                "validation_rules": [
                    {
                        "field_name": "user_id",
                        "rule_type": "null_check",
                        "rule_config": {"allow_null": False}
                    },
                    {
                        "field_name": "user_id",
                        "rule_type": "uniqueness_check",
                        "rule_config": {}
                    },
                    {
                        "field_name": "email",
                        "rule_type": "pattern_check",
                        "rule_config": {
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
                        }
                    },
                    {
                        "field_name": "age",
                        "rule_type": "range_check",
                        "rule_config": {"min_value": 18, "max_value": 100}
                    },
                    {
                        "field_name": "status",
                        "rule_type": "allowed_values",
                        "rule_config": {"values": ["active", "inactive", "suspended"]}
                    }
                ]
            },
            {
                "table_name": "products",
                "enabled": True,
                "validation_rules": [
                    {
                        "field_name": "product_id",
                        "rule_type": "null_check",
                        "rule_config": {"allow_null": False}
                    },
                    {
                        "field_name": "price",
                        "rule_type": "range_check",
                        "rule_config": {"min_value": 0.01, "max_value": 999999}
                    },
                    {
                        "field_name": "quantity",
                        "rule_type": "null_check",
                        "rule_config": {"allow_null": True, "max_null_percentage": 10}
                    },
                    {
                        "field_name": "category",
                        "rule_type": "allowed_values",
                        "rule_config": {"values": ["Electronics", "Furniture", "Books"]}
                    }
                ]
            }
        ]
    }
    
    with open('comprehensive_test_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return 'comprehensive_test_config.json'

def main():
    """Run comprehensive test"""
    print("\n" + "="*70)
    print("COMPREHENSIVE DATA VALIDATION TEST")
    print("="*70)
    
    try:
        # Setup
        print("\n[1/5] Creating test database...")
        db_file = create_comprehensive_test_db()
        print(f"      ✓ Database created: {db_file}")
        
        print("\n[2/5] Creating test configuration...")
        config_file = create_test_config()
        print(f"      ✓ Configuration created: {config_file}")
        
        # Run validation
        print("\n[3/5] Connecting to database...")
        conn = sqlite3.connect(db_file)
        print("      ✓ Connection established")
        
        print("\n[4/5] Running validations...")
        validator = DataValidationManager(config_file, conn)
        results = validator.validate_all_tables(use_parallel=False)
        print(f"      ✓ Validated {len(results)} tables")
        
        print("\n[5/5] Generating report...")
        report = validator.generate_report()
        report_file = 'comprehensive_test_report.json'
        validator.save_report_to_file(report_file)
        print(f"      ✓ Report saved: {report_file}")
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        summary = report['summary']
        print(f"Total Checks:      {summary['total_checks']}")
        print(f"Passed Checks:     {summary['passed_checks']}")
        print(f"Failed Checks:     {summary['failed_checks']}")
        print(f"Pass Percentage:   {summary['pass_percentage']:.1f}%")
        
        if report['failed_validations']:
            print(f"\nFailed Validations ({len(report['failed_validations'])}):")
            for failure in report['failed_validations'][:5]:  # Show first 5
                print(f"  • {failure['field_name']} ({failure['rule_type']})")
                print(f"    {failure['message']}")
        
        print("\n" + "="*70)
        print("✓ COMPREHENSIVE TEST COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
        # Cleanup
        conn.close()
        print("Files created (for manual verification):")
        print(f"  - {db_file}")
        print(f"  - {config_file}")
        print(f"  - {report_file}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
