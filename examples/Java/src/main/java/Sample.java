// Copyright (C) 2019-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

import java.io.*;
import java.nio.file.*;
import java.util.*;
import com.alibaba.fastjson.JSON;
import org.apache.commons.csv.*;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVFormat;
import com.pdfun.config.*;

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

    private static void testGuideCsvConfig() throws IOException {
        String content = readCsvFile("newbie_guide_define.csv");
        List<NewbieGuideDefine> data = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            if (record.size() == 0)
                continue;
            NewbieGuideDefine item = new NewbieGuideDefine();
            item.parseFrom(record);
            data.add(item);
        }

        System.out.printf("load %d box\n", data.size());
        data.forEach((item)->{
            System.out.println(JSON.toJSONString(item));
        });
    }

    private static void testGuideJsonConfig() {
        String filename = "src/main/resources/newbie_guide_define.json";
        String content = readFileContent(filename);
        List<NewbieGuideDefine> conflist = JSON.parseArray(content, NewbieGuideDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            NewbieGuideDefine item = conflist.get(i);
            System.out.println(JSON.toJSONString(item));
        }
    }

    private static void testSoldierCsvConfig() throws IOException {
        String content = readCsvFile("soldier_property_define.csv");
        List<SoldierPropertyDefine> data = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            if (record.size() == 0)
                continue;
            SoldierPropertyDefine item = new SoldierPropertyDefine();
            item.parseFrom(record);
            data.add(item);
        }

        System.out.printf("load %d soldier\n", data.size());
        data.forEach((item)->{
            System.out.println(JSON.toJSONString(item));
        });
    }

    private static void testSoldierJsonConfig() {
        String filename = "src/main/resources/soldier_property_define.json";
        String content = readFileContent(filename);
        List<SoldierPropertyDefine> conflist = JSON.parseArray(content, SoldierPropertyDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            SoldierPropertyDefine item = conflist.get(i);
            System.out.println(JSON.toJSONString(item));
        }
    }

    private static void testGlobalCsvConfig() throws IOException {
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

    private static void testGlobalJsonConfig() {
        String filename = "src/main/resources/global_property_define.json";
        String content = readFileContent(filename);
        GlobalPropertyDefine obj = JSON.parseObject(content, GlobalPropertyDefine.class);
        System.out.println(JSON.toJSONString(obj));
    }

    private static void testBoxCsvConfig() throws IOException {
        String content = readCsvFile("box_probability_define.csv");
        List<BoxProbabilityDefine> data = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            if (record.size() == 0)
                continue;
            BoxProbabilityDefine item = new BoxProbabilityDefine();
            item.parseFrom(record);
            data.add(item);
        }
        System.out.printf("load %d box\n", data.size());
        data.forEach((item)->{
            System.out.println(JSON.toJSONString(item));
        });
    }

    private static void testBoxJsonConfig() {
        String filename = "src/main/resources/box_probability_define.json";
        String content = readFileContent(filename);
        List<BoxProbabilityDefine> conflist = JSON.parseArray(content, BoxProbabilityDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            BoxProbabilityDefine item = conflist.get(i);
            System.out.println(JSON.toJSONString(item));
        }
    }

    public static void main(String[] args) {
        try {
            Path currentRelativePath = Paths.get("");
            String s = currentRelativePath.toAbsolutePath().toString();
            System.out.println("Current working path is: " + s);

            System.out.println("run csv case");
            testGuideCsvConfig();
            testSoldierCsvConfig();
            testGlobalCsvConfig();
            testBoxCsvConfig();

            System.out.println("run json case");
            testGuideJsonConfig();
            testSoldierJsonConfig();
            testGlobalJsonConfig();
            testBoxJsonConfig();
        }
        catch(Exception ex) {
            ex.printStackTrace();
        }
    }
}