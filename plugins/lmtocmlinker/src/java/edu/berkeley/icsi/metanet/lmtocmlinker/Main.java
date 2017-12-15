package edu.berkeley.icsi.metanet.lmtocmlinker;

import edu.berkeley.icsi.metanet.repository.LexicalUnit;
import edu.berkeley.icsi.metanet.repository.LinguisticMetaphor;
import edu.berkeley.icsi.metanet.repository.MetaNetFactory;
import edu.berkeley.icsi.metanet.repository.Schema;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.AdjustmentEvent;
import java.awt.event.AdjustmentListener;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.BoxLayout;

import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTable;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.RowFilter;
import javax.swing.ScrollPaneConstants;
import javax.swing.SwingWorker;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableColumn;
import javax.swing.table.TableRowSorter;

import org.protege.editor.owl.model.OWLModelManager;
import org.protege.editor.owl.ui.view.AbstractOWLViewComponent;
import org.protege.owl.codegeneration.inference.ReasonerBasedInference;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * A tab plugin to Protege for assigning LMs automatically to CMs.
 *
 * @author jhong
 */
public class Main extends AbstractOWLViewComponent {

    private static final long serialVersionUID = 5343269347459987441L;
    private OWLOntology owlModel;
    private SearchPanel searchPanel;
    private JSplitPane resultPanel;
    private JSplitPane mainPanel;
    private HashMap<String, Set<String>> frames;
    private MetaNetFactory factory;
    private JTextArea consoleText;
    private JScrollPane resultsPane;
    private JScrollPane consolePane;
    private ResultTable resultTable;
    private MetaphorFinder finder;
    private String[] tableHeaders = {"Linguistic Metaphor",
        "Source Lexical Units",
        "Target Lexical Units",
        "Source Schemas",
        "Target Schemas",
        "Metaphors",
        "Source Frame",
        "Target Frame"};
    private Object[][] data = {
        {"", "", "", "", "", "", "", ""}
    };
    private SearchPanelListItem[] selected;
    private ReasonerBasedInference reasoner;
    
    /**
     * Initializes the tab
     *
     */
    public void initialiseOWLView() throws Exception {

        System.err.println("Initializing tab");
        setLayout(new BorderLayout());
        try {
            OWLModelManager manager = getOWLModelManager();
            owlModel = manager.getActiveOntology();

            System.err.println("Retrieving reasoner");
            reasoner = new ReasonerBasedInference(owlModel,
                    manager.getOWLReasonerManager().getCurrentReasoner());
            System.err.println("Initializing metanet factory");
            factory = new MetaNetFactory(owlModel, reasoner);

            System.err.println("Retrieving frame index");

            consoleText = new JTextArea();

            // let's get a list of all the frames
            FrameNetLUIndexParser parser = new FrameNetLUIndexParser();
            frames = parser.getLU2FrameMap();

            consoleText.append("Read in "+frames.size()+" LUs.");
            

            System.err.println("Initializing the metaphor finder");
            finder = new MetaphorFinder(owlModel, factory, frames, consoleText);
            
            // setting up the UI
            System.err.println("Setting up the search panel");
            searchPanel = new SearchPanel(owlModel, factory);
            searchPanel.searchButton.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    System.err.println("Commencing search action...");
                    selected = new SearchPanelListItem[searchPanel.selectedList.lingListModel.size()];
                    searchPanel.selectedList.lingListModel.copyInto(selected);
                    SwingWorker worker = new SwingWorker<Object[][], Void>() {
                        @Override
                        protected Object[][] doInBackground() throws Exception {
                            Object[][] data = new Object[selected.length][8];
                            int i = 0;
                            for (SearchPanelListItem item: selected) {
                                OWLNamedIndividual linguisticMetaphor = item.individual();
                                LinguisticMetaphor lm = factory.getLinguisticMetaphor(linguisticMetaphor.getIRI().toString());
                                Object[] row = finder.findCMsforLM(lm);
                                resultTable.addDataRow(row);
                                data[i] = row;
                                i++;
                            }
                            return data;
                        }

                    };
                    System.err.println("Running search on " + selected.length + " LMs");
                    worker.execute();
                }
            });

            mainPanel = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
            mainPanel.setDividerLocation(300);
            mainPanel.setOneTouchExpandable(true);
            mainPanel.setResizeWeight(0.0);
            mainPanel.setDividerSize(5);
            mainPanel.setLeftComponent(searchPanel);

            resultPanel = new JSplitPane(JSplitPane.VERTICAL_SPLIT);

            resultTable = new ResultTable(data, tableHeaders);
            
            resultsPane = new JScrollPane(resultTable);
            resultsPane.setViewportView(resultTable);
            resultsPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_ALWAYS);

            consolePane = new JScrollPane(consoleText);

            resultPanel.setDividerLocation(450);
            resultPanel.setResizeWeight(0.0);
            resultPanel.setDividerSize(0);
            resultPanel.setLeftComponent(resultTable.getStuffer(resultsPane));
            resultPanel.setRightComponent(consolePane);

            mainPanel.setRightComponent(resultPanel);

            add(mainPanel, BorderLayout.CENTER);
            mainPanel.validate();

        } catch (Exception e) {
            JLabel error = new JLabel("There was an error loading the plugin, please double check that you have the correct Metaphor repository loaded and try again");
            add(error, BorderLayout.PAGE_START);
            JButton refresh = new JButton("Reload");
            refresh.addActionListener(new ActionListener() {
                public void actionPerformed(ActionEvent e) {
                    try {
                        initialiseOWLView();
                    } catch (Exception e1) {
                        // TODO Auto-generated catch block
                        e1.printStackTrace();
                    }
                }
            });
            add(refresh, BorderLayout.CENTER);
            e.printStackTrace();
        }

    }

    @Override
    protected void disposeOWLView() {
        owlModel = null;
    }
}
