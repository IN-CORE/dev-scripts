package edu.illinois.ncsa.glossary;

import org.wikidata.wdtk.datamodel.helpers.Datamodel;
import org.wikidata.wdtk.datamodel.helpers.ItemDocumentBuilder;
import org.wikidata.wdtk.datamodel.helpers.StatementBuilder;
import org.wikidata.wdtk.datamodel.interfaces.*;
import org.wikidata.wdtk.wikibaseapi.ApiConnection;
import org.wikidata.wdtk.wikibaseapi.LoginFailedException;
import org.wikidata.wdtk.wikibaseapi.WikibaseDataEditor;
import org.wikidata.wdtk.wikibaseapi.WikibaseDataFetcher;
import org.wikidata.wdtk.wikibaseapi.apierrors.MediaWikiApiErrorException;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;

public class Main {

    public static void main(String[] args) throws IOException, LoginFailedException, MediaWikiApiErrorException {
        // Parse Text File
        String filepath = "resources/terms.txt";
        List<String> terms = readFileIntoList(filepath);

        String baseURL = "https://resilience-glossary.ncsa.illinois.edu/mediawiki/api.php";

        ApiConnection connection = new ApiConnection(baseURL);
        WikibaseDataFetcher fetcher = new WikibaseDataFetcher(connection, baseURL);

        connection.login("Admin", "PASSWORD IN LASTPASS");
        WikibaseDataEditor editor = new WikibaseDataEditor(connection, baseURL);


        PropertyDocument propertyDocument = (PropertyDocument) fetcher.getEntityDocument("P3");

        for (String term : terms) {


            ItemIdValue noid = ItemIdValue.NULL;
            ItemDocument newTerm = ItemDocumentBuilder.forItemId(noid)
                                                      .withLabel(term, "en")
                                                      .build();

            ItemDocument newDocument = editor.createItemDocument(newTerm, "Created from Seeder Tool");

        }
    }

    public static List<String> readFileIntoList(String file) {
        List<String> lines = Collections.emptyList();
        try {
            lines = Files.readAllLines(Paths.get(file), StandardCharsets.UTF_8);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return lines;
    }
}
