#!/bin/sh

make migrate-local

uvicorn hackathon.main:create_app --factory --host 0.0.0.0 --port 80

# Run the main container process
exec "$@"
