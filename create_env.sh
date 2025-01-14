#!/bin/bash

# ==============================================================
# Script to create and set up virtual environments
# for the project: base, loftr, depth, and slam.
#
# This script will:
#   - Check if virtual environments exist; if not, create them.
#   - Install necessary packages in each environment in parallel.
#   - For the slam environment, perform additional setup steps.
#
# Author: Andrew Kent
# Date: 2024-12-04
# ==============================================================

clear

# Function to print colorful messages (directly to screen)
print_color() {
    local COLOR="$1"
    local MESSAGE="$2"
    local RESET='\033[0m'
    case $COLOR in
        "red")     COLOR_CODE='\033[0;31m' ;;
        "green")   COLOR_CODE='\033[0;32m' ;;
        "yellow")  COLOR_CODE='\033[1;33m' ;;
        "blue")    COLOR_CODE='\033[0;34m' ;;
        "magenta") COLOR_CODE='\033[0;35m' ;;
        "cyan")    COLOR_CODE='\033[0;36m' ;;
        *)         COLOR_CODE='\033[0m'    ;;
    esac
    echo -e "${COLOR_CODE}${MESSAGE}${RESET}"
}

# A helper function to run commands and color-code their output based on environment
run_command_colorful() {
    local ENV_NAME="$1"
    # The second parameter is the color we want for this environment's pip output
    local ENV_COLOR="$2"
    # Shift so that $@ will be the actual commands to run
    shift 2

    # Map color name to an ANSI code
    case $ENV_COLOR in
        "red")     ENV_COLOR_CODE='\033[0;31m' ;;
        "green")   ENV_COLOR_CODE='\033[0;32m' ;;
        "yellow")  ENV_COLOR_CODE='\033[1;33m' ;;
        "blue")    ENV_COLOR_CODE='\033[0;34m' ;;
        "magenta") ENV_COLOR_CODE='\033[0;35m' ;;
        "cyan")    ENV_COLOR_CODE='\033[0;36m' ;;
        *)         ENV_COLOR_CODE='\033[0m'    ;;
    esac
    local RESET='\033[0m'

    # Run the provided command(s); pipe the output through while-loop to prefix
    # each line with environment name, timestamp, and color.
    "$@" 2>&1 | while IFS= read -r line; do
        echo -e "${ENV_COLOR_CODE}[$ENV_NAME] $(date +'%Y-%m-%d %H:%M:%S') ${line}${RESET}"
    done
}

# Get the absolute path to the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# List of environments and their respective requirement files
declare -A ENVIRONMENTS
ENVIRONMENTS=(
    ["base"]="requirements/base.txt"
    ["depth"]="requirements/depth.txt"
    ["slam"]="requirements/slam.txt"
)

# Optionally, you can define distinct colors for each environment here
declare -A ENV_COLORS
ENV_COLORS=(
    ["base"]="blue"
    ["resnet"]="cyan"
    ["loftr"]="magenta"
    ["depth"]="green"
    ["slam"]="yellow"
)

# Create virtual environments if they don't exist
for ENV in "${!ENVIRONMENTS[@]}"; do
    if [ ! -d "$PROJECT_ROOT/venv/$ENV" ]; then
        python3.9 -m venv "$PROJECT_ROOT/venv/$ENV"
        print_color "green" "Created virtual environment: venv/$ENV"
    else
        print_color "yellow" "Virtual environment already exists: venv/$ENV"
    fi
done

# Function to set up an environment
setup_env() {
    local ENV_NAME="$1"
    local REQUIREMENTS_FILE="$2"
    local EXTRA_STEPS="$3"
    local COLOR_FOR_ENV="${ENV_COLORS[$ENV_NAME]}"

    print_color "$COLOR_FOR_ENV" "\nSetting up environment: $ENV_NAME"

    (
        source "$PROJECT_ROOT/venv/$ENV_NAME/bin/activate"

        # Upgrade pip/setuptools/wheel
        run_command_colorful "$ENV_NAME" "$COLOR_FOR_ENV" pip install --upgrade pip setuptools wheel

        # Install special packages if needed
        if [ "$ENV_NAME" == "slam" ]; then
            run_command_colorful "$ENV_NAME" "$COLOR_FOR_ENV" \
                pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 \
                -f https://download.pytorch.org/whl/torch_stable.html
        elif [ "$ENV_NAME" == "depth" ]; then
            run_command_colorful "$ENV_NAME" "$COLOR_FOR_ENV" \
                pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 \
                -f https://download.pytorch.org/whl/torch_stable.html
            run_command_colorful "$ENV_NAME" "$COLOR_FOR_ENV" \
                pip install mmcv-full==1.5.0 \
                -f https://download.openmmlab.com/mmcv/dist/cu113/torch1.11.0/index.html
        fi

        # Install general requirements
        if [ -f "$PROJECT_ROOT/$REQUIREMENTS_FILE" ]; then
            run_command_colorful "$ENV_NAME" "$COLOR_FOR_ENV" \
                pip install -r "$PROJECT_ROOT/$REQUIREMENTS_FILE"
        else
            print_color "red" "Requirements file not found: $REQUIREMENTS_FILE"
        fi

        # Run any extra steps (like DROID-SLAM setup for slam)
        if [ ! -z "$EXTRA_STEPS" ]; then
            eval "$EXTRA_STEPS"
        fi

        deactivate
    )
}

# Extra steps for slam environment
EXTRA_STEPS_SLAM='
cd "$PROJECT_ROOT/venv/slam"
if [ ! -d "DROID-SLAM" ]; then
    print_color "blue" "Cloning DROID-SLAM repository..."
    git clone --recursive https://github.com/princeton-vl/DROID-SLAM.git
    print_color "green" "Cloned DROID-SLAM repository"
fi
cd DROID-SLAM

# Use hardcoded path to cpp_extension.py
CPP_EXTENSION_FILE="$PROJECT_ROOT/venv/slam/lib/python3.9/site-packages/torch/utils/cpp_extension.py"
if [ -f "$CPP_EXTENSION_FILE" ]; then
    print_color "magenta" "Modifying $CPP_EXTENSION_FILE to skip CUDA version check..."
    sed -i "386s/^/# /" "$CPP_EXTENSION_FILE"
    sed -i "387s/^/# /" "$CPP_EXTENSION_FILE"
else
    print_color "red" "Error: cpp_extension.py file not found at $CPP_EXTENSION_FILE!"
    deactivate
    exit 1
fi

# Build and install DROID-SLAM
print_color "blue" "Building and installing DROID-SLAM..."
python3 setup.py install

cd "$PROJECT_ROOT"
'

# ----------------------------------------------------------------------
# Run each environment setup in parallel
# ----------------------------------------------------------------------
setup_env "base"   "${ENVIRONMENTS[base]}"   &
setup_env "depth"  "${ENVIRONMENTS[depth]}"  &
setup_env "slam"   "${ENVIRONMENTS[slam]}"   "$EXTRA_STEPS_SLAM" &

# Wait for all background jobs to finish
wait

# Print success message
print_color "green" "\nAll environments have been set up successfully (in parallel)."
