package edu.illinois.ncsa.fragility.Dataset;

import com.sun.org.apache.xerces.internal.dom.DeferredElementImpl;
import edu.illinois.ncsa.fragility.Serialization.Serializable;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.xpath.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class DatasetSchemaInfo extends Serializable {
    private String description;
    private String file;
    private String format;
    private String version;
    private String name;
    private String type;
    private String category;

    public ArrayList<DatasetProperty> properties;

    public DatasetSchemaInfo(String description, String file, String format, String version, String name, String type, String category) {
        this.description = description;
        this.file = file;
        this.format = format;
        this.version = version;
        this.name = name;
        this.type = type;
        this.category = category;
    }

    public static ArrayList<DatasetSchemaInfo> getDatasetMetadata(String pluginPath, Map<String, String> pluginPropertiesMap) {
        Document dom = getPathAsXmlDocument(pluginPath);
        XPathFactory xPathfactory = XPathFactory.newInstance();
        XPath xpath = xPathfactory.newXPath();

        ArrayList<DatasetSchemaInfo> datasetSchemaInfoMetadata = new ArrayList<>();

        Node root = null;
        try {
            XPathExpression expr = xpath.compile("//extension[@point=\"edu.illinois.ncsa.ergo.gis.gisSchemas\"]");
            root = ((NodeList) expr.evaluate(dom, XPathConstants.NODESET)).item(0);
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }

        //get root as element extension and attribute point with value "edu.illinois.ncsa.ergo.gis.gisSchemas"
        if (root != null) {
            NodeList elementNodes = root.getChildNodes();

            for (int i = 0; i < elementNodes.getLength(); i++) {
                Node elementNode = elementNodes.item(i);
                if (elementNode.getNodeType() == Node.ELEMENT_NODE) {
                    String name = ((DeferredElementImpl) elementNode).getAttribute("name");
                    String type = ((DeferredElementImpl) elementNode).getAttribute("type");
                    String description = ((DeferredElementImpl) elementNode).getAttribute("description");
                    String file = ((DeferredElementImpl) elementNode).getAttribute("file");
                    String format = ((DeferredElementImpl) elementNode).getAttribute("format");
                    String version = ((DeferredElementImpl) elementNode).getAttribute("version");

                    String categoryTemp = ((DeferredElementImpl) elementNode).getAttribute("category");
                    String category = categoryTemp;
                    if (pluginPropertiesMap.containsKey(categoryTemp)) {
                        category = pluginPropertiesMap.get(categoryTemp);
                    }

                    DatasetSchemaInfo datasetSchemaInfo = new DatasetSchemaInfo(description, file, format, version, name, type, category);

                    datasetSchemaInfoMetadata.add(datasetSchemaInfo);
                }
            }
        }

        return datasetSchemaInfoMetadata;
    }

    /**
     * Retrieves the DatasetSchemaInfo from the specific list based on the filename
     * @param dataSchemaList
     * @param filename
     * @return
     */
    public static DatasetSchemaInfo filterDatasetFromList(List<DatasetSchemaInfo> dataSchemaList, String filename) {
        for (DatasetSchemaInfo element : dataSchemaList) {
            if (filename.contains(element.getFile().replace("gisSchemas/", ""))) {
                return element;
            }
        }

        return null;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getFile() {
        return file;
    }

    public void setFile(String file) {
        this.file = file;
    }

    public String getFormat() {
        return format;
    }

    public void setFormat(String format) {
        this.format = format;
    }

    public String getVersion() {
        return version;
    }

    public void setVersion(String version) {
        this.version = version;
    }

    public String getName() {
        return name;
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

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public ArrayList<DatasetProperty> getProperties() {
        return properties;
    }

    public void setProperties(ArrayList<DatasetProperty> properties) {
        this.properties = properties;
    }

}
