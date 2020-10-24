# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


JAVA_MGR_CLASS_TEMPLATE = """

import java.io.*;
import java.util.function.Function;
import org.apache.commons.io.FileUtils;

public class %s {
    final public static String CSV_SEP = "%s";      // CSV field seperator
    final public static String CSV_QUOTE = "%s";  // CSV field quote
    
    final public static String TAKSI_ARRAY_DELIM = "%s";
    final public static String TAKSI_MAP_DELIM1 = "%s";
    final public static String TAKSI_MAP_DELIM2 = "%s";
    
    // parse text to boolean value
    public static boolean parseBool(String text) {
        if (!text.isEmpty()) {
            return text.equals("1") ||
                    text.equalsIgnoreCase("y") ||
                    text.equalsIgnoreCase("on") ||
                    text.equalsIgnoreCase("yes")  ||
                    text.equalsIgnoreCase("true");
        }
        return false;
    }

    public static String readFileContent(String filepath) throws IOException {
        File file = new File(filepath);
        return FileUtils.readFileToString(file, "%s");
    }

    // You can set your own file reader here
    public static Function<String, String> reader;
"""

JAVA_LOAD_ALL_METHOD_TEMPLATE = """
    public static void loadAllConfig() throws IOException {
        if (reader == null) {
            reader = reader = (filepath) -> {
                try {
                    return readFileContent(filepath);
                } catch(IOException e) {
                    throw new UncheckedIOException(e);
                }
            };
        }
%s
    }
"""

JAVA_KV_LOAD_FUNC_TEMPLATE = """
    public static void loadFrom(String content) throws IOException
    {
        List<CSVRecord> records = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            records.add(record);
        }
        %s instance = new %s();
        instance.parseFrom(records);
        instance_ = instance;
    }
"""

JAVA_LOAD_FUNC_TEMPLATE = """
    public static void loadFrom(String content) throws IOException
    {
        List<%s> data = new ArrayList<>();
        CSVParser parser = CSVParser.parse(content, CSVFormat.EXCEL);
        for (CSVRecord record : parser)
        {
            if (record.size() == 0)
                continue;
            %s item = new %s();
            item.parseFrom(record);
            data.add(item);
        }
        data_ = data;
    }
"""

JAVA_GET_METHOD_TEMPLATE = """
    // get an item by key
    public static %s getItem(%s)
    {
        for (%s item : data_)
        {
            if (%s)
            {
                return item;
            }
        }
        return null;
    }
"""

JAVA_RANGE_METHOD_TEMPLATE = """
    // get a range of items by key
    public static ArrayList<%s> getRange(%s)
    {
        ArrayList<%s> range = new ArrayList<>();
        for (%s item : data_)
        {
            if (%s)
            {
                range.add(item);
            }
        }
       return range;
    }
"""