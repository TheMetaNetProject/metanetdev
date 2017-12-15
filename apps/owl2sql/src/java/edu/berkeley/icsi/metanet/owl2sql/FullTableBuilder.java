package edu.berkeley.icsi.metanet.owl2sql;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Map;
import java.util.Set;

import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLDataPropertyExpression;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;

import com.mysql.jdbc.exceptions.jdbc4.MySQLIntegrityConstraintViolationException;

/**
 * This table builder builds using a static database schema
 *
 * @author brandon
 *
 */
public class FullTableBuilder implements TableBuilder {

    private int numLogErrors, numBuildErrors;
    private boolean loggingEnabled;
    private BufferedWriter errorLogger;
    private OWLOntology ont;
    private Set<OWLOntology> ontClosure;
    private Statement stmt;
    private HashMap<OWLObjectProperty, HashSet<OWLClass>> objPropDomains,
            objPropRanges;
    private HashMap<OWLDataProperty, HashSet<OWLClass>> dataPropDomains;
    private String logPath;
    private boolean verbose = false;

    /**
     * Initializes the TableBuilder object
     *
     * @throws FileNotFoundException
     */
    FullTableBuilder(OWLOntology ont, Statement stmt, boolean verbose) {
        this.ont = ont;
        this.stmt = stmt;
        this.verbose = verbose;
        ontClosure = ont.getImports();
        loggingEnabled = false;
        objPropDomains = new HashMap<OWLObjectProperty, HashSet<OWLClass>>();
        objPropRanges = new HashMap<OWLObjectProperty, HashSet<OWLClass>>();
        dataPropDomains = new HashMap<OWLDataProperty, HashSet<OWLClass>>();
        println("Initialized TableBuilder");
        logPath = "";
    }

    /**
     * Enables error logging to the given file during the table building process
     *
     * @param logFile - a File object representing the file to wish we wish to
     * write error logs
     * @throws IOException
     */
    public void enableErrorLogging(String logPath) throws IOException {
        File logFile = new File(logPath);
        if (logFile.exists()) {
            logFile.delete();
            println("Previous log file at " + logPath + " deleted");
        }
        logFile.createNewFile();
        println("New log file at " + logPath + " created");
        errorLogger = new BufferedWriter(new FileWriter(logFile));
        loggingEnabled = true;
        this.logPath = logPath;
        println("Error logging enabled");
    }

    /**
     * Outputs the given text to the error log if error logging is enabled.
     * Otherwise, does nothing.
     *
     * @param text
     */
    protected void logError(String text) {
        numBuildErrors++;
        if (loggingEnabled) {
            try {
                errorLogger.write(text + "\n");
            } catch (IOException e) {
                numLogErrors++;
            }
        }
    }

    /**
     * Prints empty string
     */
    protected void println() {
        if (verbose) {
            System.out.println();
        }
    }

    /**
     * Gives update
     *
     * @param update
     */
    protected void println(String line) {
        if (verbose) {
            System.out.println(line);
        }
    }

    /**
     * Prints progress bar i.e. updateProgress()
     *
     * @param update
     */
    protected void print(String update) {
        if (verbose) {
            System.out.print(update);
        }
    }

    /**
     * Initializes the tables of the SQL schema
     *
     * @throws SQLException
     */
    protected void initializeTables() throws SQLException {
        String datatype = Basics.DEFAULT_SQL_DATATYPE;

        println("Initializing SQL tables");

        stmt.execute(
                "CREATE TABLE Class ("
                + "name " + datatype + " NOT NULL,"
                + "PRIMARY KEY (name))");

        stmt.execute(
                "CREATE TABLE ClassRelationship ("
                + "subclass " + datatype + " NOT NULL,"
                + "superclass " + datatype + " NOT NULL,"
                + "PRIMARY KEY (subclass, superclass), "
                + "FOREIGN KEY (subclass) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (superclass) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");

        stmt.execute(
                "CREATE TABLE Individual ("
                + "name " + datatype + " NOT NULL,"
                + "class " + datatype + " NOT NULL,"
                + "PRIMARY KEY (name, class),"
                + "FOREIGN KEY (class) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");

        stmt.execute(
                "CREATE TABLE ObjectPropertyType ("
                + "name " + datatype + " NOT NULL, "
                + "isFunctional BOOLEAN NOT NULL, "
                + "isInverseFunctional BOOLEAN NOT NULL, "
                + "isSymmetric BOOLEAN NOT NULL,"
                + "isAsymmetric BOOLEAN NOT NULL, "
                + "isTransitive BOOLEAN NOT NULL,"
                + "isReflexive BOOLEAN NOT NULL, "
                + "isIrreflexive BOOLEAN NOT NULL, "
                + "PRIMARY KEY (name))");
        stmt.execute(
                "CREATE TABLE ObjectPropertyDomain ("
                + "domainClass " + datatype + " NOT NULL, "
                + "property " + datatype + " NOT NULL, "
                + "PRIMARY KEY (property, domainClass), "
                + "FOREIGN KEY (property) "
                + "REFERENCES ObjectPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (domainClass) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE )");
        stmt.execute(
                "CREATE TABLE ObjectPropertyRange ("
                + "property " + datatype + " NOT NULL, "
                + "rangeClass " + datatype + " NOT NULL, "
                + "PRIMARY KEY (property, rangeClass), "
                + "FOREIGN KEY (property) "
                + "REFERENCES ObjectPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (rangeClass) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE ObjectPropertyInstance ("
                + "id BIGINT NOT NULL AUTO_INCREMENT, "
                + "domainClass " + datatype + " NOT NULL,"
                + "domainIndividual " + datatype + " NOT NULL,"
                + "property " + datatype + " NOT NULL,"
                + "rangeClass " + datatype + " NOT NULL,"
                + "rangeIndividual " + datatype + " NOT NULL,"
                + "PRIMARY KEY (id), "
                + /*
                 "UNIQUE (domainIndividual, domainClass, rangeIndividual," +
                 "rangeClass, property)," + */ "FOREIGN KEY (domainIndividual, domainClass) REFERENCES "
                + "Individual(name, class) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (rangeIndividual, rangeClass) REFERENCES "
                + "Individual(name, class) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (property, domainClass) "
                + "REFERENCES ObjectPropertyDomain(property, domainClass) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (property, rangeClass) "
                + "REFERENCES ObjectPropertyRange(property, rangeClass) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE ObjectPropertyRelationship ("
                + "subproperty " + datatype + " NOT NULL, "
                + "superproperty " + datatype + " NOT NULL, "
                + "isInferred BOOLEAN DEFAULT false, "
                + "PRIMARY KEY (subproperty, superproperty), "
                + "FOREIGN KEY (subproperty) REFERENCES ObjectPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (superproperty) REFERENCES ObjectPropertyType(name)"
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE ObjectPropertyInverse ("
                + "property " + datatype + ", "
                + "inverseProperty " + datatype + ", "
                + "PRIMARY KEY (property, inverseProperty), "
                + "FOREIGN KEY (property) REFERENCES ObjectPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (inverseProperty) REFERENCES ObjectPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE DataPropertyType ("
                + "name " + datatype + " NOT NULL,"
                + "isFunctional BOOLEAN NOT NULL, "
                + "PRIMARY KEY (name))");
        stmt.execute(
                "CREATE TABLE DataPropertyDomain ("
                + "domainClass " + datatype + " NOT NULL, "
                + "property " + datatype + " NOT NULL, "
                + "PRIMARY KEY (property, domainClass), "
                + "FOREIGN KEY (property) "
                + "REFERENCES DataPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (domainClass) REFERENCES Class(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE DataPropertyRelationship ("
                + "subproperty " + datatype + " NOT NULL, "
                + "superproperty " + datatype + " NOT NULL, "
                + "isInferred BOOLEAN DEFAULT false, "
                + "PRIMARY KEY (subproperty, superproperty), "
                + "FOREIGN KEY (subproperty) REFERENCES DataPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (superproperty) REFERENCES DataPropertyType(name) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
        stmt.execute(
                "CREATE TABLE DataPropertyInstance ("
                + "id BIGINT NOT NULL AUTO_INCREMENT, "
                + "domainClass " + datatype + " NOT NULL,"
                + "domainIndividual " + datatype + " NOT NULL,"
                + "property " + datatype + " NOT NULL,"
                + "value TEXT NOT NULL, "
                + "PRIMARY KEY (id), "
                + "FOREIGN KEY (domainIndividual, domainClass) "
                + "REFERENCES Individual(name, class) "
                + "ON DELETE CASCADE ON UPDATE CASCADE, "
                + "FOREIGN KEY (property, domainClass) "
                + "REFERENCES DataPropertyDomain(property, domainClass) "
                + "ON DELETE CASCADE ON UPDATE CASCADE)");
    }

    /**
     * Populates the Class table with the names of each class in the ontology
     *
     * @throws SQLException
     */
    protected void handleClassSchema() throws SQLException {
        Set<OWLClass> owlClasses = ont.getClassesInSignature(true);
        HashMap<String, String> classFieldsMap = new HashMap<String, String>();
        int numOwlClasses = owlClasses.size();
        int prog = 0;

        /*
         * Initialize progress update
         */
        print("Building class schema --- 0 of " + numOwlClasses);

        for (OWLClass owlClass : owlClasses) {
            classFieldsMap.put("name", Utilities.getName(owlClass));
            stmt.execute(Utilities.getInsertString("Class", classFieldsMap));
            prog++;
            print("\rBuilding class schema --- " + prog + " of "
                    + numOwlClasses);
        }
        println();

        classFieldsMap = new HashMap<String, String>();
        for (OWLClass owlClass : owlClasses) {
            classFieldsMap.put("subclass", Utilities.getName(owlClass));
            for (OWLClassExpression superclassExp :
                    owlClass.getSuperClasses(ontClosure)) {
                for (OWLClass superclass :
                        Utilities.extractClasses(superclassExp)) {
                    classFieldsMap.put("superclass",
                            Utilities.getName(superclass));
                    stmt.execute(Utilities.getInsertString("ClassRelationship",
                            classFieldsMap));
                }
            }
        }
    }

    /**
     * Populates data for all object property types, domains, ranges, and
     * relationships
     *
     * @throws SQLException
     */
    protected void handleObjPropSchema() throws SQLException {
        String objPropName, supPropName;
        boolean fun, invFun, trans, sym, asym, ref, irref;
        int numSupProps, prog, numObjProps, numInvProps;

        HashSet<OWLClass> domainClasses, rangeClasses;
        HashMap<String, String> typeFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> domainFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> rangeFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> relFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> invFieldsMap =
                new HashMap<String, String>();
        HashSet<String> declaredSupPropStrings = new HashSet<String>();
        HashSet<String> invPropStrings = new HashSet<String>();
        HashSet<OWLObjectProperty> ancestorProps;
        Set<OWLObjectProperty> objProps = ont.getObjectPropertiesInSignature(true);

        /*
         * Initialize progress printout
         */
        prog = 0;
        numObjProps = objProps.size();
        print("Building object property schema --- 0 of "
                + numObjProps);

        /*
         * Begin looping through all object properties
         */
        for (OWLObjectProperty objProp : objProps) {
            domainClasses = new HashSet<OWLClass>();
            rangeClasses = new HashSet<OWLClass>();
            objPropName = Utilities.getName(objProp);
            fun = objProp.isFunctional(ontClosure);
            invFun = objProp.isInverseFunctional(ontClosure);
            trans = objProp.isTransitive(ontClosure);
            sym = objProp.isSymmetric(ontClosure);
            asym = objProp.isAsymmetric(ontClosure);
            ref = objProp.isReflexive(ontClosure);
            irref = objProp.isIrreflexive(ontClosure);
            /*
             * Update progress printout
             */
            prog++;
            print("\rBuilding object property schema --- " + prog
                    + " of " + numObjProps);

            /*
             * Handle entries into the ObjectPropertyType table
             */
            typeFieldsMap.put("name", objPropName);
            typeFieldsMap.put("isFunctional", String.valueOf(fun));
            typeFieldsMap.put("isInverseFunctional", String.valueOf(invFun));
            typeFieldsMap.put("isTransitive", String.valueOf(trans));
            typeFieldsMap.put("isSymmetric", String.valueOf(sym));
            typeFieldsMap.put("isAsymmetric", String.valueOf(asym));
            typeFieldsMap.put("isReflexive", String.valueOf(ref));
            typeFieldsMap.put("isIrreflexive", String.valueOf(irref));
            stmt.execute(Utilities.getInsertString("ObjectPropertyType",
                    typeFieldsMap));

            /*
             * Saves all explicitly declared super properties for later update 
             * execution. Also finds implicit super properties.
             */
            relFieldsMap.put("subproperty", objPropName);
            relFieldsMap.put("isInferred", "false");
            ancestorProps = Utilities.getSuperProps(objProp, ontClosure);
            ancestorProps.remove(objProp);

            for (OWLObjectPropertyExpression superPropExp :
                    objProp.getSuperProperties(ontClosure)) {
                if (superPropExp.isAnonymous()) {
                    logError(objPropName + " has anonymous superproperty "
                            + superPropExp + ". Cannot insert into the "
                            + "ObjectPropertyRelationship table.");
                } else {
                    ancestorProps.remove(superPropExp.asOWLObjectProperty());
                    supPropName = Utilities.getName(
                            superPropExp.asOWLObjectProperty());
                    relFieldsMap.put("superproperty", supPropName);
                    declaredSupPropStrings.add(Utilities.getInsertString(
                            "ObjectPropertyRelationship", relFieldsMap));
                }
            }

            /*
             * Saves all implicit super properties for later update execution.
             */

            relFieldsMap.put("isInferred", "true");
            for (OWLObjectProperty ancestorProp : ancestorProps) {
                relFieldsMap.put("superproperty", Utilities.getName(
                        ancestorProp));
                declaredSupPropStrings.add(Utilities.getInsertString(
                        "ObjectPropertyRelationship", relFieldsMap));
            }

            /*
             * Saves all inverse property declarations for later update 
             * execution.
             */
            invFieldsMap.put("property", objPropName);
            for (OWLObjectPropertyExpression invPropExp :
                    objProp.getInverses(ontClosure)) {
                if (invPropExp.isAnonymous()) {
                    logError("Object property " + objPropName + " has "
                            + "anonymous inverse " + invPropExp + ". Cannot "
                            + "insert into the ObjectPropertyInverse table.");
                } else {
                    invFieldsMap.put("inverseProperty", Utilities.getName(
                            invPropExp.asOWLObjectProperty()));
                    invPropStrings.add(Utilities.getInsertString(
                            "ObjectPropertyInverse", invFieldsMap));
                }
            }

            /*
             * Get all domains and ranges. Finds every class that is in the 
             * declared domain or range of each property and its 
             * super-properties.
             */
            for (OWLObjectProperty superProp : Utilities.getSuperProps(objProp,
                    ontClosure)) {
                for (OWLClassExpression domainExp :
                        superProp.getDomains(ontClosure)) {
                    for (OWLClass domain :
                            Utilities.extractClasses(domainExp)) {
                        domainClasses.addAll(Utilities.getSubClasses(domain,
                                ontClosure));
                    }
                }
                for (OWLClassExpression rangeExp :
                        superProp.getRanges(ontClosure)) {
                    for (OWLClass range : Utilities.extractClasses(rangeExp)) {
                        domainClasses.addAll(Utilities.getSubClasses(range,
                                ontClosure));
                    }
                }
            }

            /*
             * Populate the ObjectPropertyDomain and ObjectPropertyRange tables.
             * If the object property and its superproperties do not specify
             * a domain or range, then it is assumed that the domain or range
             * is global.
             */
            if (domainClasses.isEmpty()) {
                domainClasses.addAll(ont.getClassesInSignature(true));
            }
            if (rangeClasses.isEmpty()) {
                rangeClasses.addAll(ont.getClassesInSignature(true));
            }

            for (OWLClass domainClass : domainClasses) {
                domainFieldsMap.put("property", objPropName);
                domainFieldsMap.put("domainClass", Utilities.getName(
                        domainClass));
                stmt.execute(Utilities.getInsertString("ObjectPropertyDomain",
                        domainFieldsMap));
            }
            for (OWLClass rangeClass : rangeClasses) {
                rangeFieldsMap.put("property", objPropName);
                rangeFieldsMap.put("rangeClass", Utilities.getName(
                        rangeClass));
                stmt.execute(Utilities.getInsertString("ObjectPropertyRange",
                        rangeFieldsMap));
            }

            /*
             * Insert into object property domain and range hashmaps
             */
            objPropDomains.put(objProp, new HashSet<OWLClass>());
            objPropRanges.put(objProp, new HashSet<OWLClass>());
            objPropDomains.get(objProp).addAll(domainClasses);
            objPropRanges.get(objProp).addAll(rangeClasses);
        }

        /*
         * Initialize next progress printout
         */
        prog = 0;
        numSupProps = declaredSupPropStrings.size();
        println();
        print("Populating object property relationships --- 0 of "
                + numSupProps);

        /*
         * Executes the declared superproperty updates
         */
        for (String declaredSupPropString : declaredSupPropStrings) {
            stmt.execute(declaredSupPropString);
            prog++;
            print(
                    "\rPopulating object property relationships --- " + prog
                    + " of " + numSupProps);
        }

        /*
         * Initialize next progress printout
         */
        prog = 0;
        numInvProps = invPropStrings.size();
        println();
        print("Populating object property inverses --- 0 of "
                + numInvProps);

        /*
         * Executes the declared inverse property updates
         */
        for (String invPropString : invPropStrings) {
            prog++;
            print("\rPopulating object property inverses --- " + prog
                    + " of " + numInvProps);
            stmt.execute(invPropString);
        }
        println();
    }

    /**
     * Populates data for all data property types, domains, and relationships
     *
     * @throws SQLException
     */
    protected void handleDataPropSchema() throws SQLException {
        String dataPropName, supPropName;
        HashSet<OWLClass> domainClasses;
        HashSet<OWLDataProperty> ancestorProps;
        boolean fun;
        int prog, numSupProps, numDataProps;

        HashMap<String, String> typeFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> domainFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> relFieldsMap =
                new HashMap<String, String>();
        HashSet<String> declaredSupPropStrings = new HashSet<String>();
        Set<OWLDataProperty> dataProps = ont.getDataPropertiesInSignature(true);

        /*
         * Initialize progress printout
         */
        prog = 0;
        numDataProps = dataProps.size();
        print("Building data property schema --- 0 of "
                + numDataProps);

        for (OWLDataProperty dataProp : dataProps) {
            dataPropName = Utilities.getName(dataProp);
            domainClasses = new HashSet<OWLClass>();
            fun = dataProp.isFunctional(ontClosure);

            /*
             * Update progress printout
             */
            prog++;
            print("\rBuilding data property schema --- " + prog
                    + " of " + numDataProps);

            /*
             * Handles entries into the DataPropertyType table
             */
            typeFieldsMap.put("name", dataPropName);
            typeFieldsMap.put("isFunctional", String.valueOf(fun));
            stmt.execute(Utilities.getInsertString("DataPropertyType",
                    typeFieldsMap));

            /*
             * Saves all declared super properties for later update execution.
             * Also finds implict super properties.
             */
            relFieldsMap.put("subproperty", dataPropName);
            relFieldsMap.put("isInferred", "false");
            ancestorProps = Utilities.getSuperProps(dataProp, ontClosure);
            ancestorProps.remove(dataProp);
            for (OWLDataPropertyExpression superPropExp :
                    dataProp.getSuperProperties(ontClosure)) {
                if (superPropExp.isAnonymous()) {
                    logError("Data property " + dataPropName
                            + " has anonymous super property" + superPropExp
                            + ". Cannot insert into DataPropertyRelationship "
                            + "table.");
                } else {
                    ancestorProps.remove(superPropExp.asOWLDataProperty());
                    supPropName = Utilities.getName(
                            superPropExp.asOWLDataProperty());
                    relFieldsMap.put("superproperty", supPropName);
                    declaredSupPropStrings.add(Utilities.getInsertString(
                            "DataPropertyRelationship", relFieldsMap));
                }
            }

            /*
             * Saves all implict super properties for later update execution
             */
            relFieldsMap.put("isInferred", "true");
            for (OWLDataProperty ancestorProp : ancestorProps) {
                relFieldsMap.put("superproperty", Utilities.getName(
                        ancestorProp));
                declaredSupPropStrings.add(Utilities.getInsertString(
                        "DataPropertyRelationship", relFieldsMap));
            }

            /*
             * Gets all domains. Finds every class that is in the domain of each 
             * property and its super-properties.
             */
            for (OWLDataProperty supProp : Utilities.getSuperProps(dataProp,
                    ontClosure)) {
                for (OWLClassExpression domainClassExp :
                        supProp.getDomains(ont)) {
                    domainClasses.addAll(Utilities.extractClasses(
                            domainClassExp));
                }
            }

            /*
             * Populates the DataPropertyDomain table. If the data property and 
             * its superproperties do not specify a domain or range, then it is 
             * assumed that the domain or range is global.
             */
            if (domainClasses.isEmpty()) {
                domainClasses.addAll(ont.getClassesInSignature(true));
            }
            for (OWLClass domainClass : domainClasses) {
                domainFieldsMap.put("property", dataPropName);
                domainFieldsMap.put("domainClass", Utilities.getName(
                        domainClass));
                stmt.execute(Utilities.getInsertString("DataPropertyDomain",
                        domainFieldsMap));
            }

            /*
             * Insert into data property domain hashmap
             */
            dataPropDomains.put(dataProp, new HashSet<OWLClass>());
            dataPropDomains.get(dataProp).addAll(domainClasses);
        }

        /*
         * Initializing next progress printout
         */
        println();
        prog = 0;
        numSupProps = declaredSupPropStrings.size();
        print("Populating data property relationships --- 0 of "
                + numSupProps);

        /*
         * Executes the declared superproperty updates
         */
        for (String declaredSupPropString : declaredSupPropStrings) {
            stmt.execute(declaredSupPropString);
            prog++;
            print(
                    "\rPopulating data property relationships --- " + prog
                    + " of " + numSupProps);
        }
        println();
    }

    /**
     * Populates data for all named individuals and their data and object
     * properties
     *
     * @throws SQLException
     */
    protected void handleInstances() throws SQLException {
        String indName, rangeIndName, className, dataPropName, objPropName,
                rangeClassName, insertStmt;
        OWLDataProperty dataProp;
        OWLObjectProperty objProp;
        OWLNamedIndividual namedInd, namedRangeInd;
        OWLClass rangeClass;
        int numInds, numObjPropInsts, prog;

        OWLClass owlClass = null;
        OWLClassExpression rangeClassExp = null;
        OWLClassExpression classExp = null;
        HashMap<String, String> indFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> dataPropFieldsMap =
                new HashMap<String, String>();
        HashMap<String, String> objPropFieldsMap =
                new HashMap<String, String>();
        Map<OWLDataPropertyExpression, Set<OWLLiteral>> dataPropMap;
        Map<OWLObjectPropertyExpression, Set<OWLIndividual>> objPropMap;
        LinkedList<String> objPropInsertStrings = new LinkedList<String>();
        Set<OWLNamedIndividual> inds = ont.getIndividualsInSignature(true);

        /*
         * Initialize progress print to STDOUT
         */
        prog = 0;
        numInds = inds.size();
        print("Populating individuals and data "
                + "property instances --- 0 of " + numInds);

        /*
         * Begin iterating through all individuals
         */
        for (OWLIndividual ind : inds) {
            /*
             * Check for anonymity
             */
            if (ind.isAnonymous()) {
                logError(ind + " is anonymous. Cannot insert into Individual"
                        + " table.");
                continue;
            }

            /*
             * Check if individual has either no class or more than one 
             * class. If so, skip this individual. If not, extract the class
             */
            namedInd = ind.asOWLNamedIndividual();
            indName = Utilities.getName(namedInd);
            if (namedInd.getTypes(ont).size() == 0) {
                logError(indName + " has no classes. Cannot insert into "
                        + "Individual table.");
                continue;
            } else if (namedInd.getTypes(ont).size() > 1) {
                logError(indName + " has more than one class. "
                        + "Cannot insert into Individual table.");
                continue;
            }
            for (OWLClassExpression singleClassExp :
                    namedInd.getTypes(ont)) {
                classExp = singleClassExp;
            }
            if (classExp.isAnonymous()) {
                logError(indName + " has anonymous class " + classExp
                        + ". Cannot insert into Individual table.");
                continue;
            }
            owlClass = classExp.asOWLClass();
            className = Utilities.getName(owlClass);
            dataPropFieldsMap.put("domainClass", className);
            objPropFieldsMap.put("domainClass", className);

            /*
             * Populate Individual table
             */
            indName = Utilities.getName(ind.asOWLNamedIndividual());
            indFieldsMap.put("name", indName);
            indFieldsMap.put("class", className);
            String query = Utilities.getInsertString("Individual",
                    indFieldsMap);
            try {
                stmt.execute(query);
            } catch (SQLException e) {
                System.err.println("Error with query: " + query);
                throw e;
            }

            /*
             * Populate DataPropertyInstance table
             */
            dataPropFieldsMap.put("domainIndividual", indName);
            dataPropMap = ind.getDataPropertyValues(ont);
            for (OWLDataPropertyExpression dataPropExp : dataPropMap.keySet()) {
                if (dataPropExp.isAnonymous()) {
                    logError(indName + " has anonymous data property "
                            + dataPropExp.toString() + ". Cannot insert into "
                            + "the DataPropertyInstance table");
                    continue;
                }
                dataProp = dataPropExp.asOWLDataProperty();
                dataPropName = Utilities.getName(dataProp);
                dataPropFieldsMap.put("property", dataPropName);

                /*
                 * Check if this object is in the domain of the data 
                 * property. If not, report it and skip the data property.
                 */
                if (!dataPropDomains.get(dataProp).contains(owlClass)) {
                    logError(indName + " of class " + className
                            + " is not in the domain of data property "
                            + dataPropName
                            + ". Cannot insert into DataPropertyInstance table.");
                    continue;
                }

                for (OWLLiteral valueLit : dataPropMap.get(dataPropExp)) {
                    dataPropFieldsMap.put("value",
                            Utilities.format(valueLit.toString()));
                    insertStmt = Utilities.getInsertString(
                            "DataPropertyInstance", dataPropFieldsMap);
                    try {
                        stmt.execute(insertStmt);
                    } catch (Exception e) {
                        System.err.println(insertStmt);
                        e.printStackTrace();
                        System.exit(1);
                    }
                }
            }

            /*
             * Save all object property instances for later execution
             */
            objPropFieldsMap.put("domainIndividual", indName);
            objPropMap = ind.getObjectPropertyValues(ont);
            for (OWLObjectPropertyExpression objPropExp : objPropMap.keySet()) {
                if (objPropExp.isAnonymous()) {
                    logError(indName + " has anonymous object property "
                            + objPropExp + ". Cannot insert into the "
                            + "ObjectPropertyInstance table.");
                    continue;
                }
                objProp = objPropExp.asOWLObjectProperty();
                objPropName = Utilities.getName(objProp);
                objPropFieldsMap.put("property", objPropName);

                /*
                 * Check if this object is in the domain of the object 
                 * property. If not, report it and skip the object property.
                 */
                if (!objPropDomains.get(objProp).contains(owlClass)) {
                    logError(indName + " of class " + className
                            + " is not in the domain of object property "
                            + objPropName + ". Cannot insert into the "
                            + "ObjectPropertyInstance table.");
                    continue;
                }

                for (OWLIndividual rangeInd : objPropMap.get(objPropExp)) {
                    if (rangeInd.isAnonymous()) {
                        logError(rangeInd + " is the anonymous individual "
                                + "mapped to " + indName + " by object property"
                                + objPropName + ". Cannot insert into the "
                                + "ObjectPropertyInstance table.");
                        continue;
                    }
                    namedRangeInd = rangeInd.asOWLNamedIndividual();
                    rangeIndName = Utilities.getName(namedRangeInd);
                    objPropFieldsMap.put("rangeIndividual", rangeIndName);

                    /*
                     * Check if the range individual has more than one class. If so,
                     * skip this object property. If not, extract its class.
                     */
                    if (rangeInd.getTypes(ont).size() > 1) {
                        logError(rangeIndName + " of class "
                                + rangeInd.getTypes(ont)
                                + " has more than one class and is mapped to "
                                + indName + " by object property " + objPropName
                                + ". Cannot insert into ObjectPropertyInstance "
                                + " table");
                        continue;
                    }
                    for (OWLClassExpression singleClassExp :
                            rangeInd.getTypes(ont)) {
                        rangeClassExp = singleClassExp;
                    }
                    if (rangeClassExp.isAnonymous()) {
                        logError(rangeIndName + " of class " + rangeClassExp
                                + " has an anonymous class and is mapped to "
                                + indName + " by object property " + objPropName
                                + ". Cannot insert into ObjectPropertyInstance "
                                + " table");
                        continue;
                    }
                    rangeClass = rangeClassExp.asOWLClass();
                    rangeClassName = Utilities.getName(rangeClass);

                    /*
                     * Check if this object is in the domain of the object 
                     * property. If not, report it and skip the object property.
                     */
                    if (!objPropRanges.get(objProp).contains(rangeClass)) {
                        logError(rangeIndName + " of class " + rangeClassName
                                + " is mapped to " + indName + " by "
                                + objPropName + " but is not in the object "
                                + "property's range. Cannot insert into the "
                                + "ObjectPropertyInstance table.");
                        continue;
                    }

                    objPropFieldsMap.put("rangeClass", rangeClassName);
                    objPropInsertStrings.add(Utilities.getInsertString(
                            "ObjectPropertyInstance", objPropFieldsMap));
                }
            }
            /*
             * Update progress printout
             */
            prog++;
            print("\rPopulating individuals and data "
                    + "property instances --- " + prog + " of " + numInds);
        }

        /*
         * Initialize next progress printout
         */
        println();
        prog = 0;
        numObjPropInsts = objPropInsertStrings.size();
        print("Populating object property instances --- 0 of "
                + numObjPropInsts);
        for (String objPropInsertString : objPropInsertStrings) {
            try {
                stmt.execute(objPropInsertString);
            } catch (MySQLIntegrityConstraintViolationException e) {
                logError("The insert statement '" + objPropInsertString
                        + "' caused an integrity constraint violation. It did not affect the database");
            }
            prog++;
            print("\rPopulating object property instances --- "
                    + prog + " of " + numObjPropInsts);
        }
        println();
    }

    protected void handleAnnotationSchema() {
    }

    /**
     * Reports number of errors encountered during the building
     *
     * @throws
     */
    protected void report() {
        if (loggingEnabled) {
            try {
                errorLogger.close();
            } catch (IOException e) {
                numLogErrors++;
            }
        }
        println("Finished building database with " + numBuildErrors
                + " skipped entries due to building errors");
        if (loggingEnabled) {
            println("Logged " + (numBuildErrors - numLogErrors)
                    + " build errors to " + logPath + " with " + numLogErrors
                    + " skipped log entries");
        }
    }

    /**
     * Creates the SQL schema and populates data on the OWL class, data
     * property, and object property schemas and reports time taken
     *
     * @throws SQLException
     */
    public void build() throws SQLException {
        long startTimeMS, endTimeMS;
        int totalTimeS;
        startTimeMS = System.currentTimeMillis();
        initializeTables();
        handleClassSchema();
        handleObjPropSchema();
        handleDataPropSchema();
        handleAnnotationSchema();
        handleInstances();
        report();
        endTimeMS = System.currentTimeMillis();
        totalTimeS = (int) ((endTimeMS - startTimeMS) / 1000);
        println("Build completed in " + totalTimeS + " seconds");
    }
}
