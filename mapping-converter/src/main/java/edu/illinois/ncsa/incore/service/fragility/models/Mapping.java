package edu.illinois.ncsa.incore.service.fragility.models;

import edu.illinois.ncsa.mapping.PropertyMatch;

import java.util.*;
import java.util.Map.Entry;

public class Mapping {
    public Map<String, String> legacyEntry = new HashMap<>();
    public Map<String, String> entry = new HashMap<>();
    public List<List<String>> rules = new ArrayList<>();

    public Mapping(List<FragilitySet> fragilitySets, PropertyMatch propertyMatch) {
        // no need to clone, as we will be serializing the values
        this.legacyEntry = propertyMatch.getMap();
        this.rules = propertyMatch.getRules();

        for (Entry<String, String> mappingEntry : legacyEntry.entrySet()) {
            String fragilityId = mappingEntry.getValue();
            Optional<FragilitySet> fragilityMatch = fragilitySets.stream().filter(
                    fragility -> fragility.legacyId.equalsIgnoreCase(fragilityId)).findFirst();

            if (fragilityMatch.isPresent()) {
                String fragilityMongoId = fragilityMatch.get().mongoId.toHexString();
                this.entry.put(mappingEntry.getKey(), fragilityMongoId);
            } else {
                System.out.println("Could not find fragility match for fragilityId: " + fragilityId);
            }
        }
    }
}
