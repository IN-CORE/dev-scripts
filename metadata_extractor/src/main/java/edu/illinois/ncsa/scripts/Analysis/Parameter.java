package edu.illinois.ncsa.scripts.Analysis;

import org.apache.xerces.dom.DeferredElementImpl;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

public class Parameter {
    private final String advanced;
    private String phylum;
    private String cardinality;
    private String key;
    private String friendlyName;
    private List<String> types;
    private String description;

    public boolean isOptional() {
        return isOptional;
    }

    public void setOptional(boolean optional) {
        isOptional = optional;
    }

    private boolean isOptional;

    public Parameter(String key, String advanced, String cardinality, String phylum, String friendlyName, boolean isOptional) {
        this.key = key;
        this.advanced = advanced;
        this.cardinality = cardinality;
        this.phylum = phylum;
        this.friendlyName = friendlyName;
        this.isOptional = isOptional;

        this.types = new ArrayList<>();
    }

    public String getPhylum() {
        return phylum;
    }

    public void setPhylum(String phylum) {
        this.phylum = phylum;
    }

    public String getCardinality() {
        return cardinality;
    }

    public void setCardinality(String cardinality) {
        this.cardinality = cardinality;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getFriendlyName() {
        return friendlyName;
    }

    public void setFriendlyName(String friendlyName) {
        this.friendlyName = friendlyName;
    }

    public List<String> getTypes() {
        return types;
    }

    public void setTypes(List<String> types) {
        this.types = types;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public static ArrayList<Parameter> parseParameters(NodeList parameterNodes) {
        ArrayList<Parameter> parameters = new ArrayList<>();

        for (int i = 0; i < parameterNodes.getLength(); i++) {
            Node parameterNode = parameterNodes.item(i);
            if (parameterNode.getNodeType() == Node.ELEMENT_NODE) {
                String key = ((DeferredElementImpl) parameterNode).getAttribute("key");
                String advanced = ((DeferredElementImpl) parameterNode).getAttribute("advanced");
                String cardinality = ((DeferredElementImpl) parameterNode).getAttribute("cardinality");
                String phylum = ((DeferredElementImpl) parameterNode).getAttribute("phylum");
                String friendlyName = ((DeferredElementImpl) parameterNode).getAttribute("friendly-name");
                boolean isOptional = ((DeferredElementImpl) parameterNode).getAttribute("optional").equalsIgnoreCase("true") ? true : false;

                Parameter parameter = new Parameter(key, advanced, cardinality, phylum, friendlyName, isOptional);

                if (phylum.equalsIgnoreCase("dataset") && parameterNode.hasChildNodes()) {

                    NodeList nodeDatasetTypes = ((DeferredElementImpl) parameterNode).item(1).getChildNodes();

                    for (int j = 0; j < nodeDatasetTypes.getLength(); j++) {
                        Node nodeDatasetType = nodeDatasetTypes.item(j);
                        if (nodeDatasetType.getNodeType() == Node.ELEMENT_NODE) {
                            parameter.getTypes().add(nodeDatasetType.getTextContent());
                        }
                    }
                }

                parameters.add(parameter);
            }
        }

        return parameters;
    }
}