# README #

Clean up incore dataset repository

## Orders for clean up process ##
1. remove orphan dataset by using `remove_dataset_with_no_space.py`
2. remove defected shapefile dataset by using `remove_defacted_shapefile_dataset.py`

### optional
1. match dataset format and actual file by using `match_datset_format_and_data.py`
2. remove dataset with certain word in certain field by using `remove_by_finding_word_from_db.py`

## Update bouding box of the dataset
1. perform dataset clean up before updating the bounding box information
2. run `update_bbox_from_data_repo.py`