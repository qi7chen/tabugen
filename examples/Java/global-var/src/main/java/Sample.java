// Copyright (C) 2019-present prototyped.cn. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

import java.io.*;
import java.nio.file.*;
import java.util.*;
import com.alibaba.fastjson.JSON;
import com.mycompany.csvconfig.GlobalPropertyDefine;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class Sample
{
    final public static String LF = "\n"; // line feed

    // read file to with CF lines
    public static String readFileContent(String filepath) {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line = null;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
                sb.append(LF); // line break
            }
        } catch(IOException ex) {
            System.err.println(ex.getMessage());
            ex.printStackTrace();
        }
        return sb.toString();
    }

    public static String readCsvFile(String key) {
        String filepath = String.format("src/main/resources/%s", key);
        return readFileContent(filepath);
    }

    private static void testCsv() throws IOException {
        String content = readCsvFile("global_property_define.csv");
        List<CSVRecord> records = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            records.add(record);
        }
        GlobalPropertyDefine instance = new GlobalPropertyDefine();
        instance.parseFrom(records);

        System.out.println(JSON.toJSONString(instance));
    }

    private static void testJson() {
        String filename = "src/main/resources/global_property_define.json";
        String content = readFileContent(filename);
        com.mycompany.jsonconfig.GlobalPropertyDefine obj = JSON.parseObject(content, com.mycompany.jsonconfig.GlobalPropertyDefine.class);
        System.out.println(JSON.toJSONString(obj));
    }

    public static void main(String[] args) {
        try {
            Path currentRelativePath = Paths.get("");
            String s = currentRelativePath.toAbsolutePath().toString();
            System.out.println("Current working path is: " + s);

            System.out.println("run csv case");
            testCsv();

            System.out.println("run json case");
            testJson();
        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
}