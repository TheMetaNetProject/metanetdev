package edu.berkeley.icsi.metanet.wiki2owl;

import java.util.Arrays;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.StringEscapeUtils;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.logging.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.semanticweb.owlapi.model.AddAxiom;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLAxiom;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassAssertionAxiom;
import org.semanticweb.owlapi.model.OWLDataFactory;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLDataPropertyAssertionAxiom;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.model.PrefixManager;

/**
 * Class for parsing MetaWiki page format pages, and specifically the 
 * template calls that contain the metaphor and frame data.  
 *
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiTemplateParser {

    private static final Logger logger = Logger.getLogger("WikiTemplateParser");
    public static int STARTTEMPLATE = 1;
    public static int ENDTEMPLATE = 2;
    public static int VARIABLE = 3;
    public static int OTHER = 4;
    private static String LETTERS_ONLY_REGEXP = "[^\\p{L}\\p{N}]";
    private String pageName;
    private String pageType;
    private StringBuffer wiki;
    private OWLOntology repository;
    private OWLOntology ontology;
    private OWLOntologyManager owlman;
    private OWLDataFactory df;
    private String sourceFrame;
    private String targetFrame;
    private PrefixManager pm;
    private String ontoPrefix;
    private String dprefix;
    private static int INFERENCE_SUBSTRING_LENGTH = 30;
    private String lang = "en";
    private static Map<String,String> frameNamesRegexp = new HashMap<String,String>();
    private static Map<String,String> articlesRegexp = new HashMap<String,String>();

    static {
//        frameNamesRegexp.put("en","^([\\p{L} ]+) (IS|ARE) ([\\p{L} ]+)$");
        frameNamesRegexp.put("en","^(.+) (IS|ARE) (.+)$");
        articlesRegexp.put("en", "^(A|AN|THE) ");
        frameNamesRegexp.put("es","^(.+) (ES|SON) (.+)$");
        articlesRegexp.put("es", "^(UN|UNA|LA) ");
//        frameNamesRegexp.put("fa","^Metaphor:([\\p{L} ]+) (IS|ARE) ([\\p{L} ]+)$");
        
        frameNamesRegexp.put("ru","^(.+) (- ЭТО) (.+)$");
        articlesRegexp.put("ru", "^");
        frameNamesRegexp.put("test","^([\\p{L} ]+) (IS|ARE) ([\\p{L} ]+)$");
    }
    
    /*
     * Constructor:
     * - reads wiki (template) content as stringbuffer
     */
    public WikiTemplateParser(String pName, String wikitext, OWLOntology repo, PrefixManager prefman, OWLOntology onto, String pref) {
        this.pageName = pName;
        // This is a hack to get around {{!}} being used to represent | in the wiki
        // First: replace all instances of {{!}} with __MEDIAWIKI_VERTICAL_BAR__
        // And then later replace __MEDIAWIKI_VERTICAL_BAR__ with |
        //
        
        this.wiki = new StringBuffer(wikitext.replace("{{!}}", "__MEDIAWIKI_VERTICAL_BAR__"));
        this.ontology = onto;
        this.repository = repo;
        this.owlman = repo.getOWLOntologyManager();
        this.df = owlman.getOWLDataFactory();
        this.pm = prefman;
        this.ontoPrefix = pref + ":";
        this.dprefix = ":";

    }

    public void setLogLevel(Level level) {
        logger.setLevel(level);
    }

    /**
     * Method to set the language of the wiki.  This will be used later for
     * determining how to parse out frame names from metaphor names.  Note that
     * the member variable lang defaults to English.
     * 
     * @param s String: presently either en, es, fa, ru
     */
    public void setLanguage(String s) {
        lang = s;
    }
    
    /*
     * Returns unique URI for a role in a frame
     * 
     * @param frameName name of frame
     * @param roleJName name of role in frame
     * @return unique URI
     */
    private String getRoleId(String frameName, String roleName) {
        if (frameName.startsWith("Frame:")) {
            //do nothing
        } else {
            frameName = "Frame:" + frameName;
        }
        return "Role_" + (frameName + "_" + roleName).replaceAll(LETTERS_ONLY_REGEXP, "_");
    }

    /*
     * Returns unique identifier for use in URI
     * 
     * Checks whether the name of the frame is namespaced.  Unnamespaced
     * frame names are assumed to be manually entered.
     * 
     * @param frameName
     * @return unique URI
     */
    private String getFrameId(String frameName) {
        if (frameName.startsWith("Frame:")) {
            // do nothing
        } else {
            frameName = "Frame:" + frameName;
        }
        return frameName.replaceAll(LETTERS_ONLY_REGEXP, "_");
    }

    /*
     * Returns unique identifier for use in URI
     * 
     * Checks whether the name of the metaphor is namespaced.
     * 
     * @param metaphorName
     * @return unique URI
     */
    private String getMetaphorId(String metaphorName) {
        if (metaphorName.startsWith("Metaphor:")) {
            // do nothing
        } else {
            metaphorName = "Metaphor:" + metaphorName;
        }
        return metaphorName.replaceAll(LETTERS_ONLY_REGEXP, "_");
    }

    private String makeInferenceLabel(String content, int numchars) {
        int endpoint = Math.max(content.indexOf(" ", numchars), numchars);
        if (content.length() <= endpoint) {
            return content;
        } else {
            return content.substring(0, endpoint) + "...";
        }
    }

    private String makeInferenceLabel(String content) {
        return makeInferenceLabel(content, INFERENCE_SUBSTRING_LENGTH);
    }

    /*
     * Returns unique names for use in URI for named entities
     * 
     * @param type usually the name of the template or page
     * @name name name of frame, metaphor, or role
     * @return unique URI name
     */
    private String getIndividualName(String type, String name) {
        if (type.equals("Linguistic metaphor")) {
            //names of linguistic metaphors are all namespaced already
            return name.replaceAll(LETTERS_ONLY_REGEXP, "_");
        } else if (type.equals("Metaphor")) {
            return getMetaphorId(name);
        } else if (type.equals("Frame")) {
            return getFrameId(name);
        } else if (type.equals("Frame family") || type.equals("Metaphor family")) {
            return (type + "_" + name).replaceAll(LETTERS_ONLY_REGEXP, "_");
        } else if (type.equals("Role")) {
            // use pageName as frameName
            return getRoleId(pageName, name);
        } else if (type.equals("IARPASourceConcept") || type.equals("IARPATargetConcept") ||
        		type.equals("MetaRC") || type.equals("CxnMP")) {
        	// name is namespaced: IConcept:DISEASE, etc.
        	return name.replaceAll(LETTERS_ONLY_REGEXP, "_");
        }
        return null;
    }

    /*
     * Translates template names to ontological class names
     * 
     * @param tname template name
     * @return class name
     */
    private static String getClassFromTemplateName(String tname) {
        if (tname.equals("Metaphor")) {
            return "Metaphor";
        } else if (tname.equals("Frame")) {
            return "Frame";
        } else if (tname.equals("LUs")) {
            return "LexicalUnit";
        } else if (tname.equals("Metaphor family")) {
            return "MetaphorFamily";
        } else if (tname.equals("Frame family")) {
            return "FrameFamily";
        } else if (tname.equals("Linguistic metaphor")) {
            return "LinguisticMetaphor";
        } else if (tname.equals("CxnMP")) {
        	return "CxnPattern";
        } else if (tname.equals("MetaRC")) {
        	return "RelationalConfiguration";
        } else {
            // e.g. Example, ...
            return tname;
        }
    }

    private void setAnnotationProperty(OWLNamedIndividual ind, String variable, String val) {
        String prop;
        if (val == null) {
            return;
        }
        prop = WikiFieldMap.trans(pageType, variable);
        OWLAnnotationProperty annoProp;
        if (prop.equals("comment")) {
            annoProp = df.getRDFSComment();
        } else if (prop.equals("label")) {
            annoProp = df.getRDFSLabel();
        } else {
            annoProp = df.getOWLAnnotationProperty(ontoPrefix + prop, pm);
        }
        OWLAnnotation anno = df.getOWLAnnotation(annoProp, df.getOWLLiteral(val));
        OWLAxiom ax = df.getOWLAnnotationAssertionAxiom(ind.getIRI(), anno);
        owlman.applyChange(new AddAxiom(repository, ax));
    }

    /*
     * Private method for setting datatype properties.  Takes template variable
     * names and translates them to property names via WIKI2REP.  Also
     * detects whether property is functional or not and acts accordingly.
     * 
     */
    private void setDataProperty(OWLNamedIndividual ind, String variable, String val) {
        String prop;
        if (val == null) {
            logger.log(Level.WARNING, "Skipping property {0} on {1} because of null value.", new Object[]{variable, pageName});
            return;
        }
        prop = WikiFieldMap.trans(pageType, variable);
        if (prop == null) {
            logger.log(Level.WARNING, "Skipping datatype property {0} for {1}", new Object[]{variable, pageName});
            return;
        }
        // if it's an annotation property, then reroute to different method
        if (WikiFieldMap.isAnnotationProp(prop)) {
            setAnnotationProperty(ind, variable, val);
            return;
        }
        OWLDataProperty property = df.getOWLDataProperty(ontoPrefix + prop, pm);
        if (property == null) {
            logger.log(Level.SEVERE, "Error with property: {0}", prop);
        }

        if (property.isFunctional(ontology)) {
            // if functional (limited to 1) then set
            OWLDataPropertyAssertionAxiom dataPropAssertion =
                    df.getOWLDataPropertyAssertionAxiom(property, ind, val);
            owlman.addAxiom(repository, dataPropAssertion);
        } else {
            // if NOT functional, then add each value
            String[] vals = val.split(",");
            for (int i = 0; i < vals.length; i++) {
                String v = vals[i].trim();
                if (!v.isEmpty()) {
                    OWLDataPropertyAssertionAxiom dataPropAssertion =
                            df.getOWLDataPropertyAssertionAxiom(property, ind, v);
                    owlman.addAxiom(repository, dataPropAssertion);
                }
            }
        }
    }

    private void setObjectProperty(OWLNamedIndividual subj, String rel, OWLNamedIndividual obj) {
        String propertyName;

        //translate property name using WIKI2REP if mapping is there
        propertyName = WikiFieldMap.trans(pageType, rel);
        if (propertyName == null) {
            logger.log(Level.WARNING, "Skipping set object property {0} for {1}", new Object[]{rel, pageName});
            return;
        }

        OWLObjectProperty property = df.getOWLObjectProperty(ontoPrefix + propertyName, pm);
        if (property == null) {
            logger.log(Level.SEVERE, "Error with property: {0}", propertyName);
        }

        // what happens if the property is functional?  Does it replace an
        // existing Axiom?
        OWLAxiom objPropAxiom = df.getOWLObjectPropertyAssertionAxiom(property, subj, obj);
        owlman.addAxiom(repository, objPropAxiom);
    }

    /*
     * Safely (prevent duplication) creates individuals with unique names.
     * 
     * For use with classes that have a hasName property.  Namespaces in the
     * name parameter overrides the tName
     * 
     * @param tName template name
     * @param name  name of the individual (metaphor name, etc.)
     * @param indName name of the RDF individual (unique)
     */
    private OWLNamedIndividual safeCreateIndividual(String tName, String name, String indName) {
        OWLNamedIndividual ind;
        // check using indName of the individual already exists
        if (repository.containsIndividualInSignature(IRI.create(pm.getIRI("") + indName))) {
            ind = df.getOWLNamedIndividual(dprefix + indName, pm);
        } else {
            //doesn't exist: create it

            // namespaces override the tName
        	if (name.startsWith("Frame:")) {
                tName = "Frame";
            } else if (name.startsWith("Metaphor:")) {
                tName = "Metaphor";
            } else if (name.startsWith("Linguistic metaphor:")) {
                tName = "Linguistic metaphor";
            }

            OWLClass c = df.getOWLClass(ontoPrefix + getClassFromTemplateName(tName), pm);
            ind = df.getOWLNamedIndividual(dprefix + indName, pm);
            OWLClassAssertionAxiom classAssertion = df.getOWLClassAssertionAxiom(c, ind);
            owlman.addAxiom(repository, classAssertion);
            if (WikiFieldMap.hasName(tName)) {
                name = name.replaceFirst("^[^:]+:", ""); // lop off namespace
                if (tName.equals("IARPASourceConcept") || tName.equals("IARPATargetConcept")) {
                	name = name.replaceAll(" ","_");
                }
                setDataProperty(ind, "hasName", name);
                setDataProperty(ind, "label", name);  // the display parameter
            }
        }
        return ind;
    }

    /*
     * Safely (prevent duplication) create roles.
     * 
     * This is a version of safeCreateIndividual but specifically for roles.
     * 
     * @param frameName    name of frame
     * @param roleName      name of role
     */
    private OWLNamedIndividual safeCreateRole(String frameName, String roleName) {
        OWLNamedIndividual ind;
        String roleId = getRoleId(frameName, roleName);
        if (repository.containsIndividualInSignature(IRI.create(pm.getIRI("") + roleId))) {
            ind = df.getOWLNamedIndividual(dprefix + roleId, pm);
        } else {
            OWLClass c = df.getOWLClass(ontoPrefix + "Role", pm);
            ind = df.getOWLNamedIndividual(dprefix + roleId, pm);
            OWLClassAssertionAxiom classAssertion = df.getOWLClassAssertionAxiom(c, ind);
            owlman.addAxiom(repository, classAssertion);
            setDataProperty(ind, "hasName", roleName);
            // lop off namespace from frameName
            frameName = frameName.replaceFirst("^[^:]+:", "");
            setDataProperty(ind, "label", frameName + "." + roleName);
        }
        return ind;
    }

    /*
     * Safely (prevent duplication) creates individuals with unique URIs
     * 
     * This is for entities that do not have names like Examples, Inferences,
     * etc. which are usually numbered.
     * 
     * @param tName name of the template
     * @return the new individual
     */
    private OWLNamedIndividual createIndividual(String tName) {
        String cName = getClassFromTemplateName(tName);
        String indName = WikiFieldMap.getInstanceName(cName);
        logger.log(Level.INFO, "Creating:{0}", indName);
        OWLClass c = df.getOWLClass(ontoPrefix + cName, pm);
        OWLNamedIndividual ind = df.getOWLNamedIndividual(dprefix + indName, pm);
        OWLClassAssertionAxiom classAssertion = df.getOWLClassAssertionAxiom(c, ind);
        owlman.addAxiom(repository, classAssertion);
        return ind;
    }

    /*
     * Safely (prevent duplication) for other kinds of individuals
     * 
     * Create individuals on the basis of template name and the
     * variable/value pairings given in the template.  Used for roles,
     * examples, etc.
     * 
     * @param tName template name
     * @param temp template data with variables as keys
     * @return new individual
     * 
     */
    private OWLNamedIndividual safeCreateIndividual(String tName, Map<String, String> temp) {
        OWLNamedIndividual ind;
        if (tName.equals("Role")) {
            ind = safeCreateRole(temp.get("frame"), temp.get("Role.Name"));
            logger.log(Level.INFO, "===created Role:({0})", temp.get("Role.Name"));
        } else if (tName.equals("Inference")) {
            if (!temp.containsKey("Inference.Description")
                    || temp.get("Inference.Description").isEmpty()) {
                return null;
            }
            ind = createIndividual(tName);
            setDataProperty(ind, "label", makeInferenceLabel(temp.get("Inference.Description")));
        } else if (tName.equals("Example")) {
            if (!temp.containsKey("Example.Text")
                    || temp.get("Example.Text").isEmpty()) {
                return null;
            }
            ind = createIndividual(tName);
            setDataProperty(ind, "label", makeInferenceLabel(temp.get("Example.Text")));
        } else {
            // for now: just create for other types
            logger.log(Level.INFO, "===creating {0}", tName);
            ind = createIndividual(tName);
        }
        return ind;
    }

    private void parseSubtemplate(OWLNamedIndividual subj, Map<String, String> subtemp) {
        OWLNamedIndividual ind;
        // special frame subtemplates
        if (subtemp.get("type").equals("Related frame")) {
            String framerelprop = WikiFieldMap.transframerel(subtemp.get("Related frame.Relation type"));
            if (framerelprop != null && subtemp.containsKey("Related frame.Name")) {
                OWLNamedIndividual rs = safeCreateIndividual("Frame", subtemp.get("Related frame.Name"), getFrameId(subtemp.get("Related frame.Name")));
                setObjectProperty(subj, framerelprop, rs);
            }
            return;
        }
        if (subtemp.get("type").equals("Linked frame")) {
        	if (subtemp.containsKey("Frame name")) {
        		OWLNamedIndividual rs = safeCreateIndividual("Frame", subtemp.get("Frame name"), getFrameId(subtemp.get("Frame name")));
        		setObjectProperty(subj,"isLinkedToFromFrame", rs);
        	}
        	return;
        }
        if (subtemp.get("type").equals("Blacklist source frames")) {
        	if (subtemp.containsKey("BlacklistSourceFrame")) {
        		OWLNamedIndividual rs = safeCreateIndividual("Frame", subtemp.get("BlacklistSourceFrame"), getFrameId(subtemp.get("BlacklistSourceFrame")));
        		setObjectProperty(subj,"hasBlacklistSourceFrame", rs);
        	}
        	return;
        }
        if (subtemp.get("type").equals("Blacklist source frame families")) {
        	if (subtemp.containsKey("BlacklistSourceFrameFamily")) {
        		OWLNamedIndividual rs = safeCreateIndividual("Frame family", subtemp.get("BlacklistSourceFrameFamily"), getFrameId(subtemp.get("BlacklistSourceFrameFamily")));
        		setObjectProperty(subj,"hasBlacklistSourceFrameFamily", rs);
        	}
        	return;
        }
        if (subtemp.get("type").equals("Blacklist target LUs") ||
        		subtemp.get("type").equals("Whitelist target LUs") ||
        		subtemp.get("type").equals("Blacklist source LUs")) {
        	for (Iterator<String> it = subtemp.keySet().iterator(); it.hasNext();) {
                String key = it.next();
                if (key.equals("frame") || key.equals("type") || key.equals("metaphor")) {
                    continue;
                }
                setDataProperty(subj, key, subtemp.get(key));
            }
        	return;
        }
        if (subtemp.get("type").equals("Binding")) {
            // report bindings to nowhere
            if (subtemp.get("Binding.Local role")==null
                    || subtemp.get("Binding.Bound role")==null) {
                logger.log(Level.SEVERE, "Error: one or both bound roles are null for binding in {0}", pageName);
                return;
            }
            ind = createIndividual("Binding");
            OWLNamedIndividual r1 = safeCreateRole(subtemp.get("frame"), subtemp.get("Binding.Local role"));
            String[] boundrole = subtemp.get("Binding.Bound role").split("[.]");
            if (boundrole.length == 1) {
                boundrole = new String[2];
                boundrole[0] = subtemp.get("frame");
                boundrole[1] = subtemp.get("Binding.Bound role");
            }
            OWLNamedIndividual r2 = safeCreateRole(boundrole[0], boundrole[1]);
            setObjectProperty(ind, "Binding.Local role", r1);
            setObjectProperty(ind, "Binding.Bound role", r2);
            setDataProperty(ind, "label", subtemp.get("frame") + "." + subtemp.get("Binding.Local role") + "=" + subtemp.get("Binding.Bound role"));
            setObjectProperty(subj, "Binding", ind);
            return;
        }
        // special metaphor subtemplates
        if (subtemp.get("type").equals("Related metaphor")) {
            String metarelprop = WikiFieldMap.transmetarel(subtemp.get("Related metaphor.Relation type"));
            if (metarelprop == null) {
                logger.log(Level.WARNING, "Unmapped metaphor relation ''{0}'' for {1}", new Object[]{subtemp.get("Related metaphor.Relation type"), pageName});
                return;
            }
            if (metarelprop != null && subtemp.containsKey("Related metaphor.Name")) {
                OWLNamedIndividual rm = safeCreateIndividual("Metaphor", subtemp.get("Related metaphor.Name"), getMetaphorId(subtemp.get("Related metaphor.Name")));
                setObjectProperty(subj, metarelprop, rm);
            }
            return;
        }
        if (subtemp.get("type").equals("Entailment")) {
            if (sourceFrame == null || targetFrame == null) {
                logger.log(Level.SEVERE, "Error: metaphor {0} is missing target/frame.  Cannot create entailments.", pageName);
                return;
            }
            if (subtemp.get("Entailment.Source inference") == null
                    || subtemp.get("Entailment.Target entailment") == null) {
                logger.log(Level.SEVERE, "Error: skipping null inferences/entailments on {0}", pageName);
                return;
            }
            ind = createIndividual("Entailment");
            OWLNamedIndividual ssc = safeCreateIndividual("Frame", sourceFrame, getIndividualName("Frame", sourceFrame));
            OWLNamedIndividual sInf = createIndividual("Inference");
            setDataProperty(sInf, "hasInferentialContent", subtemp.get("Entailment.Source inference"));
            setDataProperty(sInf, "label", makeInferenceLabel(subtemp.get("Entailment.Source inference")));
            setObjectProperty(sInf, "isInferenceOfFrame", ssc);

            OWLNamedIndividual tsc = safeCreateIndividual("Frame", targetFrame, getIndividualName("Frame", targetFrame));
            OWLNamedIndividual tInf = createIndividual("Inference");
            setDataProperty(tInf, "hasInferentialContent", subtemp.get("Entailment.Target entailment"));
            setDataProperty(tInf, "label", makeInferenceLabel(subtemp.get("Entailment.Target entailment")));
            setObjectProperty(tInf, "isInferenceOfFrame", tsc);

            setObjectProperty(ind, "hasSourceInference", sInf);
            setObjectProperty(ind, "hasTargetInference", tInf);
            setDataProperty(ind, "label", makeInferenceLabel(subtemp.get("Entailment.Target entailment"), 20) + "<=" + makeInferenceLabel(subtemp.get("Entailment.Source inference"), 20));
            setObjectProperty(subj, "hasEntailment", ind);
            return;
        }
        if (subtemp.get("type").equals("Mapping")) {
            if (sourceFrame == null || targetFrame == null) {
                logger.log(Level.SEVERE, "Error: metaphor {0} is missing target/frame.  Cannot create role mappings.", pageName);
                return;
            }
            if (subtemp.get("Source") == null
                    || subtemp.get("Target") == null) {
                logger.log(Level.SEVERE, "Error: source/target roles are null for mapping in {0}", pageName);
                return;
            }
            ind = createIndividual("Mapping");
            OWLNamedIndividual src = safeCreateRole(sourceFrame, subtemp.get("Source"));
            OWLNamedIndividual tg = safeCreateRole(targetFrame, subtemp.get("Target"));
            setObjectProperty(ind, "Source", src);
            setObjectProperty(ind, "Target", tg);
            setDataProperty(ind, "label", targetFrame + "." + subtemp.get("Target") + "<=" + sourceFrame + "." + subtemp.get("Source"));
            setObjectProperty(subj, "Mapping", ind);
            return;
        }
        if (subtemp.get("type").equals("Metaphor.Alias")) {
            String prov = subtemp.get("Metaphor.Alias.Name")
                    + "(" + subtemp.get("Metaphor.Alias.Provenance") + ":"
                    + subtemp.get("Metaphor.Alias.Page no") + ")";
            setDataProperty(subj, "Metaphor.Alias", prov);
            return;
        }
        if (subtemp.get("type").equals("LUs")) {
            if (!subtemp.containsKey("LUs.Lemmas")
                    || subtemp.get("LUs.Lemmas").isEmpty()
                    || pageType.equals("Metaphor")) {
                return;
            }
            String[] lemmas = subtemp.get("LUs.Lemmas").split(",");
            for (int i = 0; i < lemmas.length; i++) {
                String lemma = lemmas[i].trim();
                if (lemma.isEmpty()) {
                    continue;
                }
                ind = createIndividual("LUs");
                setDataProperty(ind, "LUs.Language", subtemp.get("LUs.Language"));
                setDataProperty(ind, "LUs.Lemmas", lemma);
                setDataProperty(ind, "label", lemma);
                setObjectProperty(subj, "LUs", ind);
            }
            return;
        }
        // typical templates with only datatype properties
        ind = safeCreateIndividual(subtemp.get("type"), subtemp);
        if (ind != null) {
            for (Iterator<String> it = subtemp.keySet().iterator(); it.hasNext();) {
                String key = it.next();
                if (key.equals("frame") || key.equals("type") || key.equals("metaphor")) {
                    continue;
                }
                // role names should be skipped, since they are defined at creation
                if (key.equals("Role.Name")) {
                    continue;
                }
                setDataProperty(ind, key, subtemp.get(key));
            }
            setObjectProperty(subj, subtemp.get("type"), ind);
        }
    }

    public void parse() {
        int nc = nextChunkType();
        if (nc != STARTTEMPLATE) {
            // find the first template block
            int ts = wiki.indexOf("{{");
            if (ts < 0) {
                // then there is no template
                return;
            }
            // if there was free text, advance to start of template
            wiki.delete(0, ts);
        }
        pageType = readTemplateName();
        // possible page types are Metaphor, Frame, Metaphor family, Frame family,
        // and IARPASourceConcept, and IARPATargetConcept
        
        OWLNamedIndividual ind = safeCreateIndividual(pageType, pageName, getIndividualName(pageType, pageName));

        Map<String, String> templ = null;
        String currentVar = null;
        sourceFrame = null;
        targetFrame = null;

        /*
         * This code depends on the current wiki design in which embedded
         * templates are only 1 level deep.
         */
        while (wiki.length() > 0) {
            nc = nextChunkType();
            if (nc == STARTTEMPLATE) {
                // start collecting subtemplate variable/value pairs
                templ = new HashMap<String, String>();
                templ.put("type", readTemplateName());
                templ.put("frame", pageName);
                logger.log(Level.INFO, "=start template:{0}", templ.get("type"));
                currentVar = null;
            } else if (nc == VARIABLE) {
            	try {
            		currentVar = readVariableName();
            	} catch (java.lang.StringIndexOutOfBoundsException ex) {
            		logger.log(Level.SEVERE,"Error processing variable name on page {0} with template {1}",new Object[]{pageName,pageType});
            		throw ex;
            	}
            } else if (nc == OTHER) {
                // either value to assign to variable or free text to ignore
                String val = readValue();
                if (templ != null) {
                    // these are properties of subtemplates, these get
                    // processed later when all the variables are in
                    templ.put(currentVar, val);
                } else if (currentVar != null) {
                    if (currentVar.equals("Source frame") || currentVar.equals("Target frame")) {
                        if (currentVar.equals("Source frame")) {
                            sourceFrame = val;
                        } else if (currentVar.equals("Target frame")) {
                            targetFrame = val;
                        }
                        OWLNamedIndividual rframe = safeCreateIndividual("Frame", val, getIndividualName("Frame", val));
                        setObjectProperty(ind, currentVar, rframe);
                    } else if (currentVar.equals("is subfamily of")) {
                        if (val != null) {
                            // this is because a metaphor or frame family can be part of multiple families
                            String[] famNames = val.split(",");
                            for (int i = 0; i < famNames.length; i++) {
                                if (famNames[i].equals("")) {
                                    continue;
                                }
                                String familyName = famNames[i].trim();
                                OWLNamedIndividual superfam = safeCreateIndividual(pageType, familyName, getIndividualName(pageType, familyName));
                                setObjectProperty(ind, currentVar + pageType, superfam);
                            }
                        }
                    } else if (currentVar.equals("Family")) {
                        if (val != null) {
                            // this is because a metaphor or frame can be part of multiple families
                            String[] famNames = val.split(",");
                            for (int i = 0; i < famNames.length; i++) {
                                if (famNames[i].equals("")) {
                                    continue;
                                }
                                if (pageType.equals("Metaphor") || pageType.equals("Frame")) {
                                    String familyType = pageType + " family";
                                    String familyName = famNames[i].trim();
                                    OWLNamedIndividual fam = safeCreateIndividual(familyType, familyName, getIndividualName(familyType, familyName));
                                    setObjectProperty(ind, "isIn" + pageType + currentVar, fam);
                                }
                            }
                        }
                    } else if (currentVar.equals("Seed")) {
                        //object property of Linguistic metaphors
                        if (val != null) {
                            OWLNamedIndividual seedM = safeCreateIndividual(pageType, val, getIndividualName(pageType, val));
                            setObjectProperty(ind, currentVar, seedM);
                        }
                    } else if (currentVar.equals("Instance of metaphor")) {
                        if (val != null) {
                            List<String> mets = Arrays.asList(val.split(","));
                            for (String met: mets) {
                                met = met.trim();
                                OWLNamedIndividual mphor = safeCreateIndividual("Metaphor", met, getMetaphorId(met));
                                setObjectProperty(ind, currentVar, mphor);
                            }
                        }
                    } else {
                        //data property of the page template
                        setDataProperty(ind, currentVar, val);
                    }
                }
            } else if (nc == ENDTEMPLATE) {
                readTemplateEnd(); // eats }}'s
                if (templ != null && templ.size() > 2) {
                    // process the subtemplate
                    // if size is less than three it means that it's an empty
                    // template, e.g. {{Related frame}}
                    logger.log(Level.INFO, "=processing template:{0}", templ.get("type"));
                    parseSubtemplate(ind, templ);
                    templ = null;
                }
                currentVar = null;
            }
        }
                
        // If the pagetype is Metaphor, and if the target or source frames
        // are null, fill it in with a substring from the name of the page.
        if (pageType.equals("Metaphor") && frameNamesRegexp.containsKey(lang) &&
                (sourceFrame==null || targetFrame==null)) {
            logger.log(Level.WARNING,"Metaphor {0} does not have frames",pageName);
            Pattern regex = Pattern.compile(frameNamesRegexp.get(lang));
            String metaphorName = pageName.replaceAll("^Metaphor:", "");
            Matcher m = regex.matcher(metaphorName);
            if (m.matches()) {
                Locale loc = new Locale(lang);
                if (sourceFrame==null) {
                    sourceFrame = StringUtils.capitalize(m.group(3).trim().replaceAll(articlesRegexp.get(lang),"").toLowerCase(loc));
                    logger.log(Level.WARNING,"==> Extracted source frame:{0}",sourceFrame);
                    OWLNamedIndividual rframe = safeCreateIndividual("Frame", sourceFrame, getIndividualName("Frame", sourceFrame));
                    setObjectProperty(ind, "Source frame", rframe);

                }
                if (targetFrame==null) {
                    targetFrame = StringUtils.capitalize(m.group(1).trim().replaceAll(articlesRegexp.get(lang),"").toLowerCase(loc));
                    logger.log(Level.WARNING,"==> Extracted target frame:{0}",targetFrame);
                    OWLNamedIndividual rframe = safeCreateIndividual("Frame", targetFrame, getIndividualName("Frame", targetFrame));
                    setObjectProperty(ind, "Target frame", rframe);
                }
            }
        }
    }

    private void trim() {
        while (wiki.length() > 0 && Character.isWhitespace(wiki.charAt(0))) {
            wiki.deleteCharAt(0);
        }
    }

    private int nextChunkType() {
        trim();
        if (wiki.indexOf("{{") == 0) {
            return STARTTEMPLATE;
        }
        if (wiki.indexOf("}}") == 0) {
            return ENDTEMPLATE;
        }
        if (wiki.indexOf("|") == 0) {
            return VARIABLE;
        }
        return OTHER;
    }

    private String readTemplateName() {
        String tname;
        int stopbar = wiki.indexOf("|");
        int stopbracket = wiki.indexOf("}}");
        int stop;
        if (stopbar > 0 & stopbracket > 0) {
            stop = Math.min(stopbar, stopbracket);
        } else {
            stop = Math.max(stopbar, stopbracket);
        }
        if (stop < 0) {
            // then there are no variables
            stop = wiki.length();
        }
        tname = wiki.substring(2, stop);
        wiki.delete(0, stop);
        return tname.trim();
    }

    private void readTemplateEnd() {
        wiki.delete(0, 2);
    }

    private String readVariableName() {
        String vname;
        int stop = wiki.indexOf("=");
        vname = wiki.substring(1, stop);
        wiki.delete(0, stop + 1);  //+1 to delete the =
        return vname.trim();
    }

    private String readValue() {
        String val;
        int stopbar = wiki.indexOf("|");
        int stopbracket = wiki.indexOf("}}");
        int stop;

        if (stopbar > 0 & stopbracket > 0) {
            stop = Math.min(stopbar, stopbracket);
        } else {
            // one of the two doesn't occur before EOF
            // read up to the one that does exist
            stop = Math.max(stopbar, stopbracket);
        }
        if (stop < 0) {
            // then read until the end
            stop = wiki.length();
        }
        val = wiki.substring(0, stop);
        wiki.delete(0, stop);
        return StringEscapeUtils.unescapeHtml4(val.trim().replace("__MEDIAWIKI_VERTICAL_BAR__", "|"));
    }
}
