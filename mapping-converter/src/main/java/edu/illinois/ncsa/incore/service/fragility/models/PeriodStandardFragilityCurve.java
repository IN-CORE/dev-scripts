package edu.illinois.ncsa.incore.service.fragility.models;

public class PeriodStandardFragilityCurve extends StandardFragilityCurve {
    public double periodParam2;
    public double periodParam1;
    public double periodParam0;
    public int periodEqnType;

    public PeriodStandardFragilityCurve() {
        super();
    }

    public PeriodStandardFragilityCurve(double median, double beta, FragilityCurveType curveType, String label,
                                        int periodEqnType, double periodParam0, double periodParam1, double periodParam2) {
        super(median, beta, curveType, label);

        this.periodEqnType = periodEqnType;
        this.periodParam0 = periodParam0;
        this.periodParam1 = periodParam1;
        this.periodParam2 = periodParam2;
    }
}
