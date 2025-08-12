#!/bin/bash
# Test import script with automatic inputs

source venv/bin/activate

# Create input file with responses
cat << EOF > test_inputs.txt

si
EOF

# Run the import script with inputs
python scripts_cli/importar_movimientos_bbva.py < test_inputs.txt

# Clean up
rm test_inputs.txt