.. ICSI MetaNet Documentation master file, created by
   sphinx-quickstart on Mon Feb  3 02:31:54 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ICSI MetaNet Developer Documentation
====================================

Overview
--------

This document describes the packages and modules developed under the
MetaNet project.  These include the two scripts ``m4affect`` and ``m4detect``
(as ``m4mapping`` and ``m4source`` are deprecated), all their dependencies,
as well as other software components make up the MetaNet system.

Python executables are implemented as python wrappers that
import each script's corresponding module in the :py:mod:`iarpatests`
package, and deploys the module's ``main()`` method.  Java executables
are implemented as shell script wrappers that set the CLASSPATH and
load the main class.

IARPA test modules:

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`iarpatests.m4detect`                      | m4detect script                                 |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`iarpatests.m4mapping`                     | m4mapping script                                |
+----------------------------------------------------+-------------------------------------------------+

Deprecated IARPA test modules:

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`iarpatests.m4affect`                      | m4affect script                                 |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`iarpatests.m4source`                      | m4source script                                 |
+----------------------------------------------------+-------------------------------------------------+

These modules depend on a number of other types of packages and modules
present in the source distribution.  These are summarized below.

IARPA file format I/O and configuration utilities:

+-----------------------------------------------------+------------------------------------------------------------------+
| :py:mod:`iarpatests.iarpaxml`                       | IARPA XML parsing and generation, logging, etc.                  |
+-----------------------------------------------------+------------------------------------------------------------------+
| :py:mod:`mnformats.mnjson`                          | MetaNet interchange JSON format                                  |
+-----------------------------------------------------+------------------------------------------------------------------+
| :py:mod:`mnformats.mnconfig`                        | Configuration file parser.  Format similar to Windows INI files  |
+-----------------------------------------------------+------------------------------------------------------------------+
| :py:mod:`mnanalysis.programsources`                 | Common program sources document parser (Deprecated)              | 
+-----------------------------------------------------+------------------------------------------------------------------+

Parsing and tagging:

+----------------------------------------------------+---------------------------------------------------------+
| :py:mod:`depparsing`                               | Dependency parsing for all languages                    |
+----------------------------------------------------+---------------------------------------------------------+
| :py:mod:`mnpipeline.persiantagger`                 | Persian POS tagger                                      |
+----------------------------------------------------+---------------------------------------------------------+
| :py:mod:`mnpipeline.treetagger`                    | TreeTagger wrapper (for English, Spanish, and Russian)  |
+----------------------------------------------------+---------------------------------------------------------+


Linguistic metaphor extraction systems:

+----------------------------------------------------+--------------------------------------------------------------+
| :py:mod:`depparsing`                               | Seed-based System (SBS)                                      |
+----------------------------------------------------+--------------------------------------------------------------+
| :py:mod:`cmsextractor`                             | Construction Matching System (CMS)                           |
+----------------------------------------------------+--------------------------------------------------------------+
| :py:mod:`lmsextractor2`                            | Language Model System v.2 (LMS2) (Persian only)              |
+----------------------------------------------------+--------------------------------------------------------------+
| :py:mod:`lmsextractor`                             | Language Model System v.1 (LMS) (Persian only) (Deprecated)  |
+----------------------------------------------------+--------------------------------------------------------------+

Mapping linguistic metaphors to conceptual metaphors:

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnrepository.cnmapping`                   | Conceptual Network Mapping System (CNMS)        |
+----------------------------------------------------+-------------------------------------------------+

Tools for extending lexical coverage of the MetaNet conceptual network:

+----------------------------------------------------+--------------------------------------------------------+
| :py:mod:`mnrepository.fnxml`                       | Support library for FrameNet extensions                |
+----------------------------------------------------+--------------------------------------------------------+
| :py:mod:`mnrepository.persianwordforms`            | Support library for Persian inflected form extensions  |
+----------------------------------------------------+--------------------------------------------------------+
| :py:mod:`mnrepository.wiktionary`                  | Support library for Wiktionary extensions              |
+----------------------------------------------------+--------------------------------------------------------+

Querying the MetaNet conceptual network:

+----------------------------------------------------+--------------------------------------------------------------+
| :py:mod:`mnrepository.metanetrdf`                  | Searching for schemas, CMs, mapping from schemas to concepts |
+----------------------------------------------------+--------------------------------------------------------------+

MetaNet Internal and Government databases:

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnrepository.metanetdb`                   | MetaNet internal database library               |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnrepository.gmrdb`                       | GMR database library                            |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnrepository.fastdbimport`                | JSON to database converter                      |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnrepository.coresupport`                 | Calculates and populates core lexical support   |
+----------------------------------------------------+-------------------------------------------------+

Reports and Data Generation:

+----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:mod:`mnrepository.gen_xca_reports`             | Generates XCA reports                                                                                                 |
+----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:mod:`mnrepository.gen_lm_data`                 | Generates Excel/TAB format version of LM data from MetaNet internal database                                          |
+----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+
| :py:mod:`mnrepository.gendemodata`                 | Generates Excel/TAB format version of LM data from GMR database, with tier1 data added from MetaNet internal database |
+----------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------+

Distributional statistics-based target and source concept/dimension mapping (Deprecated):

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mapping`                                  | Mapping from expressions to concepts            |
+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`source`                                   | Mapping from concepts to dimensions             |
+----------------------------------------------------+-------------------------------------------------+

Affect computation (Deprecated):

+----------------------------------------------------+-------------------------------------------------+
| :py:mod:`mnpipeline.affectlookup`                  | Affect computation for all languages            |
+----------------------------------------------------+-------------------------------------------------+

Topic-specific document collection:

+----------------------------------------------------+--------------------------------------------+
| :py:mod:`document_collection`                      | Collect topic specific documents           |
+----------------------------------------------------+--------------------------------------------+

Project-internal Gold standard testing:

+----------------------------------------------------+-------------------------------------------------------------+
| :py:mod:`iarpatests.comparegold`                   | Script for comparing results with gold standard             |
+----------------------------------------------------+-------------------------------------------------------------+
| :py:mod:`iarpatests.gsdb2m4detectinput`            | Script for retrieving gold standard data from web interface |
+----------------------------------------------------+-------------------------------------------------------------+

MetaNet Wiki/OWL conversion:

+----------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| :java:package:`edu.berkeley.icsi.metanet.wiki2owl` | Connects to the MetaNet Wiki, downloads pages, and converts to RDF/OWL.  Implements a command as well as a plugin for Protege  |
+----------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+
| :java:package:`edu.berkeley.icsi.metanet.owl2sql`  | Converts MetaNet RDF/OWL to MySQL.                                                                                             |
+----------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------------+



Installation
------------

Although most of the provided source code is Python and therefore does not inherently
require compilation, the build infrastructure includes compilation and installation
phases to allow for development using other languages, such as Java.  Compilation is
achieved by executing the following command at the top of the source tree::

% ant install

The command above builds independently executable components in the system.  To build
plugins, the following command should be used::

% ant installplugins

The build system assumes that Apache Ant (http://ant.apache.org/) is available in
the system PATH.  Running the system requires Python 2.7.3.  The following
are 3rd party modules used by the metaphor detection and mapping system.  The
list also includes the versions that were used at the time this document was
created:

* CouchDB==1.0
* Jinja2==2.7.2
* MarkupSafe==0.18
* MySQL-python==1.2.5
* PyYAML==3.11
* Pygments==1.6
* SPARQLWrapper==1.6.0
* Sphinx==1.2.1
* XlsxWriter==0.5.3
* backports.ssl-match-hostname==3.4.0.2
* beautifulsoup4==4.3.2
* bunch==1.0.1
* certifi==14.05.14
* couchdbkit==0.6.5
* docutils==0.11
* gensim==0.8.9
* html5lib==0.95
* http-parser==0.8.3
* httplib2==0.8
* ipython==2.3.1
* isodate==0.4.9
* javalang==0.9.5
* javasphinx==0.9.10
* jdatetime==1.3
* jsonschema==2.3.0
* lxml==3.3.0
* nltk==3.0.0b2
* numpy==1.8.0
* openpyxl==1.8.4
* pymongo==2.7.2
* pyparsing==2.0.1
* pyzmq==14.4.1
* rdflib==4.1.0
* rdflib-jsonld==0.2-dev
* restkit==4.2.2
* scipy==0.13.2
* setproctitle==1.1.8
* simplejson==3.3.2
* socketpool==0.5.3
* tailer==0.3
* tornado==4.0.2
* ujson==1.33
* unicodecsv==0.9.4
* wsgiref==0.1.2
* zope.interface==4.1.0

Some of the Java components, such as :java:package:`edu.berkeley.icsi.metanet.wiki2owl`,
depends on Protege 4.x being installed somewhere on the system.  It's location should
be specified via the PROTEGE_HOME environment variable.  When ``ant installplugins`` runs,
it will pull libraries from Protege, as well as install plugins into Protege's plugins
directory.

Compilation produces a directory structure at the top of the distribution as follows::

	/dist
		/bin
		/lib/python
		/doc
		/etc

The executables, e.g. the ``m4xxx`` scripts are installed into ``/dist/bin``, while
the supporting python libraries are installed into ``/dist/lib``.

Assuming that ``MNDEV`` refers to the root of the tree, the following environment variables
must be exported in order to execute the resulting scripts::

	export PATH=$MNDEV/dist/bin:$PATH
	export PYTHONPATH=$MNDEV/dist/lib/python:$PYTHONPATH


A number of programs, including ``m4detect``, ``m4mapping``, ``fastdbimport``, and ``gendemodata``
are configured for use using a configuration file.  The location of this configuration file
can be set via the MNSYSTEM_CONF environment variable or set at command invocation time through
a command line parameter.  The format of the file is similar to Windows INI files and is parsed
through the :py:mod:`mnformats.mnconfig` module.  The configuration used for the latest round
of evaluations and GMR generation is included in the ``MNDEV/python/etc`` directory as ``mnsystem.conf``.

Documentation
-------------

This documentation was produced using Sphinx (http://sphinx-doc.org/), and can be
re-generated as follows::

% cd docs
% make install

This requires that ``sphinx`` be installed as a python module, and for the MetaNet system
python modules to be in the ``PYTHONPATH``.  HTML documentation can then be accessed at::

/dist/doc/html/



Package contents
----------------

.. toctree::
   :maxdepth: 3

   cmsextractor
   depparsing
   iarpatests
   lmsextractor
   lmsextractor2
   mapping
   mnanalysis
   mnformats
   mnpipeline
   mnrepository
   source
   document_collection
   java/packages

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

