#!/usr/bin/env python
"""Verify that GemmaClient is being used."""

from app.services.model_client import get_model_client

client = get_model_client()
print(f'Model client type: {type(client).__name__}')
print(f'Is GemmaClient: {type(client).__name__ == "GemmaClient"}')

if hasattr(client, 'model'):
    print(f'Model: {client.model}')
