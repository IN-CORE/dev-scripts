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
    },
    "studio-BuildingClusterRecovery": {
        "name": "Building Cluster Recovery",
        "tags": ["Building"],
        "manual": "building_cluster_recovery.html",
    },
    "studio-BuildingEconLoss": {
        "name": "Building Economic Loss",
        "tags": ["Building"],
        "manual": "building_loss.html",
    },
    "studio-BuildingFunctionality": {
        "name": "Building Functionality",
        "tags": ["Building"],
        "manual": "building_func.html",
    },
    "studio-BuildingNonStructDamage": {
        "name": "Building Non-Structural Damage",
        "tags": ["Building"],
        "manual": "building_nonstructural_dmg.html",
    },
    "studio-BuildingStructuralDamage": {
        "name": "Building Structural Damage",
        "tags": ["Building"],
        "manual": "building_structural_dmg.html",
    },
    "studio-BuyoutDecision": {
        "name": "Buyout Decision",
        "tags": ["Decision Support"],
        "manual": "buyout_decision.html",
    },
    "studio-CapitalShocks": {
        "name": "Capital Shocks",
        "tags": ["Economic"],
        "manual": "capital_shocks.html",
    },
    "studio-CombinedWindWaveSurgeBuildingDamage": {
        "name": "Combined Wind Wave Surge Building Damage",
        "tags": ["Building"],
        "manual": "combined_wind_wave_surge_building_dmg.html",
    },
    "studio-CombinedWindWaveSurgeBuildingLoss": {
        "name": "Combined Wind Wave Surge Building Loss",
        "tags": ["Building"],
        "manual": "combined_wind_wave_surge_building_loss.html",
    },
    "studio-CommercialBuildingRecovery": {
        "name": "Commercial Building Recovery",
        "tags": ["Socioeconomic"],
        "manual": "commercial_building_recovery.html",
    },
    "studio-CumulativeBuildingDamage": {
        "name": "Cumulative Building Damage",
        "tags": ["Building"],
        "manual": "cumulative_building_dmg.html",
    },
    "studio-EpfDamage": {
        "name": "Electric Power Facility Damage",
        "tags": ["Lifeline"],
        "manual": "epf_dmg.html",
    },
    "studio-EpfRepairCost": {
        "name": "Electric Power Facility Repair Cost",
        "tags": ["Lifeline"],
        "manual": "epf_repair_cost.html",
    },
    "studio-EpfRestoration": {
        "name": "Electric Power Facility Restoration",
        "tags": ["LifeLine"],
        "manual": "epf_restoration.html",
    },
    "studio-EpnFunctionality": {
        "name": "Electric Power Network Functionality",
        "tags": ["Lifeline"],
        "manual": "epn_functionality.html",
    },
    "studio-GalvestonCGEModel": {
        "name": "Galveston CGE Model",
        "tags": ["Economic"],
        "manual": "galveston_cge.html",
    },
    "studio-GasFacilityDamage": {
        "name": "Gas Facility Damage",
        "tags": ["Lifeline"],
        "manual": "gas_facility_damage.html",
    },
    "studio-HousingRecoverySequential": {
        "name": "Housing Recovery Sequential",
        "tags": ["Socioeconomic", "Decision Support"],
        "manual": "housing_household_recovery.html",
    },
    "studio-HousingUnitAllocation": {
        "name": "Housing Unit Allocation",
        "tags": ["Socioeconomic"],
        "manual": "housingunitallocation.html",
    },
    "studio-HousingValuationRecovery": {
        "name": "Housing Valuation Recovery",
        "tags": ["Socioeconomic"],
        "manual": "housing_recovery.html",
    },
    "studio-INDP": {
        "name": "Infrastructure Network Disruption Planning",
        "tags": ["Decision Support"],
        "manual": "indp.html",
    },
    "studio-JoplinCGEModel": {
        "name": "Joplin CGE Model",
        "tags": ["Economic"],
        "manual": "joplin_cge.html",
    },
    "studio-JoplinEmpiricalBuildingRestoration": {
        "name": "Joplin Empirical Building Restoration",
        "tags": ["Building"],
        "manual": "",
    },
    "studio-MeanDamage": {"name": "Mean Damage", "tags": [], "manual": "mean_dmg.html"},
    "studio-MlEnabledCgeSlc": {
        "name": "Machine Learning Enabled CGE SLC",
        "tags": ["Economic"],
        "manual": "ml_slc_cge.html",
    },
    "studio-MlEnabledCgeJoplin": {
        "name": "Machine Learning Enabled CGE Joplin",
        "tags": ["Economic"],
        "manual": "ml_joplin_cge.html",
    },
    "studio-MonteCarloLimitStateProbability": {
        "name": "Monte Carlo Limit State Probability",
        "tags": ["Decision Support"],
        "manual": "mc_limit_state_prob.html",
    },
    "studio-MultiObjectiveRetrofitOptimization": {
        "name": "Multi-Objective Retrofit Optimization",
        "tags": ["Decision Support"],
        "manual": "multi_retrofit_optimization.html",
    },
    "studio-NciFunctionality": {
        "name": "Network Cascading Interdependency Functionality",
        "tags": ["Decision Support"],
        "manual": "nci_functionality.html",
    },
    "studio-PipelineDamage": {
        "name": "Pipeline Damage",
        "tags": ["Lifeline"],
        "manual": "pipeline_dmg.html",
    },
    "studio-PipelineDamageRepairRate": {
        "name": "Pipeline Damage Repair Rate",
        "tags": ["Lifeline"],
        "manual": "pipeline_dmg_w_repair_rate.html",
    },
    "studio-PipelineFunctionality": {
        "name": "Pipeline Functionality",
        "tags": ["Lifeline"],
        "manual": "pipeline_functionality.html",
    },
    "studio-PipelineRepairCost": {
        "name": "Pipeline Repair Cost",
        "tags": ["Lifeline"],
        "manual": "pipeline_repair_cost.html",
    },
    "studio-PipelineRestoration": {
        "name": "Pipeline Restoration",
        "tags": ["Lifeline"],
        "manual": "pipeline_restoration.html",
    },
    "studio-PopulationDislocation": {
        "name": "Population Dislocation",
        "tags": ["Socioeconomic"],
        "manual": "populationdislocation.html",
    },
    "studio-ResidentialBuildingRecovery": {
        "name": "Residential Building Recovery",
        "tags": ["Socioeconomic", "Decision Support"],
        "manual": "residential_building_recovery.html",
    },
    "studio-RoadDamage": {
        "name": "Road Damage",
        "tags": ["Lifeline"],
        "manual": "road_dmg.html",
    },
    "studio-SaltLakeCGEModel": {
        "name": "Salt Lake CGE Model",
        "tags": ["Economic"],
        "manual": "slc_cge.html",
    },
    "studio-SeasideCGEModel": {
        "name": "Seaside CGE Model",
        "tags": ["Economic"],
        "manual": "seaside_cge.html",
    },
    "studio-SocialVulnerabilityScore": {
        "name": "Social Vulnerability Score",
        "tags": ["Socioeconomic"],
        "manual": "social_vulnerability_score.html",
    },
    "studio-TornadoEpnDamage": {
        "name": "Tornado Electric Power Network Damage",
        "tags": ["Lifeline"],
        "manual": "tornadoepn_dmg.html",
    },
    "studio-TrafficFlowRecovery": {
        "name": "Traffic Flow Recovery",
        "tags": ["Decision Support", "Lifeline"],
        "manual": "traffic_flow_recovery.html",
    },
    "studio-WaterFacilityDamage": {
        "name": "Water Facility Damage",
        "tags": ["Lifeline"],
        "manual": "waterfacility_dmg.html",
    },
    "studio-WaterFacilityRepairCost": {
        "name": "Water Facility Repair Cost",
        "tags": ["Lifeline"],
        "manual": "water_facility_repair_cost.html",
    },
    "studio-WaterFacilityRestoration": {
        "name": "Water Facility Restoration",
        "tags": ["Lifeline"],
        "manual": "water_facility_restoration.html",
    },
    "studio-WfnFunctionality": {
        "name": "Water Facility Network Functionality",
        "tags": ["Lifeline"],
        "manual": "wfn_functionality.html",
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
            "Archetype Mapping": ["Archetype Mapping type"],
        },
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
            "Archetype Mapping": ["Archetype Mapping type"],
        },
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
            "Archetype Mapping": ["Archetype Mapping type"],
        },
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

# add input dataset types in dependency graph
for analysis_name, analysis_class in analysis_classes.items():
    spec = analysis_class.get_spec()
    dependency_graph[analysis_name]["inputs"] = dict()
    hazards = spec.get("input_hazards", [])
    datasets = spec.get("input_datasets", [])
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
