package edu.berkeley.icsi.metanet.wiki2owl;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Defines translations from MetaNet Semantic MediaWiki property names to
 * OWL property names, as well as some other facilities for translation
 * from wiki to owl.
 * 
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiFieldMap {

    private static final Map<String, String> WIKI2REP = new HashMap<String, String>();
    private static final Map<String, String> LINGMET_WIKI2REP = new HashMap<String, String>();
    private static final Map<String, String> FRAMEREL = new HashMap<String, String>();
    private static final Map<String, String> METAREL = new HashMap<String, String>();
    private static final Map<String, String> ICONCEPT2REP = new HashMap<String, String>();
    private static final Set<String> NAMED_CLASSES = new HashSet<String>();
    private static final Set<String> ANNOTATION_PROPERTIES = new HashSet<String>();
    private static Map<String,Integer> instanceCounter = new HashMap<String,Integer>();
    
    static {
        // unmapped - skip
        WIKI2REP.put("Metaphor_Family", null);

        // general name translation
        WIKI2REP.put("PageName", "hasName");
        WIKI2REP.put("Name gloss", "hasNameGloss");
        WIKI2REP.put("Name transcription", "hasNameTranscription");
        WIKI2REP.put("Role.Name gloss", "hasNameGloss");
        WIKI2REP.put("Role.Name transcription", "hasNameTranscription");
        WIKI2REP.put("Cultural scope","hasCulturalScope");
        WIKI2REP.put("Description","hasDescription");
        
        //frame properties
        WIKI2REP.put("Type", "hasFrameType");
        WIKI2REP.put("FrameNet frame", "correspondsToFrameNet");
        WIKI2REP.put("Cultural information", "hasCulturalContent");
        WIKI2REP.put("Applicability", "isApplicableToLanguage");
        WIKI2REP.put("Comments", "comment");
        WIKI2REP.put("Entered by", "wasEnteredBy");
        WIKI2REP.put("Status", "hasStatus");
        WIKI2REP.put("Other aliases", "hasAlias");
        WIKI2REP.put("Tags", "hasTag");
        WIKI2REP.put("Tag", "hasTag");
        WIKI2REP.put("Last reviewed by", "wasLastReviewedBy");
        WIKI2REP.put("Role.Name", "hasName");
        WIKI2REP.put("Role.Definition", "hasDefinition");
        WIKI2REP.put("Role.Type", "hasRoleType");
        WIKI2REP.put("Role.FrameNet role", "correspondsToFrameElement");
        WIKI2REP.put("Role", "hasRoles");
        WIKI2REP.put("Binding.Local role", "hasBoundRole1");
        WIKI2REP.put("Binding.Bound role", "hasBoundRole2");
        WIKI2REP.put("Binding", "hasBindings");
        WIKI2REP.put("Inference.Description", "hasInferentialContent");
        WIKI2REP.put("Inference.Type", "hasInferenceType");
        WIKI2REP.put("Inference", "hasInference");
        WIKI2REP.put("LUs.Language", "isFromLanguage");
        WIKI2REP.put("LUs.Lemmas", "hasLemma");
        WIKI2REP.put("LUs", "hasLexicalUnit");
        WIKI2REP.put("Program alias", "hasProgramAlias");

        // metaphor properties
        WIKI2REP.put("Metaphor.Alias", "hasAlias");
        WIKI2REP.put("Metaphor Level", "hasMetaphorLevel");
        WIKI2REP.put("Metaphor Type", "hasMetaphorType");
        WIKI2REP.put("Example", "hasExample");
        WIKI2REP.put("Mapping", "hasMappings");
        WIKI2REP.put("Example.Language", "isFromLanguage");
        WIKI2REP.put("Example.Text", "hasSentence");
        WIKI2REP.put("Example.Gloss", "hasSentenceGloss");
        WIKI2REP.put("Example.English translation", "hasSentenceTranslation");
        WIKI2REP.put("Example.Transcription", "hasSentenceTranscription");
        WIKI2REP.put("Example.Comments", "comment");
        WIKI2REP.put("Example.Annotation", "hasAnnotation");
        WIKI2REP.put("Example.Provenance", "hasProvenance");
        WIKI2REP.put("Source frame", "hasSourceFrame");
        WIKI2REP.put("Target frame", "hasTargetFrame");
        WIKI2REP.put("Investigated for", "wasInvestigatedFor");
        WIKI2REP.put("Source", "hasSourceRole");
        WIKI2REP.put("Target", "hasTargetRole");
        WIKI2REP.put("Experiential basis", "hasExperientialBasis");
        
        //ignored for now
        WIKI2REP.put("LinkEnglish","hasEnglishCorrespondent");
        WIKI2REP.put("LinkSpanish","hasSpanishCorrespondent");
        WIKI2REP.put("LinkPersian","hasPersianCorrespondent");
        WIKI2REP.put("LinkRussian","hasRussianCorrespondent");
        
        //family properties
        WIKI2REP.put("is subfamily ofMetaphor family", "isMetaphorSubfamilyOf");
        WIKI2REP.put("is subfamily ofFrame family", "isFrameSubfamilyOf");
        WIKI2REP.put("Metaphor family type", "hasMetaphorFamilyType");
        WIKI2REP.put("Metaphor family status", "hasStatus");
        WIKI2REP.put("FrameFamilyTag", "hasTag");
        WIKI2REP.put("FrameFamilyStatus", "hasStatus");
        
        //CxnMP and MetaRC properties
        WIKI2REP.put("CxnMPType", "hasCxnPType");
        WIKI2REP.put("CxnMPGroup", "isInCxnPGroup");
        WIKI2REP.put("CxnMPDescription", "hasDescription");
        WIKI2REP.put("CxnMPQueryCode", "hasQueryCode");
        WIKI2REP.put("MetaRCGroup", "isInRCGroup");
        WIKI2REP.put("MetaRCDescription", "hasDescription");
        WIKI2REP.put("MetaRCComments", "comment");
        WIKI2REP.put("MetaRCScore", "hasMetaphoricityScore");
        WIKI2REP.put("MetaRCQueryCode", "hasQueryCode");
        
        //Linguistic metaphor properties
        LINGMET_WIKI2REP.put("PageName", "hasName");
        LINGMET_WIKI2REP.put("Name gloss", "hasNameGloss");
        LINGMET_WIKI2REP.put("Type","hasLinguisticMetaphorType");
        LINGMET_WIKI2REP.put("Source", "hasLinguisticSource");        
        LINGMET_WIKI2REP.put("Target", "hasLinguisticTarget");
        LINGMET_WIKI2REP.put("Comments", "comment");
        LINGMET_WIKI2REP.put("Entered by", "wasEnteredBy");
        LINGMET_WIKI2REP.put("Status", "hasStatus");
        LINGMET_WIKI2REP.put("Tags", "hasTag");
        LINGMET_WIKI2REP.put("Tag", "hasTag");
        LINGMET_WIKI2REP.put("Seed", "isFromSeedMetaphor");
        LINGMET_WIKI2REP.put("Instance of metaphor", "isInstanceOfMetaphor");
        LINGMET_WIKI2REP.put("Example", "hasExample");
        LINGMET_WIKI2REP.put("Example.Language", "isFromLanguage");
        LINGMET_WIKI2REP.put("Example.Text", "hasSentence");
        LINGMET_WIKI2REP.put("Example.Gloss", "hasSentenceGloss");
        LINGMET_WIKI2REP.put("Example.English translation", "hasSentenceTranslation");
        LINGMET_WIKI2REP.put("Example.Comments", "comment");
        LINGMET_WIKI2REP.put("Example.Annotation", "hasAnnotation");
        LINGMET_WIKI2REP.put("Example.Provenance", "hasProvenance");
        LINGMET_WIKI2REP.put("Verification status", "hasVerificationStatus");
        
        //frame relations
        FRAMEREL.put("makes use of", "makesUseOfFrame");
        FRAMEREL.put("is subcase of", "isSubcaseOfFrame");
        FRAMEREL.put("is somehow related to", "isRelatedToFrame");
        FRAMEREL.put("is related to", "isRelatedToFrame");
        FRAMEREL.put("is a subprocess of", "isSubprocessOfFrame");
        FRAMEREL.put("is in a scalar opposition to", "isInAScalarOppositionToFrame");
        FRAMEREL.put("is a perspective on", "isAPerspectiveOnFrame");
        FRAMEREL.put("incorporates as a role", "incorporatesFrameAsRole");
        FRAMEREL.put("is in causal relation with", "isInCausalRelationWithFrame");

        //metaphor relations
        METAREL.put("is a source subcase of", "isSourceSubcaseOfMetaphor");
        METAREL.put("is a target subcase of", "isTargetSubcaseOfMetaphor");
        METAREL.put("is a mapping within", "isAMappingWithinMetaphor");
        METAREL.put("makes use of", "makesUseOfMetaphor");
        METAREL.put("has as transitive subpart 1", "hasTransitiveSubpart1Metaphor");
        METAREL.put("has as transitive subpart 2", "hasTransitiveSubpart2Metaphor");
        METAREL.put("is in some source relation to", "isRelatedToMetaphorBySource");
        METAREL.put("is in some target relation to", "isRelatedToMetaphorByTarget");
        METAREL.put("is an entailment of", "isEntailedByMetaphor");
        METAREL.put("is in some way related to", "isRelatedToMetaphor");
        METAREL.put("is related to", "isRelatedToMetaphor");
        METAREL.put("is in a dual relationship with", "isADualOfMetaphor");

        // this one gets special treatment: just set up both relations
        METAREL.put("is both a source and target subcase of", null);

        // concept properties
        ICONCEPT2REP.put("Type","hasConceptType");
        ICONCEPT2REP.put("Status","hasConceptStatus");
        ICONCEPT2REP.put("SourceID","hasConceptID");
        ICONCEPT2REP.put("Owner","hasConceptOwner");
        ICONCEPT2REP.put("LUs","hasConceptLUs");
        ICONCEPT2REP.put("Definition","hasConceptDefinition");
        ICONCEPT2REP.put("Comments","comment");
        ICONCEPT2REP.put("ConceptType","hasConceptType");
        ICONCEPT2REP.put("ConceptStatus","hasConceptStatus");
        ICONCEPT2REP.put("ConceptOwner","hasConceptOwner");
        ICONCEPT2REP.put("ConceptGroup","hasConceptGroup");
        ICONCEPT2REP.put("ConceptDefinition","hasConceptDefinition");
        ICONCEPT2REP.put("ConceptComment","comment");
        ICONCEPT2REP.put("WhitelistTargetLU","hasWhitelistTargetLU");
        ICONCEPT2REP.put("BlacklistTargetLU","hasBlacklistTargetLU");
        ICONCEPT2REP.put("BlacklistSourceLU","hasBlacklistSourceLU");
        
        // Classes that have a hasName field-- note these are the corresponding
        // template names
        NAMED_CLASSES.add("Metaphor");
        NAMED_CLASSES.add("Frame");
        NAMED_CLASSES.add("Metaphor family");
        NAMED_CLASSES.add("Frame family");
        NAMED_CLASSES.add("Role");
        NAMED_CLASSES.add("Linguistic metaphor");
        NAMED_CLASSES.add("IARPASourceConcept");
        NAMED_CLASSES.add("IARPATargetConcept");
        NAMED_CLASSES.add("CxnMP");
        NAMED_CLASSES.add("MetaRC");
        
        ANNOTATION_PROPERTIES.add("hasProvenance");
        ANNOTATION_PROPERTIES.add("hasProvenancePageNumber");
        ANNOTATION_PROPERTIES.add("wasEnteredBy");
        ANNOTATION_PROPERTIES.add("wasLastReviewedBy");
        ANNOTATION_PROPERTIES.add("comment");
        ANNOTATION_PROPERTIES.add("label");

    }
    
    /*
     * Used to retrieve monotonically increasing numbered instance names
     * 
     * @param className name of class
     * @return      string of the form class_N
     */
    public static String getInstanceName(String className) {
        Integer val;
        if (instanceCounter.containsKey(className)) {
            val = new Integer(instanceCounter.get(className).intValue()+1);
        } else {
            val = new Integer(1);
        }
        instanceCounter.put(className, val);
        return className+"_"+val;
    }
    
    /*
     * Translates wiki field (template variable names) to OWL property names.
     * 
     * @param   pageType    Type of page: a template name
     * @param   fieldName   wiki field/variable name
     * @return              owl property name if know, fieldName passed through if not
     * 
     */
    public static String trans(String pageType, String fieldName) {
        Map<String, String> lookup = WIKI2REP;
        if (pageType.equals("Linguistic metaphor")) {
            lookup = LINGMET_WIKI2REP;
        } else if (pageType.equals("IARPASourceConcept") || pageType.equals("IARPATargetConcept")) {
        	lookup = ICONCEPT2REP;
        }
        if (lookup.containsKey(fieldName)) {
            return lookup.get(fieldName);
        } else {
            return fieldName;
        }
    }
    
    /*
     * Reports whether a class (Frame, Metaphor, etc.) has a hasName property.
     * 
     * This is done by a lookup into a static set of class names, so nothing
     * clever going on here
     * 
     * @param   className   Name of ontology class (Metaphor, Frame, etc.)
     * @return              true if that class has a hasName property, false otherwise
     */
    public static boolean hasName(String className) {
        if (NAMED_CLASSES.contains(className)) {
            return true;
        }
        return false;
    }
    
    /*
     * Translates metaphor relation names from wiki property to OWL property
     * 
     * @param   relName Name of the metaphor relation
     * @return  OWL property name if known, or relName passed-through if not
     */
    public static String transmetarel(String relName) {
        if (METAREL.containsKey(relName)) {
            return METAREL.get(relName);
        } else {
            return relName;
        }
    }
    
    /*
     * Translates frame relation names from wiki property to OWL property
     * 
     * @param   relName Name of the frame relation
     * @return  OWL property name if known, or relName passed-through if not
     */
    public static String transframerel(String relName) {
        if (FRAMEREL.containsKey(relName)) {
            return FRAMEREL.get(relName);
        } else {
            return relName;
        }
    }
    
    public static boolean isAnnotationProp(String prop) {
        if (ANNOTATION_PROPERTIES.contains(prop)) {
            return true;
        } else {
            return false;
        }
    }
}
