package edu.berkeley.icsi.metanet.lmtocmlinker;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;
import javax.xml.stream.XMLEventReader;
import javax.xml.stream.XMLInputFactory;
import javax.xml.stream.XMLStreamException;
import javax.xml.stream.events.Attribute;
import javax.xml.stream.events.EndElement;
import javax.xml.stream.events.StartElement;
import javax.xml.stream.events.XMLEvent;

public class FrameNetLUIndexParser {

    static final String LU = "lu";
    static final String LEXUNIT = "name";
    static final String FRAME = "frameName";

    static final String localfile = "/Users/jhong/Desktop/luIndex.xml";
    private static final String FRAMENETURL = "https://framenet2.icsi.berkeley.edu/fnReports/data/luIndex.xml";
    
    /**
     * Takes a FrameNet LU Index document URL and generates a HashMap
     * that maps Lemmas to a set of Frames, e.g. "push.v", ["Cause_motion", etc]
     * 
     * @param URL string to FrameNet LU Index XML
     * @return HashMap from lemmas to sets of frame names
     * @throws IOException 
     */
    public HashMap<String, Set<String>> getLU2FrameMap() throws IOException {

        HashMap<String, Set<String>> frames = new HashMap<String, Set<String>>();
        try {
            XMLInputFactory inputFactory = XMLInputFactory.newInstance();
            URL file = new URL(FRAMENETURL);
//            FileInputStream in = new FileInputStream(localfile);
            
            InputStream in = file.openStream();
            
            XMLEventReader eventReader = inputFactory.createXMLEventReader(in);

            String luname = null;
            String framename = null;

            while (eventReader.hasNext()) {
                XMLEvent event = eventReader.nextEvent();

                
                if (event.isStartElement()) {
                    StartElement startElement = event.asStartElement();

                    if (startElement.getName().getLocalPart().equals(LU)) {
                        @SuppressWarnings("unchecked")
                        Iterator<Attribute> attributes = startElement.getAttributes();

                        // read out luname and framenet per <lu> element
                        while (attributes.hasNext()) {
                            Attribute attribute = attributes.next();
                            if (attribute.getName().toString().equals(LEXUNIT)) {
                                luname = attribute.getValue();
                            } else if (attribute.getName().toString().equals(FRAME)) {
                                framename = attribute.getValue();
                            }
                        }
                    }

                }
                
                // at the close of the <lu> element, update the frames HashMap
                if (event.isEndElement()) {
                    EndElement endElement = event.asEndElement();
                    if (endElement.getName().getLocalPart().equals(LU)) {
                        if (frames.containsKey(luname)) {
                            frames.get(luname).add(framename);
                        } else {
                            Set<String> vals = new HashSet<String>();
                            vals.add(framename);
                            frames.put(luname, vals);
                        }
                    }
                }
            }

        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (XMLStreamException e) {
            e.printStackTrace();
        }
        return frames;
    }
}
