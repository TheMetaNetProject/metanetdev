/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package edu.berkeley.icsi.metanet.lmtocmlinker;

import edu.berkeley.icsi.metanet.repository.LexicalUnit;
import edu.berkeley.icsi.metanet.repository.LinguisticMetaphor;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;
import edu.berkeley.icsi.metanet.repository.Metaphor;
import edu.berkeley.icsi.metanet.repository.Schema;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import javax.swing.JTextArea;
import org.apache.commons.lang3.StringUtils;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 *
 * @author jhong
 */
public class MetaphorFinder {

    private OWLOntology owlModel;
    private Map<String, Set<String>> frames;
    private JTextArea console;
    private MetaNetFactory factory;
    private Collection<? extends Schema> schemas;
    private Collection<? extends LexicalUnit> lus;
    private Map<String, Set<LexicalUnit>> lemma2lu;
    private Map<String, Set<Schema>> frame2schema;

    MetaphorFinder(OWLOntology model, MetaNetFactory mfact, Map<String, Set<String>> frames, JTextArea console) {
        this.owlModel = model;
        this.factory = mfact;
        this.frames = frames;
        this.console = console;
        this.schemas = factory.getAllSchemaInstances();
        this.lus = factory.getAllLexicalUnitInstances();
        setLemma2Lu(doLexicalUnitPreprocessing());
        setFrame2Schema(doSchemaPreprocessing());
    }

    public void setLemma2Lu(Map<String, Set<LexicalUnit>> ll) {
        lemma2lu = ll;
    }

    public void setFrame2Schema(Map<String, Set<Schema>> fs) {
        frame2schema = fs;
    }

    public Map<String, Set<Schema>> doSchemaPreprocessing() {
        console.append("Preprocessing schemas.\n");
        Map<String, Set<Schema>> frame2schemaMap = new HashMap<String, Set<Schema>>();
        for (Schema s : schemas) {
            Set<String> corrframes = new HashSet<String>(s.getCorrespondsToFrameNet());
            for (String fname : corrframes) {
                if (frame2schemaMap.containsKey(fname)) {
                    frame2schemaMap.get(fname).add(s);
                } else {
                    Set<Schema> sset = new HashSet<Schema>();
                    sset.add(s);
                    frame2schemaMap.put(fname, sset);
                }
            }
        }
        return frame2schemaMap;
    }

    public Map<String, Set<LexicalUnit>> doLexicalUnitPreprocessing() {
        console.append("Preprocessing lexical units.\n");
        //Index LUs by lemma
        Map<String, Set<LexicalUnit>> lemma2luMap = new HashMap<String, Set<LexicalUnit>>();
        for (LexicalUnit lu : lus) {
            String lemma = lu.getHasLemma();
            if (lemma2luMap.containsKey(lemma)) {
                lemma2luMap.get(lemma).add(lu);
            } else {
                Set<LexicalUnit> lset = new HashSet<LexicalUnit>();
                lset.add(lu);
                lemma2luMap.put(lemma, lset);
            }
        }
        return lemma2luMap;
    }

    public Object[][] runSearch(Collection<SearchPanelListItem> items) {

        console.append("Starting processing LMs\n");
        System.err.println("In runSearch...\n");
        ArrayList<Object[]> data = new ArrayList<Object[]>();

        for (SearchPanelListItem item : items) {
            Object[] args = new Object[8];
            for (int i = 0; i < 8; i++) {
                args[i] = "";
            }
            OWLNamedIndividual linguisticMetaphor = item.individual();
            LinguisticMetaphor lm = factory.getLinguisticMetaphor(linguisticMetaphor.getIRI().toString());

            args = findCMsforLM(lm);
        }

        Object[][] results = new Object[data.size()][8];
        for (int i = 0; i < data.size(); i++) {
            results[i] = data.get(i);
        }

        return results;

    }

    public Object[] findCMsforLM(LinguisticMetaphor lm) {
        Object[] args = new Object[8];
        for (int i = 0; i < 8; i++) {
            args[i] = "";
        }
        String lmName = lm.getHasName();
        console.append("\n==================================\nProcessing " + lmName + "\n");

        args[0] = lmName;

        // retrieve the target and source lemmas from the LM
        String targetLemma = lm.getHasLinguisticTarget();
        String sourceLemma = lm.getHasLinguisticSource();

        Set<String> targetFrames = new HashSet<String>();
        Set<String> sourceFrames = new HashSet<String>();
        if (frames.containsKey(sourceLemma)) {
            sourceFrames = frames.get(sourceLemma);
            console.append("Lemma " + sourceLemma + " matched " + sourceFrames.size() + " frames.\n");
        }
        if (frames.containsKey(targetLemma)) {
            targetFrames = frames.get(targetLemma);
            console.append("Lemma " + sourceLemma + " matched " + targetFrames.size() + " frames.\n");
        }

        // find all schemas that refer to these frames
        Set<Schema> sourceSchemas = new HashSet<Schema>();
        Set<Schema> targetSchemas = new HashSet<Schema>();
        for (String fname : targetFrames) {
            if (frame2schema.containsKey(fname)) {
                targetSchemas.addAll(frame2schema.get(fname));
            }
        }
        for (String fname : sourceFrames) {
            if (frame2schema.containsKey(fname)) {
                sourceSchemas.addAll(frame2schema.get(fname));
            }
        }
        // each lemma can be found in one of a number of LUs, so initialize lists
        Set<LexicalUnit> targetLUs = lemma2lu.get(targetLemma);
        Set<LexicalUnit> sourceLUs = lemma2lu.get(sourceLemma);

        // fill in LU names and Schema names for source
        if (sourceLUs != null) {
            List<String> lunames = new ArrayList<String>();
            for (LexicalUnit lu : sourceLUs) {
                lunames.add(lu.getHasLemma());
                Schema sc = lu.getIsDefinedRelativeToSchema();
                if (sc == null) {
                    console.append(lmName + ": LU " + lu.getHasLemma() + " has no linked Schema");
                } else {
                    sourceSchemas.add(sc);
                }
            }
            args[1] = StringUtils.join(lunames, ",");
        } else {
            console.append(lmName + ": Source LexicalUnits NOT present in database.\n");
        }
        args[3] = getSchemaNames(sourceSchemas);

        /* fill in LU names and Schema names for target */
        /* make list of targetSchemas */
        if (targetLUs != null) {
            List<String> lunames = new ArrayList<String>();
            for (LexicalUnit lu : targetLUs) {
                lunames.add(lu.getHasLemma());
                Schema tg = lu.getIsDefinedRelativeToSchema();
                if (tg == null) {
                    console.append(lmName + ": LU " + lu.getHasLemma() + " has no linked Schema");
                } else {
                    targetSchemas.add(tg);
                }
            }
            args[2] = StringUtils.join(lunames, ",");
        } else {
            console.append(lmName + ": Target LexicalUnits NOT present in database.\n");
        }
        args[4] = getSchemaNames(targetSchemas);

        /* try to find metaphors */
        Set<Metaphor> metaphors = new HashSet<Metaphor>();
        for (Schema sourceS : sourceSchemas) {
            // get Metaphors that match both TARGET and source
            Collection<Metaphor> mets = (Collection<Metaphor>) sourceS.getIsSourceDomainOfMetaphors();
            for (Metaphor m : mets) {
                // exact match
                Schema targetOfM = m.getHasTargetSchema();
                if (targetSchemas.contains(targetOfM)) {
                    metaphors.add(m);
                }
                // target side makes use of the targetSchema(s)
                Collection<Schema> tgUses = (Collection<Schema>) targetOfM.getMakesUseOfSchema();
                for (Schema tgS : tgUses) {
                    if (targetSchemas.contains(tgS)) {
                        metaphors.add(m);
                    }
                }
            }
        }
        if (metaphors.isEmpty()) {
            Set<Metaphor> foundcms = getMetaphorsFromSourceSchemas(sourceSchemas);
            for (Metaphor ssmet : foundcms) {
                metaphors.add(ssmet);
            }
        }
        // add the ones that we found to the existing set
        Set<Metaphor> cms = new HashSet<Metaphor>(lm.getIsInstanceOfMetaphor());
        for (Metaphor newm : metaphors) {
            if (!cms.contains(newm)) {
                cms.add(newm);
                lm.addIsInstanceOfMetaphor(newm);
            }
        }
        List<String> matchingMetaphors = new ArrayList<String>();
        for (Metaphor icm : cms) {
            matchingMetaphors.add(icm.getHasName());
        }
        args[5] = StringUtils.join(matchingMetaphors, ",");

        // frames in framenet that match the source lemma
        args[6] = StringUtils.join(sourceFrames, ",");

        // frames in framenet that match the target lemma
        args[7] = StringUtils.join(targetFrames, ",");

        return args;
    }

    private Set<Metaphor> getMetaphorsFromSourceSchemas(Collection<Schema> schemas) {
        List<Collection<Schema>> schemaq = new ArrayList<Collection<Schema>>();
        Set<Metaphor> mprocessed = new HashSet<Metaphor>();
        Set<Schema> sprocessed = new HashSet<Schema>();
        Set<Metaphor> results = new HashSet<Metaphor>();
        schemaq.add(schemas);
        int i = 0;
        while (i < schemaq.size()) {
            Collection<Schema> schemalist = schemaq.get(i);
            Set<Metaphor>metaphors = new HashSet<Metaphor>();
            innerfor:for (Schema schema : schemalist) {
                if (sprocessed.contains(schema)) {
                    continue innerfor;
                }
                for (Metaphor m: schema.getIsSourceDomainOfMetaphors()) {
                    if (mprocessed.contains(m)==false) {
                        metaphors.add(m);
                        mprocessed.add(m);
                    }
                }
                sprocessed.add(schema);
            }
            results.addAll(getGeneralMetaphors(metaphors));
            if (results.isEmpty()) {
                console.append("No metaphors found.\n");
                Set<Schema> subcases = new HashSet<Schema>();
                for (Schema schema: schemas) {
                    for (Schema subschema: schema.getIsSubcaseOfSchema()) {
                        if (sprocessed.contains(subschema)==false) {
                            subcases.add(subschema);
                        }
                    }
                }
                if (subcases.size() > 0) {
                    schemaq.add(subcases);
                }
            }
            i++;
        }
        return results;
    }

    private Set<Metaphor> getGeneralMetaphors(Collection<Metaphor> mm) {
        Set<Metaphor> filtered = new HashSet<Metaphor>();
        mainloop: for (Metaphor m : mm) {
            console.append("\nConsidering " + m.getHasName() + "\n");
            // skip if marked as entailed
            if (m.getHasMetaphorType().contains("Entailed")) {
                console.append("==> skipping because it is Entailed!\n");
                continue mainloop;
            }
            // stip if not General
            console.append("Metaphor level is " + m.getHasMetaphorLevel() + "\n");

            String level = m.getHasMetaphorLevel();
            if (level != null && level.equals("Specific")) {
                console.append("==> skipping because it is specific\n");
                continue mainloop;
            }

            // Skip if it is entailed by another metaphor
            if (m.getIsEntailedByMetaphor().isEmpty() == false) {
                console.append("==>skipping because it is entailed by other metaphors, they are:\n");
                for (Metaphor entm : m.getIsEntailedByMetaphor()) {
                    console.append("====> " + entm.getHasName() + "\n");
                }
                continue mainloop;
            }

            // skip if this metaphor is a subcase of any metaphor in the list mm
            if (m.getIsSubcaseOfMetaphor().isEmpty()) {
                // this metaphor is not a subcase of any other metaphor
                // so far so good
            } else {
                for (Metaphor subcasem : m.getIsSubcaseOfMetaphor()) {
                    if (mm.contains(m)) {
                        console.append("==>skipping because " + m.getHasName() + " is a subcase of " + subcasem.getHasName() + "\n");
                        continue mainloop;
                    }
                }
            }

            // otherwise: add
            console.append("Adding " + m.getHasName() + "\n");
            filtered.add(m);
        }
        return filtered;
    }
    

    private String getSchemaNames(Set<Schema> schemas) {
        List<String> names = new ArrayList<String>();
        for (Schema s : schemas) {
            names.add(s.getHasName());
        }
        return StringUtils.join(names, ",");
    }
}
