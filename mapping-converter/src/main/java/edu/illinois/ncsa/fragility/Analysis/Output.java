package edu.illinois.ncsa.fragility.Analysis;

import com.sun.org.apache.xerces.internal.dom.DeferredElementImpl;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;

public class Output {
    private String friendlyName;
    private String key;
    private String phylum;
    private String format;
    private String geom;
    private String guids;

    public Output(String friendlyName, String key, String phylum, String format, String geom, String guids) {
        this.friendlyName = friendlyName;
        this.key = key;
        this.phylum = phylum;
        this.format = format;
        this.geom = geom;
        this.guids = guids;
    }

    public String getFriendlyName() {
        return friendlyName;
    }

    public void setFriendlyName(String friendlyName) {
        this.friendlyName = friendlyName;
    }

    public String getKey() {
        return key;
    }

    public void setKey(String key) {
        this.key = key;
    }

    public String getPhylum() {
        return phylum;
    }

    public void setPhylum(String phylum) {
        this.phylum = phylum;
    }

    public String getFormat() {
        return format;
    }

    public void setFormat(String format) {
        this.format = format;
    }

    public String getGeom() {
        return geom;
    }

    public void setGeom(String geom) {
        this.geom = geom;
    }

    public String getGuids() {
        return guids;
    }

    public void setGuids(String guids) {
        this.guids = guids;
    }

    public static ArrayList<Output> parseOutputs(NodeList outputNodes) {
        ArrayList<Output> outputs = new ArrayList<>();

        for (int i = 0; i < outputNodes.getLength(); i++) {
            Node outputNode = outputNodes.item(i);
            if (outputNode.getNodeType() == Node.ELEMENT_NODE) {
                String friendlyName = ((DeferredElementImpl) outputNode).getAttribute("friendly-name");
                String key = ((DeferredElementImpl) outputNode).getAttribute("key");
                String phylum = ((DeferredElementImpl) outputNode).getAttribute("phylum");
                String format = ((DeferredElementImpl) outputNode).getAttribute("format");
                String geom = ((DeferredElementImpl) outputNode).getAttribute("geom");
                String guids = ((DeferredElementImpl) outputNode).getAttribute("guids");

                Output output = new Output(friendlyName, key, phylum, format, geom, guids);
                outputs.add(output);
            }
        }

        return outputs;
    }
}
