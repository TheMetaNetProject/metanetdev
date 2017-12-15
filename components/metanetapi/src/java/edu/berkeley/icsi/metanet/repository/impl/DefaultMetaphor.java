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
 * Source Class: DefaultMetaphor <br>
 * @version generated on Tue Mar 05 15:42:49 PST 2013 by jhong
 */
public class DefaultMetaphor extends WrappedIndividualImpl implements Metaphor {

    public DefaultMetaphor(OWLOntology ontology, IRI iri, CodeGenerationInference inf) {
        super(ontology, iri, inf);
    }





    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#entailsMetaphor
     */
     
    public Collection<? extends Metaphor> getEntailsMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ENTAILSMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasEntailsMetaphor() {
	   return !getEntailsMetaphor().isEmpty();
    }

    public void addEntailsMetaphor(Metaphor newEntailsMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ENTAILSMETAPHOR,
                                       newEntailsMetaphor);
    }

    public void removeEntailsMetaphor(Metaphor oldEntailsMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ENTAILSMETAPHOR,
                                          oldEntailsMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasEntailment
     */
     
    public Collection<? extends Entailment> getHasEntailment() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASENTAILMENT,
                                               DefaultEntailment.class);
    }

    public boolean hasHasEntailment() {
	   return !getHasEntailment().isEmpty();
    }

    public void addHasEntailment(Entailment newHasEntailment) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASENTAILMENT,
                                       newHasEntailment);
    }

    public void removeHasEntailment(Entailment oldHasEntailment) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASENTAILMENT,
                                          oldHasEntailment);
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
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasMappings
     */
     
    public Collection<? extends Mapping> getHasMappings() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASMAPPINGS,
                                               DefaultMapping.class);
    }

    public boolean hasHasMappings() {
	   return !getHasMappings().isEmpty();
    }

    public void addHasMappings(Mapping newHasMappings) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASMAPPINGS,
                                       newHasMappings);
    }

    public void removeHasMappings(Mapping oldHasMappings) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASMAPPINGS,
                                          oldHasMappings);
    }


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasSourceSchema
     */
     
    public Schema getHasSourceSchema() {
        // For functional object properties, return the first one or null
        Collection<? extends Schema>c = getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASSOURCESCHEMA,
                                               DefaultSchema.class);
        if (c.isEmpty()) return null;
        return (Schema)c.iterator().next();
    }

    public boolean hasHasSourceSchema() {
	   return getHasSourceSchema() != null;
    }

    public void addHasSourceSchema(Schema newHasSourceSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASSOURCESCHEMA,
                                       newHasSourceSchema);
    }

    public void removeHasSourceSchema(Schema oldHasSourceSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASSOURCESCHEMA,
                                          oldHasSourceSchema);
    }


    /* ***************************************************
     * Functional Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasTargetSchema
     */
     
    public Schema getHasTargetSchema() {
        // For functional object properties, return the first one or null
        Collection<? extends Schema>c = getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASTARGETSCHEMA,
                                               DefaultSchema.class);
        if (c.isEmpty()) return null;
        return (Schema)c.iterator().next();
    }

    public boolean hasHasTargetSchema() {
	   return getHasTargetSchema() != null;
    }

    public void addHasTargetSchema(Schema newHasTargetSchema) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASTARGETSCHEMA,
                                       newHasTargetSchema);
    }

    public void removeHasTargetSchema(Schema oldHasTargetSchema) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASTARGETSCHEMA,
                                          oldHasTargetSchema);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasTransitiveSubpart1Metaphor
     */
     
    public Collection<? extends Metaphor> getHasTransitiveSubpart1Metaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART1METAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasHasTransitiveSubpart1Metaphor() {
	   return !getHasTransitiveSubpart1Metaphor().isEmpty();
    }

    public void addHasTransitiveSubpart1Metaphor(Metaphor newHasTransitiveSubpart1Metaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART1METAPHOR,
                                       newHasTransitiveSubpart1Metaphor);
    }

    public void removeHasTransitiveSubpart1Metaphor(Metaphor oldHasTransitiveSubpart1Metaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART1METAPHOR,
                                          oldHasTransitiveSubpart1Metaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasTransitiveSubpart2Metaphor
     */
     
    public Collection<? extends Metaphor> getHasTransitiveSubpart2Metaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART2METAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasHasTransitiveSubpart2Metaphor() {
	   return !getHasTransitiveSubpart2Metaphor().isEmpty();
    }

    public void addHasTransitiveSubpart2Metaphor(Metaphor newHasTransitiveSubpart2Metaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART2METAPHOR,
                                       newHasTransitiveSubpart2Metaphor);
    }

    public void removeHasTransitiveSubpart2Metaphor(Metaphor oldHasTransitiveSubpart2Metaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_HASTRANSITIVESUBPART2METAPHOR,
                                          oldHasTransitiveSubpart2Metaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isEntailedByMetaphor
     */
     
    public Collection<? extends Metaphor> getIsEntailedByMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISENTAILEDBYMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsEntailedByMetaphor() {
	   return !getIsEntailedByMetaphor().isEmpty();
    }

    public void addIsEntailedByMetaphor(Metaphor newIsEntailedByMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISENTAILEDBYMETAPHOR,
                                       newIsEntailedByMetaphor);
    }

    public void removeIsEntailedByMetaphor(Metaphor oldIsEntailedByMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISENTAILEDBYMETAPHOR,
                                          oldIsEntailedByMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isInMetaphorFamily
     */
     
    public Collection<? extends MetaphorFamily> getIsInMetaphorFamily() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISINMETAPHORFAMILY,
                                               DefaultMetaphorFamily.class);
    }

    public boolean hasIsInMetaphorFamily() {
	   return !getIsInMetaphorFamily().isEmpty();
    }

    public void addIsInMetaphorFamily(MetaphorFamily newIsInMetaphorFamily) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISINMETAPHORFAMILY,
                                       newIsInMetaphorFamily);
    }

    public void removeIsInMetaphorFamily(MetaphorFamily oldIsInMetaphorFamily) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISINMETAPHORFAMILY,
                                          oldIsInMetaphorFamily);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isRelatedToMetaphor
     */
     
    public Collection<? extends Metaphor> getIsRelatedToMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsRelatedToMetaphor() {
	   return !getIsRelatedToMetaphor().isEmpty();
    }

    public void addIsRelatedToMetaphor(Metaphor newIsRelatedToMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHOR,
                                       newIsRelatedToMetaphor);
    }

    public void removeIsRelatedToMetaphor(Metaphor oldIsRelatedToMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHOR,
                                          oldIsRelatedToMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isRelatedToMetaphorBySource
     */
     
    public Collection<? extends Metaphor> getIsRelatedToMetaphorBySource() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYSOURCE,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsRelatedToMetaphorBySource() {
	   return !getIsRelatedToMetaphorBySource().isEmpty();
    }

    public void addIsRelatedToMetaphorBySource(Metaphor newIsRelatedToMetaphorBySource) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYSOURCE,
                                       newIsRelatedToMetaphorBySource);
    }

    public void removeIsRelatedToMetaphorBySource(Metaphor oldIsRelatedToMetaphorBySource) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYSOURCE,
                                          oldIsRelatedToMetaphorBySource);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isRelatedToMetaphorByTarget
     */
     
    public Collection<? extends Metaphor> getIsRelatedToMetaphorByTarget() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYTARGET,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsRelatedToMetaphorByTarget() {
	   return !getIsRelatedToMetaphorByTarget().isEmpty();
    }

    public void addIsRelatedToMetaphorByTarget(Metaphor newIsRelatedToMetaphorByTarget) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYTARGET,
                                       newIsRelatedToMetaphorByTarget);
    }

    public void removeIsRelatedToMetaphorByTarget(Metaphor oldIsRelatedToMetaphorByTarget) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISRELATEDTOMETAPHORBYTARGET,
                                          oldIsRelatedToMetaphorByTarget);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSourceSubcaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsSourceSubcaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSOURCESUBCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsSourceSubcaseOfMetaphor() {
	   return !getIsSourceSubcaseOfMetaphor().isEmpty();
    }

    public void addIsSourceSubcaseOfMetaphor(Metaphor newIsSourceSubcaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSOURCESUBCASEOFMETAPHOR,
                                       newIsSourceSubcaseOfMetaphor);
    }

    public void removeIsSourceSubcaseOfMetaphor(Metaphor oldIsSourceSubcaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSOURCESUBCASEOFMETAPHOR,
                                          oldIsSourceSubcaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSourceSupercaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsSourceSupercaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSOURCESUPERCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsSourceSupercaseOfMetaphor() {
	   return !getIsSourceSupercaseOfMetaphor().isEmpty();
    }

    public void addIsSourceSupercaseOfMetaphor(Metaphor newIsSourceSupercaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSOURCESUPERCASEOFMETAPHOR,
                                       newIsSourceSupercaseOfMetaphor);
    }

    public void removeIsSourceSupercaseOfMetaphor(Metaphor oldIsSourceSupercaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSOURCESUPERCASEOFMETAPHOR,
                                          oldIsSourceSupercaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSubcaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsSubcaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsSubcaseOfMetaphor() {
	   return !getIsSubcaseOfMetaphor().isEmpty();
    }

    public void addIsSubcaseOfMetaphor(Metaphor newIsSubcaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFMETAPHOR,
                                       newIsSubcaseOfMetaphor);
    }

    public void removeIsSubcaseOfMetaphor(Metaphor oldIsSubcaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUBCASEOFMETAPHOR,
                                          oldIsSubcaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isSupercaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsSupercaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsSupercaseOfMetaphor() {
	   return !getIsSupercaseOfMetaphor().isEmpty();
    }

    public void addIsSupercaseOfMetaphor(Metaphor newIsSupercaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFMETAPHOR,
                                       newIsSupercaseOfMetaphor);
    }

    public void removeIsSupercaseOfMetaphor(Metaphor oldIsSupercaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISSUPERCASEOFMETAPHOR,
                                          oldIsSupercaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTargetSubcaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsTargetSubcaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTARGETSUBCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsTargetSubcaseOfMetaphor() {
	   return !getIsTargetSubcaseOfMetaphor().isEmpty();
    }

    public void addIsTargetSubcaseOfMetaphor(Metaphor newIsTargetSubcaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTARGETSUBCASEOFMETAPHOR,
                                       newIsTargetSubcaseOfMetaphor);
    }

    public void removeIsTargetSubcaseOfMetaphor(Metaphor oldIsTargetSubcaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTARGETSUBCASEOFMETAPHOR,
                                          oldIsTargetSubcaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTargetSupercaseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsTargetSupercaseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTARGETSUPERCASEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsTargetSupercaseOfMetaphor() {
	   return !getIsTargetSupercaseOfMetaphor().isEmpty();
    }

    public void addIsTargetSupercaseOfMetaphor(Metaphor newIsTargetSupercaseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTARGETSUPERCASEOFMETAPHOR,
                                       newIsTargetSupercaseOfMetaphor);
    }

    public void removeIsTargetSupercaseOfMetaphor(Metaphor oldIsTargetSupercaseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTARGETSUPERCASEOFMETAPHOR,
                                          oldIsTargetSupercaseOfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTransitiveSubpart1OfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsTransitiveSubpart1OfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART1OFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsTransitiveSubpart1OfMetaphor() {
	   return !getIsTransitiveSubpart1OfMetaphor().isEmpty();
    }

    public void addIsTransitiveSubpart1OfMetaphor(Metaphor newIsTransitiveSubpart1OfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART1OFMETAPHOR,
                                       newIsTransitiveSubpart1OfMetaphor);
    }

    public void removeIsTransitiveSubpart1OfMetaphor(Metaphor oldIsTransitiveSubpart1OfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART1OFMETAPHOR,
                                          oldIsTransitiveSubpart1OfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isTransitiveSubpart2OfMetaphor
     */
     
    public Collection<? extends Metaphor> getIsTransitiveSubpart2OfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART2OFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsTransitiveSubpart2OfMetaphor() {
	   return !getIsTransitiveSubpart2OfMetaphor().isEmpty();
    }

    public void addIsTransitiveSubpart2OfMetaphor(Metaphor newIsTransitiveSubpart2OfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART2OFMETAPHOR,
                                       newIsTransitiveSubpart2OfMetaphor);
    }

    public void removeIsTransitiveSubpart2OfMetaphor(Metaphor oldIsTransitiveSubpart2OfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISTRANSITIVESUBPART2OFMETAPHOR,
                                          oldIsTransitiveSubpart2OfMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#isUsedByMetaphor
     */
     
    public Collection<? extends Metaphor> getIsUsedByMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_ISUSEDBYMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasIsUsedByMetaphor() {
	   return !getIsUsedByMetaphor().isEmpty();
    }

    public void addIsUsedByMetaphor(Metaphor newIsUsedByMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_ISUSEDBYMETAPHOR,
                                       newIsUsedByMetaphor);
    }

    public void removeIsUsedByMetaphor(Metaphor oldIsUsedByMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_ISUSEDBYMETAPHOR,
                                          oldIsUsedByMetaphor);
    }


    /* ***************************************************
     * Object Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#makesUseOfMetaphor
     */
     
    public Collection<? extends Metaphor> getMakesUseOfMetaphor() {
        return getDelegate().getPropertyValues(getOwlIndividual(),
                                               Vocabulary.OBJECT_PROPERTY_MAKESUSEOFMETAPHOR,
                                               DefaultMetaphor.class);
    }

    public boolean hasMakesUseOfMetaphor() {
	   return !getMakesUseOfMetaphor().isEmpty();
    }

    public void addMakesUseOfMetaphor(Metaphor newMakesUseOfMetaphor) {
        getDelegate().addPropertyValue(getOwlIndividual(),
                                       Vocabulary.OBJECT_PROPERTY_MAKESUSEOFMETAPHOR,
                                       newMakesUseOfMetaphor);
    }

    public void removeMakesUseOfMetaphor(Metaphor oldMakesUseOfMetaphor) {
        getDelegate().removePropertyValue(getOwlIndividual(),
                                          Vocabulary.OBJECT_PROPERTY_MAKESUSEOFMETAPHOR,
                                          oldMakesUseOfMetaphor);
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
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasExperientialBasis
     */
     
    public String getHasExperientialBasis() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASEXPERIENTIALBASIS, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasExperientialBasis() {
	return getHasExperientialBasis() != null;
    }

    public void addHasExperientialBasis(String newHasExperientialBasis) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASEXPERIENTIALBASIS, newHasExperientialBasis);
    }

    public void removeHasExperientialBasis(String oldHasExperientialBasis) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASEXPERIENTIALBASIS, oldHasExperientialBasis);
    }


    /* ***************************************************
     * Functional Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasMetaphorLevel
     */
     
    public String getHasMetaphorLevel() {
        // for functional properties, return either the first value or null
	Collection<? extends String> c = getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORLEVEL, String.class);
        if (c.isEmpty()) return null;
        return (String)c.iterator().next();
    }

    public boolean hasHasMetaphorLevel() {
	return getHasMetaphorLevel() != null;
    }

    public void addHasMetaphorLevel(String newHasMetaphorLevel) {
	getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORLEVEL, newHasMetaphorLevel);
    }

    public void removeHasMetaphorLevel(String oldHasMetaphorLevel) {
	getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORLEVEL, oldHasMetaphorLevel);
    }


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#hasMetaphorType
     */
     
    public Collection<? extends String> getHasMetaphorType() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORTYPE, String.class);
    }

    public boolean hasHasMetaphorType() {
		return !getHasMetaphorType().isEmpty();
    }

    public void addHasMetaphorType(String newHasMetaphorType) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORTYPE, newHasMetaphorType);
    }

    public void removeHasMetaphorType(String oldHasMetaphorType) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_HASMETAPHORTYPE, oldHasMetaphorType);
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


    /* ***************************************************
     * Data Property https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl#wasInvestigatedFor
     */
     
    public Collection<? extends String> getWasInvestigatedFor() {
		return getDelegate().getPropertyValues(getOwlIndividual(), Vocabulary.DATA_PROPERTY_WASINVESTIGATEDFOR, String.class);
    }

    public boolean hasWasInvestigatedFor() {
		return !getWasInvestigatedFor().isEmpty();
    }

    public void addWasInvestigatedFor(String newWasInvestigatedFor) {
	    getDelegate().addPropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_WASINVESTIGATEDFOR, newWasInvestigatedFor);
    }

    public void removeWasInvestigatedFor(String oldWasInvestigatedFor) {
		getDelegate().removePropertyValue(getOwlIndividual(), Vocabulary.DATA_PROPERTY_WASINVESTIGATEDFOR, oldWasInvestigatedFor);
    }


}
