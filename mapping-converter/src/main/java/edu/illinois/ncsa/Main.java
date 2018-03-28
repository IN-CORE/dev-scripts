package edu.illinois.ncsa;

import com.mongodb.MongoClient;
import edu.illinois.ncsa.fragility.Fragility.JaxPModel.FragilityDataset;
import edu.illinois.ncsa.fragility.Replacer;
import edu.illinois.ncsa.incore.service.fragility.models.FragilitySet;
import edu.illinois.ncsa.incore.service.fragility.models.MappingSet;
import edu.illinois.ncsa.mapping.MatchFilterMap;
import edu.illinois.ncsa.tools.common.exceptions.NoSuchElementException;
import org.apache.commons.io.FilenameUtils;
import org.mongodb.morphia.Datastore;
import org.mongodb.morphia.Morphia;

import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Unmarshaller;
import java.io.*;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Main {
    // public static void main(String[] args) throws Exception {
    //     URL url = Main.class.getClassLoader().getResource("Large Pipeline Fragility Mapping.xml");
    //     MatchFilterMap matchFilterMap = MatchFilterMap.loadMatchFilterMapFromUrl(url);
    //     MappingSet mappingSet = new MappingSet("test", new ArrayList<>(), matchFilterMap);
    //     MatchFilter test = mappingSet.mappings.get(0).getAsMatchFilter();
    //
    //
    //     int x = 0;
    // }

    public static void main(String[] args) throws Exception {
        // Save to MongoDB
        String dbName = "fragilitydb";
        String hostUri = "localhost";
        int port = 27017;

        MongoClient client = new MongoClient(hostUri, port);

        Set<Class> classesToMap = new HashSet<>();
        classesToMap.add(FragilitySet.class);
        classesToMap.add(MappingSet.class);

        Morphia morphia = new Morphia(classesToMap);

        Datastore datastore = morphia.createDatastore(client, dbName);

        String fragilityPath = "C:\\Users\\omar\\OneDrive for Business\\Fragilities and Mapping";
        File fragilityDirectory = new File(fragilityPath);

        for (File file : fragilityDirectory.listFiles()) {
            // inside each folder is a mapping and fragility
            if (file.isDirectory()) {
                // contains mapping and fragility files
                List<File> files = Arrays.asList(file.listFiles());

                File fragilityFile = files.stream().filter(f -> f.getName().startsWith("FRAG_")).findFirst().get();
                List<FragilitySet> fragilitySets = parseFragilitySet(fragilityFile);

                datastore.save(fragilitySets);

                // Save to database, get id?

                for (File datasetFile : files) {
                    if (datasetFile.getName().startsWith("MAP_")) {
                        String name = FilenameUtils.removeExtension(datasetFile.getName()).substring(4);
                        MatchFilterMap matchFilterMap = MatchFilterMap.loadMatchFilterMapFromUrl(datasetFile.toURL());
                        MappingSet mappingSet = new MappingSet(name, fragilitySets, matchFilterMap);

                        datastore.save(mappingSet);
                    }
                }
            }
        }
    }

    private static List<FragilitySet> parseFragilitySet(
            File file) throws UnsupportedEncodingException, FileNotFoundException, JAXBException, NoSuchElementException {
        String filename = FilenameUtils.removeExtension(file.getName());

        InputStream inputStream = new FileInputStream(file);
        Reader reader = new InputStreamReader(inputStream, "UTF-16");
        JAXBContext jaxbContext = JAXBContext.newInstance(FragilityDataset.class);

        Unmarshaller jaxbUnmarshaller = jaxbContext.createUnmarshaller();
        FragilityDataset dataset = (FragilityDataset) jaxbUnmarshaller.unmarshal(reader);

        Replacer replacer = new Replacer();

        String inventoryType = replacer.inventoryReplace.get(file.getName());
        String hazardType = replacer.hazardReplace.get(file.getName());

        List<FragilitySet> fragilitySet = FragilitySet.parse(hazardType, inventoryType, dataset);

        return fragilitySet;
    }
}
