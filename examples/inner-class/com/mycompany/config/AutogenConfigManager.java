package com.mycompany.config;

import java.util.*;
import java.io.*;

public class AutogenConfigManager {

    // load file content to lines
    public static String[] readFileToTextLines(String filepath) {
        ArrayList<String> lines = new ArrayList<String>();
        try {
            File fin = new File(filepath);
            BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(fin), "UTF-8"));
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
            reader.close();
        } catch(IOException ex) {
            System.err.println(ex.getMessage());
        }
        return lines.toArray(new String[lines.size()]);
    }

    // parse text to boolean value
    public static boolean parseBool(String text) {
        if (!text.isEmpty()) {
            return text.equals("1") || text.equalsIgnoreCase("on") ||
                text.equalsIgnoreCase("yes")  || text.equalsIgnoreCase("true");
        }
        return false;
    }

    public static void loadAllConfig() {
        BoxProbabilityDefine.loadFromFile("csv/boxprobabilitydefine.csv");
    }
}
