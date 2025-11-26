#!/bin/bash
# Fix Port 5000 Issue on macOS
# Helps resolve port conflicts, especially with AirPlay Receiver

PORT=5000

echo "Checking port $PORT usage..."

if command -v lsof > /dev/null 2>&1; then
    PID=$(lsof -ti:$PORT -sTCP:LISTEN 2>/dev/null)
    
    if [ -n "$PID" ]; then
        PROCESS=$(ps -p $PID -o comm= 2>/dev/null || echo "Unknown")
        echo "⚠️  Port $PORT is in use by process: $PROCESS (PID: $PID)"
        echo ""
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "On macOS, this is often AirPlay Receiver."
            echo ""
            echo "Options:"
            echo "1. Disable AirPlay Receiver:"
            echo "   System Preferences → General → AirDrop & Handoff"
            echo "   Uncheck 'AirPlay Receiver'"
            echo ""
            echo "2. Use a different port:"
            echo "   Edit config/.env and set: PORT=5001"
            echo ""
            echo "3. Kill the process (use with caution):"
            read -p "   Kill process $PID ($PROCESS)? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                kill -9 $PID 2>/dev/null && echo "✅ Process killed" || echo "❌ Failed to kill process"
            fi
        else
            echo "To free the port:"
            echo "  kill -9 $PID"
            echo ""
            echo "Or use a different port in config/.env:"
            echo "  PORT=5001"
        fi
    else
        echo "✅ Port $PORT is available"
    fi
else
    echo "⚠️  'lsof' command not found. Cannot check port usage."
    echo "Install with: brew install lsof (macOS) or apt-get install lsof (Linux)"
fi

