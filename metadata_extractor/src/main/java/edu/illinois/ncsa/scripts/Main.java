package edu.illinois.ncsa.scripts;

import com.google.common.io.Files;
import edu.illinois.ncsa.scripts.Analysis.ErgoAnalysis;
import edu.illinois.ncsa.scripts.Dataset.DatasetProperty;
import edu.illinois.ncsa.scripts.Dataset.DatasetSchemaInfo;
import edu.illinois.ncsa.scripts.Dataset.PropertyMetadata;
import edu.illinois.ncsa.scripts.Serialization.Serializable;
import org.w3c.dom.Document;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;

public class Main {

    public static void main(String[] args) {
        File ergoPath = new File("C:\\Users\\omar\\git\\ergo\\");
        File nistPath = new File("C:\\Users\\omar\\git\\incore-v1\\");

        List<File> plugins = new ArrayList<>();
        plugins.addAll(Arrays.asList(ergoPath.listFiles()));
        plugins.addAll(Arrays.asList(nistPath.listFiles()));

        List<DatasetSchemaInfo> datasets = new ArrayList<>();
        List<ErgoAnalysis> analyses = new ArrayList<>();

        for (File pluginPath : plugins) {
            if (pluginPath.isDirectory()) {
                File pluginAnalysisPath = new File(pluginPath + "\\descriptions\\");
                File pluginSchemaPath = new File(pluginPath + "\\gisSchemas\\");
                File pluginXmlPath = new File(pluginPath + "\\plugin.xml");

                if (pluginXmlPath.exists()) {
                    analyses.addAll(parseAnalyses(pluginXmlPath));
                }

                if (pluginSchemaPath.exists()) {
                    datasets.addAll(parseDatasets(pluginSchemaPath));
                }
            }
        }

        System.out.println("-------------- Analyses -----------------");

        for (ErgoAnalysis analysis : analyses) {
            System.out.println(analysis.toTSV());
        }

        System.out.println("-------------- Datasets -----------------");

        for (DatasetSchemaInfo dataset : datasets) {
            System.out.println(dataset.toTSV());
        }

        System.out.println("-------------- Properties -----------------");

        for (DatasetSchemaInfo dataset : datasets) {
            for (DatasetProperty property : dataset.properties) {
                System.out.println(dataset.getName() + "\t" + property.toTSV());
            }
        }
    }

    private static List<ErgoAnalysis> parseAnalyses(File pluginPath) {
        String pluginPropertiesPath = pluginPath.getParent() + "\\plugin.properties";
        Map<String, String> pluginProperties = getPluginProperties(pluginPropertiesPath);

        ArrayList<ErgoAnalysis> ergoAnalyses = ErgoAnalysis.getAnalysisMetadata(pluginPath.toString(), pluginProperties);

        return ergoAnalyses;
    }

    private static List<DatasetSchemaInfo> parseDatasets(File pluginPath) {
        String pluginXmlPath = pluginPath.getParent() + "\\plugin.xml";
        String pluginPropertiesPath = pluginPath.getParent() + "\\plugin.properties";

        Map<String, String> pluginProperties = getPluginProperties(pluginPropertiesPath);
        ArrayList<DatasetSchemaInfo> datasetSchemaInfoList = DatasetSchemaInfo.getDatasetMetadata(pluginXmlPath, pluginProperties);

        for (DatasetSchemaInfo datasetSchemaInfo : datasetSchemaInfoList) {
            File schemaPath = new File(pluginPath.getParent() + "\\" + datasetSchemaInfo.getFile());

            if (schemaPath.exists() && Files.getFileExtension(schemaPath.toString()).equals("xsd")) {
                String metadataPath = getMetadataPath(schemaPath.toString());

                // Retrieve Attribute Metadata
                File metadataFile = new File(metadataPath);
                ArrayList<PropertyMetadata> propertyMetadataList;
                if (metadataFile.exists()) {
                    propertyMetadataList = PropertyMetadata.getMetadata(metadataPath);
                } else {
                    propertyMetadataList = null;
                }

                // Retrieve dataset attributes from .xsd schema file
                Document dom = Serializable.getPathAsXmlDocument(schemaPath.getPath());
                if (dom != null) {
                    ArrayList<DatasetProperty> datasetProperties = DatasetProperty.parsePropertiesFromDOM(dom);

                    // Match metadata with attribute
                    if (propertyMetadataList != null) {
                        for (DatasetProperty datasetProperty : datasetProperties) {
                            PropertyMetadata metadataElement = PropertyMetadata.filterMetadataFromList(propertyMetadataList,
                                                                                                       datasetProperty.getName());

                            datasetProperty.metadata = metadataElement;
                        }
                    }

                    datasetSchemaInfo.properties = datasetProperties;
                }
            }
        }

        return datasetSchemaInfoList;
    }


    /**
     * Retrieves the .xml file under gisMetadata
     *
     * @param schemaPathString Path to the schema file (.xsd) file
     * @return Full path to the .xml metadata file
     */
    private static String getMetadataPath(String schemaPathString) {
        Path schemaPath = Paths.get(schemaPathString);
        String filename = schemaPath.getFileName().toString();

        Path metadataFilePath = Paths.get(schemaPath.getParent().getParent() + "/gisMetadata/" + filename.replace(".xsd", ".xml"));

        return metadataFilePath.toString();
    }

    private static Map<String, String> getPluginProperties(String pluginPropertiesPath) {
        File pluginProperties = new File(pluginPropertiesPath);
        Map<String, String> properties = new HashMap<>();

        if (pluginProperties.exists()) {
            List<String> lines = new ArrayList<>();

            try {
                lines = Files.readLines(pluginProperties, Charset.defaultCharset());
            } catch (IOException e) {
                e.printStackTrace();
            }

            for (String property : lines) {
                if (property.contains("=")) {
                    String[] split = property.split("=");
                    properties.put("%" + split[0].trim(), split[1].trim());
                }
            }
        }

        return properties;
    }
}
