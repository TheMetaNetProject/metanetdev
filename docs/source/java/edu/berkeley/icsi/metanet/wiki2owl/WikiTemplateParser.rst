.. java:import:: java.util Arrays

.. java:import:: org.apache.commons.lang3 StringUtils

.. java:import:: java.util HashMap

.. java:import:: java.util Iterator

.. java:import:: java.util List

.. java:import:: java.util Locale

.. java:import:: java.util Map

.. java:import:: java.util.regex Matcher

.. java:import:: java.util.regex Pattern

.. java:import:: org.semanticweb.owlapi.model AddAxiom

.. java:import:: org.semanticweb.owlapi.model IRI

.. java:import:: org.semanticweb.owlapi.model OWLAnnotation

.. java:import:: org.semanticweb.owlapi.model OWLAnnotationProperty

.. java:import:: org.semanticweb.owlapi.model OWLAxiom

.. java:import:: org.semanticweb.owlapi.model OWLClass

.. java:import:: org.semanticweb.owlapi.model OWLClassAssertionAxiom

.. java:import:: org.semanticweb.owlapi.model OWLDataFactory

.. java:import:: org.semanticweb.owlapi.model OWLDataProperty

.. java:import:: org.semanticweb.owlapi.model OWLDataPropertyAssertionAxiom

.. java:import:: org.semanticweb.owlapi.model OWLNamedIndividual

.. java:import:: org.semanticweb.owlapi.model OWLObjectProperty

.. java:import:: org.semanticweb.owlapi.model OWLOntology

.. java:import:: org.semanticweb.owlapi.model OWLOntologyManager

.. java:import:: org.semanticweb.owlapi.model PrefixManager

WikiTemplateParser
==================

.. java:package:: edu.berkeley.icsi.metanet.wiki2owl
   :noindex:

.. java:type:: public class WikiTemplateParser

   Class for parsing pages in the metanet semantic mediawiki that are structured by templates.

   :author: jhong

Fields
------
ENDTEMPLATE
^^^^^^^^^^^

.. java:field:: public static int ENDTEMPLATE
   :outertype: WikiTemplateParser

OTHER
^^^^^

.. java:field:: public static int OTHER
   :outertype: WikiTemplateParser

STARTTEMPLATE
^^^^^^^^^^^^^

.. java:field:: public static int STARTTEMPLATE
   :outertype: WikiTemplateParser

VARIABLE
^^^^^^^^

.. java:field:: public static int VARIABLE
   :outertype: WikiTemplateParser

Constructors
------------
WikiTemplateParser
^^^^^^^^^^^^^^^^^^

.. java:constructor:: public WikiTemplateParser(String pName, String wikitext, OWLOntology repo, PrefixManager prefman, OWLOntology onto, String pref)
   :outertype: WikiTemplateParser

Methods
-------
parse
^^^^^

.. java:method:: public void parse()
   :outertype: WikiTemplateParser

setLanguage
^^^^^^^^^^^

.. java:method:: public void setLanguage(String s)
   :outertype: WikiTemplateParser

   Method to set the language of the wiki. This will be used later for determining how to parse out schema names from metaphor names. Note that the member variable lang defaults to English.

   :param s: String: presently either en, es, fa, ru

setLogLevel
^^^^^^^^^^^

.. java:method:: public void setLogLevel(Level level)
   :outertype: WikiTemplateParser

