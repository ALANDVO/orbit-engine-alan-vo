#!/bin/bash
cd /var/lib/alan-portfolio/workspaces/alan/orbit-engine-alan-vo/backend
python3 -m pytest tests/ -v 2>&1
