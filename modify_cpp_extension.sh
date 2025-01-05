#!/bin/bash

# Path to the cpp_extension.py file
CPP_EXTENSION_FILE="/usr/local/lib/python3.10/dist-packages/torch/utils/cpp_extension.py"

# Check if the file exists
if [ -f "$CPP_EXTENSION_FILE" ]; then
    echo "Modifying $CPP_EXTENSION_FILE to skip CUDA version check..."
    
    # Comment out lines 386 and 387
    sed -i "386s/^/# /" "$CPP_EXTENSION_FILE"
    sed -i "387s/^/# /" "$CPP_EXTENSION_FILE"
    
    echo "Modification complete."
else
    echo "Error: cpp_extension.py file not found at $CPP_EXTENSION_FILE!"
    exit 1
fi
