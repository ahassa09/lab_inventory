#!/bin/bash

cd "/Users/aminahassan/Desktop/work/lab_inventory"

/Library/Frameworks/Python.framework/Versions/3.12/bin/streamlit run inventory_admin.py &
sleep 3
open http://localhost:8501