package edu.berkeley.icsi.metanet.metalookup;

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

public class XMLParser {
	
	static final String LU = "lu";
	static final String LEXUNIT = "name";
	static final String NAME = "frameName";
	
	public HashMap<String, Set<String>> parseDocument(String luDoc) throws IOException {
		//List<Frame> frames = new ArrayList<Frame>();
		HashMap<String, Set<String>> frames = new HashMap<String, Set<String>>();
		try {
			XMLInputFactory inputFactory = XMLInputFactory.newInstance();
			URL file = new URL(luDoc);
			InputStream in = file.openStream();
			XMLEventReader eventReader = inputFactory.createXMLEventReader(in);
			
			Frame frame = null;
			
			while (eventReader.hasNext()) {
				XMLEvent event = eventReader.nextEvent();
				
				if (event.isStartElement()) {
					StartElement startElement = event.asStartElement();
					
					if (startElement.getName().getLocalPart() == (LU)) {
						frame = new Frame();
						@SuppressWarnings("unchecked")
						Iterator<Attribute> attributes = startElement.getAttributes();
						
						while (attributes.hasNext()) {
							Attribute attribute = attributes.next();
							if (attribute.getName().toString().equals(LEXUNIT)) {
								frame.setLexicalUnit(attribute.getValue());
							} else if (attribute.getName().toString().equals(NAME)) {
								frame.setName(attribute.getValue());
							}
						}
					}
					
				}
				
				if (event.isEndElement()) {
					EndElement endElement = event.asEndElement();
					if (endElement.getName().getLocalPart() == (LU)) {
						if (frames.containsKey(frame.getLexicalUnit())) {
							Set<String> vals = frames.get(frame.getLexicalUnit());
							vals.add(frame.getName());
							frames.put(frame.getLexicalUnit(), vals);
						} else {
							Set<String> vals = new HashSet<String>();
							vals.add(frame.getName());
							frames.put(frame.getLexicalUnit(), vals);
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
