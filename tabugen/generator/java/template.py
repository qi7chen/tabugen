# Copyright (C) 2018-present ichenq@outlook.com. All rights reserved.
# Distributed under the terms and conditions of the Apache License.
# See accompanying files LICENSE.


JAVA_MGR_CLASS_TEMPLATE = """

public class %s {
    final public static String TABULAR_CSV_SEP = "%s";     // CSV field separator
    final public static String TABULAR_CSV_QUOTE = "%s";   // CSV field quote
    
    final public static String TABULAR_ARRAY_DELIM = "%s";      // array item delimiter
    final public static String TABULAR_MAP_DELIM1 = "%s";       // map item delimiter
    final public static String TABULAR_MAP_DELIM2 = "%s";       // map key-value delimiter
    
    // `Boolean.parseBoolean()` only detects "true"
    public static boolean parseBool(String text) {
        if (text.isEmpty()) {
            return false;
        }        
        return text.equals("1") ||
                text.equalsIgnoreCase("Y") ||
                text.equalsIgnoreCase("ON") ||
                text.equalsIgnoreCase("True");
    }
"""
