"""CLI for data quality validation"""
import argparse, sys, sqlite3, json, logging
from pathlib import Path
from data_validator import DataValidationManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_connection(db_type: str, params: dict):
    """Create database connection"""
    try:
        if db_type.lower() == 'sqlite':
            if not params.get('database'):
                raise ValueError("SQLite needs database path")
            conn = sqlite3.connect(params['database'])
            logger.info(f"SQLite: {params['database']}")
            return conn
        elif db_type.lower() == 'oracle':
            import cx_Oracle
            dsn = f"{params['host']}:{params.get('port', 1521)}/{params['sid']}"
            conn = cx_Oracle.connect(params['username'], params['password'], dsn)
            logger.info(f"Oracle: {dsn}")
            return conn
        elif db_type.lower() == 'mysql':
            import mysql.connector
            conn = mysql.connector.connect(
                host=params['host'], user=params['username'], password=params['password'],
                database=params['database'], port=params.get('port', 3306))
            logger.info(f"MySQL: {params['database']}")
            return conn
        elif db_type.lower() == 'postgres':
            import psycopg2
            conn = psycopg2.connect(
                host=params['host'], user=params['username'], password=params['password'],
                database=params['database'], port=params.get('port', 5432))
            logger.info(f"PostgreSQL: {params['database']}")
            return conn
        elif db_type.lower() == 'mssql':
            import pyodbc
            conn_str = (f"Driver={{ODBC Driver 17 for SQL Server}};Server={params['host']};"
                       f"Database={params['database']};UID={params['username']};PWD={params['password']};")
            conn = pyodbc.connect(conn_str)
            logger.info(f"SQL Server: {params['database']}")
            return conn
        else:
            raise ValueError(f"Unsupported DB: {db_type}")
    except ImportError as e:
        logger.error(f"Missing driver: {e}")
        raise
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        raise

def validate_args(args) -> bool:
    """Validate command line arguments"""
    if not args.config:
        logger.error("Config required (-c)")
        return False
    if not Path(args.config).exists():
        logger.error(f"Config not found: {args.config}")
        return False
    return True

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Config-driven data validation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  python validate_data.py -c config.json -d test.db\n"
               "  python validate_data.py -c config.json -d test.db --parallel")
    
    parser.add_argument('-c', '--config', required=True, help='Config JSON file')
    parser.add_argument('-d', '--database', help='Database path/connection')
    parser.add_argument('-o', '--output', help='Output report file')
    parser.add_argument('--db-type', default='sqlite', 
                       choices=['sqlite', 'oracle', 'mysql', 'postgres', 'mssql'],
                       help='Database type (default: sqlite)')
    parser.add_argument('--parallel', action='store_true', help='Use parallel processing')
    parser.add_argument('--workers', type=int, default=4, help='Parallel workers (default: 4)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not validate_args(args):
        sys.exit(1)
    
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
        
        db_type = args.db_type
        params = config.get('database_connection', {})
        if args.database:
            params['database'] = args.database
        
        logger.info(f"Connecting to {db_type}...")
        connection = get_database_connection(db_type, params)
        
        logger.info("Starting validation...")
        validator = DataValidationManager(args.config, connection)
        validator.validate_all_tables(use_parallel=args.parallel, max_workers=args.workers)
        
        validator.print_summary()
        
        if args.output:
            validator.save_report_to_file(args.output)
        
        connection.close()
        logger.info("Done")
        
    except Exception as e:
        logger.error(f"Failed: {e}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == '__main__':
    main()
