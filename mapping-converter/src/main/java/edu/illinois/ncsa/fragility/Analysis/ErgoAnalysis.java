package edu.illinois.ncsa.fragility.Analysis;

import com.sun.org.apache.xerces.internal.dom.DeferredElementImpl;
import edu.illinois.ncsa.fragility.Serialization.Serializable;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.xpath.*;
import java.io.File;
import java.util.ArrayList;
import java.util.Map;

public class ErgoAnalysis extends Serializable {
    private ProjectType type;
    private String category;
    private String name;
    private String description;
    private String tag;
    private String id;
    private String descriptor;
    private ErgoAnalysisInfo analysisInfo;

    public ErgoAnalysis(String id, String category, String name, String description, String tag, String descriptor, ProjectType projectType) {
        this.id = id;
        this.category = category;
        this.name = name;
        this.description = description;
        this.tag = tag;
        this.descriptor = descriptor;
        this.type = projectType;
    }

    public static ArrayList<ErgoAnalysis> getAnalysisMetadata(String pluginPath, Map<String, String> pluginPropertiesMap) {
        Document dom = getPathAsXmlDocument(pluginPath);
        XPathFactory xPathfactory = XPathFactory.newInstance();
        XPath xpath = xPathfactory.newXPath();

        ArrayList<ErgoAnalysis> analysisMetadata = new ArrayList<>();

        Node root = null;
        try {
            XPathExpression expr = xpath.compile("//extension[@point=\"edu.illinois.ncsa.ergo.core.analysis.newAnalyses\"]");
            root = ((NodeList) expr.evaluate(dom, XPathConstants.NODESET)).item(0);
        } catch (XPathExpressionException e) {
            e.printStackTrace();
        }

        //get root as element extension and attribute point with value "edu.illinois.ncsa.ergo.core.analysis.newAnalyses"
        if (root != null) {
            NodeList elementNodes = root.getChildNodes();

            for (int i = 0; i < elementNodes.getLength(); i++) {
                Node elementNode = elementNodes.item(i);
                if (elementNode.getNodeType() == Node.ELEMENT_NODE) {
                    String id = ((DeferredElementImpl) elementNode).getAttribute("id").trim();
                    String name = ((DeferredElementImpl) elementNode).getAttribute("name").trim();
                    String description = ((DeferredElementImpl) elementNode).getAttribute("description").trim();
                    String tag = ((DeferredElementImpl) elementNode).getAttribute("tag").trim();
                    String descriptor = ((DeferredElementImpl) elementNode).getAttribute("descriptor").trim();

                    String categoryTemp = ((DeferredElementImpl) elementNode).getAttribute("category").trim();
                    String category = categoryTemp;

                    if (pluginPropertiesMap.containsKey(categoryTemp)) {
                        category = pluginPropertiesMap.get(categoryTemp);
                    }

                    ProjectType projectType = pluginPath.startsWith("C:\\Users\\omar\\git\\ergo") ? ProjectType.ERGO : ProjectType.INCORE;
                    ErgoAnalysis ergoMetadata = new ErgoAnalysis(id, category, name, description, tag, descriptor, projectType);

                    //Load Analysis Information
                    File pluginDir = new File(pluginPath);
                    File descriptorPath = new File(pluginDir.getParent().toString() + "/" + descriptor);
                    if (descriptorPath.exists()) {
                        ErgoAnalysisInfo analysisInfo = ErgoAnalysisInfo.loadDescriptor(descriptorPath.toString());

                        ergoMetadata.analysisInfo = analysisInfo;
                    }

                    analysisMetadata.add(ergoMetadata);
                }
            }
        }

        return analysisMetadata;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getDescriptor() {
        return descriptor;
    }

    public ErgoAnalysisInfo getAnalysisInfo() {
        return analysisInfo;
    }

    public void setAnalysisInfo(ErgoAnalysisInfo analysisInfo) {
        this.analysisInfo = analysisInfo;
    }

    public ProjectType getType() {
        return type;
    }

    public void setType(ProjectType type) {
        this.type = type;
    }
}