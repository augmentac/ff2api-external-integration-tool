#!/bin/bash

# Barrier-Breaking LTL Tracking Demo Startup Script
# This script starts the production demo of the barrier-breaking system

echo "🚀 Starting Barrier-Breaking LTL Tracking Demo..."
echo "=================================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Streamlit is installed
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit is not installed"
    echo "💡 Install with: pip3 install streamlit"
    exit 1
fi

# Check if the demo app exists
if [ ! -f "barrier_breaking_demo_app.py" ]; then
    echo "❌ Demo app not found: barrier_breaking_demo_app.py"
    exit 1
fi

echo "✅ All dependencies found!"
echo "🔧 Starting Streamlit app on port 8504..."
echo ""
echo "🌐 Open your browser and navigate to:"
echo "   http://localhost:8504"
echo ""
echo "📋 Features available:"
echo "   • Live tracking demonstration"
echo "   • Barrier-breaking system showcase"
echo "   • Real-time tracking with Apple Silicon ARM64 CPU barrier solved"
echo "   • Production-ready interface"
echo ""
echo "🛑 Press Ctrl+C to stop the demo"
echo "=================================================="

# Start the Streamlit app
python3 -m streamlit run barrier_breaking_demo_app.py --server.port 8504 