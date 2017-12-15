package edu.berkeley.icsi.metanet.metalookup;

import java.awt.Color;
import java.awt.Component;
import java.awt.Dimension;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;

import javax.swing.BoxLayout;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.RowFilter;
import javax.swing.ScrollPaneConstants;
import javax.swing.UIManager;
import javax.swing.border.EmptyBorder;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableRowSorter;

import org.semanticweb.owlapi.model.OWLAnnotationProperty;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;

import edu.berkeley.icsi.metanet.repository.*;
import java.util.Collection;
import org.apache.commons.lang3.StringUtils;

public class ResultTable extends JSplitPane {

    private OWLOntology owlModel;
    private EntityLibrary library;
    private SearchPanelListItem[] items;
    private Object[][] results;
    private HashMap<String, Set<String>> frames;
    private JScrollPane resultsPane;
    private JScrollPane console;
    private JTextArea consoleText;
    private DefaultTableModel dm;
    private TableRowSorter<DefaultTableModel> sorter;
    /* it doesn't make sense for this to be here, but for now ... */
    private MetaNetFactory factory;

    class Stuffer extends JPanel {

        private JTextField filter;

        Stuffer(JScrollPane results) {
            setLayout(new BoxLayout(this, BoxLayout.PAGE_AXIS));

            JPanel filterPane = new JPanel();
            JLabel filterText = new JLabel("Filter");
            filter = new JTextField(50);
            filter.getDocument().addDocumentListener(
                    new DocumentListener() {
                        public void changedUpdate(DocumentEvent e) {
                            newFilter();
                        }

                        public void insertUpdate(DocumentEvent e) {
                            newFilter();
                        }

                        public void removeUpdate(DocumentEvent e) {
                            newFilter();
                        }
                    });

            filterPane.add(filterText);
            filterText.setLabelFor(filter);
            filterPane.add(filter);

            add(results);
            add(filterPane);
        }

        public void newFilter() {
            RowFilter<DefaultTableModel, Object> rf = null;
            //If current expression doesn't parse, don't update.
            try {
                rf = RowFilter.regexFilter("(?i)" + filter.getText(), 0);
            } catch (java.util.regex.PatternSyntaxException e) {
                return;
            }
            sorter.setRowFilter(rf);
        }
    }

    ResultTable() {
        super(JSplitPane.VERTICAL_SPLIT);

        owlModel = null;
        library = null;
        items = null;
        results = null;
        resultsPane = new JScrollPane();
        console = new JScrollPane();

        String[] tableHeaders = {"Linguistic Metaphor",
            "Source Lexical Units",
            "Target Lexical Units",
            "Source Schemas",
            "Target Schemas",
            "Metaphors",
            "Source Frame",
            "Target Frame"};

        Object[][] data = {
            {"", "", "", "", "", "", "", ""}
        };

        JTable resultTable = new JTable(data, tableHeaders);

        resultsPane.add(resultTable);
        resultTable.setFillsViewportHeight(true);
        resultsPane.setViewportView(resultTable);

        consoleText = new JTextArea();
        consoleText.setEditable(false);
        console = new JScrollPane(consoleText);

        setDividerLocation(450);
        setResizeWeight(0.0);
        setDividerSize(0);
        setLeftComponent(new Stuffer(resultsPane));
        setRightComponent(console);

    }

    ResultTable(OWLOntology owlModel, MetaNetFactory mfact, SearchPanelListItem[] items, EntityLibrary library, HashMap<String, Set<String>> frames) {

        super(JSplitPane.VERTICAL_SPLIT);

        this.owlModel = owlModel;
        this.factory = mfact;
        this.library = library;
        this.items = items;
        this.frames = frames;
        consoleText = new JTextArea();
        consoleText.setEditable(false);

        runSearch();

        String[] tableHeaders = {"Linguistic Metaphor",
            "Source Lexical Units",
            "Target Lexical Units",
            "Source Schemas",
            "Target Schemas",
            "Metaphors",
            "Source Frame",
            "Target Frame"};

        dm = new DefaultTableModel() {
            public Class<String> getColumnClass(int columnIndex) {
                return String.class;
            }

            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        dm.setDataVector(results, tableHeaders);
        JTable resultTable = new JTable(dm);
        sorter = new TableRowSorter<DefaultTableModel>(dm);
        TableColumn column = null;
        for (int i = 0; i < 8; i++) {
            column = resultTable.getColumnModel().getColumn(i);
            column.setPreferredWidth(150);
        }
        resultTable.setDefaultRenderer(String.class, new MultiLineTableCellRenderer());
        resultTable.setFillsViewportHeight(true);
        resultTable.setAutoCreateRowSorter(true);
        resultTable.setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        resultTable.setShowGrid(true);
        resultTable.setShowVerticalLines(true);
        resultTable.setShowHorizontalLines(true);
        resultTable.setGridColor(Color.LIGHT_GRAY);
        resultTable.setAutoscrolls(true);
        resultTable.setRowSorter(sorter);

        resultsPane = new JScrollPane(resultTable);
        resultsPane.setViewportView(resultTable);
        resultsPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_ALWAYS);

        console = new JScrollPane(consoleText);

        setDividerLocation(450);
        setResizeWeight(0.0);
        setDividerSize(0);
        setLeftComponent(new Stuffer(resultsPane));
        setRightComponent(console);

    }

    private void runSearch() {

        OWLDataProperty hasLinguisticTarget = library.getDataProperties().get("hasLinguisticTarget");
        OWLDataProperty hasLinguisticSource = library.getDataProperties().get("hasLinguisticSource");
        OWLAnnotationProperty label = library.getAnnotations().get("label");
        OWLDataProperty hasName = library.getDataProperties().get("hasName"); // name for most Entities
        OWLDataProperty hasLemma = library.getDataProperties().get("hasLemma"); // name for LexicalUnits
        OWLObjectProperty hasLexicalUnit = library.getObjectProperties().get("hasLexicalUnit");
        OWLObjectProperty hasSourceSchema = library.getObjectProperties().get("hasSourceSchema");
        OWLObjectProperty hasTargetSchema = library.getObjectProperties().get("hasTargetSchema");
        ArrayList<Object[]> data = new ArrayList<Object[]>();

        for (SearchPanelListItem item : items) {
            Object[] args = new Object[8];
            for (int i = 0; i < 8; i++) {
                args[i] = "";
            }
            OWLNamedIndividual linguisticMetaphor = item.individual();
            LinguisticMetaphor lm = factory.getLinguisticMetaphor(linguisticMetaphor.getIRI().toString());

            // Experimenting here with using the metanet api.

//			String targetLexUnit = stripQuotations(linguisticMetaphor.getDataPropertyValues(hasLinguisticTarget, owlModel).toString());
//			String sourceLexUnit = stripQuotations(linguisticMetaphor.getDataPropertyValues(hasLinguisticSource, owlModel).toString());
            String targetLemma = lm.getHasLinguisticTarget();
            String sourceLemma = lm.getHasLinguisticSource();

            List<LexicalUnit> targetLUs = new ArrayList<LexicalUnit>();
            List<LexicalUnit> sourceLUs = new ArrayList<LexicalUnit>();

            Collection<? extends LexicalUnit> lus = factory.getAllLexicalUnitInstances();
            for (LexicalUnit lu : lus) {
                String lemma = lu.getHasLemma();
                if (lemma.equals(targetLemma)) {
                    targetLUs.add(lu);

                } else if (lemma.equals(sourceLemma)) {
                    sourceLUs.add(lu);
                }
            }
            /* fill in LU names and Schema names for source */
            if (!sourceLUs.isEmpty()) {
                List<String> lunames = new ArrayList<String>();
                List<String> schemanames = new ArrayList<String>();
                for (LexicalUnit lu : sourceLUs) {
                    lunames.add(lu.getHasLemma());
                    Schema sc = lu.getIsDefinedRelativeToSchema();
                    if (sc==null) {
                        consoleText.append(item.toString()+": LU "+lu.getHasLemma()+" has no linked Schema");
                    } else {
                        schemanames.add(sc.getHasName());
                    }                }
                args[1] = StringUtils.join(lunames, ",");
                args[3] = StringUtils.join(schemanames, ",");
            } else {
                consoleText.append(item.toString() + ": Source LexicalUnits NOT present in database.\n");
            }
            /* fill in LU names and Schema names for target */
            /* make list of targetSchemas */
            List<Schema> targetSchemas = new ArrayList<Schema>();
            if (!targetLUs.isEmpty()) {
                List<String> lunames = new ArrayList<String>();
                List<String> schemanames = new ArrayList<String>();
                for (LexicalUnit lu : targetLUs) {
                    lunames.add(lu.getHasLemma());
                    Schema tg = lu.getIsDefinedRelativeToSchema();
                    targetSchemas.add(tg);
                    if (tg==null) {
                        consoleText.append(item.toString()+": LU "+lu.getHasLemma()+" has no linked Schema");
                    } else {
                        schemanames.add(tg.getHasName());
                    }
                }
                args[2] = StringUtils.join(lunames, ",");
                args[4] = StringUtils.join(schemanames, ",");
            } else {
                consoleText.append(item.toString() + ": Target LexicalUnits NOT present in database.\n");
            }

            /* try to find metaphors */
            if (!sourceLUs.isEmpty() && !targetLUs.isEmpty()) {
                List<String> matches = new ArrayList<String>();
                for (LexicalUnit slu : sourceLUs) {
                    Schema sourceS = slu.getIsDefinedRelativeToSchema();
                    if (sourceS==null) {
                        consoleText.append(item.toString()+": LU "+slu.getHasLemma()+" has no linked Schema");
                        continue;
                    }
                    Collection<Metaphor> mets = (Collection<Metaphor>)sourceS.getIsSourceDomainOfMetaphors();
                    for (Metaphor m: mets) {
                        if (targetSchemas.contains(m.getHasTargetSchema())) {
                            matches.add(m.getHasName());
                        }
                    }
                }
                args[5] = StringUtils.join(matches,",");
            }

            if (frames.get(sourceLemma) != null) {
                for (String str : frames.get(sourceLemma)) {
                    args[6] = args[6] + str + "\n";
                }
            }

            if (frames.get(targetLemma) != null) {
                for (String str : frames.get(targetLemma)) {
                    args[7] = args[7] + str + "\n";
                }
            }

            args[0] = item.toString();
            data.add(args);
        }

        Object[][] results = new Object[data.size()][8];
        for (int i = 0; i < data.size(); i++) {
            results[i] = data.get(i);
        }

        this.results = results;

    }

    private String stripQuotations(String raw) {
        //Because Linguistic Metaphors' names include random string, these next few lines will give us the actual name
        String[] arr = raw.split("\"");
        raw = arr[1];

        return raw;
    }

    class MultiLineTableCellRenderer extends JTextArea implements TableCellRenderer {

        private List<List<Integer>> rowColHeight = new ArrayList<List<Integer>>();

        public MultiLineTableCellRenderer() {
            setLineWrap(true);
            setWrapStyleWord(true);
            setOpaque(true);
        }

        public Component getTableCellRendererComponent(
                JTable table, Object value, boolean isSelected, boolean hasFocus,
                int row, int column) {
            if (isSelected) {
                setForeground(table.getSelectionForeground());
                setBackground(table.getSelectionBackground());
            } else {
                setForeground(table.getForeground());
                setBackground(table.getBackground());
            }
            setFont(table.getFont());
            if (hasFocus) {
                setBorder(UIManager.getBorder("Table.focusCellHighlightBorder"));
                if (table.isCellEditable(row, column)) {
                    setForeground(UIManager.getColor("Table.focusCellForeground"));
                    setBackground(UIManager.getColor("Table.focusCellBackground"));
                }
            } else {
                setBorder(new EmptyBorder(1, 2, 1, 2));
            }
            if (value != null) {
                setText(value.toString());
            } else {
                setText("");
            }
            adjustRowHeight(table, row, column);
            return this;
        }

        /**
         * Calculate the new preferred height for a given row, and sets the
         * height on the table.
         */
        private void adjustRowHeight(JTable table, int row, int column) {
            //The trick to get this to work properly is to set the width of the column to the 
            //textarea. The reason for this is that getPreferredSize(), without a width tries 
            //to place all the text in one line. By setting the size with the with of the column, 
            //getPreferredSize() returnes the proper height which the row should have in
            //order to make room for the text.
            int cWidth = table.getTableHeader().getColumnModel().getColumn(column).getWidth();
            setSize(new Dimension(cWidth, 1000));
            int prefH = getPreferredSize().height;
            while (rowColHeight.size() <= row) {
                rowColHeight.add(new ArrayList<Integer>(column));
            }
            List<Integer> colHeights = rowColHeight.get(row);
            while (colHeights.size() <= column) {
                colHeights.add(0);
            }
            colHeights.set(column, prefH);
            int maxH = prefH;
            for (Integer colHeight : colHeights) {
                if (colHeight > maxH) {
                    maxH = colHeight;
                }
            }
            if (table.getRowHeight(row) != maxH) {
                table.setRowHeight(row, maxH);
            }
        }
    }
}