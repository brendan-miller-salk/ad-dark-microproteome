#!/bin/bash

# Brain Microproteins Dashboard Launch Script
echo "🧬 Launching Brain Microproteins Dashboard..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate conda environment
echo "📦 Activating conda environment 'github'..."
source /Users/brendanmiller/miniconda/etc/profile.d/conda.sh
conda activate github

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate conda environment 'github'"
    echo "Please make sure the environment exists and try again."
    exit 1
fi

# Navigate to the script directory
cd "$SCRIPT_DIR"

# Check if the Python file exists
if [ ! -f "microproteins_dashboard.py" ]; then
    echo "❌ microproteins_dashboard.py not found in current directory"
    exit 1
fi

echo "🚀 Starting Brain Microproteins Dashboard on port 8505..."
echo "📂 Working directory: $SCRIPT_DIR"
echo "🌐 The dashboard will be available at: http://localhost:8505"
echo ""
echo "📋 Dashboard Features:"
echo "   • 📊 Interactive CSV viewing with filtering/sorting"
echo "   • 🌐 Clickable UCSC Genome Browser links"
echo "   • 🎨 Color-coded Swiss-Prot vs Noncanonical microproteins"
echo "   • 📥 Download filtered results"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Launch Streamlit
streamlit run microproteins_dashboard.py --server.port 8505 --server.headless true

# If we get here, the server has stopped
echo ""
echo "🛑 Brain Microproteins Dashboard has stopped"