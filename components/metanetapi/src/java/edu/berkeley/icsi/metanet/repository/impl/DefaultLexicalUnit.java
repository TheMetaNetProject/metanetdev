package edu.berkeley.icsi.metanet.repository.impl;

import edu.berkeley.icsi.metanet.repository.*;

import java.util.Collection;

import org.protege.owl.codegeneration.WrappedIndividual;
import org.protege.owl.codegeneration.impl.WrappedIndividualImpl;
import org.protege.owl.codegeneration.inference.CodeGenerationInference;

import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLOntology;


/**
 * Generated by Protege (http://protege.stanford.edu).<br>
 * Source Class: DefaultLexicalUnit <br>
 * @version generated on Tue Mar 05 15:42:49 PST 2013 by jhong
 */
public class DefaultLexicalUnit extends WrappedIndividualImpl implements LexicalUnit {

    public DefaultLexicalUnit(OWLOntology ontology, IRI iri, CodeGenerationInference inf) {
        super(ontology, iri, inf);
    }





    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasExample
     */
     
    public Collection<? extends Example> getHasExample() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASEXAMPLE,
                                               DefaultExample.class);
    }

    public boolean hasHasExample() {
	   return !getHasExample().isEmpty();
    }

    public void addHasExample(Example newHasExample) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASEXAMPLE,
                                       newHasExample);
    }

    public void removeHasExample(Example oldHasExample) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASEXAMPLE,
                                          oldHasExample);
    }


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isDefinedRelativeToSchema
     */
     
    public Schema getIsDefinedRelativeToSchema() {
        // For functional object properties, return the first one or null
        Collection<? extends Schema>c = getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISDEFINEDRELATIVETOSCHEMA,
                                               DefaultSchema.class);
        if (c.isEmpty()) return null;
        return (Schema)c.iterator().next();
    }

    public boolean hasIsDefinedRelativeToSchema() {
	   return getIsDefinedRelativeToSchema() != null;
    }

    public void addIsDefinedRelativeToSchema(Schema newIsDefinedRelativeToSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISDEFINEDRELATIVETOSCHEMA,
                                       newIsDefinedRelativeToSchema);
    }

    public void removeIsDefinedRelativeToSchema(Schema oldIsDefinedRelativeToSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISDEFINEDRELATIVETOSCHEMA,
                                          oldIsDefinedRelativeToSchema);
    }


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasAlias
     */
     
    public Collection<? extends String> getHasAlias() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASALIAS, String.class);
    }

    public boolean hasHasAlias() {
		return !getHasAlias().isEmpty();
    }

    public void addHasAlias(Object newHasAlias) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASALIAS, newHasAlias);
    }

    public void removeHasAlias(Object oldHasAlias) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASALIAS, oldHasAlias);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasLemma
     */
     
    public String getHasLemma() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASLEMMA, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasLemma() {
	return getHasLemma() != null;
    }

    public void addHasLemma(String newHasLemma) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASLEMMA, newHasLemma);
    }

    public void removeHasLemma(String oldHasLemma) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASLEMMA, oldHasLemma);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasName
     */
     
    public String getHasName() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAME, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasName() {
	return getHasName() != null;
    }

    public void addHasName(String newHasName) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAME, newHasName);
    }

    public void removeHasName(String oldHasName) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAME, oldHasName);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasNameGloss
     */
     
    public String getHasNameGloss() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAMEGLOSS, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasNameGloss() {
	return getHasNameGloss() != null;
    }

    public void addHasNameGloss(String newHasNameGloss) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAMEGLOSS, newHasNameGloss);
    }

    public void removeHasNameGloss(String oldHasNameGloss) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASNAMEGLOSS, oldHasNameGloss);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isFromLanguage
     */
     
    public String getIsFromLanguage() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISFROMLANGUAGE, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasIsFromLanguage() {
	return getIsFromLanguage() != null;
    }

    public void addIsFromLanguage(String newIsFromLanguage) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISFROMLANGUAGE, newIsFromLanguage);
    }

    public void removeIsFromLanguage(String oldIsFromLanguage) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISFROMLANGUAGE, oldIsFromLanguage);
    }


}
