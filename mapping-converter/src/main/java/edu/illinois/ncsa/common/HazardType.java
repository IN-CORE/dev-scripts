package edu.illinois.ncsa.common;

public enum HazardType {
    Earthquake("earthquake"),
    Tornado("tornado"),
    Tsunami("tsunami"),
    Wildfire("wildfire");

    private String value;

    private HazardType(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
