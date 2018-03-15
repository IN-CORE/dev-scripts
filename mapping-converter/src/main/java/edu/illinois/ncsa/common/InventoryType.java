package edu.illinois.ncsa.common;

public enum InventoryType {
    Building("building"),
    Bridge("bridge"),
    BuriedPipeline("buried_pipeline"),
    WaterFacility("water_facility"),
    ElectricFacility("electric_facility"),
    GasFacility("gas_facility"),
    Roadway("roadway"),
    Railway("railway"),
    ElectricPowerLine("electric_power_line");

    private String value;

    private InventoryType(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
