package edu.berkeley.icsi.metanet.repository;

import java.util.Collection;

import org.protege.owl.codegeneration.WrappedIndividual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * 
 * <p>
 * Generated by Protege (http://protege.stanford.edu). <br>
 * Source Class: SchemaFamily <br>
 * @version generated on Tue Mar 05 15:42:50 PST 2013 by jhong
 */

public interface SchemaFamily extends WrappedIndividual {

    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasExample
     */
     
    /**
     * Gets all property values for the hasExample property.<p>
     * 
     * @returns a collection of values for the hasExample property.
     */
    Collection<? extends Example> getHasExample();

    /**
     * Checks if the class has a hasExample property value.<p>
     * 
     * @return true if there is a hasExample property value.
     */
    boolean hasHasExample();

    /**
     * Adds a hasExample property value.<p>
     * 
     * @param newHasExample the hasExample property value to be added
     */
    void addHasExample(Example newHasExample);

    /**
     * Removes a hasExample property value.<p>
     * 
     * @param oldHasExample the hasExample property value to be removed.
     */
    void removeHasExample(Example oldHasExample);


    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasSchemas
     */
     
    /**
     * Gets all property values for the hasSchemas property.<p>
     * 
     * @returns a collection of values for the hasSchemas property.
     */
    Collection<? extends Schema> getHasSchemas();

    /**
     * Checks if the class has a hasSchemas property value.<p>
     * 
     * @return true if there is a hasSchemas property value.
     */
    boolean hasHasSchemas();

    /**
     * Adds a hasSchemas property value.<p>
     * 
     * @param newHasSchemas the hasSchemas property value to be added
     */
    void addHasSchemas(Schema newHasSchemas);

    /**
     * Removes a hasSchemas property value.<p>
     * 
     * @param oldHasSchemas the hasSchemas property value to be removed.
     */
    void removeHasSchemas(Schema oldHasSchemas);


    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSchemaSubfamilyOf
     */
     
    /**
     * Gets all property values for the isSchemaSubfamilyOf property.<p>
     * 
     * @returns a collection of values for the isSchemaSubfamilyOf property.
     */
    Collection<? extends SchemaFamily> getIsSchemaSubfamilyOf();

    /**
     * Checks if the class has a isSchemaSubfamilyOf property value.<p>
     * 
     * @return true if there is a isSchemaSubfamilyOf property value.
     */
    boolean hasIsSchemaSubfamilyOf();

    /**
     * Adds a isSchemaSubfamilyOf property value.<p>
     * 
     * @param newIsSchemaSubfamilyOf the isSchemaSubfamilyOf property value to be added
     */
    void addIsSchemaSubfamilyOf(SchemaFamily newIsSchemaSubfamilyOf);

    /**
     * Removes a isSchemaSubfamilyOf property value.<p>
     * 
     * @param oldIsSchemaSubfamilyOf the isSchemaSubfamilyOf property value to be removed.
     */
    void removeIsSchemaSubfamilyOf(SchemaFamily oldIsSchemaSubfamilyOf);


    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSchemaSuperfamilyOf
     */
     
    /**
     * Gets all property values for the isSchemaSuperfamilyOf property.<p>
     * 
     * @returns a collection of values for the isSchemaSuperfamilyOf property.
     */
    Collection<? extends SchemaFamily> getIsSchemaSuperfamilyOf();

    /**
     * Checks if the class has a isSchemaSuperfamilyOf property value.<p>
     * 
     * @return true if there is a isSchemaSuperfamilyOf property value.
     */
    boolean hasIsSchemaSuperfamilyOf();

    /**
     * Adds a isSchemaSuperfamilyOf property value.<p>
     * 
     * @param newIsSchemaSuperfamilyOf the isSchemaSuperfamilyOf property value to be added
     */
    void addIsSchemaSuperfamilyOf(SchemaFamily newIsSchemaSuperfamilyOf);

    /**
     * Removes a isSchemaSuperfamilyOf property value.<p>
     * 
     * @param oldIsSchemaSuperfamilyOf the isSchemaSuperfamilyOf property value to be removed.
     */
    void removeIsSchemaSuperfamilyOf(SchemaFamily oldIsSchemaSuperfamilyOf);


    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasAlias
     */
     
    /**
     * Gets all property values for the hasAlias property.<p>
     * 
     * @returns a collection of values for the hasAlias property.
     */
    Collection<? extends String> getHasAlias();

    /**
     * Checks if the class has a hasAlias property value.<p>
     * 
     * @return true if there is a hasAlias property value.
     */
    boolean hasHasAlias();

    /**
     * Adds a hasAlias property value.<p>
     * 
     * @param newHasAlias the hasAlias property value to be added
     */
    void addHasAlias(Object newHasAlias);

    /**
     * Removes a hasAlias property value.<p>
     * 
     * @param oldHasAlias the hasAlias property value to be removed.
     */
    void removeHasAlias(Object oldHasAlias);



    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasName
     */
     
    /**
     * Gets the value for the hasName functional property.<p>
     * 
     * @returns the value for the hasName property or null
     */
    String getHasName();

    /**
     * Checks if the class has a hasName property value.<p>
     * 
     * @return true if there is a hasName property value.
     */
    boolean hasHasName();

    /**
     * Adds a hasName property value.<p>
     * 
     * @param newHasName the hasName property value to be added
     */
    void addHasName(String newHasName);

    /**
     * Removes a hasName property value.<p>
     * 
     * @param oldHasName the hasName property value to be removed.
     */
    void removeHasName(String oldHasName);



    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasNameGloss
     */
     
    /**
     * Gets the value for the hasNameGloss functional property.<p>
     * 
     * @returns the value for the hasNameGloss property or null
     */
    String getHasNameGloss();

    /**
     * Checks if the class has a hasNameGloss property value.<p>
     * 
     * @return true if there is a hasNameGloss property value.
     */
    boolean hasHasNameGloss();

    /**
     * Adds a hasNameGloss property value.<p>
     * 
     * @param newHasNameGloss the hasNameGloss property value to be added
     */
    void addHasNameGloss(String newHasNameGloss);

    /**
     * Removes a hasNameGloss property value.<p>
     * 
     * @param oldHasNameGloss the hasNameGloss property value to be removed.
     */
    void removeHasNameGloss(String oldHasNameGloss);



    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isFromLanguage
     */
     
    /**
     * Gets the value for the isFromLanguage functional property.<p>
     * 
     * @returns the value for the isFromLanguage property or null
     */
    String getIsFromLanguage();

    /**
     * Checks if the class has a isFromLanguage property value.<p>
     * 
     * @return true if there is a isFromLanguage property value.
     */
    boolean hasIsFromLanguage();

    /**
     * Adds a isFromLanguage property value.<p>
     * 
     * @param newIsFromLanguage the isFromLanguage property value to be added
     */
    void addIsFromLanguage(String newIsFromLanguage);

    /**
     * Removes a isFromLanguage property value.<p>
     * 
     * @param oldIsFromLanguage the isFromLanguage property value to be removed.
     */
    void removeIsFromLanguage(String oldIsFromLanguage);



    /* ***************************************************
     * Common interfaces
     */

    OWLNamedIndividual getOwlIndividual();

    OWLOntology getOwlOntology();

    void delete();

}
