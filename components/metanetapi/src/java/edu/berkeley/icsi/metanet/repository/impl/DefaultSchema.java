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
 * Source Class: DefaultSchema <br>
 * @version generated on Tue Mar 05 15:42:50 PST 2013 by jhong
 */
public class DefaultSchema extends WrappedIndividualImpl implements Schema {

    public DefaultSchema(OWLOntology ontology, IRI iri, CodeGenerationInference inf) {
        super(ontology, iri, inf);
    }





    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasBindings
     */
     
    public Collection<? extends Binding> getHasBindings() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASBINDINGS,
                                               DefaultBinding.class);
    }

    public boolean hasHasBindings() {
	   return !getHasBindings().isEmpty();
    }

    public void addHasBindings(Binding newHasBindings) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASBINDINGS,
                                       newHasBindings);
    }

    public void removeHasBindings(Binding oldHasBindings) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASBINDINGS,
                                          oldHasBindings);
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
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasInference
     */
     
    public Collection<? extends Inference> getHasInference() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASINFERENCE,
                                               DefaultInference.class);
    }

    public boolean hasHasInference() {
	   return !getHasInference().isEmpty();
    }

    public void addHasInference(Inference newHasInference) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASINFERENCE,
                                       newHasInference);
    }

    public void removeHasInference(Inference oldHasInference) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASINFERENCE,
                                          oldHasInference);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasLexicalUnit
     */
     
    public Collection<? extends LexicalUnit> getHasLexicalUnit() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASLEXICALUNIT,
                                               DefaultLexicalUnit.class);
    }

    public boolean hasHasLexicalUnit() {
	   return !getHasLexicalUnit().isEmpty();
    }

    public void addHasLexicalUnit(LexicalUnit newHasLexicalUnit) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASLEXICALUNIT,
                                       newHasLexicalUnit);
    }

    public void removeHasLexicalUnit(LexicalUnit oldHasLexicalUnit) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASLEXICALUNIT,
                                          oldHasLexicalUnit);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasRoles
     */
     
    public Collection<? extends Role> getHasRoles() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASROLES,
                                               DefaultRole.class);
    }

    public boolean hasHasRoles() {
	   return !getHasRoles().isEmpty();
    }

    public void addHasRoles(Role newHasRoles) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASROLES,
                                       newHasRoles);
    }

    public void removeHasRoles(Role oldHasRoles) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASROLES,
                                          oldHasRoles);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isInSchemaFamily
     */
     
    public Collection<? extends SchemaFamily> getIsInSchemaFamily() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISINSCHEMAFAMILY,
                                               DefaultSchemaFamily.class);
    }

    public boolean hasIsInSchemaFamily() {
	   return !getIsInSchemaFamily().isEmpty();
    }

    public void addIsInSchemaFamily(SchemaFamily newIsInSchemaFamily) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISINSCHEMAFAMILY,
                                       newIsInSchemaFamily);
    }

    public void removeIsInSchemaFamily(SchemaFamily oldIsInSchemaFamily) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISINSCHEMAFAMILY,
                                          oldIsInSchemaFamily);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isRelatedToSchema
     */
     
    public Collection<? extends Schema> getIsRelatedToSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISRELATEDTOSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsRelatedToSchema() {
	   return !getIsRelatedToSchema().isEmpty();
    }

    public void addIsRelatedToSchema(Schema newIsRelatedToSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISRELATEDTOSCHEMA,
                                       newIsRelatedToSchema);
    }

    public void removeIsRelatedToSchema(Schema oldIsRelatedToSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISRELATEDTOSCHEMA,
                                          oldIsRelatedToSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSourceDomainOfMetaphors
     */
     
    public Collection<? extends Metaphor> getIsSourceDomainOfMetaphors() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSOURCEDOMAINOFMETAPHORS,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsSourceDomainOfMetaphors() {
	   return !getIsSourceDomainOfMetaphors().isEmpty();
    }

    public void addIsSourceDomainOfMetaphors(Metaphor newIsSourceDomainOfMetaphors) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSOURCEDOMAINOFMETAPHORS,
                                       newIsSourceDomainOfMetaphors);
    }

    public void removeIsSourceDomainOfMetaphors(Metaphor oldIsSourceDomainOfMetaphors) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSOURCEDOMAINOFMETAPHORS,
                                          oldIsSourceDomainOfMetaphors);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSubcaseOfSchema
     */
     
    public Collection<? extends Schema> getIsSubcaseOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsSubcaseOfSchema() {
	   return !getIsSubcaseOfSchema().isEmpty();
    }

    public void addIsSubcaseOfSchema(Schema newIsSubcaseOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFSCHEMA,
                                       newIsSubcaseOfSchema);
    }

    public void removeIsSubcaseOfSchema(Schema oldIsSubcaseOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFSCHEMA,
                                          oldIsSubcaseOfSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSubprocessOfSchema
     */
     
    public Collection<? extends Schema> getIsSubprocessOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUBPROCESSOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsSubprocessOfSchema() {
	   return !getIsSubprocessOfSchema().isEmpty();
    }

    public void addIsSubprocessOfSchema(Schema newIsSubprocessOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUBPROCESSOFSCHEMA,
                                       newIsSubprocessOfSchema);
    }

    public void removeIsSubprocessOfSchema(Schema oldIsSubprocessOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUBPROCESSOFSCHEMA,
                                          oldIsSubprocessOfSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSupercaseOfSchema
     */
     
    public Collection<? extends Schema> getIsSupercaseOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsSupercaseOfSchema() {
	   return !getIsSupercaseOfSchema().isEmpty();
    }

    public void addIsSupercaseOfSchema(Schema newIsSupercaseOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFSCHEMA,
                                       newIsSupercaseOfSchema);
    }

    public void removeIsSupercaseOfSchema(Schema oldIsSupercaseOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFSCHEMA,
                                          oldIsSupercaseOfSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSuperprocessOfSchema
     */
     
    public Collection<? extends Schema> getIsSuperprocessOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUPERPROCESSOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsSuperprocessOfSchema() {
	   return !getIsSuperprocessOfSchema().isEmpty();
    }

    public void addIsSuperprocessOfSchema(Schema newIsSuperprocessOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUPERPROCESSOFSCHEMA,
                                       newIsSuperprocessOfSchema);
    }

    public void removeIsSuperprocessOfSchema(Schema oldIsSuperprocessOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUPERPROCESSOFSCHEMA,
                                          oldIsSuperprocessOfSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTargetDomainOfMetaphors
     */
     
    public Collection<? extends Metaphor> getIsTargetDomainOfMetaphors() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTARGETDOMAINOFMETAPHORS,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsTargetDomainOfMetaphors() {
	   return !getIsTargetDomainOfMetaphors().isEmpty();
    }

    public void addIsTargetDomainOfMetaphors(Metaphor newIsTargetDomainOfMetaphors) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTARGETDOMAINOFMETAPHORS,
                                       newIsTargetDomainOfMetaphors);
    }

    public void removeIsTargetDomainOfMetaphors(Metaphor oldIsTargetDomainOfMetaphors) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTARGETDOMAINOFMETAPHORS,
                                          oldIsTargetDomainOfMetaphors);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isUsedBySchema
     */
     
    public Collection<? extends Schema> getIsUsedBySchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISUSEDBYSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasIsUsedBySchema() {
	   return !getIsUsedBySchema().isEmpty();
    }

    public void addIsUsedBySchema(Schema newIsUsedBySchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISUSEDBYSCHEMA,
                                       newIsUsedBySchema);
    }

    public void removeIsUsedBySchema(Schema oldIsUsedBySchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISUSEDBYSCHEMA,
                                          oldIsUsedBySchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#makesUseOfSchema
     */
     
    public Collection<? extends Schema> getMakesUseOfSchema() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_MAKESUSEOFSCHEMA,
                                               DefaultSchema.class);
    }

    public boolean hasMakesUseOfSchema() {
	   return !getMakesUseOfSchema().isEmpty();
    }

    public void addMakesUseOfSchema(Schema newMakesUseOfSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_MAKESUSEOFSCHEMA,
                                       newMakesUseOfSchema);
    }

    public void removeMakesUseOfSchema(Schema oldMakesUseOfSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_MAKESUSEOFSCHEMA,
                                          oldMakesUseOfSchema);
    }


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#correspondsToFrameNet
     */
     
    public Collection<? extends String> getCorrespondsToFrameNet() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_CORRESPONDSTOFRAMENET, String.class);
    }

    public boolean hasCorrespondsToFrameNet() {
		return !getCorrespondsToFrameNet().isEmpty();
    }

    public void addCorrespondsToFrameNet(String newCorrespondsToFrameNet) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_CORRESPONDSTOFRAMENET, newCorrespondsToFrameNet);
    }

    public void removeCorrespondsToFrameNet(String oldCorrespondsToFrameNet) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_CORRESPONDSTOFRAMENET, oldCorrespondsToFrameNet);
    }


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasAlias
     */
     
    public Collection<? extends Object> getHasAlias() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASALIAS, Object.class);
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
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasCulturalContent
     */
     
    public String getHasCulturalContent() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASCULTURALCONTENT, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasCulturalContent() {
	return getHasCulturalContent() != null;
    }

    public void addHasCulturalContent(String newHasCulturalContent) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASCULTURALCONTENT, newHasCulturalContent);
    }

    public void removeHasCulturalContent(String oldHasCulturalContent) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASCULTURALCONTENT, oldHasCulturalContent);
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
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasSchemaType
     */
     
    public Collection<? extends String> getHasSchemaType() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASSCHEMATYPE, String.class);
    }

    public boolean hasHasSchemaType() {
		return !getHasSchemaType().isEmpty();
    }

    public void addHasSchemaType(String newHasSchemaType) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASSCHEMATYPE, newHasSchemaType);
    }

    public void removeHasSchemaType(String oldHasSchemaType) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASSCHEMATYPE, oldHasSchemaType);
    }


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isApplicableToLanguage
     */
     
    public Collection<? extends String> getIsApplicableToLanguage() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISAPPLICABLETOLANGUAGE, String.class);
    }

    public boolean hasIsApplicableToLanguage() {
		return !getIsApplicableToLanguage().isEmpty();
    }

    public void addIsApplicableToLanguage(String newIsApplicableToLanguage) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISAPPLICABLETOLANGUAGE, newIsApplicableToLanguage);
    }

    public void removeIsApplicableToLanguage(String oldIsApplicableToLanguage) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_ISAPPLICABLETOLANGUAGE, oldIsApplicableToLanguage);
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