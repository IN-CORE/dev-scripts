package edu.illinois.ncsa.scripts.Dataset;

import org.apache.xerces.dom.DeferredElementImpl;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

public class DatasetProperty {
    private String name;
    private String type;
    private List<String> restrictions;
    public PropertyMetadata metadata;

    public DatasetProperty(String name, String type) {
        this.name = name;
        this.type = type;
    }

    /**
     * Parse All the Properties from the .XSD file and return them as DatasetProperties
     *
     * @param dom Document Object Model
     * @return Parsed Properties
     */
    public static ArrayList<DatasetProperty> parsePropertiesFromDOM(Document dom) {
        ArrayList<DatasetProperty> ergoXmlElements = new ArrayList<>();

        Element root = dom.getDocumentElement();

        Node sequenceRoot = root.getElementsByTagName("xsd:sequence").item(0);

        if (sequenceRoot == null) {
            return ergoXmlElements;
        }

        NodeList elementNodes = sequenceRoot.getChildNodes();

        for (int i = 0; i < elementNodes.getLength(); i++) {
            Node elementNode = elementNodes.item(i);

            if (elementNode.getNodeType() == Node.ELEMENT_NODE) {
                String name = ((DeferredElementImpl) elementNode).getAttribute("name");
                String type = ((DeferredElementImpl) elementNode).getAttribute("type");

                DatasetProperty element = new DatasetProperty(name, type);

                if (elementNode.hasChildNodes()) {
                    Node simpleType = ((DeferredElementImpl) elementNode).getElementsByTagName("xsd:simpleType").item(0);
                    if (simpleType != null) {
                        NodeList restrictionNodes = ((DeferredElementImpl) simpleType).getElementsByTagName("xsd:restriction");

                        element.setType(((DeferredElementImpl) restrictionNodes.item(0)).getAttribute("base"));

                        if (restrictionNodes.getLength() != 0) {
                            List<String> restrictedValues = getRestrictionValues(restrictionNodes);
                            element.setRestrictions(restrictedValues);
                        }
                    }
                }

                ergoXmlElements.add(element);
            }
        }

        return ergoXmlElements;
    }

    private static List<String> getRestrictionValues(NodeList restrictionNodes) {
        List<String> restrictedValues = new ArrayList<>();

        NodeList restrictionValueNodes = ((DeferredElementImpl) restrictionNodes.item(0)).getElementsByTagName("xsd:enumeration");

        for (int i = 0; i < restrictionValueNodes.getLength(); i++) {
            Node restrictionNode = restrictionValueNodes.item(i);

            if (restrictionNode.getNodeType() == Node.ELEMENT_NODE) {
                restrictedValues.add(((DeferredElementImpl) restrictionNode).getAttribute("value"));
            }
        }

        return restrictedValues;
    }

    public static DatasetProperty getRootElement(Document dom) {
        Node root = dom.getDocumentElement().getElementsByTagName("xsd:element").item(0);

        String name = ((DeferredElementImpl) root).getAttribute("name");
        String type = ((DeferredElementImpl) root).getAttribute("type");

        DatasetProperty rootElement = new DatasetProperty(name, type);

        return rootElement;
    }

    public String getName() {
        return name;
    }

    public String getSanitizedName() {
        return name.replace("ergo.", "").replace("maeviz.", "");
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public List<String> getRestrictions() {
        return restrictions;
    }

    public void setRestrictions(List<String> restrictions) {
        this.restrictions = restrictions;
    }

    public boolean hasRestrictions() {
        return (restrictions != null && !restrictions.isEmpty());
    }

    public PropertyMetadata getMetadata() {
        return metadata;
    }

    public void setMetadata(PropertyMetadata metadata) {
        this.metadata = metadata;
    }

    public String toTSV() {
        if (metadata != null) {
            return name + "\t" + type + "\t" + metadata.getDescription();
        } else {
            return name + "\t" + type;
        }
    }

    public String toCSV() {
        if (metadata != null) {
            return name + ", " + type + ", " + metadata.getDescription();
        } else {
            return name + ", " + type;
        }
    }
}
