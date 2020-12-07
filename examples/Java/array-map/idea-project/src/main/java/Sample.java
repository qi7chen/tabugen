// Copyright (C) 2019-present prototyped.cn. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

import java.io.*;
import java.nio.file.*;
import java.util.*;
import com.alibaba.fastjson.JSON;
import org.apache.commons.csv.*;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVFormat;

public class Sample
{

    // read file to with CF lines
    public static String readFileContent(String filepath) {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(filepath))) {
            String line = null;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
                sb.append("\n"); // line break
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
        String content = readCsvFile("newbie_guide_define.csv");
        List<com.mycompany.csvconfig.NewbieGuideDefine> data = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            if (record.size() == 0)
                continue;
            com.mycompany.csvconfig.NewbieGuideDefine item = new com.mycompany.csvconfig.NewbieGuideDefine();
            item.parseFrom(record);
            data.add(item);
        }

        System.out.printf("load %d box\n", data.size());
        data.forEach((item)->{
            System.out.printf("%s %s %d\n", item.Name, item.Name, item.Goods.size());
        });
    }

    private static void testJson() {
        String filename = "src/main/resources/newbie_guide_define.json";
        String content = readFileContent(filename);
        List<com.mycompany.jsonconfig.NewbieGuideDefine> conflist = JSON.parseArray(content, com.mycompany.jsonconfig.NewbieGuideDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            com.mycompany.jsonconfig.NewbieGuideDefine item = conflist.get(i);
            System.out.printf("%s %s %d\n", item.Name, item.Name, item.Goods.size());
        }
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