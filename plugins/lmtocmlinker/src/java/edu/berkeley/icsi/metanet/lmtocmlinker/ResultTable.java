package edu.berkeley.icsi.metanet.lmtocmlinker;

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
import java.util.HashSet;
import org.apache.commons.lang3.StringUtils;

public class ResultTable extends JTable {

    private DefaultTableModel dm;
    private TableRowSorter<DefaultTableModel> sorter;

    ResultTable(Object[][] data, String[] tableHeaders) {
        dm = new DefaultTableModel() {
            public Class<String> getColumnClass(int columnIndex) {
                return String.class;
            }

            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        dm.setDataVector(data, tableHeaders);
        setModel(dm);
        sorter = new TableRowSorter<DefaultTableModel>(dm);
        TableColumn column = null;
        for (int i = 0; i < 8; i++) {
            column = getColumnModel().getColumn(i);
            column.setPreferredWidth(150);
        }
        setDefaultRenderer(String.class, new MultiLineTableCellRenderer());
        setFillsViewportHeight(true);
        setAutoCreateRowSorter(true);
        setAutoResizeMode(JTable.AUTO_RESIZE_OFF);
        setShowGrid(true);
        setShowVerticalLines(true);
        setShowHorizontalLines(true);
        setGridColor(Color.LIGHT_GRAY);
        setAutoscrolls(true);
        setRowSorter(sorter);

    }
    
    public void setDataHeaders(Object[][] data, String[] headers) {
        dm.setDataVector(data, headers);
        setModel(dm);
        sorter.setModel(dm);
        setRowSorter(sorter);
    }
    
    public void addDataRow(Object[] rowData) {
        dm.addRow(rowData);
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

    public Stuffer getStuffer (JScrollPane results) {
        return new Stuffer(results);
    }
    
    public class Stuffer extends JPanel {

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
}