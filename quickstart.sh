#!/bin/bash

# ============================================================================
# Informatica Framework - Quick Start Guide
# ============================================================================
# This script demonstrates how to quickly get started with the framework
# ============================================================================

echo "========================================================================"
echo "Informatica Metadata to JSON Configuration Framework"
echo "Quick Start Guide"
echo "========================================================================"
echo ""

# Check Python version
echo "[1/5] Checking Python version..."
python --version

# Install requirements
echo ""
echo "[2/5] Installing requirements..."
pip install -r requirements.txt

# Run main framework
echo ""
echo "[3/5] Running main framework..."
echo "Output: output/customer_etl_config.json"
python informatica_framework.py

# Run examples
echo ""
echo "[4/5] Running all examples..."
python example_usage.py

# List output files
echo ""
echo "[5/5] Generated output files:"
find output -type f -name "*.json" | sort

echo ""
echo "========================================================================"
echo "Framework setup complete!"
echo "========================================================================"
echo ""
echo "Log file: logs/informatica_framework.log"
echo "Output directory: output/"
echo ""
echo "Next steps:"
echo "1. Review generated JSON files in output/ directory"
echo "2. Check logs/informatica_framework.log for execution details"
echo "3. Modify example mapping data in example_usage.py"
echo "4. Run 'python informatica_framework.py' with your own mapping data"
echo ""
