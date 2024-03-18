#!/bin/bash

python rs_builder.py \
  --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "2", "1"], "pcts": [1, 1, 1]}' \
  --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [5, 10, 5]}' \
  --result_name "Galveston 3 rules" \
  --token ".incoretoken" \
  --service_url "https://incore-dev.ncsa.illinois.edu" \
  --space "commresiliencegal"
  # --space "galveston-app" on prod


python rs_builder.py \
  --rules '{"testbed": "slc", "rules": 3, "zones": ["COUNCIL DISTRICT 1", "COUNCIL DISTRICT 2", "COUNCIL DISTRICT 3"], "strtypes": ["URML", "URMM", "URML"], "pcts": [10, 20, 20]}' \
  --retrofits '{"ret_keys": ["Wood or Metal Deck Diaphragms Retrofitted", "Wood or Metal Deck Diaphragms Retrofitted", "Wood or Metal Deck Diaphragms Retrofitted"], "ret_vals": ["", "", ""]}'\
  --result_name "SLC 3 rules" \
  --token ".incoretoken" \
  --service_url "https://incore-dev.ncsa.illinois.edu" \
  --space "commresilienceslc"
  # --space "slc-app" on prod

python rs_builder.py \
  --rules '{"testbed": "joplin", "rules": 3, "zones": ["","",""], "strtypes": ["1", "2", "3"], "pcts": [34.5, 50, 20]}' \
  --retrofits '{"ret_keys": ["retrofit_2", "retrofit_2", "retrofit_2"], "ret_vals": ["", "", ""]}'\
  --result_name "Joplin 3 rules" \
  --token ".incoretoken" \
  --service_url "https://incore-dev.ncsa.illinois.edu" \
  --space "commresiliencejoplin"
  # --space "joplin-app" on prod
