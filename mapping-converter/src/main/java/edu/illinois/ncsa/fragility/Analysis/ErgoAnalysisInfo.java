package edu.illinois.ncsa.fragility.Analysis;

import com.sun.org.apache.xerces.internal.dom.DeferredElementImpl;
import edu.illinois.ncsa.fragility.Serialization.Serializable;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

public class ErgoAnalysisInfo {
    private String id;
    private String helpContext;
    private NodeList parameterNodes;
    private ArrayList<Output> outputs;
    private String analysisType;
    private List<Parameter> analysisInputs;
    private List<Output> analyisOutputs;
    private List<String> producedTypes;

    public ErgoAnalysisInfo(String id, String helpContext, List<Parameter> analysisInputs, ArrayList<Output> outputs) {

        this.id = id;
        this.helpContext = helpContext;
        this.analysisInputs = analysisInputs;
        this.analyisOutputs = outputs;
    }

    public String getHelpContext() {
        return helpContext;
    }

    public void setHelpContext(String helpContext) {
        this.helpContext = helpContext;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getAnalysisType() {
        return analysisType;
    }

    public void setAnalysisType(String analysisType) {
        this.analysisType = analysisType;
    }

    public List<Parameter> getAnalysisInputs() {
        return analysisInputs;
    }

    public List<String> getInputTypes() {
        List<String> inputTypes = new ArrayList<>();

        for (Parameter analysisInput : analysisInputs) {
            inputTypes.addAll(analysisInput.getTypes());
        }

        return inputTypes;
    }

    public void setAnalysisInputs(List<Parameter> analysisInputs) {
        this.analysisInputs = analysisInputs;
    }

    public List<Output> getAnalyisOutputs() {
        return analyisOutputs;
    }

    public void setAnalyisOutputs(List<Output> analyisOutputs) {
        this.analyisOutputs = analyisOutputs;
    }

    public List<String> getProducedTypes() {
        return producedTypes;
    }

    public void setProducedTypes(List<String> producedTypes) {
        this.producedTypes = producedTypes;
    }

    public static ErgoAnalysisInfo loadDescriptor(String path) {
        Document dom = Serializable.getPathAsXmlDocument(path);
        Node root = dom.getDocumentElement();
        String id = ((DeferredElementImpl) root).getAttribute("id");
        String helpContext = ((DeferredElementImpl) root).getAttribute("help-context");

        NodeList parameterNodes = ((DeferredElementImpl) root).getElementsByTagName("parameter");
        NodeList outputNodes = ((DeferredElementImpl) root).getElementsByTagName("output");

        ArrayList<Parameter> parameters = Parameter.parseParameters(parameterNodes);
        ArrayList<Output> outputs = Output.parseOutputs(outputNodes);

        ErgoAnalysisInfo descriptor = new ErgoAnalysisInfo(id, helpContext, parameters, outputs);

        return descriptor;
    }
}
