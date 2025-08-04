#!/bin/sh
# Clean build script for Render or local use
rm -rf node_modules dist .vite src/*.jsx
npm install
npm run build
