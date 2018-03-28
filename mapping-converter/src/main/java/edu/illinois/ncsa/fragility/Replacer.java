package edu.illinois.ncsa.fragility;

import edu.illinois.ncsa.common.HazardType;
import edu.illinois.ncsa.common.InventoryType;
import edu.illinois.ncsa.incore.service.fragility.models.PaperReference;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;

public class Replacer {
    public HashMap<String, String> hazardReplace = new HashMap<>();
    public HashMap<String, String> inventoryReplace = new HashMap<>();

    public HashMap<String, List<String>> authorReplace = new HashMap<>();
    public HashMap<String, PaperReference> paperReplace = new HashMap<>();

    public Replacer() {
        authorReplace.put("Suppasri et al. 2015", Arrays.asList("Anawat Suppasri", "Fumihiko Imamura", "Shunichi Koshimura"));
        paperReplace.put("Suppasri et al. 2015", new PaperReference(
                "Tsunami hazard and casualty estimation in a coastal area that neighbors the Indian Ocean and South China Sea", "2013",
                "10.1142/S1793431112500108"));

        authorReplace.put("Bracci", Arrays.asList("J.M.Bracci", "A.M.Reinhorn", "J.B.Mander"));
        paperReplace.put("Bracci", new PaperReference("NCEER-92-0027", "1992"));

        authorReplace.put("Eidinger (2004)", Arrays.asList("John M. Eidinger"));
        paperReplace.put("Eidinger (2004)", new PaperReference("Seismic Guidelines for Water Pipelines", "2005"));

        authorReplace.put("Elnashai", Arrays.asList("Oh-Sung Kwon", "Amr S. Elnashai"));
        paperReplace.put("Elnashai", new PaperReference(
                "The effect of material and ground motion uncertainty on the seismicvulnerability curves of RC structure", "2005",
                "10.1016/j.engstruct.2005.07.010"));

        authorReplace.put("Honegger and Eguchi (1992)", Arrays.asList("Douglas G. Honegger", "Ronald T. Eguchi"));
        paperReplace.put("Honegger and Eguchi (1992)", new PaperReference(
                "Determination of the relative vulnerabilities to Seismic damage for dan diego country water Authority (SDCWA) Water Transmission Pipelines",
                "1992"));

        authorReplace.put("MAE", Arrays.asList("Mid-America Earthquake (MAE) Center"));

        authorReplace.put("HAZUS", Arrays.asList("HAZUS"));

        authorReplace.put("FEMA", Arrays.asList("Federal Emergency Management Agency (FEMA)"));

        authorReplace.put("O'Rourke, T and Jeon (1999)", Arrays.asList("Thomas Dennis O'Rourke", "Sang-Soo Jeon"));
        paperReplace.put("O'Rourke, T and Jeon (1999)",
                         new PaperReference("Factors affecting the earthquake damage of water distribution systems", "1999"));

        authorReplace.put("R.DesRoches", Arrays.asList("Reginald DesRoches"));

        authorReplace.put("O'Rourke, M and Ayala (1993)", Arrays.asList("Michael O'Rourke", "Gustavo Ayala"));
        paperReplace.put("O'Rourke, M and Ayala (1993)",
                         new PaperReference("Pipeline Damage Due to Wave Propagation", "1992", "10.1061/(ASCE)0733-9410(1993)119:9(1490)"));

        authorReplace.put("HAZUS-DesRoches", Arrays.asList("HAZUS", "Reginald DesRoches"));

        authorReplace.put("Elnashai and Jeong : Steelman", Arrays.asList("Amr S. Elnashai", "Seong-Hoon Jeong", "Joshua S. Steelman"));

        authorReplace.put("Elnashai Kuchma Ji", Arrays.asList("Jun Ji", "Amr S. Elnashai", "Daniel A. Kuchma"));
        paperReplace.put("Elnashai Kuchma Ji",
                         new PaperReference("Seismic Fragility Assessment for Reinforced Concrete High -Rise Buildings", "2007"));

        authorReplace.put("Hueste", Arrays.asList("Jong-Wha Bai", "Mary Beth D. Hueste"));
        paperReplace.put("Hueste", new PaperReference(
                "Deterministic and Probabilistic Evaluation of Retrofit Alternatives for a Five-Story Flat-Slab RC Building", "2007"));

        authorReplace.put("Elnashai and Erberik", Arrays.asList("Amr S. Elnashai", "M. Altug Erberik"));
        paperReplace.put("Elnashai and Erberik", new PaperReference("Seismic Vulnerability of Flat-Slab Structures", "2003"));

        authorReplace.put("Ellingwood", Arrays.asList("Bruce Ellingwood"));

        authorReplace.put("Wen and Li", Arrays.asList("Li", "Yi-Kwei Wen"));

        authorReplace.put("Literature", Arrays.asList("Literature"));

        authorReplace.put("CSU", Arrays.asList("Colorado State University"));

        authorReplace.put("Eidinger", Arrays.asList("John M. Eidinger"));

        authorReplace.put("O'Rourke", Arrays.asList("Thomas Dennis O'Rourke"));

        authorReplace.put("Suppasri et al. 2013",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));

        paperReplace.put("Suppasri et al. 2013", new PaperReference(
                "Building damage characteristics based on surveyed data and fragility curves of the 2011 Great East Japan tsunami", "2014",
                "10.1007/s11069-012-0487-8"));

        authorReplace.put("Suppasri et al. 2014",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));
        paperReplace.put("Suppasri et al. 2014", new PaperReference(
                "Building damage characteristics based on surveyed data and fragility curves of the 2011 Great East Japan tsunami", "2014",
                "10.1007/s11069-012-0487-8"));

        authorReplace.put("Suppasri et al. 2016",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));

        paperReplace.put("Suppasri et al. 2016", new PaperReference(
                "Building damage characteristics based on surveyed data and fragility curves of the 2011 Great East Japan tsunami", "2014",
                "10.1007/s11069-012-0487-8"));

        authorReplace.put("Suppasri et al. 2017",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));
        paperReplace.put("Suppasri et al. 2017", new PaperReference(
                "Building damage characteristics based on surveyed data and fragility curves of the 2011 Great East Japan tsunami", "2014",
                "10.1007/s11069-012-0487-8"));

        authorReplace.put("Suppasri et al. 2018",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));
        paperReplace.put("Suppasri et al. 2018", new PaperReference(
                "Building damage characteristics based on surveyed data and fragility curves of the 2011 Great East Japan tsunami", "2014",
                "10.1007/s11069-012-0487-8"));

        authorReplace.put("Suppasri et al. 2013",
                          Arrays.asList("Anawat Suppasri", "Erick Mas", "Ingrid Charvet", "Rashmin Gunasekera", "Kentaro Imai",
                                        "Yo Fukutani", "Yoshi Abe", "Fumihiko Imamura"));

        hazardReplace.put("Buried_Pipeline_Fragilities_v1.1.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Buried_Pipeline_Fragilities_v1.1.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("Default_Bridge_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Default_Bridge_Fragilities.xml", InventoryType.Bridge.getValue());

        hazardReplace.put("Default_Building_Fragilities_1.0.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Default_Building_Fragilities_1.0.xml", InventoryType.Building.getValue());

        hazardReplace.put("Electric_Equipment_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Electric_Equipment_Fragilities.xml", InventoryType.ElectricFacility.getValue());

        hazardReplace.put("Electric_Power_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Electric_Power_Facility_Fragilities_for_INA.xml", InventoryType.ElectricFacility.getValue());

        hazardReplace.put("Gas_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Gas_Facility_Fragilities_for_INA.xml", InventoryType.GasFacility.getValue());

        hazardReplace.put("Hazus_Buried_Pipeline_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Hazus_Buried_Pipeline_Fragilities.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("Non_Structural_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Non_Structural_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("Potable_Water_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Potable_Water_Facility_Fragilities_for_INA.xml", InventoryType.WaterFacility.getValue());

        hazardReplace.put("Roadway_Fragility.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Roadway_Fragility.xml", InventoryType.Roadway.getValue());

        hazardReplace.put("Sample_Buried_Pipeline_Fragility_Set_with_Liquefaction.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Sample_Buried_Pipeline_Fragility_Set_with_Liquefaction.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("Tornado_Building_Fragilities.xml", HazardType.Tornado.getValue());
        inventoryReplace.put("Tornado_Building_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("Tsunami_Fragilities.xml", HazardType.Tsunami.getValue());
        inventoryReplace.put("Tsunami_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("Water_Tank_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("Water_Tank_Fragilities.xml", InventoryType.WaterFacility.getValue());

        // Fragility and Mappings Combined

        hazardReplace.put("FRAG_Buried_Pipeline_Fragilities_v1.1.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Buried_Pipeline_Fragilities_v1.1.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("FRAG_Centerville_Building_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Centerville_Building_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("FRAG_Default_Bridge_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Default_Bridge_Fragilities.xml", InventoryType.Bridge.getValue());

        hazardReplace.put("FRAG_Default Building Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Default Building Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("FRAG_Default_Building_Fragilities_1.0.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Default_Building_Fragilities_1.0.xml", InventoryType.Building.getValue());

        hazardReplace.put("FRAG_Electric_Equipment_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Electric_Equipment_Fragilities.xml", InventoryType.ElectricFacility.getValue());

        hazardReplace.put("FRAG_Electric_Power_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Electric_Power_Facility_Fragilities_for_INA.xml", InventoryType.ElectricFacility.getValue());

        hazardReplace.put("FRAG_Gas_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Gas_Facility_Fragilities_for_INA.xml", InventoryType.GasFacility.getValue());

        hazardReplace.put("FRAG_Hazus Electric Power Facility Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Hazus Electric Power Facility Fragilities.xml", InventoryType.ElectricFacility.getValue());

        hazardReplace.put("FRAG_Hazus Potable Water Facility Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Hazus Potable Water Facility Fragilities.xml", InventoryType.WaterFacility.getValue());

        hazardReplace.put("FRAG_Hazus Tornado Electric Power Line Fragility.xml", HazardType.Tornado.getValue());
        inventoryReplace.put("FRAG_Hazus Tornado Electric Power Line Fragility.xml", InventoryType.ElectricPowerLine.getValue());

        hazardReplace.put("FRAG_Hazus_Buried_Pipeline_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Hazus_Buried_Pipeline_Fragilities.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("FRAG_Potable_Water_Facility_Fragilities_for_INA.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Potable_Water_Facility_Fragilities_for_INA.xml", InventoryType.WaterFacility.getValue());

        hazardReplace.put("FRAG_Roadway_Fragility.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Roadway_Fragility.xml", InventoryType.Roadway.getValue());

        hazardReplace.put("FRAG_Sample_Buried_Pipeline_Fragility_Set_with_Liquefaction.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Sample_Buried_Pipeline_Fragility_Set_with_Liquefaction.xml", InventoryType.BuriedPipeline.getValue());

        hazardReplace.put("FRAG_Tornado_Building_Fragilities.xml", HazardType.Tornado.getValue());
        inventoryReplace.put("FRAG_Tornado_Building_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("FRAG_Tsunami_Fragilities.xml", HazardType.Tsunami.getValue());
        inventoryReplace.put("FRAG_Tsunami_Fragilities.xml", InventoryType.Building.getValue());

        hazardReplace.put("FRAG_Water_Tank_Fragilities.xml", HazardType.Earthquake.getValue());
        inventoryReplace.put("FRAG_Water_Tank_Fragilities.xml", InventoryType.WaterFacility.getValue());
    }
}
