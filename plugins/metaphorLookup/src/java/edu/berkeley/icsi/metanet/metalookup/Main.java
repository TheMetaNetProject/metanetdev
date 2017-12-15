package edu.berkeley.icsi.metanet.metalookup;

import edu.berkeley.icsi.metanet.repository.MetaNetFactory;
import java.awt.BorderLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.HashMap;
import java.util.Set;

import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;

import org.protege.editor.owl.model.OWLModelManager;
import org.protege.editor.owl.ui.view.AbstractOWLViewComponent;
import org.protege.owl.codegeneration.inference.ReasonerBasedInference;
import org.semanticweb.owlapi.model.OWLOntology;

// an example tab
public class Main extends AbstractOWLViewComponent {
	private static final long serialVersionUID = 5343269347459987438L;
	private static final String FRAMENETURL = "https://framenet2.icsi.berkeley.edu/fnReports/data/luIndex.xml";
	
	/* Declaring class variables
	 * an instance of AVis will have a mainPanel which contains the toolBar, selectorPane, and graphComponent
	 */
	private OWLOntology owlModel;
	private SearchPanel searchPanel;
	private JSplitPane resultPanel;
	private EntityLibrary library;
	private JSplitPane mainPanel;
	private HashMap<String, Set<String>> frames;
    private MetaNetFactory factory;
        
	// startup code
	public void initialiseOWLView() throws Exception{
		
		setLayout(new BorderLayout());
		try {
			OWLModelManager manager = getOWLModelManager();
			owlModel = manager.getActiveOntology();
                        factory = new MetaNetFactory(owlModel,
                            new ReasonerBasedInference(owlModel, manager.getOWLReasonerManager().getCurrentReasoner()));
			library = new EntityLibrary(owlModel);
			// let's get a list of all the frames
			XMLParser parser = new XMLParser();
			frames = parser.parseDocument(FRAMENETURL);
			// setting up the UI
			searchPanel = new SearchPanel(owlModel,factory);
			searchPanel.searchButton.addActionListener(new ActionListener() {
				public void actionPerformed(ActionEvent e) {
					SearchPanelListItem[] selected = new SearchPanelListItem[searchPanel.selectedList.lingListModel.size()];
					searchPanel.selectedList.lingListModel.copyInto(selected);
					//System.out.println(selected.length);
					resultPanel = new ResultTable(owlModel, factory, selected, library, frames);
					mainPanel.setRightComponent(resultPanel);
					mainPanel.setDividerLocation(300);
					mainPanel.setResizeWeight(0.0);
					mainPanel.setDividerSize(0);
					mainPanel.validate();
				}
			});
			
			mainPanel = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
			mainPanel.setDividerLocation(300);
			mainPanel.setResizeWeight(0.0);
			mainPanel.setDividerSize(0);
			mainPanel.setLeftComponent(searchPanel);
			mainPanel.setRightComponent(new ResultTable());
			
			add(mainPanel, BorderLayout.CENTER);
			
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

