package edu.berkeley.icsi.metanet.repository;

import java.util.Collection;

import org.protege.owl.codegeneration.WrappedIndividual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * 
 * <p>
 * Generated by Protege (http://protege.stanford.edu). <br>
 * Source Class: Inference <br>
 * @version generated on Tue Mar 05 15:42:49 PST 2013 by jhong
 */

public interface Inference extends WrappedIndividual {

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
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isInferenceOfSchema
     */
     
    /**
     * Gets all property values for the isInferenceOfSchema property.<p>
     * 
     * @returns a collection of values for the isInferenceOfSchema property.
     */
    Collection<? extends Schema> getIsInferenceOfSchema();

    /**
     * Checks if the class has a isInferenceOfSchema property value.<p>
     * 
     * @return true if there is a isInferenceOfSchema property value.
     */
    boolean hasIsInferenceOfSchema();

    /**
     * Adds a isInferenceOfSchema property value.<p>
     * 
     * @param newIsInferenceOfSchema the isInferenceOfSchema property value to be added
     */
    void addIsInferenceOfSchema(Schema newIsInferenceOfSchema);

    /**
     * Removes a isInferenceOfSchema property value.<p>
     * 
     * @param oldIsInferenceOfSchema the isInferenceOfSchema property value to be removed.
     */
    void removeIsInferenceOfSchema(Schema oldIsInferenceOfSchema);


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSourceInferenceOf
     */
     
    /**
     * Gets the property value for the isSourceInferenceOf functional property.<p>
     * 
     * @returns a value for the isSourceInferenceOf property or null
     */
    Entailment getIsSourceInferenceOf();

    /**
     * Checks if the class has a isSourceInferenceOf property value.<p>
     * 
     * @return true if there is a isSourceInferenceOf property value.
     */
    boolean hasIsSourceInferenceOf();

    /**
     * Adds a isSourceInferenceOf property value.<p>
     * 
     * @param newIsSourceInferenceOf the isSourceInferenceOf property value to be added
     */
    void addIsSourceInferenceOf(Entailment newIsSourceInferenceOf);

    /**
     * Removes a isSourceInferenceOf property value.<p>
     * 
     * @param oldIsSourceInferenceOf the isSourceInferenceOf property value to be removed.
     */
    void removeIsSourceInferenceOf(Entailment oldIsSourceInferenceOf);


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTargetInferenceOf
     */
     
    /**
     * Gets the property value for the isTargetInferenceOf functional property.<p>
     * 
     * @returns a value for the isTargetInferenceOf property or null
     */
    Entailment getIsTargetInferenceOf();

    /**
     * Checks if the class has a isTargetInferenceOf property value.<p>
     * 
     * @return true if there is a isTargetInferenceOf property value.
     */
    boolean hasIsTargetInferenceOf();

    /**
     * Adds a isTargetInferenceOf property value.<p>
     * 
     * @param newIsTargetInferenceOf the isTargetInferenceOf property value to be added
     */
    void addIsTargetInferenceOf(Entailment newIsTargetInferenceOf);

    /**
     * Removes a isTargetInferenceOf property value.<p>
     * 
     * @param oldIsTargetInferenceOf the isTargetInferenceOf property value to be removed.
     */
    void removeIsTargetInferenceOf(Entailment oldIsTargetInferenceOf);


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
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasInferenceType
     */
     
    /**
     * Gets the value for the hasInferenceType functional property.<p>
     * 
     * @returns the value for the hasInferenceType property or null
     */
    Object getHasInferenceType();

    /**
     * Checks if the class has a hasInferenceType property value.<p>
     * 
     * @return true if there is a hasInferenceType property value.
     */
    boolean hasHasInferenceType();

    /**
     * Adds a hasInferenceType property value.<p>
     * 
     * @param newHasInferenceType the hasInferenceType property value to be added
     */
    void addHasInferenceType(Object newHasInferenceType);

    /**
     * Removes a hasInferenceType property value.<p>
     * 
     * @param oldHasInferenceType the hasInferenceType property value to be removed.
     */
    void removeHasInferenceType(Object oldHasInferenceType);



    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasInferentialContent
     */
     
    /**
     * Gets the value for the hasInferentialContent functional property.<p>
     * 
     * @returns the value for the hasInferentialContent property or null
     */
    String getHasInferentialContent();

    /**
     * Checks if the class has a hasInferentialContent property value.<p>
     * 
     * @return true if there is a hasInferentialContent property value.
     */
    boolean hasHasInferentialContent();

    /**
     * Adds a hasInferentialContent property value.<p>
     * 
     * @param newHasInferentialContent the hasInferentialContent property value to be added
     */
    void addHasInferentialContent(String newHasInferentialContent);

    /**
     * Removes a hasInferentialContent property value.<p>
     * 
     * @param oldHasInferentialContent the hasInferentialContent property value to be removed.
     */
    void removeHasInferentialContent(String oldHasInferentialContent);



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