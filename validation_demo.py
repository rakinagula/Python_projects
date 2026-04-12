"""Demo showing data validation usage"""
import sqlite3, json, sys, logging
from pathlib import Path
from data_validator import DataValidationManager, ValidationRule, TableValidator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_sample_database(db_file: str):
    """Create sample SQLite database with test data"""
    logger.info(f"Creating: {db_file}")
    if Path(db_file).exists():
        Path(db_file).unlink()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, customer_name TEXT, email TEXT, customer_age INTEGER, status TEXT, registration_date DATE)')
    cursor.executemany('INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)',
        [(1, 'John Smith', 'john.smith@email.com', 35, 'Active', '2020-01-15'),
         (2, 'Jane Doe', 'jane.doe@email.com', 28, 'Active', '2021-03-22'),
         (3, 'Bob Johnson', 'bob.johnson@email.com', 42, 'Inactive', '2019-06-10'),
         (4, 'Alice Brown', 'alice.brown@email.com', 31, 'Active', '2022-05-08'),
         (5, 'Charlie Wilson', 'invalid-email', 25, 'Suspended', '2023-01-20'),
         (6, 'Diana Lee', 'diana.lee@email.com', 150, 'Active', '2020-11-30'),
         (7, 'Eve Martinez', None, 29, 'Active', '2021-09-12'),
         (8, 'Frank Thomas', 'frank@email.com', 33, 'Active', '2022-02-14')])
    cursor.execute('CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_amount DECIMAL(10,2), order_status TEXT, order_date DATE)')
    cursor.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)',
        [(1001, 1, 150.00, 'Delivered', '2023-01-15'),
         (1002, 2, 250.50, 'Shipped', '2023-02-20'),
         (1003, 1, 99.99, 'Processing', '2023-03-10'),
         (1004, 3, 500.00, 'Delivered', '2023-01-25'),
         (1005, 4, -50.00, 'Cancelled', '2023-02-15'),
         (1006, 2, None, 'Pending', '2023-03-05'),
         (1007, 5, 200.00, 'Invalid_Status', '2023-03-15'),
         (1008, 8, 350.00, 'Delivered', '2023-04-01'),
         (1009, 1, 175.25, 'Returned', '2023-04-05')])
    cursor.execute('CREATE TABLE products (product_id INTEGER PRIMARY KEY, product_name TEXT, price DECIMAL(10,2), category TEXT, stock_quantity INTEGER)')
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?)',
        [(101, 'Laptop', 999.99, 'Electronics', 25),
         (102, 'Mouse', 29.99, 'Electronics', 150),
         (103, 'T-Shirt', 19.99, 'Clothing', 200),
         (104, 'Jeans', 59.99, 'Clothing', 100),
         (105, 'Novel', 14.99, 'Books', 50),
         (106, 'Coffee Maker', 79.99, 'Home', 30),
         (107, 'Invalid Product', -50.00, 'Food', -10),
         (108, 'Headphones', 149.99, 'InvalidCategory', 75),
         (109, 'Desk Chair', 199.99, 'Home', 40),
         (110, 'Monitor', 299.99, 'Electronics', 60)])
    conn.commit()
    conn.close()
    logger.info(f"Created: {db_file}")


def demo_sequential_validation():
    """Demonstrate sequential validation"""
    print("\n" + "="*70)
    print("DEMO 1: SEQUENTIAL VALIDATION OF ALL TABLES")
    print("="*70)
    
    # Create sample database
    db_file = 'demo_validation.db'
    create_sample_database(db_file)
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Create validation manager
    config_file = 'validation_config.json'
    validator = DataValidationManager(config_file, conn)
    
    # Run sequential validation
    results = validator.validate_all_tables(use_parallel=False)
    
    # Print summary
    validator.print_summary()
    
    # Save report
    report_file = 'validation_report_sequential.json'
    validator.save_report_to_file(report_file)
    print(f"Report saved to: {report_file}\n")
    
    conn.close()
    return report_file


def demo_parallel_validation():
    """Demonstrate parallel validation"""
    print("\n" + "="*70)
    print("DEMO 2: PARALLEL VALIDATION OF MULTIPLE TABLES")
    print("="*70)
    
    # Create sample database
    db_file = 'demo_validation.db'
    if not Path(db_file).exists():
        create_sample_database(db_file)
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Create validation manager
    config_file = 'validation_config.json'
    validator = DataValidationManager(config_file, conn)
    
    # Run parallel validation with 3 workers
    print("Running parallel validation with 3 workers...")
    results = validator.validate_all_tables(use_parallel=True, max_workers=3)
    
    # Print summary
    validator.print_summary()
    
    # Save report
    report_file = 'validation_report_parallel.json'
    validator.save_report_to_file(report_file)
    print(f"Report saved to: {report_file}\n")
    
    conn.close()
    return report_file


def demo_single_table_validation():
    """Demonstrate custom validation on a single table"""
    print("\n" + "="*70)
    print("DEMO 3: CUSTOM VALIDATION ON SINGLE TABLE")
    print("="*70)
    
    # Create sample database
    db_file = 'demo_validation.db'
    if not Path(db_file).exists():
        create_sample_database(db_file)
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Create config file
    config_file = 'validation_config.json'
    validator = DataValidationManager(config_file, conn)
    
    # Validate only customers table
    print("\nValidating only the 'customers' table...\n")
    table_name, results = validator.validate_single_table('customers')
    
    # Print results
    print(f"Table: {table_name}")
    print(f"Total checks: {len(results)}")
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {status} | {result.field_name} ({result.rule_type}): {result.message}")
    
    conn.close()


def demo_programmatic_usage():
    """Demonstrate programmatic usage of the validator"""
    print("\n" + "="*70)
    print("DEMO 4: PROGRAMMATIC USAGE EXAMPLE")
    print("="*70)
    
    # Create sample database
    db_file = 'demo_validation.db'
    if not Path(db_file).exists():
        create_sample_database(db_file)
    
    # Connect to database
    conn = sqlite3.connect(db_file)
    
    # Create custom validation rules
    print("\nCreating custom validation rules for 'customers' table...")
    custom_rules = [
        ValidationRule({
            'field_name': 'customer_id',
            'rule_type': 'null_check',
            'enabled': True,
            'rule_config': {'allow_null': False}
        }),
        ValidationRule({
            'field_name': 'customer_age',
            'rule_type': 'range_check',
            'enabled': True,
            'rule_config': {'min_value': 18, 'max_value': 100}
        }),
        ValidationRule({
            'field_name': 'status',
            'rule_type': 'allowed_values',
            'enabled': True,
            'rule_config': {'values': ['Active', 'Inactive', 'Suspended']}
        })
    ]
    
    # Create table validator
    table_validator = TableValidator(conn, 'customers', custom_rules)
    
    # Run validations
    print(f"\nRunning {len(custom_rules)} validation rules on 'customers' table...")
    results = table_validator.run_all_validations()
    
    # Display results
    print(f"\nValidation Results:")
    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"  {status} | {result.field_name}")
        print(f"      Rule: {result.rule_type}")
        print(f"      Message: {result.message}")
        if result.failed_count > 0:
            print(f"      Failed: {result.failed_count}/{result.total_count} records")
        print()
    
    conn.close()


def display_report_summary(report_file: str):
    """Display a summary of validation report"""
    try:
        with open(report_file, 'r') as f:
            report = json.load(f)
        
        print(f"\nReport Summary from {report_file}:")
        print("-" * 50)
        summary = report['summary']
        print(f"  Total Checks: {summary['total_checks']}")
        print(f"  Passed: {summary['passed_checks']}")
        print(f"  Failed: {summary['failed_checks']}")
        print(f"  Pass Rate: {summary['pass_percentage']:.2f}%")
        
    except Exception as e:
        logger.error(f"Error reading report: {e}")


def main():
    """Main demo function"""
    print("\n" + "="*70)
    print("DATA VALIDATION MODULE - COMPREHENSIVE DEMO")
    print("="*70)
    
    try:
        # Run demonstrations
        print("\nSelect which demo to run:")
        print("1. Sequential Validation")
        print("2. Parallel Validation")
        print("3. Single Table Validation")
        print("4. Programmatic Usage")
        print("5. Run All Demos")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            demo_sequential_validation()
        elif choice == '2':
            demo_parallel_validation()
        elif choice == '3':
            demo_single_table_validation()
        elif choice == '4':
            demo_programmatic_usage()
        elif choice == '5':
            demo_sequential_validation()
            demo_parallel_validation()
            demo_single_table_validation()
            demo_programmatic_usage()
        else:
            print("Invalid choice. Running all demos...")
            demo_sequential_validation()
            demo_parallel_validation()
            demo_single_table_validation()
            demo_programmatic_usage()
        
        print("\n" + "="*70)
        print("DEMO COMPLETED")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
