package edu.illinois.ncsa.scripts.Serialization;

import com.google.common.collect.ArrayListMultimap;
import com.google.common.collect.Multimap;
import edu.illinois.ncsa.scripts.Analysis.ErgoAnalysis;
import edu.illinois.ncsa.scripts.Analysis.Output;
import edu.illinois.ncsa.scripts.Analysis.Parameter;
import edu.illinois.ncsa.scripts.Analysis.ProjectType;
import edu.illinois.ncsa.scripts.Dataset.DatasetProperty;
import edu.illinois.ncsa.scripts.Dataset.DatasetSchemaInfo;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.*;

/**
 * Serialization utils for converting the data to JSON for use with vis.js
 */
public class SerializationUtils {

    private static class Node {
        String id;
        String parentId;
        String parentName;
        DatasetSchemaInfo parent;
        String name;

        public Node(String id, String name, DatasetSchemaInfo parent, String parentId, String parentName) {
            this.id = id;
            this.name = name;
            this.parent = parent;
            this.parentId = parentId;
            this.parentName = parentName;
        }
    }

    public static String exportNodesToJSON(List<ErgoAnalysis> analyses, ArrayList<DatasetSchemaInfo> datasetSchemaInfos) {
        List<String> inputsAndOutputs = new ArrayList<>();
        JSONArray jsonArray = new JSONArray();

        for (ErgoAnalysis analysis : analyses) {
            String group = analysis.getType() == ProjectType.ERGO ? "g1" : "g2";
            List<Parameter> inputs = analysis.getAnalysisInfo().getAnalysisInputs();
            List<Output> outputs = analysis.getAnalysisInfo().getAnalyisOutputs();

            inputsAndOutputs.addAll(combineAndFlatten(inputs, outputs));

            try {
                if (inputs.size() > 0 || outputs.size() > 0) {
                    jsonArray.put(new JSONObject().put("id", analysis.getTag() + "Analysis")
                            .put("label", analysis.getName())
                            .put("shape", "box")
                            .put("group", group)
                            .put("size", 50)
                            .put("category", analysis.getCategory().toLowerCase()));
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        for (DatasetSchemaInfo datasetSchemaInfo : datasetSchemaInfos) {
            try {
                if(inputsAndOutputs.contains(datasetSchemaInfo.getType())) {
                    jsonArray.put(new JSONObject().put("id", datasetSchemaInfo.getType() + "DatasetSchemaInfo")
                            .put("label", datasetSchemaInfo.getName())
                            .put("group", "g3")
                            .put("size", 50)
                            .put("shape", "box"));
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        return jsonArray.toString();
    }

    public static String exportAnalysisEdgesToJSON(ArrayList<ErgoAnalysis> analyses) {
        JSONArray jsonArray = new JSONArray();

        for (ErgoAnalysis analysis : analyses) {
            try {
                for (Parameter input : analysis.getAnalysisInfo().getAnalysisInputs()) {
                    for (String type : input.getTypes()) {
                        JSONObject obj = new JSONObject().put("from", type + "DatasetSchemaInfo")
                                .put("to", analysis.getTag() + "Analysis")
                                .put("arrows", "to");

                        if (input.isOptional()) {
                            obj.put("dashes", true);
                        }

                        jsonArray.put(obj);
                    }
                }

                for (Output output : analysis.getAnalysisInfo().getAnalyisOutputs()) {
                    JSONObject obj = new JSONObject().put("from", analysis.getTag() + "Analysis")
                            .put("to", output.getKey() + "DatasetSchemaInfo")
                            .put("arrows", "to");

                    jsonArray.put(obj);
                }

            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        return jsonArray.toString();
    }

    public static List<String> exportNodesToJson(ArrayList<DatasetSchemaInfo> allDatasetSchemaInfos) {
        ArrayList<Node> nodes = new ArrayList<>();

        //NODES
        JSONArray jsonNodeArray = new JSONArray();
        JSONArray jsonEdgeArray = new JSONArray();

        for (DatasetSchemaInfo dataset : allDatasetSchemaInfos) {
            for (DatasetProperty property : dataset.getProperties()) {
                String nodeId = property.getSanitizedName() + "Property";

                nodes.add(new Node(nodeId, property.getSanitizedName(), dataset, dataset.getType() + "Dataset", dataset.getType()));
            }
        }

        Multimap<String, Node> nodesMap = getDuplicates(nodes);
        Set<DatasetSchemaInfo> datasets = new HashSet<>();

        for (String key : nodesMap.keySet()) {
            Collection<Node> duplicateNodes = nodesMap.get(key);
            List<Node> duplicateNodesList = (List) duplicateNodes;

            //Create Property Nodes
            jsonNodeArray.put(createNode(key, key, "ellipse", 999));

            //Connect Nodes to Parent
            for (Node node : duplicateNodesList) {
                datasets.add(node.parent);
                jsonEdgeArray.put(createEdge(node.parentId, key));
            }
        }


        int i = 0;
        for (DatasetSchemaInfo dataset : datasets) {
            //Create Dataset Nodes
            if (!dataset.getProperties().isEmpty()) {
                jsonNodeArray.put(createNode(dataset.getType() + "Dataset", dataset.getName(), "diamond", i));
                i++;
            }
        }

        ArrayList<String> json = new ArrayList<>();
        json.add(jsonNodeArray.toString());
        json.add(jsonEdgeArray.toString());

        return json;
    }


    /**
     * Gets duplicates in the form of a Multimap, keys with no duplicates are not included
     *
     * @param nodes List of nodes containing duplicates
     * @return Multimap containing the duplicates
     */
    private static Multimap<String, Node> getDuplicates(ArrayList<Node> nodes) {

        Multimap<String, Node> duplicates = ArrayListMultimap.create();

        //Add matching here
        for (Node node : nodes) {
            duplicates.put(node.name, node);
        }

        List<String> keys = new ArrayList<>(duplicates.keySet());
        //Remove non-duplicates from the duplicate list
        for (String key : keys) {
            Collection<Node> entryValues = duplicates.get(key);

            //If the array has no duplicates remove it from the Map
            if (entryValues.size() == 1) {
                duplicates.asMap().remove(key);
            }
        }

        return duplicates;
    }

    /**
     * Interlinks nodes and adds them to the jsonarray supplied.
     *
     * @param jsonArray Array to add interlinked nodes to
     * @param nodes     Nodes to interlink
     */
    private static void interlinkNodes(JSONArray jsonArray, List<Node> nodes) {
        for (int i = 0; i < nodes.size() - 1; i++) {
            for (int j = i + 1; j < nodes.size(); j++) {
                jsonArray.put(createEdge(nodes.get(i).id, nodes.get(j).id, "red"));
            }
        }
    }

    /**
     * Helper method to create an edge between two node
     *
     * @param from  Id of the "from" Node
     * @param to    Id of the "to" Node
     * @param color Color of the Edge
     * @return the object created as a JSONObject
     */
    private static JSONObject createEdge(String from, String to, String color) {
        try {
            JSONObject edge = new JSONObject().put("from", from)
                    .put("to", to)
                    .put("color", new JSONObject().put("color", color));

            return edge;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Helper method to create an edge between two node
     *
     * @param from Id of the "from" Node
     * @param to   Id of the "to" Node
     * @return the object created as a JSONObject
     */
    private static JSONObject createEdge(String from, String to) {
        try {
            JSONObject edge = new JSONObject().put("from", from)
                    .put("to", to);

            return edge;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Helper method to create a node
     *
     * @param id    Id of the node
     * @param label Label of the node
     * @param shape Shape of the node
     * @param group Group of the Node
     * @return JSONObject as a node
     */
    private static JSONObject createNode(String id, String label, String shape, int group) {
        try {
            JSONObject node = new JSONObject().put("id", id)
                    .put("label", label)
                    .put("shape", shape)
                    .put("group", group);

            return node;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Helper method to create a node
     *
     * @param id    Id of the node
     * @param label Label of the node
     * @param shape Shape of the node
     * @param color Color of the Node
     * @return JSONObject as a node
     */
    private static JSONObject createNode(String id, String label, String shape, String color) {
        try {
            JSONObject node = new JSONObject().put("id", id)
                    .put("label", label)
                    .put("shape", shape)
                    .put("color", color);

            return node;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Helper method to create a node
     *
     * @param id    Id of the node
     * @param label Label of the node
     * @param shape Shape of the node
     * @return JSONObject as a node
     */
    private static JSONObject createNode(String id, String label, String shape) {
        try {
            JSONObject node = new JSONObject().put("id", id)
                    .put("label", label)
                    .put("shape", shape);

            return node;
        } catch (JSONException e) {
            e.printStackTrace();
            return null;
        }
    }

    private static List<String> combineAndFlatten(List<Parameter> inputs, List<Output> outputs) {
        List<String> combined = new ArrayList<>();

        for (Parameter input : inputs) {
            combined.addAll(input.getTypes());
        }

        for (Output output : outputs) {
            combined.add(output.getKey());
        }

        return combined;
    }
}
