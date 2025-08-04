#!/bin/sh
# Clean build script for Render or local use
rm -rf node_modules dist .vite
npm install
npm run build
