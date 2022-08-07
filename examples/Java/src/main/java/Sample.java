// Copyright (C) 2019-present ichenq@outlook.com. All rights reserved.
// Distributed under the terms and conditions of the Apache License.
// See accompanying files LICENSE.

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

import com.alibaba.fastjson.JSON;
import org.apache.commons.io.FileUtils;
import org.apache.commons.csv.*;
import com.pdfun.config.*;

public class Sample {
    public static ArrayList<Map<String, String>> ReadCSVRecords(String filename) throws IOException {
        ArrayList<Map<String, String>> records = new ArrayList<>();
        File file = new File(toFilePath(filename));
        List<String> header = null;
        CSVParser parser = CSVParser.parse(file, StandardCharsets.UTF_8, CSVFormat.EXCEL);
        for (CSVRecord record : parser) {
            List<String> row = record.toList();
            if (header == null) {
                header = row;
            } else {
                Map<String, String> rec = new HashMap<>();
                for (int i = 0; i < row.size(); i++)
                {
                    rec.put(header.get(i), row.get(i));
                }
                records.add(rec);
            }
        }
        return records;
    }

    public static Map<String, String> RecordsToDict(ArrayList<Map<String, String>> records) {
        Map<String, String> dict = new HashMap<>();
        for (Map<String, String> record : records) {
            dict.put(record.get("Key"), record.get("Value"));
        }
        return dict;
    }

    private static String toFilePath(String filename) {
        return String.format("../datasheet/res/%s", filename);
    }

    private static void testGuideCsvConfig() throws IOException {
        ArrayList<Map<String, String>> records = ReadCSVRecords("newbie_guide_define.csv");
        for (Map<String, String> record : records) {
            NewbieGuideDefine val = new NewbieGuideDefine();
            val.parseFrom(record);
            String content = JSON.toJSONString(val);
            System.out.println(content);
        }
        System.out.printf("load %d box\n", records.size());
    }

    private static void testGuideJsonConfig() throws IOException {
        File file = new File(toFilePath("newbie_guide_define.json"));
        String content = FileUtils.readFileToString(file, StandardCharsets.UTF_8);
        List<NewbieGuideDefine> conflist = JSON.parseArray(content, NewbieGuideDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            NewbieGuideDefine item = conflist.get(i);
            System.out.println(JSON.toJSONString(item));
        }
    }

    private static void testSoldierCsvConfig() throws IOException {
        ArrayList<Map<String, String>> records = ReadCSVRecords("soldier_property_define.csv");
        for (Map<String, String> record : records) {
            SoldierPropertyDefine val = new SoldierPropertyDefine();
            val.parseFrom(record);
            String content = JSON.toJSONString(val);
            System.out.println(content);
        }
        System.out.printf("load %d soldier\n", records.size());
    }

    private static void testSoldierJsonConfig() throws IOException {
        File file = new File(toFilePath("soldier_property_define.json"));
        String content = FileUtils.readFileToString(file, StandardCharsets.UTF_8);
        List<SoldierPropertyDefine> conflist = JSON.parseArray(content, SoldierPropertyDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            SoldierPropertyDefine item = conflist.get(i);
            System.out.println(JSON.toJSONString(item));
        }
    }

    private static void testGlobalCsvConfig() throws IOException {
        ArrayList<Map<String, String>> records = ReadCSVRecords("global_property_define.csv");
        Map<String, String> dict = RecordsToDict(records);
        GlobalPropertyDefine instance = new GlobalPropertyDefine();
        instance.parseFrom(dict);
        String content = JSON.toJSONString(instance);
        System.out.println(content);
    }

    private static void testGlobalJsonConfig() throws IOException {
        File file = new File(toFilePath("global_property_define.json"));
        String content = FileUtils.readFileToString(file, StandardCharsets.UTF_8);
        GlobalPropertyDefine obj = JSON.parseObject(content, GlobalPropertyDefine.class);
        String text = JSON.toJSONString(obj);
        System.out.println(text);
    }

    private static void testBoxCsvConfig() throws IOException {
        ArrayList<Map<String, String>> records = ReadCSVRecords("box_probability_define.csv");
        for (Map<String, String> record : records) {
            SoldierPropertyDefine val = new SoldierPropertyDefine();
            val.parseFrom(record);
            String content = JSON.toJSONString(val);
            System.out.println(content);
        }
        System.out.printf("load %d box_probability\n", records.size());
    }

    private static void testBoxJsonConfig() throws IOException {
        File file = new File(toFilePath("box_probability_define.json"));
        String content = FileUtils.readFileToString(file, StandardCharsets.UTF_8);
        List<BoxProbabilityDefine> conflist = JSON.parseArray(content, BoxProbabilityDefine.class);
        for (int i = 0; i < conflist.size(); i++) {
            BoxProbabilityDefine item = conflist.get(i);
            String text = JSON.toJSONString(item);
            System.out.println(text);
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
        } catch (Exception ex) {
            ex.printStackTrace();
        }
    }
}
