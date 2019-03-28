import java.io.*;
import java.util.*;
import com.mycompany.config.*;

public class Sample
{
    public static String readFileContent(String filepath) {
        filepath = String.format("csv/%s", filepath);
        StringBuilder sb = new StringBuilder();
        try {
            BufferedReader reader = new BufferedReader(new FileReader(filepath));
            String line = null;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
                sb.append('\n'); // line break
            }
            reader.close();
        } catch(IOException ex) {
            System.err.println(ex.getMessage());
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        AutogenConfigManager.reader = (filepath) -> readFileContent(filepath);
        AutogenConfigManager.loadAllConfig();
        ArrayList<BoxProbabilityDefine> boxdata = BoxProbabilityDefine.getData();
        System.out.printf("load %d box", boxdata.size());
    }
}