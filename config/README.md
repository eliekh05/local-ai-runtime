# config/ — Configuration Directory

This directory contains configuration templates and (eventually) active
configuration files for the local-ai-runtime system.

## Files in this directory

| File | Status | Purpose |
|---|---|---|
| `server.config.example.json` | Template | HTTP server settings |
| `model.config.example.json` | Template | Model profile settings |
| `server.config.json` | **Not yet created** | Your actual server config |
| `model.config.json` | **Not yet created** | Your actual model config |
| `model_registry.json` | **Not yet created** | Created by model registry system |

## How to use the config system

> ⚠️ The config system is not yet implemented. This is a plan.

1. Copy the example files:
   ```bash
   cp server.config.example.json server.config.json
   cp model.config.example.json model.config.json
   ```

2. Edit `model.config.json` to point to your GGUF file and set the correct
   `chat_template` for that model.

3. Edit `server.config.json` if you need to change the port or host.

## What should NOT be committed

- `server.config.json` — May contain local paths
- `model.config.json` — Contains local file paths
- `model_registry.json` — Machine-specific (generated at runtime)
- `cache_manifest.json` — Machine-specific (generated at runtime)

These are listed in `.gitignore` (once that file is created).

## What SHOULD be committed

- `*.example.json` files — These are templates for other developers
- This README

## Config file parsing

The backend reads these files at startup (once implemented in Phase 1.1/1.4).
Changes to `model.config.json` require a server restart or a PUT to `/config`
(once that endpoint is implemented).
