/**
 * boilerpipe
 *
 * Copyright (c) 2009 Christian Kohlschütter
 *
 * The author licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package de.l3s.boilerpipe.demo;

import java.net.URL;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintStream;
import java.io.Writer;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import de.l3s.boilerpipe.extractors.ArticleExtractor;

/**
 * Demonstrates how to use Boilerpipe to get the main content as plain text.
 * Note: In real-world cases, you'd probably want to download the file first using a fault-tolerant crawler.
 * 
 * @author Christian Kohlschütter
 * @author Jason Bolton as well!
 * @see HTMLHighlightDemo if you need HTML as well.
 */

// NOTE: args[0] is input directory of html
//       args[1] is output for JSON

public class DocumentProcessor {
    public static void main(final String[] args) throws Exception {
        // args[0] is main directory with the query subdirectories
        // put all the query directories into an array
        File[] subDirectories = new File(args[0]).listFiles();
        String htmlFilePath = "";
        // keep track of documents processed
        // int documentsProcessed = 0;
        // TO DO: tidy this up, right now master directory is assumed to have sub directories for each query
        // which is weird to say the least
        // NEW: build up a JSON and save a JSON file
        DocumentJSONSet allDocs = new DocumentJSONSet() ;
        for (File subDir : subDirectories) {
            String subDirName = subDir.toString();
            // list of all the files for this query
            System.out.println(subDirName);
            File[] htmlFiles = new File(subDirName).listFiles();
            for (File htmlFile : htmlFiles) {
                // get the file path
                htmlFilePath = htmlFile.toString();
                URL url = new URL("file://"+htmlFilePath);
                // build readers to set everything to UTF-8
                BufferedReader in = new BufferedReader(new InputStreamReader(url.openStream(),"UTF-8"));
                PrintStream out = new PrintStream(System.out, true, "UTF-8");
                // print out the YAML for this document
                // first get the url
                FileReader reader = new FileReader(htmlFilePath);
                BufferedReader bf = new BufferedReader(reader);
                // the html has the url as the 1st line
                String docURL = bf.readLine();
                // the html has the query as the second line
                String queryString = bf.readLine();
                bf.close();
                reader.close();
                // then output the yaml for the document
                System.out.println("---");
                // get the doc id from the file name
                String docId = htmlFilePath.split("/")[htmlFilePath.split("/").length-1];
                docId = docId.substring(0,docId.length()-5);
                System.out.println("document id: "+docId);
                //System.out.println("document id: "+documentsProcessed);
                System.out.println("url: "+docURL);
                System.out.println("query: "+queryString);
                System.out.println("text: ");
                //documentsProcessed++;
                String naturalText = ArticleExtractor.INSTANCE.getText(in);
                naturalText = naturalText.replace("---"," ");
                out.println(naturalText);
                // also make a DocumentJSON and put into the DocumentJSONSet
                DocumentJSON thisDoc = new DocumentJSON();
                thisDoc.name = docId;
                //thisDoc.name = Integer.toString(documentsProcessed);
                thisDoc.provenance = docURL;
                thisDoc.pubdate = "";
                thisDoc.description = "this document found with following query: "+queryString;
                thisDoc.corpus = "gun control - general web";
                thisDoc.type = "web document";
                thisDoc.size = 0;
                thisDoc.text = naturalText;
                // add to overall set of documents
                allDocs.listOfDocs.add(thisDoc);
            }
        }

        // Also try other extractors!
//        System.out.println(DefaultExtractor.INSTANCE.getText(url));
//       System.out.println(CommonExtractors.CANOLA_EXTRACTOR.getText(url));
//       output the JSON to file
        Gson finalGSON = new Gson();
        String outputJSON = finalGSON.toJson(allDocs);
        try {
            Writer writer = new BufferedWriter(new OutputStreamWriter(
                        new FileOutputStream(args[1]),"UTF-8"));
            writer.write(outputJSON);
            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
