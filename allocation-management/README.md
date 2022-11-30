# Allocation Management for Owner

This is a collection of scripts to handle the owner entry update in incore datasets.

Adding owner item needs the update of the user quota.
It is done by scanning the members list in the public user id and if the 
dataset id is a member of public id, the owner should be changed to the public id's name. 
Then, the quota should be reduced by the number and size of the dataset.

The regular dataset, dfr3 dataset, and hazard dataset should be calculated separated 
based on the dataset chracteristics.

## Procedures
- Update all the dataset's owner entry
-- run update-owner.py
- Update the owner based on public id member list
-- run recalculate-public-space.py