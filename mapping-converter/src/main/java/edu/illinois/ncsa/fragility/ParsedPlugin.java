package edu.illinois.ncsa.fragility;

import edu.illinois.ncsa.fragility.Analysis.ErgoAnalysis;
import edu.illinois.ncsa.fragility.Dataset.DatasetSchemaInfo;

import java.util.List;

public class ParsedPlugin {
    private List<ErgoAnalysis> Analyses;
    private List<DatasetSchemaInfo> datasetSchemaInfos;

    public ParsedPlugin(List<ErgoAnalysis> analyses, List<DatasetSchemaInfo> datasetSchemaInfos) {
        Analyses = analyses;
        this.datasetSchemaInfos = datasetSchemaInfos;
    }

    public List<DatasetSchemaInfo> getDatasetSchemaInfos() {
        return datasetSchemaInfos;
    }

    public void setDatasetSchemaInfos(List<DatasetSchemaInfo> datasetSchemaInfos) {
        this.datasetSchemaInfos = datasetSchemaInfos;
    }

    public List<ErgoAnalysis> getAnalyses() {
        return Analyses;
    }

    public void setAnalyses(List<ErgoAnalysis> analyses) {
        Analyses = analyses;
    }
}
