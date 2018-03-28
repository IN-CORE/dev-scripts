package edu.illinois.ncsa.incore.service.fragility.models;

/**
 * Created by omar on 11/17/2016.
 */
public class CustomExpressionFragilityCurve extends FragilityCurve {
    public String expression;

    public CustomExpressionFragilityCurve() {
        super();
    }

    public CustomExpressionFragilityCurve(String expression, String label) {
        super(label);
        this.expression = expression;
    }
}
