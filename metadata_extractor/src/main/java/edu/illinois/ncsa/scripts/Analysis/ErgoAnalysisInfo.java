package edu.illinois.ncsa.scripts.Analysis;

import edu.illinois.ncsa.scripts.Serialization.Serializable;
import org.apache.xerces.dom.DeferredElementImpl;
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
    private List<Output> analysisOutputs;
    private List<String> producedTypes;

    @Override
    public String toString() {
        return id + "\t" + helpContext + '\t' + parameterNodes + '\t' + outputs + '\t' + analysisType + '\t' +
            analysisInputs  + '\t'+ analysisOutputs + '\t' + producedTypes + '\t';
    }

    public ErgoAnalysisInfo(String id, String helpContext, List<Parameter> analysisInputs, ArrayList<Output> outputs) {

        this.id = id;
        this.helpContext = helpContext;
        this.analysisInputs = analysisInputs;
        this.analysisOutputs = outputs;
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

    public List<Output> getAnalysisOutputs() {
        return analysisOutputs;
    }

    public void setAnalysisOutputs(List<Output> analysisOutputs) {
        this.analysisOutputs = analysisOutputs;
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
