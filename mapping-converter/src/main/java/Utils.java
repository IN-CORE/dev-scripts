import com.google.common.io.Files;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Utils {

    /**
     * Retrieves the .xml file under gisMetadata
     *
     * @param schemaPathString Path to the schema file (.xsd) file
     * @return Full path to the .xml metadata file
     */
    public static String getMetaDataPath(String schemaPathString) {
        Path schemaPath = Paths.get(schemaPathString);
        String filename = schemaPath.getFileName().toString();

        Path metadataFilePath = Paths.get(schemaPath.getParent().getParent() + "/gisMetadata/" + filename.replace(".xsd", ".xml"));

        return metadataFilePath.toString();
    }

    public static Map<String, String> getPluginProperties(String pluginPropertiesPath) {
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
