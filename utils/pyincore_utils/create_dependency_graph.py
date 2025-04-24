import json
from collections import defaultdict

from pyincore import IncoreClient
from pyincore.analyses.bridgedamage import BridgeDamage
from pyincore.analyses.buildingclusterrecovery import BuildingClusterRecovery
from pyincore.analyses.buildingeconloss import BuildingEconLoss
from pyincore.analyses.buildingfunctionality import BuildingFunctionality
from pyincore.analyses.buildingnonstructuraldamage import BuildingNonStructDamage
from pyincore.analyses.buildingstructuraldamage import BuildingStructuralDamage
from pyincore.analyses.buyoutdecision import BuyoutDecision
from pyincore.analyses.capitalshocks import CapitalShocks
from pyincore.analyses.combinedwindwavesurgebuildingdamage import (
    CombinedWindWaveSurgeBuildingDamage,
)
from pyincore.analyses.combinedwindwavesurgebuildingloss import (
    CombinedWindWaveSurgeBuildingLoss,
)
from pyincore.analyses.commercialbuildingrecovery import CommercialBuildingRecovery
from pyincore.analyses.cumulativebuildingdamage import CumulativeBuildingDamage
from pyincore.analyses.epfdamage import EpfDamage
from pyincore.analyses.epfrepaircost import EpfRepairCost
from pyincore.analyses.epfrestoration import EpfRestoration
from pyincore.analyses.epnfunctionality import EpnFunctionality
from pyincore.analyses.galvestoncge import GalvestonCGEModel
from pyincore.analyses.gasfacilitydamage import GasFacilityDamage
from pyincore.analyses.housingrecoverysequential import HousingRecoverySequential
from pyincore.analyses.housingunitallocation import HousingUnitAllocation
from pyincore.analyses.housingvaluationrecovery import HousingValuationRecovery
from pyincore.analyses.indp import INDP
from pyincore.analyses.joplincge import JoplinCGEModel
from pyincore.analyses.joplinempiricalbuildingrestoration import (
    JoplinEmpiricalBuildingRestoration,
)
from pyincore.analyses.meandamage import MeanDamage
from pyincore.analyses.mlenabledcgeslc import MlEnabledCgeSlc
from pyincore.analyses.mlenabledcgejoplin import MlEnabledCgeJoplin
from pyincore.analyses.montecarlolimitstateprobability import (
    MonteCarloLimitStateProbability,
)
from pyincore.analyses.multiobjectiveretrofitoptimization import (
    MultiObjectiveRetrofitOptimization,
)
from pyincore.analyses.ncifunctionality import NciFunctionality
from pyincore.analyses.pipelinedamage import PipelineDamage
from pyincore.analyses.pipelinedamagerepairrate import PipelineDamageRepairRate
from pyincore.analyses.pipelinefunctionality import PipelineFunctionality
from pyincore.analyses.pipelinerepaircost import PipelineRepairCost
from pyincore.analyses.pipelinerestoration import PipelineRestoration
from pyincore.analyses.populationdislocation import PopulationDislocation
from pyincore.analyses.residentialbuildingrecovery import ResidentialBuildingRecovery
from pyincore.analyses.roaddamage import RoadDamage
from pyincore.analyses.saltlakecge import SaltLakeCGEModel
from pyincore.analyses.seasidecge import SeasideCGEModel
from pyincore.analyses.socialvulnerabilityscore import SocialVulnerabilityScore
from pyincore.analyses.tornadoepndamage import TornadoEpnDamage
from pyincore.analyses.trafficflowrecovery import TrafficFlowRecovery
from pyincore.analyses.waterfacilitydamage import WaterFacilityDamage
from pyincore.analyses.waterfacilityrepaircost import WaterFacilityRepairCost
from pyincore.analyses.waterfacilitydamage import WaterFacilityDamage
from pyincore.analyses.waterfacilityrestoration import WaterFacilityRestoration
from pyincore.analyses.wfnfunctionality import WfnFunctionality

client = IncoreClient()

# Create a dictionary of all the classes
analysis_classes = {
    "studio-BridgeDamage": BridgeDamage(client),
    "studio-BuildingClusterRecovery": BuildingClusterRecovery(client),
    "studio-BuildingEconLoss": BuildingEconLoss(client),
    "studio-BuildingFunctionality": BuildingFunctionality(client),
    "studio-BuildingNonStructDamage": BuildingNonStructDamage(client),
    "studio-BuildingStructuralDamage": BuildingStructuralDamage(client),
    "studio-BuyoutDecision": BuyoutDecision(client),
    "studio-CapitalShocks": CapitalShocks(client),
    "studio-CombinedWindWaveSurgeBuildingDamage": CombinedWindWaveSurgeBuildingDamage(
        client
    ),
    "studio-CombinedWindWaveSurgeBuildingLoss": CombinedWindWaveSurgeBuildingLoss(
        client
    ),
    "studio-CommercialBuildingRecovery": CommercialBuildingRecovery(client),
    "studio-CumulativeBuildingDamage": CumulativeBuildingDamage(client),
    "studio-EpfDamage": EpfDamage(client),
    "studio-EpfRepairCost": EpfRepairCost(client),
    "studio-EpfRestoration": EpfRestoration(client),
    "studio-EpnFunctionality": EpnFunctionality(client),
    "studio-GalvestonCGEModel": GalvestonCGEModel(client),
    "studio-GasFacilityDamage": GasFacilityDamage(client),
    "studio-HousingRecoverySequential": HousingRecoverySequential(client),
    "studio-HousingUnitAllocation": HousingUnitAllocation(client),
    "studio-HousingValuationRecovery": HousingValuationRecovery(client),
    "studio-INDP": INDP(client),
    "studio-JoplinCGEModel": JoplinCGEModel(client),
    "studio-JoplinEmpiricalBuildingRestoration": JoplinEmpiricalBuildingRestoration(
        client
    ),
    "studio-MeanDamage": MeanDamage(client),
    "studio-MlEnabledCgeSlc": MlEnabledCgeSlc(client),
    "studio-MlEnabledCgeJoplin": MlEnabledCgeJoplin(client),
    "studio-MonteCarloLimitStateProbability": MonteCarloLimitStateProbability(client),
    "studio-MultiObjectiveRetrofitOptimization": MultiObjectiveRetrofitOptimization(
        client
    ),
    "studio-NciFunctionality": NciFunctionality(client),
    "studio-PipelineDamage": PipelineDamage(client),
    "studio-PipelineDamageRepairRate": PipelineDamageRepairRate(client),
    "studio-PipelineFunctionality": PipelineFunctionality(client),
    "studio-PipelineRepairCost": PipelineRepairCost(client),
    "studio-PipelineRestoration": PipelineRestoration(client),
    "studio-PopulationDislocation": PopulationDislocation(client),
    "studio-ResidentialBuildingRecovery": ResidentialBuildingRecovery(client),
    "studio-RoadDamage": RoadDamage(client),
    "studio-SaltLakeCGEModel": SaltLakeCGEModel(client),
    "studio-SeasideCGEModel": SeasideCGEModel(client),
    "studio-SocialVulnerabilityScore": SocialVulnerabilityScore(client),
    "studio-TornadoEpnDamage": TornadoEpnDamage(client),
    "studio-TrafficFlowRecovery": TrafficFlowRecovery(client),
    "studio-WaterFacilityDamage": WaterFacilityDamage(client),
    "studio-WaterFacilityRepairCost": WaterFacilityRepairCost(client),
    "studio-WaterFacilityRestoration": WaterFacilityRestoration(client),
    "studio-WfnFunctionality": WfnFunctionality(client),
}

# create a dictionary of pretty names
pretty_tagged_names = {
    "studio-BridgeDamage": {
        "name": "Bridge Damage",
        "tags": ["Bridge"],
        "manual": "bridge_dmg.html",
        "parameter_defaults": {
            "result_name": "bridge-damage-result",
            "fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_geology_dataset_id": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 4,
            "hazard_id": None,
            "hazard_type": None,
        },
    },
    "studio-BuildingClusterRecovery": {
        "name": "Building Cluster Recovery",
        "tags": ["Building"],
        "manual": "building_cluster_recovery.html",
        "parameter_defaults": {
            "result_name": "building-recovery-result",
            "uncertainty": True,
            "sample_size": 35,
            "random_sample_size": 50,
            "no_of_weeks": 100,
            "num_cpu": 4,
        },
    },
    "studio-BuildingEconLoss": {
        "name": "Building Economic Loss",
        "tags": ["Building"],
        "manual": "building_loss.html",
        "parameter_defaults": {
            "result_name": "building-econ-loss-result",
            "inflation_factor": 0.0,
        },
    },
    "studio-BuildingFunctionality": {
        "name": "Building Functionality",
        "tags": ["Building"],
        "manual": "building_func.html",
        "parameter_defaults": {"result_name": "bldg-functionality-result"},
    },
    "studio-BuildingNonStructDamage": {
        "name": "Building Non-Structural Damage",
        "tags": ["Building"],
        "manual": "building_nonstructural_dmg.html",
        "parameter_defaults": {
            "result_name": "building-nonstruct-dmg-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": "Acceleration-Sensitive Fragility ID Code",
            "use_liquefaction": True,
            "liq_geology_dataset_id": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
        },
    },
    "studio-BuildingStructuralDamage": {
        "name": "Building Structural Damage",
        "tags": ["Building"],
        "manual": "building_structural_dmg.html",
        "parameter_defaults": {
            "result_name": "building-struct-dmg-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "use_liquefaction": False,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
            "seed": 1234,
            "liquefaction_geology_dataset_id": None,
        },
    },
    "studio-BuyoutDecision": {
        "name": "Buyout Decision",
        "tags": ["Decision Support"],
        "manual": "buyout_decision.html",
        "parameter_defaults": {
            "fema_buyout_cap": 250000.0,
            "residential_archetypes": None,
            "result_name": "buyout-decision-result",
        },
    },
    "studio-CapitalShocks": {
        "name": "Capital Shocks",
        "tags": ["Economic"],
        "manual": "capital_shocks.html",
        "parameter_defaults": {"result_name": "capital-shocks-result"},
    },
    "studio-CombinedWindWaveSurgeBuildingDamage": {
        "name": "Combined Wind Wave Surge Building Damage",
        "tags": ["Building"],
        "manual": "combined_wind_wave_surge_building_dmg.html",
        "parameter_defaults": {
            "result_name": "combined-wind-wave-surge-building-damage-result"
        },
    },
    "studio-CombinedWindWaveSurgeBuildingLoss": {
        "name": "Combined Wind Wave Surge Building Loss",
        "tags": ["Building"],
        "manual": "combined_wind_wave_surge_building_loss.html",
        "parameter_defaults": {
            "result_name": "combined-wind-wave-surge-building-loss-result"
        },
    },
    "studio-CommercialBuildingRecovery": {
        "name": "Commercial Building Recovery",
        "tags": ["Socioeconomic"],
        "manual": "commercial_building_recovery.html",
        "parameter_defaults": {
            "result_name": "commercial-building-recovery-result",
            "num_samples": 10,
            "repair_key": None,
            "seed": 1234,
        },
    },
    "studio-CumulativeBuildingDamage": {
        "name": "Cumulative Building Damage",
        "tags": ["Building"],
        "manual": "cumulative_building_dmg.html",
        "parameter_defaults": {
            "result_name": "cumulative-building-damage-result",
            "num_cpu": 4,
        },
    },
    "studio-EpfDamage": {
        "name": "Electric Power Facility Damage",
        "tags": ["Lifeline"],
        "manual": "epf_dmg.html",
        "parameter_defaults": {
            "result_name": "epf-damage-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "liquefaction_fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_geology_dataset_id": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
        },
    },
    "studio-EpfRepairCost": {
        "name": "Electric Power Facility Repair Cost",
        "tags": ["Lifeline"],
        "manual": "epf_repair_cost.html",
        "parameter_defaults": {"result_name": "epf-repair-cost-result", "num_cpu": 1},
    },
    "studio-EpfRestoration": {
        "name": "Electric Power Facility Restoration",
        "tags": ["LifeLine"],
        "manual": "epf_restoration.html",
        "parameter_defaults": {
            "result_name": "epf-restoration-result",
            "restoration_key": None,
            "end_time": 365.0,
            "time_interval": 1.0,
            "pf_interval": 0.1,
            "discretized_days": "[1, 3, 7, 30, 90]",
        },
    },
    "studio-EpnFunctionality": {
        "name": "Electric Power Network Functionality",
        "tags": ["Lifeline"],
        "manual": "epn_functionality.html",
        "parameter_defaults": {
            "result_name": "epn-functionality-result",
            "gate_station_node_list": None,
        },
    },
    "studio-GalvestonCGEModel": {
        "name": "Galveston CGE Model",
        "tags": ["Economic"],
        "manual": "galveston_cge.html",
        "parameter_defaults": {"model_iterations": 1, "solver_path": None},
    },
    "studio-GasFacilityDamage": {
        "name": "Gas Facility Damage",
        "tags": ["Lifeline"],
        "manual": "gas_facility_damage.html",
        "parameter_defaults": {
            "result_name": "gas-facility-damage-result",
            "fragility_key": None,
            "liquefaction_fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_geology_dataset_id": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
            "hazard_id": None,
            "hazard_type": None,
        },
    },
    "studio-HousingRecoverySequential": {
        "name": "Housing Recovery Sequential",
        "tags": ["Socioeconomic", "Decision Support"],
        "manual": "housing_household_recovery.html",
        "parameter_defaults": {
            "result_name": "housing-recovery-sequential-result",
            "t_delta": None,
            "t_final": None,
            "seed": 1234,
            "num_cpu": 4,
        },
    },
    "studio-HousingUnitAllocation": {
        "name": "Housing Unit Allocation",
        "tags": ["Socioeconomic"],
        "manual": "housingunitallocation.html",
        "parameter_defaults": {
            "result_name": "housing-unit-allocation-result",
            "seed": 1234,
            "iterations": 10,
        },
    },
    "studio-HousingValuationRecovery": {
        "name": "Housing Valuation Recovery",
        "tags": ["Socioeconomic"],
        "manual": "housing_recovery.html",
        "parameter_defaults": {
            "base_year": 2008,
            "result_name": "housing-valuation-recovery-result",
        },
    },
    "studio-INDP": {
        "name": "Infrastructure Network Disruption Planning",
        "tags": ["Decision Support"],
        "manual": "indp.html",
        "parameter_defaults": {
            "network_type": "from_csv",
            "MAGS": "[1000]",
            "sample_range": "[0]",
            "dislocation_data_type": "incore",
            "return_model": "step_function",
            "testbed_name": None,
            "extra_commodity": None,
            "RC": None,
            "layers": None,
            "method": "INDP",
            "t_steps": 10,
            "time_resource": True,
            "save_model": False,
            "solver_engine": None,
            "solver_path": None,
            "solver_time_limit": None,
        },
    },
    "studio-JoplinCGEModel": {
        "name": "Joplin CGE Model",
        "tags": ["Economic"],
        "manual": "joplin_cge.html",
        "parameter_defaults": {"model_iterations": 1, "solver_path": None},
    },
    "studio-JoplinEmpiricalBuildingRestoration": {
        "name": "Joplin Empirical Building Restoration",
        "tags": ["Building"],
        "manual": "",
        "parameter_defaults": {
            "result_name": "joplin-empirical-building-restoration",
            "target_functionality_level": 0,
            "seed": 1234,
        },
    },
    "studio-MeanDamage": {
        "name": "Mean Damage",
        "tags": [],
        "manual": "mean_dmg.html",
        "parameter_defaults": {
            "result_name": "mean-damage-result",
            "damage_interval_keys": "['DS_0', 'DS_1', 'DS_2', 'DS_3', 'DS_4']",
            "num_cpu": 1,
        },
    },
    "studio-MlEnabledCgeSlc": {
        "name": "Machine Learning Enabled CGE SLC",
        "tags": ["Economic"],
        "manual": "ml_slc_cge.html",
        "parameter_defaults": {"result_name": "salt-lake-ml-enabled-cge"},
    },
    "studio-MlEnabledCgeJoplin": {
        "name": "Machine Learning Enabled CGE Joplin",
        "tags": ["Economic"],
        "manual": "ml_joplin_cge.html",
        "parameter_defaults": {"result_name": "joplin-ml-enabled-cge"},
    },
    "studio-MonteCarloLimitStateProbability": {
        "name": "Monte Carlo Limit State Probability",
        "tags": ["Decision Support"],
        "manual": "mc_limit_state_prob.html",
        "parameter_defaults": {
            "result_name": "monte_carlo_limit_state_probability-result",
            "num_cpu": 8,
            "num_samples": 10,
            "damage_interval_keys": "['DS_0', 'DS_1', 'DS_2', 'DS_3']",
            "failure_state_keys": "['DS_1', 'DS_2', 'DS_3']",
            "seed": 1234,
        },
    },
    "studio-MultiObjectiveRetrofitOptimization": {
        "name": "Multi-Objective Retrofit Optimization",
        "tags": ["Decision Support"],
        "manual": "multi_retrofit_optimization.html",
        "parameter_defaults": {
            "result_name": "multiobjective-retrofit-optimization-result",
            "model_solver": "ipopt",
            "num_epsilon_steps": 2,
            "max_budget": "default",
            "budget_available": None,
            "inactive_submodels": None,
            "scale_data": None,
            "scaling_factor": None,
        },
    },
    "studio-NciFunctionality": {
        "name": "Network Cascading Interdependency Functionality",
        "tags": ["Decision Support"],
        "manual": "nci_functionality.html",
        "parameter_defaults": {
            "result_name": "nci-functionality-result",
            "discretized_days": "[1, 3, 7, 30, 90]",
        },
    },
    "studio-PipelineDamage": {
        "name": "Pipeline Damage",
        "tags": ["Lifeline"],
        "manual": "pipeline_dmg.html",
        "parameter_defaults": {
            "result_name": "pipeline-damage-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "num_cpu": 1,
            "liquefaction_geology_dataset_id": None,
        },
    },
    "studio-PipelineDamageRepairRate": {
        "name": "Pipeline Damage Repair Rate",
        "tags": ["Lifeline"],
        "manual": "pipeline_dmg_w_repair_rate.html",
        "parameter_defaults": {
            "result_name": "pipeline-damage-repair-rate-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_fragility_key": None,
            "num_cpu": 1,
            "liquefaction_geology_dataset_id": None,
        },
    },
    "studio-PipelineFunctionality": {
        "name": "Pipeline Functionality",
        "tags": ["Lifeline"],
        "manual": "pipeline_functionality.html",
        "parameter_defaults": {
            "result_name": "pipeline-functionality-result",
            "num_samples": 100,
        },
    },
    "studio-PipelineRepairCost": {
        "name": "Pipeline Repair Cost",
        "tags": ["Lifeline"],
        "manual": "pipeline_repair_cost.html",
        "parameter_defaults": {
            "result_name": "pipeline-repair-cost-result",
            "num_cpu": 1,
            "diameter": 20,
            "segment_length": 20,
        },
    },
    "studio-PipelineRestoration": {
        "name": "Pipeline Restoration",
        "tags": ["Lifeline"],
        "manual": "pipeline_restoration.html",
        "parameter_defaults": {
            "result_name": "pipeline-restoration-result",
            "num_cpu": 1,
            "num_available_workers": 4,
            "restoration_key": "Restoration ID Code",
        },
    },
    "studio-PopulationDislocation": {
        "name": "Population Dislocation",
        "tags": ["Socioeconomic"],
        "manual": "populationdislocation.html",
        "parameter_defaults": {
            "result_name": "population-dislocation-result",
            "seed": 1234,
            "choice_dislocation": False,
            "choice_dislocation_cutoff": 0.0,
            "choice_dislocation_ds": None,
            "unsafe_occupancy": False,
            "unsafe_occupancy_cutoff": 0.0,
            "unsafe_occupancy_ds": None,
        },
    },
    "studio-ResidentialBuildingRecovery": {
        "name": "Residential Building Recovery",
        "tags": ["Socioeconomic", "Decision Support"],
        "manual": "residential_building_recovery.html",
        "parameter_defaults": {
            "result_name": "residential-building-recovery-result",
            "num_samples": 10,
            "repair_key": None,
            "seed": 1234,
        },
    },
    "studio-RoadDamage": {
        "name": "Road Damage",
        "tags": ["Lifeline"],
        "manual": "road_dmg.html",
        "parameter_defaults": {
            "result_name": "road-damage-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_geology_dataset_id": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
        },
    },
    "studio-SaltLakeCGEModel": {
        "name": "Salt Lake CGE Model",
        "tags": ["Economic"],
        "manual": "slc_cge.html",
        "parameter_defaults": {"model_iterations": 1, "solver_path": None},
    },
    "studio-SeasideCGEModel": {
        "name": "Seaside CGE Model",
        "tags": ["Economic"],
        "manual": "seaside_cge.html",
        "parameter_defaults": {"print_solver_output": False, "solver_path": None},
    },
    "studio-SocialVulnerabilityScore": {
        "name": "Social Vulnerability Score",
        "tags": ["Socioeconomic"],
        "manual": "social_vulnerability_score.html",
        "parameter_defaults": {"result_name": "social-vulnerability-score-result"},
    },
    "studio-TornadoEpnDamage": {
        "name": "Tornado Electric Power Network Damage",
        "tags": ["Lifeline"],
        "manual": "tornadoepn_dmg.html",
        "parameter_defaults": {
            "result_name": "tornado-epn-damage-result",
            "tornado_id": None,
            "seed": 1234,
        },
    },
    "studio-TrafficFlowRecovery": {
        "name": "Traffic Flow Recovery",
        "tags": ["Decision Support", "Lifeline"],
        "manual": "traffic_flow_recovery.html",
        "parameter_defaults": {
            "num_cpu": 1,
            "pm": 1,
            "ini_num_population": 5,
            "population_size": 3,
            "num_generation": 2,
            "mutation_rate": 0.1,
            "crossover_rate": 1.0,
        },
    },
    "studio-WaterFacilityDamage": {
        "name": "Water Facility Damage",
        "tags": ["Lifeline"],
        "manual": "waterfacility_dmg.html",
        "parameter_defaults": {
            "result_name": "water-facility-damage-result",
            "hazard_type": None,
            "hazard_id": None,
            "fragility_key": None,
            "use_liquefaction": False,
            "liquefaction_geology_dataset_id": None,
            "liquefaction_fragility_key": None,
            "use_hazard_uncertainty": False,
            "num_cpu": 1,
        },
    },
    "studio-WaterFacilityRepairCost": {
        "name": "Water Facility Repair Cost",
        "tags": ["Lifeline"],
        "manual": "water_facility_repair_cost.html",
        "parameter_defaults": {
            "result_name": "water-facility-repair-cost-result",
            "num_cpu": 1,
        },
    },
    "studio-WaterFacilityRestoration": {
        "name": "Water Facility Restoration",
        "tags": ["Lifeline"],
        "manual": "water_facility_restoration.html",
        "parameter_defaults": {
            "result_name": "water-facility-restoration-result",
            "restoration_key": "Restoration ID Code",
            "end_time": 100.0,
            "time_interval": 1.0,
            "pf_interval": 0.05,
            "discretized_days": "[1, 3, 7, 30, 90]",
        },
    },
    "studio-WfnFunctionality": {
        "name": "Water Facility Network Functionality",
        "tags": ["Lifeline"],
        "manual": "wfn_functionality.html",
        "parameter_defaults": {
            "result_name": "wfn-functionality-result",
            "tank_node_list": "[]",
            "pumpstation_node_list": "[]",
        },
    },
}

tool_afters = {
    "studio-BuildingStructuralDamage": {
        "studio-MaxDamageStateTool": [{"from": "ds_result", "to": "Output dataset"}]
    },
    "studio-EpfDamage": {
        "studio-MaxDamageStateTool": [{"from": "ds_result", "to": "Output dataset"}]
    },
    "studio-BridgeDamage": {
        "studio-MaxDamageStateTool": [{"from": "ds_result", "to": "Output dataset"}]
    },
    "studio-SaltLakeCGEModel": {
        "studio-CGEPostProcessTool": [
            {"from": "household-count", "to": "Household Count"},
            {"from": "domestic-supply", "to": "Domestic supply"},
            {"from": "gross-income", "to": "Gross Income"},
            {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
            {"from": "post-disaster-factor-demand", "to": "Post Demand"},
        ]
    },
    "studio-JoplinCGEModel": {
        "studio-CGEPostProcessTool": [
            {"from": "household-count", "to": "Household Count"},
            {"from": "domestic-supply", "to": "Domestic supply"},
            {"from": "gross-income", "to": "Gross Income"},
            {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
            {"from": "post-disaster-factor-demand", "to": "Post Demand"},
        ]
    },
    "studio-GalvestonCGEModel": {
        "studio-CGEPostProcessTool": [
            {"from": "household-count", "to": "Household Count"},
            {"from": "domestic-supply", "to": "Domestic supply"},
            {"from": "gross-income", "to": "Gross Income"},
            {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
            {"from": "post-disaster-factor-demand", "to": "Post Demand"},
        ]
    },
    "studio-MlEnabledCgeJoplin": {
        "studio-CGEPostProcessTool": [
            {"from": "household-count", "to": "Household Count"},
            {"from": "domestic-supply", "to": "Domestic supply"},
            {"from": "gross-income", "to": "Gross Income"},
            {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
            {"from": "post-disaster-factor-demand", "to": "Post Demand"},
        ]
    },
    "studio-MlEnabledCgeSlc": {
        "studio-CGEPostProcessTool": [
            {"from": "household-count", "to": "Household Count"},
            {"from": "domestic-supply", "to": "Domestic supply"},
            {"from": "gross-income", "to": "Gross Income"},
            {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
            {"from": "post-disaster-factor-demand", "to": "Post Demand"},
        ]
    },
    "studio-PopulationDislocation": {
        "studio-DislPostProcessTool": [{"from": "result", "to": "Dislocation Output"}]
    },
    "studio-MonteCarloLimitStateProbability": {
        "studio-BuildingFailureClusterTool": [
            {"from": "failure_probability", "to": "Building Failure Probability"}
        ]
    },
    "studio-BuildingFunctionality": {
        "studio-BuildingFunctionalityClusterTool": [
            {"from": "functionality_probability", "to": "Functionality Probability"}
        ]
    },
}

tools = {
    "studio-MaxDamageStateTool": {
        "before": {
            "studio-BuildingStructuralDamage": [
                {"from": "ds_result", "to": "Output dataset"}
            ],
            "studio-EpfDamage": [{"from": "ds_result", "to": "Output dataset"}],
            "studio-BridgeDamage": [{"from": "ds_result", "to": "Output dataset"}],
        },
        "after": {
            "studio-BuildingDamageSummaryTool": [
                {"from": "Max Damage", "to": "Max Damage State"}
            ]
        },
        "pretty_name": "Max Damage State Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {"Output dataset": ["ergo:buildingDamageVer6"]},
        "parameter_defaults": {},
    },
    "studio-BuildingDamageSummaryTool": {
        "before": {
            "studio-MaxDamageStateTool": [
                {"from": "Max Damage", "to": "Max Damage State"}
            ]
        },
        "after": {},
        "pretty_name": "Building Damage Summary Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {
            "Max Damage State": ["Max damage State type"],
            "Buildings": [
                "ergo:buildingInventoryVer4",
                "ergo:buildingInventoryVer5",
                "ergo:buildingInventoryVer6",
                "ergo:buildingInventoryVer7",
            ],
            "Archetype Mapping": ["ncsa:archetype-mapping"],
        },
        "parameter_defaults": {},
    },
    "studio-CGEPostProcessTool": {
        "before": {
            "studio-SaltLakeCGEModel": [
                {"from": "household-count", "to": "Household Count"},
                {"from": "domestic-supply", "to": "Domestic supply"},
                {"from": "gross-income", "to": "Gross Income"},
                {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
                {"from": "post-disaster-factor-demand", "to": "Post Demand"},
            ],
            "studio-JoplinCGEModel": [
                {"from": "household-count", "to": "Household Count"},
                {"from": "domestic-supply", "to": "Domestic supply"},
                {"from": "gross-income", "to": "Gross Income"},
                {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
                {"from": "post-disaster-factor-demand", "to": "Post Demand"},
            ],
            "studio-GalvestonCGEModel": [
                {"from": "household-count", "to": "Household Count"},
                {"from": "domestic-supply", "to": "Domestic supply"},
                {"from": "gross-income", "to": "Gross Income"},
                {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
                {"from": "post-disaster-factor-demand", "to": "Post Demand"},
            ],
            "studio-MlEnabledCgeJoplin": [
                {"from": "household-count", "to": "Household Count"},
                {"from": "domestic-supply", "to": "Domestic supply"},
                {"from": "gross-income", "to": "Gross Income"},
                {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
                {"from": "post-disaster-factor-demand", "to": "Post Demand"},
            ],
            "studio-MlEnabledCgeSlc": [
                {"from": "household-count", "to": "Household Count"},
                {"from": "domestic-supply", "to": "Domestic supply"},
                {"from": "gross-income", "to": "Gross Income"},
                {"from": "pre-disaster-factor-demand", "to": "Pre Demand"},
                {"from": "post-disaster-factor-demand", "to": "Post Demand"},
            ],
        },
        "after": {},
        "pretty_name": "CGE Post Process Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {
            "Household Count": ["incore:HouseholdCount"],
            "Domestic supply": ["incore:Employment"],
            "Gross Income": ["incore:Employment"],
            "Pre Demand": ["incore:FactorDemand"],
            "Post Demand": ["incore:FactorDemand"],
        },
        "parameter_defaults": {},
    },
    "studio-DislPostProcessTool": {
        "before": {
            "studio-PopulationDislocation": [
                {"from": "result", "to": "Dislocation Output"}
            ]
        },
        "after": {},
        "pretty_name": "Population Dislocation Post Process Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {"Dislocation Output": ["incore:popDislocation"]},
        "parameter_defaults": {},
    },
    "studio-BuildingFailureClusterTool": {
        "before": {
            "studio-MonteCarloLimitStateProbability": [
                {"from": "failure_probability", "to": "Building Failure Probability"}
            ]
        },
        "after": {},
        "pretty_name": "Building Failure Cluster Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {
            "Building Failure Probability": ["incore:failureProbability"],
            "Buildings": [
                "ergo:buildingInventoryVer4",
                "ergo:buildingInventoryVer5",
                "ergo:buildingInventoryVer6",
                "ergo:buildingInventoryVer7",
            ],
            "Archetype Mapping": ["ncsa:archetype-mapping"],
        },
        "parameter_defaults": {},
    },
    "studio-BuildingFunctionalityClusterTool": {
        "before": {
            "studio-BuildingFunctionality": [
                {"from": "functionality_probability", "to": "Functionality Probability"}
            ]
        },
        "after": {},
        "pretty_name": "Building Functionality Cluster Tool",
        "tags": ["Pyincore Utility"],
        "manual": None,
        "inputs": {
            "Functionality Probability": ["incore:funcProbability"],
            "Buildings": [
                "ergo:buildingInventoryVer4",
                "ergo:buildingInventoryVer5",
                "ergo:buildingInventoryVer6",
                "ergo:buildingInventoryVer7",
            ],
            "Archetype Mapping": ["ncsa:archetype-mapping"],
        },
        "parameter_defaults": {},
    },
}

input_types_for_analysis = defaultdict(list)
output_types_for_analysis = defaultdict(list)
seen_types = set()

for analysis_name, analysis_class in analysis_classes.items():
    spec = analysis_class.get_spec()

    for input in spec["input_datasets"]:
        if type(input["type"]) == list:
            for t in input["type"]:
                input_types_for_analysis[t].append((analysis_name, input["id"]))
                seen_types.add(t)
        else:
            input_types_for_analysis[input["type"]].append((analysis_name, input["id"]))
            seen_types.add(input["type"])
    for output in spec["output_datasets"]:
        if type(output["type"]) == list:
            for t in output["type"]:
                output_types_for_analysis[t].append((analysis_name, output["id"]))
                seen_types.add(t)
        else:
            output_types_for_analysis[output["type"]].append(
                (analysis_name, output["id"])
            )
            seen_types.add(output["type"])

dependency_graph = defaultdict(dict)

for type in list(seen_types):
    # add befores
    for analysis_name, propertyA in input_types_for_analysis[type]:
        for other_type, propertyB in output_types_for_analysis[type]:
            if dependency_graph[analysis_name].get("before", None) is None:
                dependency_graph[analysis_name]["before"] = set(
                    {(other_type, propertyB, propertyA)}
                )
            else:
                dependency_graph[analysis_name]["before"].add(
                    (other_type, propertyB, propertyA)
                )
    # add afters
    for analysis_name, propertyA in output_types_for_analysis[type]:
        for other_type, propertyB in input_types_for_analysis[type]:
            if dependency_graph[analysis_name].get("after", None) is None:
                dependency_graph[analysis_name]["after"] = set(
                    {(other_type, propertyA, propertyB)}
                )
            else:
                dependency_graph[analysis_name]["after"].add(
                    (other_type, propertyA, propertyB)
                )

# Convert sets to lists
for value in dependency_graph.values():
    for k, v in value.items():
        if k == "before":
            value[k] = defaultdict(list)
            for analysis, propA, propB in list(v):
                value[k][analysis].append({"from": propA, "to": propB})

            # value[k] = dict(
            #     [
            #         (analysis, {"from": propB, "to": propA})
            #         for analysis, propA, propB in list(v)
            #     ]
            # )
        else:
            value[k] = defaultdict(list)
            for analysis, propA, propB in list(v):
                value[k][analysis].append({"from": propA, "to": propB})

            # value[k] = dict(
            #     [
            #         (analysis, {"from": propA, "to": propB})
            #         for analysis, propA, propB in list(v)
            #     ]
            # )

    if value.get("before", None) is None:
        value["before"] = {}
    if value.get("after", None) is None:
        value["after"] = {}

if len(analysis_classes) != len(dependency_graph):
    print("Some analyses are missing from the dependency graph\nAdding them now:")
    for analysis_name in analysis_classes.keys():
        if analysis_name not in dependency_graph:
            print(analysis_name)
            dependency_graph[analysis_name] = {"before": {}, "after": {}}

# Add pretty names
for analysis_name, value in dependency_graph.items():
    value["pretty_name"] = pretty_tagged_names[analysis_name]["name"]
    value["tags"] = pretty_tagged_names[analysis_name]["tags"]
    value["manual"] = pretty_tagged_names[analysis_name]["manual"]
    value["parameter_defaults"] = pretty_tagged_names[analysis_name][
        "parameter_defaults"
    ]

# add input dataset types in dependency graph
for analysis_name, analysis_class in analysis_classes.items():
    spec = analysis_class.get_spec()
    dependency_graph[analysis_name]["inputs"] = dict()
    hazards = spec.get("input_hazards", [])
    datasets = spec.get("input_datasets", [])
    parameters = spec.get("input_parameters", [])
    for hazard in hazards:
        dependency_graph[analysis_name]["inputs"][hazard["id"]] = (
            hazard["type"] if isinstance(hazard["type"], list) else [hazard["type"]]
        )
    for dataset in datasets:
        dependency_graph[analysis_name]["inputs"][dataset["id"]] = (
            dataset["type"] if isinstance(dataset["type"], list) else [dataset["type"]]
        )

# add tools to dependency graph
for key, value in tools.items():
    dependency_graph[key] = value

# add links to tools from analyses
for key, value in tool_afters.items():
    for k, v in value.items():
        dependency_graph[key]["after"][k] = v

json.dump(dependency_graph, open("test_dependencyGraph.json", "w"), indent=4)
