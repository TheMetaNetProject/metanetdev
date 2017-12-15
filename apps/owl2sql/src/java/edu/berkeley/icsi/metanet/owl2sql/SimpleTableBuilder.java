package edu.berkeley.icsi.metanet.owl2sql;

import java.io.IOException;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map.Entry;
import java.util.Set;

import org.semanticweb.owlapi.model.OWLAnnotation;
import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLAnnotationSubject;
import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * Class that handles building a simplified translation of an OWL ontology to
 * RDB tables. Rather than using tables to capture abstract entities and
 * relationships in an OWL ontology, this class builds tables corresponding to
 * actual classes in the OWL schema.
 *
 * @author brandon
 *
 */
public class SimpleTableBuilder implements TableBuilder {

    private OWLOntology ont;
    private Statement stmt;
    private OWLClass mfClass, cmClass, lmClass, schClass, exClass;
    private OWLObjectProperty hasSrcSch, hasTgtSch, hasExample, inMetFam,
            hasLU, isInstanceOfCM, isFromSeed;
    private OWLDataProperty hasSentence, hasSource, hasTarget, hasLemma, hasTag;
    private HashMap<String, Integer> mfIDs = new HashMap<String, Integer>();
    private HashMap<String, Integer> cmIDs = new HashMap<String, Integer>();
    private HashMap<String, Integer> lmIDs = new HashMap<String, Integer>();
    private HashMap<String, Integer> schIDs = new HashMap<String, Integer>();
    private HashMap<String, Integer> exIDs = new HashMap<String, Integer>();
    private boolean verbose = false;

    /**
     * Basic constructor
     *
     * @param ont - The OWL ontology
     * @param stmt - A Statement created from a Connection to the database
     * server
     */
    SimpleTableBuilder(OWLOntology ont, Statement stmt, boolean verbose) {
        this.ont = ont;
        this.stmt = stmt;
        this.verbose = verbose;
        setPointers();
    }

    /**
     * Sets pointers to each of the appropriate OWL classes, object properties,
     * and data properties
     */
    protected void setPointers() {
        String className, objPropName, dataPropName, annoPropName;

        // Set OWLClass pointers
        for (OWLClass owlClass : ont.getClassesInSignature(true)) {
            className = Utilities.getName(owlClass);
            if (className.equals("MetaphorFamily")) {
                mfClass = owlClass;
            } else if (className.equals("VettedMetaphor")) {
                cmClass = owlClass;
            } else if (className.equals("LinguisticMetaphor")) {
                lmClass = owlClass;
            } else if (className.equals("VettedSchema")) {
                schClass = owlClass;
            } else if (className.equals("Example")) {
                exClass = owlClass;
            }
        }

        // Set OWLObjectProperty pointers
        for (OWLObjectProperty objProp : ont.getObjectPropertiesInSignature(true)) {
            objPropName = Utilities.getName(objProp);
            if (objPropName.equals("hasTargetSchema")) {
                hasTgtSch = objProp;
            } else if (objPropName.equals("hasSourceSchema")) {
                hasSrcSch = objProp;
            } else if (objPropName.equals("hasExample")) {
                hasExample = objProp;
            } else if (objPropName.equals("isInMetaphorFamily")) {
                inMetFam = objProp;
            } else if (objPropName.equals("hasLexicalUnit")) {
                hasLU = objProp;
            } else if (objPropName.equals("isInstanceOfMetaphor")) {
                isInstanceOfCM = objProp;
            } else if (objPropName.equals("isFromSeedMetaphor")) {
                isFromSeed = objProp;
            }
        }

        // Set OWLDataProperty pointers
        for (OWLDataProperty dataProp : ont.getDataPropertiesInSignature(true)) {
            dataPropName = Utilities.getName(dataProp);
            if (dataPropName.equals("hasSentence")) {
                hasSentence = dataProp;
            } else if (dataPropName.equals("hasLinguisticSource")) {
                hasSource = dataProp;
            } else if (dataPropName.equals("hasLinguisticTarget")) {
                hasTarget = dataProp;
            } else if (dataPropName.equals("hasLemma")) {
                hasLemma = dataProp;
            } else if (dataPropName.equals("hasTag")) {
                hasTag = dataProp;
            }
        }

    }

    /**
     * Initializes the tables in the database
     *
     * @throws SQLException - Thrown if there is an error initializing the
     * tables
     */
    protected void initTables() throws SQLException {
        statusUpdate("Initializing tables");
        String strType = Basics.DEFAULT_SQL_DATATYPE;

        try {
            stmt.execute(
                    "CREATE TABLE MetaphorFamily ("
                    + "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
                    + "name " + strType + " NOT NULL,"
                    + "PRIMARY KEY (id))");
            stmt.execute(
                    "CREATE TABLE OWLSchema ("
                    + "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
                    + "name " + strType + " NOT NULL,"
                    + "LUs TEXT,"
                    + "PRIMARY KEY (id))");
            stmt.execute(
                    "CREATE TABLE ConceptualMetaphor ("
                    + "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
                    + "name " + strType + " NOT NULL,"
                    + "targetSchID BIGINT UNSIGNED,"
                    + "sourceSchID BIGINT UNSIGNED,"
                    + "PRIMARY KEY (id),"
                    + "FOREIGN KEY (targetSchID) REFERENCES OWLSchema(id),"
                    + "FOREIGN KEY (sourceSchID) REFERENCES OWLSchema(id))");
            stmt.execute(
                    "CREATE TABLE LinguisticMetaphor ("
                    + "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
                    + "name " + strType + " NOT NULL,"
                    + "target " + strType + " NOT NULL,"
                    + "source " + strType + " NOT NULL,"
                    + "tags TEXT, "
                    + "sourceCluster TEXT,"
                    + "sourceLabel " + strType + ","
                    + "PRIMARY KEY (id))");
            stmt.execute(
                    "CREATE TABLE Example ("
                    + "id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,"
                    + "text TEXT NOT NULL,"
                    + "lmID BIGINT UNSIGNED,"
                    + "PRIMARY KEY (id),"
                    + "FOREIGN KEY (lmID) REFERENCES LinguisticMetaphor(id))");
            stmt.execute(
                    "CREATE TABLE CMtoMF ("
                    + "cmID BIGINT UNSIGNED NOT NULL,"
                    + "mfID BIGINT UNSIGNED NOT NULL,"
                    + "PRIMARY KEY (cmID, mfID),"
                    + "FOREIGN KEY (cmID) REFERENCES ConceptualMetaphor(id),"
                    + "FOREIGN KEY (mfID) REFERENCES MetaphorFamily(id))");
            stmt.execute(
                    "CREATE TABLE LMtoCM ("
                    + "lmID BIGINT UNSIGNED NOT NULL,"
                    + "cmID BIGINT UNSIGNED NOT NULL,"
                    + "PRIMARY KEY (lmID, cmID),"
                    + "FOREIGN KEY (cmID) REFERENCES ConceptualMetaphor(id),"
                    + "FOREIGN KEY (lmID) REFERENCES LinguisticMetaphor(id))");
        } catch (SQLException e) {
            SQLException ex = new SQLException("Error creating tables");
            ex.initCause(e);
            throw ex;
        }
    }

    protected void populateIndividuals() throws SQLException {
        OWLNamedIndividual namedInd, sourceSchema, targetSchema;
        HashMap<String, String> fieldValueMap;
        String insertStr, sentence, target, source;
        Set<OWLIndividual> examples;
        Set<String> exampleUpdateStrings = new HashSet<String>();
        HashMap<Integer, Integer> cmToMFMap = new HashMap<Integer, Integer>();
        int id;

        // Handle metaphor families
        fieldValueMap = new HashMap<String, String>();
        id = 1;
        for (OWLIndividual ind : mfClass.getIndividuals(ont)) {
            if (ind.isAnonymous()) {
                statusUpdate(ind + " is an anonymous individual. Skipping.");
                continue;
            }
            namedInd = ind.asOWLNamedIndividual();
            fieldValueMap.put("name", Utilities.getName(namedInd));
            insertStr = Utilities.getInsertString("MetaphorFamily", fieldValueMap);
            stmt.execute(insertStr);

            mfIDs.put(Utilities.getName(namedInd), id);
            id++;
        }

        // Handle schemas
        String luBlob;
        String lemmaValue;

        fieldValueMap = new HashMap<String, String>();
        id = 1;
        for (OWLIndividual ind : schClass.getIndividuals(ont)) {
            if (ind.isAnonymous()) {
                statusUpdate(ind + " is an anonymous individual. Skipping.");
                continue;
            }
            namedInd = ind.asOWLNamedIndividual();
            fieldValueMap.put("name", Utilities.getName(namedInd));

            // Create the LU blob
            Set<OWLIndividual> LUs = ind.getObjectPropertyValues(hasLU, ont);
            luBlob = "";
            for (OWLIndividual lu : LUs) {
                if (lu.isAnonymous()) {
                    continue;
                }
                lemmaValue = getDataPropValue(lu.asOWLNamedIndividual(),
                        hasLemma);
                if (lemmaValue == null) {
                    continue;
                }
                luBlob += lemmaValue + ", ";
            }
            fieldValueMap.put("LUs", luBlob.replaceAll("'", "''"));

            String query = Utilities.getInsertString("OWLSchema", fieldValueMap);
            try {
                stmt.execute(query);
            } catch (SQLException e) {
                System.err.print("Error in query:" + query);
                throw e;
            }
            schIDs.put(Utilities.getName(namedInd), id);
            id++;
        }

        // Handle conceptual (vetted) metaphors
        OWLNamedIndividual namedMF;
        int mfID;

        fieldValueMap = new HashMap<String, String>();
        id = 1;

        for (OWLIndividual ind : cmClass.getIndividuals(ont)) {
            if (ind.isAnonymous()) {
                statusUpdate(ind + " is an anonymous individual. Skipping.");
                continue;
            }
            namedInd = ind.asOWLNamedIndividual();
            fieldValueMap.put("name", Utilities.getName(namedInd));

            targetSchema = getObjPropValue(namedInd, hasTgtSch);
            if (targetSchema == null) {
                continue;
            }
            fieldValueMap.put("targetSchID", String.valueOf(schIDs.get(Utilities.getName(targetSchema))));

            sourceSchema = getObjPropValue(namedInd, hasSrcSch);
            if (sourceSchema == null) {
                continue;
            }
            if (schIDs.get(Utilities.getName(sourceSchema)) == null) {
                //System.out.println(Utilities.getName(sourceSchema) + " has no cached ID!");
                continue;
            }
            fieldValueMap.put("sourceSchID", String.valueOf(schIDs.get(Utilities.getName(sourceSchema))));

            for (OWLIndividual mf : namedInd.getObjectPropertyValues(inMetFam, ont)) {
                if (mf.isAnonymous()) {
                    continue;
                }

                namedMF = mf.asOWLNamedIndividual();
                mfID = mfIDs.get(Utilities.getName(namedMF));
                cmToMFMap.put(id, mfID);
            }

            stmt.execute(Utilities.getInsertString("ConceptualMetaphor",
                    fieldValueMap));

            cmIDs.put(Utilities.getName(namedInd), id);
            id++;
        }

        // Handle CMtoMF join table
        fieldValueMap = new HashMap<String, String>();
        for (Entry<Integer, Integer> entry : cmToMFMap.entrySet()) {
            fieldValueMap.put("cmID", String.valueOf(entry.getKey()));
            fieldValueMap.put("mfID", String.valueOf(entry.getValue()));
            stmt.execute(Utilities.getInsertString("CMtoMF", fieldValueMap));
        }

        // Handle examples
        fieldValueMap = new HashMap<String, String>();
        id = 1;
        for (OWLIndividual ind : exClass.getIndividuals(ont)) {
            if (ind.isAnonymous()) {
                statusUpdate(ind + " is an anonymous individual. Skipping.");
                continue;
            }
            namedInd = ind.asOWLNamedIndividual();

            sentence = getDataPropValue(namedInd, hasSentence);
            if (sentence == null) {
                continue;
            }
            fieldValueMap.put("text", Utilities.format(sentence));

            stmt.execute(Utilities.getInsertString("Example",
                    fieldValueMap));

            exIDs.put(Utilities.getName(namedInd), id);
            id++;
        }

        // Handle linguistic metaphors
        OWLNamedIndividual namedExample;
        Integer exID, cmID;
        String tagsBlob;

        fieldValueMap = new HashMap<String, String>();
        HashMap<String, String> exampleValueMap = new HashMap<String, String>();
        HashMap<Integer, Integer> lmToCMMap = new HashMap<Integer, Integer>();
        id = 1;

        for (OWLIndividual ind : lmClass.getIndividuals(ont)) {
            if (ind.isAnonymous()) {
                statusUpdate(ind + " is an anonymous individual. Skipping.");
                continue;
            }
            namedInd = ind.asOWLNamedIndividual();
            fieldValueMap.put("name", Utilities.getName(namedInd));

            source = getDataPropValue(namedInd, hasSource);
            if (source == null) {
                continue;
            }
            fieldValueMap.put("source", source);

            target = getDataPropValue(namedInd, hasTarget);
            if (target == null) {
                continue;
            }
            fieldValueMap.put("target", target);

            tagsBlob = "";
            for (OWLLiteral tag : namedInd.getDataPropertyValues(hasTag, ont)) {
                tagsBlob += tag.getLiteral() + ", ";
            }
            if (tagsBlob.endsWith(", ")) {
                tagsBlob = tagsBlob.substring(0, tagsBlob.length() - 2);
            }
            fieldValueMap.put("tags", tagsBlob);

            // Get and cache associated examples of this LM
            examples = namedInd.getObjectPropertyValues(hasExample, ont);
            for (OWLIndividual example : examples) {
                if (example.isAnonymous()) {
                    continue;
                }
                namedExample = example.asOWLNamedIndividual();
                exID = exIDs.get(Utilities.getName(namedExample));
                exampleValueMap.put("lmID", String.valueOf(id));
                exampleUpdateStrings.add(Utilities.getUpdateString("Example",
                        "id", exID, exampleValueMap));
            }

            // Get and cache LM to CM relationships
            for (OWLIndividual cm : namedInd.getObjectPropertyValues(isInstanceOfCM, ont)) {
                if (cm.isAnonymous()) {
                    continue;
                }
                cmID = cmIDs.get(Utilities.getName(cm.asOWLNamedIndividual()));
                if (cmID != null) {
                    lmToCMMap.put(id, cmID);
                }
            }

            stmt.execute(Utilities.getInsertString("LinguisticMetaphor",
                    fieldValueMap));

            lmIDs.put(Utilities.getName(namedInd), id);
            id++;
        }

        // Handle LMtoCM join table
        fieldValueMap = new HashMap<String, String>();
        for (Entry<Integer, Integer> entry : lmToCMMap.entrySet()) {
            fieldValueMap.put("lmID", String.valueOf(entry.getKey()));
            fieldValueMap.put("cmID", String.valueOf(entry.getValue()));
            stmt.execute(Utilities.getInsertString("LMtoCM", fieldValueMap));
        }

        // Update LM references for the Example table
        for (String updateStr : exampleUpdateStrings) {
            stmt.execute(updateStr);
        }

        // Handle LM source cluster column
        OWLNamedIndividual namedLM, seed;
        String lmName, seedName, verb;
        HashMap<String, BlobIDsTuple> clusterMap = new HashMap<String, BlobIDsTuple>();
        BlobIDsTuple tuple;
        fieldValueMap = new HashMap<String, String>();
        for (OWLIndividual lm : lmClass.getIndividuals(ont)) {
            if (lm.isAnonymous()) {
                continue;
            }
            namedLM = lm.asOWLNamedIndividual();
            lmName = Utilities.getName(namedLM);
            verb = getDataPropValue(namedLM, hasSource);
            seed = getObjPropValue(namedLM, isFromSeed);
            if (seed == null) {
                seedName = lmName;
            } else {
                seedName = Utilities.getName(seed);
            }
            if (!clusterMap.containsKey(seedName)) {
                tuple = new BlobIDsTuple();
                clusterMap.put(seedName, tuple);
            } else {
                tuple = clusterMap.get(seedName);
            }
            tuple.addToBlob(verb);
            tuple.ids.add(lmIDs.get(lmName));
        }
        for (String seedKey : clusterMap.keySet()) {
            tuple = clusterMap.get(seedKey);
            String sourceLabel = seedKey.split("_")[2];
            fieldValueMap.put("sourceCluster", tuple.getBlob());
            fieldValueMap.put("sourceLabel", sourceLabel);
            for (Integer lmID : tuple.ids) {
                if (lmID == null) {
                    continue;
                }
                stmt.execute(Utilities.getUpdateString("LinguisticMetaphor",
                        "id", lmID.intValue(),
                        fieldValueMap));
            }
        }

    }

    /**
     * Handles status updates to STDOUT
     *
     * @param msg
     */
    protected void statusUpdate(String msg) {
        if (verbose) {
            System.out.println(msg);
        }
    }

    @Override
    public void build() throws SQLException {
        initTables();
        populateIndividuals();
    }

    @Override
    public void enableErrorLogging(String logPath) throws IOException {
        // TODO Auto-generated method stub
    }

    /**
     * Gets at most one instance of the given object property associated with
     * the given OWL individual
     *
     * @param ind
     * @param objProp
     * @return
     */
    private OWLNamedIndividual getObjPropValue(OWLNamedIndividual ind,
            OWLObjectProperty objProp) {

        Set<OWLIndividual> values = ind.getObjectPropertyValues(objProp, ont);
        if (values.size() > 0) {
            for (OWLIndividual value : values) {
                return value.asOWLNamedIndividual();
            }
        }

        return null;
    }

    /**
     * Gets at most one instance of the given data property associated with the
     * given OWL individual
     *
     * @param ind
     * @param dataProp
     * @return a string literal if the given OWLNamedIndividual has the
     * associated data property
     */
    private String getDataPropValue(OWLNamedIndividual ind, OWLDataProperty dataProp) {
        Set<OWLLiteral> values = ind.getDataPropertyValues(dataProp, ont);
        for (OWLLiteral value : values) {
            return value.getLiteral();
        }
        return null;
    }

    class BlobIDsTuple {

        private String blob = "";
        private HashSet<String> verbSet = new HashSet<String>();
        Set<Integer> ids = new HashSet<Integer>();

        protected void addToBlob(String str) {
            if (!verbSet.contains(str)) {
                verbSet.add(str);
                blob += str + ", ";
            }
        }

        protected String getBlob() {
            return blob;
        }
    }
}
