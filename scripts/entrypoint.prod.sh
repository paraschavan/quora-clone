#!/bin/bash

# Exit on error and enable error tracing
set -e
set -x  # Enable command tracing

# Function for cleanup on error
cleanup() {
    local exit_code=$?
    echo "Error occurred with exit code $exit_code. Cleaning up..."
    # Add any cleanup tasks here
    exit $exit_code
}

# Only trap errors if we're running in bash
if [ -n "$BASH_VERSION" ]; then
    trap 'cleanup' ERR
fi

echo "Running pre-commands..."
/app/scripts/pre_commands.sh

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running Server in Production Mode"

echo "Setting system limits..."
ulimit -n 65536 || true

echo "Verifying directory permissions..."
# Verify directories exist and are writable
for dir in /app/core/staticfiles; do
    if [ ! -w "$dir" ]; then
        echo "Error: Directory $dir is not writable"
        ls -la "$dir"
        exit 1
    fi
    echo "Directory $dir is writable"
done

echo "Starting Daphne..."
echo "Python path: $PYTHONPATH"
echo "Django settings module: $DJANGO_SETTINGS_MODULE"

exec daphne \
    -b 0.0.0.0 \
    -p ${DJANGO_PORT} \
    core.config.asgi:application
