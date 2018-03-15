package edu.illinois.ncsa.incore.service.fragility.models;

import edu.illinois.ncsa.common.HazardType;
import edu.illinois.ncsa.common.InventoryType;
import edu.illinois.ncsa.mapping.MatchFilterMap;
import edu.illinois.ncsa.mapping.PropertyMatch;
import org.bson.types.ObjectId;
import org.mongodb.morphia.annotations.Entity;
import org.mongodb.morphia.annotations.Id;

import java.util.ArrayList;
import java.util.List;

@Entity("MappingSet")
public class MappingSet {
    @Id
    public ObjectId id;

    public String name;

    public String hazardType = "earthquake";
    public String inventoryType = "building";

    public List<Mapping> mappings = new ArrayList<>();

    public MappingSet(String name, List<FragilitySet> fragilitySets, MatchFilterMap matchFilterMap) {
        this.name = name;

        this.hazardType = matchHazardType(name);
        this.inventoryType = matchInventoryType(name);

        List<Mapping> mappings = new ArrayList<>();

        for (PropertyMatch propertyMatch : matchFilterMap.getPropertyMatches()) {
            Mapping mapping = new Mapping(fragilitySets, propertyMatch);
            mappings.add(mapping);
        }

        this.mappings = mappings;
    }

    private static String matchInventoryType(String datasetName) {
        String filename = datasetName.toLowerCase();

        if (filename.contains("building")) {
            return InventoryType.Building.getValue();
        } else if (filename.contains("bridge")) {
            return InventoryType.Bridge.getValue();
        } else if (filename.contains("gas facility")) {
            return InventoryType.GasFacility.getValue();
        } else if (filename.contains("water facility")) {
            return InventoryType.WaterFacility.getValue();
        } else if (filename.contains("water tank")) {
            return InventoryType.WaterFacility.getValue();
        } else if (filename.contains("roadway")) {
            return InventoryType.Roadway.getValue();
        } else if (filename.contains("pipeline")) {
            return InventoryType.BuriedPipeline.getValue();
        } else if (filename.contains("pipe")) {
            return InventoryType.BuriedPipeline.getValue();
        } else if (filename.contains("power facility")) {
            return InventoryType.ElectricFacility.getValue();
        } else if (filename.contains("electric substation")) {
            return InventoryType.ElectricFacility.getValue();
        } else if (filename.contains("electric power plant")) {
            return InventoryType.ElectricFacility.getValue();
        } else {
            return InventoryType.Building.getValue();
        }
    }

    private static String matchHazardType(String datasetName) {
        String filename = datasetName.toLowerCase();

        if (filename.contains("tsunami")) {
            return HazardType.Tsunami.getValue();
        } else if (filename.contains("tornado")) {
            return HazardType.Tornado.getValue();
        } else {
            return HazardType.Earthquake.getValue();
        }
    }
}
