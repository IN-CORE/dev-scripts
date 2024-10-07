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
    "BridgeDamage": BridgeDamage(client),
    "BuildingClusterRecovery": BuildingClusterRecovery(client),
    "BuildingEconLoss": BuildingEconLoss(client),
    "BuildingFunctionality": BuildingFunctionality(client),
    "BuildingNonStructDamage": BuildingNonStructDamage(client),
    "BuildingStructuralDamage": BuildingStructuralDamage(client),
    "BuyoutDecision": BuyoutDecision(client),
    "CapitalShocks": CapitalShocks(client),
    "CombinedWindWaveSurgeBuildingDamage": CombinedWindWaveSurgeBuildingDamage(client),
    "CombinedWindWaveSurgeBuildingLoss": CombinedWindWaveSurgeBuildingLoss(client),
    "CommercialBuildingRecovery": CommercialBuildingRecovery(client),
    "CumulativeBuildingDamage": CumulativeBuildingDamage(client),
    "EpfDamage": EpfDamage(client),
    "EpfRepairCost": EpfRepairCost(client),
    "EpfRestoration": EpfRestoration(client),
    "EpnFunctionality": EpnFunctionality(client),
    "GalvestonCGEModel": GalvestonCGEModel(client),
    "GasFacilityDamage": GasFacilityDamage(client),
    "HousingRecoverySequential": HousingRecoverySequential(client),
    "HousingUnitAllocation": HousingUnitAllocation(client),
    "HousingValuationRecovery": HousingValuationRecovery(client),
    "INDP": INDP(client),
    "JoplinCGEModel": JoplinCGEModel(client),
    "JoplinEmpiricalBuildingRestoration": JoplinEmpiricalBuildingRestoration(client),
    "MeanDamage": MeanDamage(client),
    "MlEnabledCgeSlc": MlEnabledCgeSlc(client),
    "MonteCarloLimitStateProbability": MonteCarloLimitStateProbability(client),
    "MultiObjectiveRetrofitOptimization": MultiObjectiveRetrofitOptimization(client),
    "NciFunctionality": NciFunctionality(client),
    "PipelineDamage": PipelineDamage(client),
    "PipelineDamageRepairRate": PipelineDamageRepairRate(client),
    "PipelineFunctionality": PipelineFunctionality(client),
    "PipelineRepairCost": PipelineRepairCost(client),
    "PipelineRestoration": PipelineRestoration(client),
    "PopulationDislocation": PopulationDislocation(client),
    "ResidentialBuildingRecovery": ResidentialBuildingRecovery(client),
    "RoadDamage": RoadDamage(client),
    "SaltLakeCGEModel": SaltLakeCGEModel(client),
    "SeasideCGEModel": SeasideCGEModel(client),
    "SocialVulnerabilityScore": SocialVulnerabilityScore(client),
    "TornadoEpnDamage": TornadoEpnDamage(client),
    "TrafficFlowRecovery": TrafficFlowRecovery(client),
    "WaterFacilityDamage": WaterFacilityDamage(client),
    "WaterFacilityRepairCost": WaterFacilityRepairCost(client),
    "WaterFacilityDamage": WaterFacilityDamage(client),
    "WaterFacilityRestoration": WaterFacilityRestoration(client),
    "WfnFunctionality": WfnFunctionality(client),
}

# create a dictionary of pretty names
pretty_names = {
    "BridgeDamage": "Bridge Damage",
    "BuildingClusterRecovery": "Building Cluster Recovery",
    "BuildingEconLoss": "Building Economic Loss",
    "BuildingFunctionality": "Building Functionality",
    "BuildingNonStructDamage": "Building Non-Structural Damage",
    "BuildingStructuralDamage": "Building Structural Damage",
    "BuyoutDecision": "Buyout Decision",
    "CapitalShocks": "Capital Shocks",
    "CombinedWindWaveSurgeBuildingDamage": "Combined Wind Wave Surge Building Damage",
    "CombinedWindWaveSurgeBuildingLoss": "Combined Wind Wave Surge Building Loss",
    "CommercialBuildingRecovery": "Commercial Building Recovery",
    "CumulativeBuildingDamage": "Cumulative Building Damage",
    "EpfDamage": "Electric Power Facility Damage",
    "EpfRepairCost": "Electric Power Facility Repair Cost",
    "EpfRestoration": "Electric Power Facility Restoration",
    "EpnFunctionality": "Electric Power Network Functionality",
    "GalvestonCGEModel": "Galveston CGE Model",
    "GasFacilityDamage": "Gas Facility Damage",
    "HousingRecoverySequential": "Housing Recovery Sequential",
    "HousingUnitAllocation": "Housing Unit Allocation",
    "HousingValuationRecovery": "Housing Valuation Recovery",
    "INDP": "Infrastructure Network Disruption Planning",
    "JoplinCGEModel": "Joplin CGE Model",
    "JoplinEmpiricalBuildingRestoration": "Joplin Empirical Building Restoration",
    "MeanDamage": "Mean Damage",
    "MlEnabledCgeSlc": "Machine Learning Enabled CGE SLC",
    "MonteCarloLimitStateProbability": "Monte Carlo Limit State Probability",
    "MultiObjectiveRetrofitOptimization": "Multi-Objective Retrofit Optimization",
    "NciFunctionality": "Network Cascading Interdependency Functionality",
    "PipelineDamage": "Pipeline Damage",
    "PipelineDamageRepairRate": "Pipeline Damage Repair Rate",
    "PipelineFunctionality": "Pipeline Functionality",
    "PipelineRepairCost": "Pipeline Repair Cost",
    "PipelineRestoration": "Pipeline Restoration",
    "PopulationDislocation": "Population Dislocation",
    "ResidentialBuildingRecovery": "Residential Building Recovery",
    "RoadDamage": "Road Damage",
    "SaltLakeCGEModel": "Salt Lake CGE Model",
    "SeasideCGEModel": "Seaside CGE Model",
    "SocialVulnerabilityScore": "Social Vulnerability Score",
    "TornadoEpnDamage": "Tornado Electric Power Network Damage",
    "TrafficFlowRecovery": "Traffic Flow Recovery",
    "WaterFacilityDamage": "Water Facility Damage",
    "WaterFacilityRepairCost": "Water Facility Repair Cost",
    "WaterFacilityDamage": "Water Facility Damage",
    "WaterFacilityRestoration": "Water Facility Restoration",
    "WfnFunctionality": "Water Facility Network Functionality",
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
    value["pretty_name"] = pretty_names[analysis_name]

json.dump(dependency_graph, open("new_dependency_graph.json", "w"), indent=4)
