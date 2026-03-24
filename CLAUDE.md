# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NiceCode is a Claude Code plugin marketplace. The guiding principle is **simplicity first**.

## Architecture

Marketplace (`.claude-plugin/marketplace.json`) → Plugins (`plugins/<name>/.claude-plugin/plugin.json`) → rules, commands, skills.

Each plugin is a self-contained bundle. Currently there is one plugin: `core`.

## Documentation

- When plugins change significantly (added, removed, renamed, or their structure changes), check `README.md` and update it to stay in sync.

## Git

- Do not add `Co-Authored-By` lines to commit messages.
- Write commit messages in English.
