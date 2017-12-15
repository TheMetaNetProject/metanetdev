package edu.berkeley.icsi.metanet.repository;

import java.util.Collection;

import org.protege.owl.codegeneration.WrappedIndividual;

import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * 
 * <p>
 * Generated by Protege (http://protege.stanford.edu). <br>
 * Source Class: Entailment <br>
 * @version generated on Tue Mar 05 15:42:49 PST 2013 by jhong
 */

public interface Entailment extends WrappedIndividual {

    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#dependsOnMappings
     */
     
    /**
     * Gets all property values for the dependsOnMappings property.<p>
     * 
     * @returns a collection of values for the dependsOnMappings property.
     */
    Collection<? extends Mapping> getDependsOnMappings();

    /**
     * Checks if the class has a dependsOnMappings property value.<p>
     * 
     * @return true if there is a dependsOnMappings property value.
     */
    boolean hasDependsOnMappings();

    /**
     * Adds a dependsOnMappings property value.<p>
     * 
     * @param newDependsOnMappings the dependsOnMappings property value to be added
     */
    void addDependsOnMappings(Mapping newDependsOnMappings);

    /**
     * Removes a dependsOnMappings property value.<p>
     * 
     * @param oldDependsOnMappings the dependsOnMappings property value to be removed.
     */
    void removeDependsOnMappings(Mapping oldDependsOnMappings);


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
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasSourceInference
     */
     
    /**
     * Gets the property value for the hasSourceInference functional property.<p>
     * 
     * @returns a value for the hasSourceInference property or null
     */
    Inference getHasSourceInference();

    /**
     * Checks if the class has a hasSourceInference property value.<p>
     * 
     * @return true if there is a hasSourceInference property value.
     */
    boolean hasHasSourceInference();

    /**
     * Adds a hasSourceInference property value.<p>
     * 
     * @param newHasSourceInference the hasSourceInference property value to be added
     */
    void addHasSourceInference(Inference newHasSourceInference);

    /**
     * Removes a hasSourceInference property value.<p>
     * 
     * @param oldHasSourceInference the hasSourceInference property value to be removed.
     */
    void removeHasSourceInference(Inference oldHasSourceInference);


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasTargetInference
     */
     
    /**
     * Gets the property value for the hasTargetInference functional property.<p>
     * 
     * @returns a value for the hasTargetInference property or null
     */
    Inference getHasTargetInference();

    /**
     * Checks if the class has a hasTargetInference property value.<p>
     * 
     * @return true if there is a hasTargetInference property value.
     */
    boolean hasHasTargetInference();

    /**
     * Adds a hasTargetInference property value.<p>
     * 
     * @param newHasTargetInference the hasTargetInference property value to be added
     */
    void addHasTargetInference(Inference newHasTargetInference);

    /**
     * Removes a hasTargetInference property value.<p>
     * 
     * @param oldHasTargetInference the hasTargetInference property value to be removed.
     */
    void removeHasTargetInference(Inference oldHasTargetInference);


    /* ***************************************************
     * Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isEntailmentOfMetaphor
     */
     
    /**
     * Gets all property values for the isEntailmentOfMetaphor property.<p>
     * 
     * @returns a collection of values for the isEntailmentOfMetaphor property.
     */
    Collection<? extends Metaphor> getIsEntailmentOfMetaphor();

    /**
     * Checks if the class has a isEntailmentOfMetaphor property value.<p>
     * 
     * @return true if there is a isEntailmentOfMetaphor property value.
     */
    boolean hasIsEntailmentOfMetaphor();

    /**
     * Adds a isEntailmentOfMetaphor property value.<p>
     * 
     * @param newIsEntailmentOfMetaphor the isEntailmentOfMetaphor property value to be added
     */
    void addIsEntailmentOfMetaphor(Metaphor newIsEntailmentOfMetaphor);

    /**
     * Removes a isEntailmentOfMetaphor property value.<p>
     * 
     * @param oldIsEntailmentOfMetaphor the isEntailmentOfMetaphor property value to be removed.
     */
    void removeIsEntailmentOfMetaphor(Metaphor oldIsEntailmentOfMetaphor);


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