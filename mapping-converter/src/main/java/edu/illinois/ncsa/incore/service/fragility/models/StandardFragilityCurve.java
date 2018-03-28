package edu.illinois.ncsa.incore.service.fragility.models;

public class StandardFragilityCurve extends FragilityCurve {
    public double median;
    public double beta;
    public FragilityCurveType curveType;

    public StandardFragilityCurve() {
        super();
    }

    public StandardFragilityCurve(double median, double beta, FragilityCurveType curveType, String label) {
        super(label);

        this.median = median;
        this.beta = beta;
        this.curveType = curveType;
    }
}
