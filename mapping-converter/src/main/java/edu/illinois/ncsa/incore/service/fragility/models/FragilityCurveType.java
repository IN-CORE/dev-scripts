package edu.illinois.ncsa.incore.service.fragility.models;

import edu.illinois.ncsa.tools.common.exceptions.NoSuchElementException;

public enum FragilityCurveType {
    LogNormal("LogNormal"),
    Normal("Normal");

    private String value;

    private FragilityCurveType(String value) {
        this.value = value;
    }

    public static FragilityCurveType fromString(String enumValue) throws NoSuchElementException {
        for (FragilityCurveType fragilityCurveType : FragilityCurveType.values()) {
            if (fragilityCurveType.value.equalsIgnoreCase(enumValue)) {
                return fragilityCurveType;
            }
        }

        throw new NoSuchElementException("Could not find fragility curve type with value corresponding to " + enumValue);
    }
}
