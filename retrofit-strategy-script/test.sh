#!/bin/bash

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "2", "1"], "pcts": [1, 1, 1]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [5, 10, 5]}' \
#   --result_name "Galveston 3 rules" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 2, "zones": ["1P", "1P"], "strtypes": ["1", "1"], "pcts": [100, 0]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation"], "ret_vals": [5, 10]}' \
#   --result_name "Galveston 2 rules mixing retrofit methods" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "1", "2"], "pcts":
#    [1, 1, 1]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [10, 10, 5]}' \
#   --result_name "Galveston 3 rules duplicate not allowed" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "1", "2"], "pcts":
#    [60, 60, 1]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [10, 5, 5]}' \
#   --result_name "Galveston 3 rules pct exceed" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "1", "2"], "pcts":
#    [0, 0, 0]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [10, 5, 5]}' \
#   --result_name "Galveston 3 rules 0 percent" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "galveston", "rules": 3, "zones": ["1P", "1P", "0.2P"], "strtypes": ["1", "1", "2"], "pcts":
#    [0, 0, 1]}' \
#   --retrofits '{"ret_keys": ["elevation", "elevation", "elevation"], "ret_vals": [10, 5, 5]}' \
#   --result_name "Galveston 3 rules with only one valid percent" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencegal"
#   # --space "galveston-app" on prod

python rs_builder.py \
  --rules '{"testbed": "slc", "rules": 3, "zones": ["1", "2", "3"], "strtypes": ["URML", "URMM", "URML"], "pcts": [10, 20, 20]}' \
  --retrofits '{"ret_keys": ["Wood or Metal Deck Diaphragms Retrofitted", "Wood or Metal Deck Diaphragms Retrofitted", "Wood or Metal Deck Diaphragms Retrofitted"], "ret_vals": ["", "", ""]}'\
  --result_name "SLC 3 rules" \
  --token ".incoretoken" \
  --service_url "https://incore-dev.ncsa.illinois.edu" \
  --space "commresilienceslc"
  # --space "slc-app" on prod

# python rs_builder.py \
#   --rules '{"testbed": "joplin", "rules": 3, "zones": ["","",""], "strtypes": ["1", "1", "1"], "pcts": [34.5, 65.5, 0]}' \
#   --retrofits '{"ret_keys": ["retrofit_1", "retrofit_2", "retrofit_3"], "ret_vals": ["", "", ""]}'\
#   --result_name "Joplin 3 rules" \
#   --token ".incoretoken" \
#   --service_url "https://incore-dev.ncsa.illinois.edu" \
#   --space "commresiliencejoplin"
#   # --space "joplin-app" on prod
