#!/bin/sh

make migrate-local

uvicorn hackathon.main:create_app --factory --reload --host 0.0.0.0 --port $HOC_SERVER_PORT

# Run the main container process
exec "$@"
