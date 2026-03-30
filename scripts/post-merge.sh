#!/bin/bash
set -e

pip install -e . --quiet --no-input 2>&1 | tail -5
