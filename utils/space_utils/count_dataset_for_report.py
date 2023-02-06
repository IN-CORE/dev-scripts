# this is a script for counting the number of dataset in public space
# public space in here is incore and ergo space
# coe is not a public because it is only for the specific users

# this script should be run after port forwarding the mongodb from kube
# kubectl port-forwarding -n incore services/incore-mongodb 270**:27017


##################
# example report
##################
# •395 datasets (60% of them are hazard data) with 187 dataset types
# •1092 fragility curves
# •Earthquake
# •Tsunami
# •Flood
# •Tornado
# •Hurricane wind
# •Surge/wave
# •17 earthquake hazards
# •3 tornado hazards
# •12 tsunami hazards with diff intensities
# •2 hurricane wave/surge hazards

###################################
# define public space dataset id
###################################
public_list = []

###################################
# define initial number variables
###################################
dataset_num = 0
earthquake_num = 0
tsunami_num = 0
flood_num = 0
tornado_num = 0
hurricane_num = 0
surge_num = 0

fragility_num = 0

#########################
# connect to database
#########################

############################
# iterate by public spaces
############################


#####################################################
# get the id lists that are recorded in the dataset
#####################################################


#######################################################
# check if it is dataset or hazard or frigility
#######################################################