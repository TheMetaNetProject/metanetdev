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
 * Source Class: DefaultInference <br>
 * @version generated on Tue Mar 05 15:42:49 PST 2013 by jhong
 */
public class DefaultInference extends WrappedIndividualImpl implements Inference {

    public DefaultInference(OWLOntology ontology, IRI iri, CodeGenerationInference inf) {
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
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isInferenceOfSchema
     */
     
    public Collection<? extends Schema> getIsInferenceOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISINFERENCEOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsInferenceOfSchema() {
	   return !getIsInferenceOfSchema().isEmpty();
    }

    public void addIsInferenceOfSchema(Schema newIsInferenceOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISINFERENCEOFSCHEMA,
                                       newIsInferenceOfSchema);
    }

    public void removeIsInferenceOfSchema(Schema oldIsInferenceOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISINFERENCEOFSCHEMA,
                                          oldIsInferenceOfSchema);
    }


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSourceInferenceOf
     */
     
    public Entailment getIsSourceInferenceOf() {
        // For functional object properties, return the first one or null
        Collection<? extends Entailment>c = getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSOURCEINFERENCEOF,
                                               DefaultEntailment.class);
        if (c.isEmpty()) return null;
        return (Entailment)c.iterator().next();
    }

    public boolean hasIsSourceInferenceOf() {
	   return getIsSourceInferenceOf() != null;
    }

    public void addIsSourceInferenceOf(Entailment newIsSourceInferenceOf) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSOURCEINFERENCEOF,
                                       newIsSourceInferenceOf);
    }

    public void removeIsSourceInferenceOf(Entailment oldIsSourceInferenceOf) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSOURCEINFERENCEOF,
                                          oldIsSourceInferenceOf);
    }


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTargetInferenceOf
     */
     
    public Entailment getIsTargetInferenceOf() {
        // For functional object properties, return the first one or null
        Collection<? extends Entailment>c = getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTARGETINFERENCEOF,
                                               DefaultEntailment.class);
        if (c.isEmpty()) return null;
        return (Entailment)c.iterator().next();
    }

    public boolean hasIsTargetInferenceOf() {
	   return getIsTargetInferenceOf() != null;
    }

    public void addIsTargetInferenceOf(Entailment newIsTargetInferenceOf) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTARGETINFERENCEOF,
                                       newIsTargetInferenceOf);
    }

    public void removeIsTargetInferenceOf(Entailment oldIsTargetInferenceOf) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTARGETINFERENCEOF,
                                          oldIsTargetInferenceOf);
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
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasInferenceType
     */
     
    public Object getHasInferenceType() {
        // for functional properties, return either the first value or null
	Collection<? extends Object> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENCETYPE, Object.class);
        if (c.isEmpty()) return null;
        return (Object)c.iterator().next();
    }

    public boolean hasHasInferenceType() {
	return getHasInferenceType() != null;
    }

    public void addHasInferenceType(Object newHasInferenceType) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENCETYPE, newHasInferenceType);
    }

    public void removeHasInferenceType(Object oldHasInferenceType) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENCETYPE, oldHasInferenceType);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasInferentialContent
     */
     
    public String getHasInferentialContent() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENTIALCONTENT, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasInferentialContent() {
	return getHasInferentialContent() != null;
    }

    public void addHasInferentialContent(String newHasInferentialContent) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENTIALCONTENT, newHasInferentialContent);
    }

    public void removeHasInferentialContent(String oldHasInferentialContent) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASINFERENTIALCONTENT, oldHasInferentialContent);
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
