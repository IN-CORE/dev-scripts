package edu.illinois.ncsa.scripts.Dataset;

import edu.illinois.ncsa.scripts.Serialization.Serializable;
import org.apache.xerces.dom.DeferredElementImpl;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

public class PropertyMetadata extends Serializable {
    private String description;
    private boolean isResult;
    private boolean isNumeric;
    private String importance;
    private String aggregationType;
    private int fieldLength;
    private String id;

    public PropertyMetadata(String id) {
        this.id = id;
    }

    /**
     * Filters a property metadata based on the element name
     * @param propertyMetadata List to filter
     * @param elementName Name to filter by
     * @return Single element contained in the list
     */
    public static PropertyMetadata filterMetadataFromList(List<PropertyMetadata> propertyMetadata, String elementName) {
        for (PropertyMetadata element : propertyMetadata) {
            String strippedName = elementName.replace("maeviz.", "").replace("ergo.", "");
            if (element.getId().equalsIgnoreCase(elementName) || element.getId().equalsIgnoreCase(strippedName)) {
                return element;
            }
        }

        return null;
    }

    public static ArrayList<PropertyMetadata> getMetadata(String path) {
        ArrayList<PropertyMetadata> metadataElements = new ArrayList<>();

        Document dom = getPathAsXmlDocument(path);

        Element root = dom.getDocumentElement();

        NodeList elementNodes = root.getChildNodes();

        for (int i = 0; i < elementNodes.getLength(); i++) {
            Node elementNode = elementNodes.item(i);

            if (elementNode.getNodeType() == Node.ELEMENT_NODE) {
                String columnId = ((DeferredElementImpl) elementNode).getAttribute("column-id");
                String friendlyName = ((DeferredElementImpl) elementNode).getAttribute("friendly-name");
                String isNumeric = ((DeferredElementImpl) elementNode).getAttribute("is-numeric");
                String importance = ((DeferredElementImpl) elementNode).getAttribute("importance");
                String isResult = ((DeferredElementImpl) elementNode).getAttribute("is-result");
                String aggType = ((DeferredElementImpl) elementNode).getAttribute("agg-type");
                String fieldLength = ((DeferredElementImpl) elementNode).getAttribute("field-length");

                PropertyMetadata metadata = new PropertyMetadata(columnId);
                metadata.setDescription(friendlyName.isEmpty() ? null : friendlyName);
                metadata.setImportance(importance.isEmpty() ? null : importance);
                metadata.setAggregationType(aggType.isEmpty() ? null : aggType);

                metadataElements.add(metadata);
            }
        }

        return metadataElements;
    }

    public int getFieldLength() {
        return fieldLength;
    }

    public void setFieldLength(int fieldLength) {
        this.fieldLength = fieldLength;
    }

    public String getAggregationType() {
        return aggregationType;
    }

    public void setAggregationType(String aggregationType) {
        this.aggregationType = aggregationType;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public boolean isResult() {
        return isResult;
    }

    public void setResult(boolean result) {
        isResult = result;
    }

    public boolean isNumeric() {
        return isNumeric;
    }

    public void setNumeric(boolean numeric) {
        isNumeric = numeric;
    }

    public String getImportance() {
        return importance;
    }

    public void setImportance(String importance) {
        this.importance = importance;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }
}
