package edu.illinois.ncsa.incore.service.fragility.models;

import edu.illinois.ncsa.fragility.Fragility.JaxPModel.FragilityDataset;
import edu.illinois.ncsa.fragility.Replacer;
import edu.illinois.ncsa.tools.common.exceptions.NoSuchElementException;
import org.bson.types.ObjectId;
import org.mongodb.morphia.annotations.Id;
import org.mongodb.morphia.annotations.Property;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class FragilitySet {
    @Id
    public ObjectId mongoId;

    public String legacyId; // base

    public String hazardType;
    public String inventoryType;

    public List<String> authors = new ArrayList<String>(); // base
    public PaperReference paperReference;
    public String description; // base

    public String resultUnit;
    public String resultType;
    public String demandType;
    public String demandUnits;

    public FragilitySet() {
    }

    public FragilitySet(String id, String description, List<String> authors, PaperReference reference, String hazardType,
                        String inventoryType) {
        this.legacyId = id;
        this.description = description;
        this.authors = authors;
        this.paperReference = reference;
        this.hazardType = hazardType;
        this.inventoryType = inventoryType;
    }

    public List<FragilityCurve> fragilityCurves;

    public static List<FragilitySet> parse(String hazardType, String inventoryType,
                                           FragilityDataset dataset) throws NoSuchElementException {
        List<FragilitySet> sets = new ArrayList<>();

        List<FragilityDataset.FragilityDatasetSets.FragilitySet> fragilitySets = dataset.getFragilityDatasetSets().getFragilitySet();

        for (FragilityDataset.FragilityDatasetSets.FragilitySet fragilitySet : fragilitySets) {
            FragilityDataset.FragilityDatasetSets.FragilitySet.FragilitySetProperties properties = fragilitySet.getFragilitySetProperties();
            FragilityDataset.FragilityDatasetSets.FragilitySet.FragilitySetLabels labels = fragilitySet.getFragilitySetLabels();
            FragilityDataset.FragilityDatasetSets.FragilitySet.FragilitySetFragilities curves = fragilitySet.getFragilitySetFragilities();

            String id = properties.getID();
            String authorStr = properties.getAuthor();
            String description = properties.getDescription();

            List<String> authors = new ArrayList<>();
            PaperReference reference = null;

            Replacer replacer = new Replacer();

            if (authorStr != null) {
                if (replacer.authorReplace.containsKey(authorStr.trim())) {
                    authors = replacer.authorReplace.get(authorStr.trim());
                } else {
                    authors = Arrays.asList(authorStr);
                }


                if (replacer.paperReplace.containsKey(authorStr.trim())) {
                    reference = replacer.paperReplace.get(authorStr.trim());
                }
            }

            FragilitySet createdSet = new FragilitySet(id, description, authors, reference, hazardType, inventoryType);
            createdSet.demandType = properties.getDemandType();
            createdSet.demandUnits = properties.getDemandUnits();

            if (properties.getResultType() != null) {
                createdSet.resultType = properties.getResultType();
            } else {
                createdSet.resultType = "Limit State";
            }

            createdSet.fragilityCurves = FragilityCurve.parseCurves(labels, curves);

            sets.add(createdSet);
        }

        return sets;
    }
}
