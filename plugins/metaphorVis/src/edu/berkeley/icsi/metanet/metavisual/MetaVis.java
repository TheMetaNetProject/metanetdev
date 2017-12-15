package edu.berkeley.icsi.metanet.metavisual;

import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

import org.protege.editor.owl.ui.view.AbstractOWLViewComponent;
import org.protege.editor.owl.model.OWLModelManager;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;

import com.mxgraph.model.mxCell;
import com.mxgraph.swing.mxGraphComponent;

// an example tab
public class MetaVis extends AbstractOWLViewComponent {
	private static final long serialVersionUID = 5343269347459987438L;
	
	/* Declaring class variables
	 * an instance of AVis will have a mainPanel which contains the toolBar, selectorPane, and graphComponent
	 */
	private OWLOntology owlModel;
	private GraphComponent graphComponent;
	private JPanel toolBar;
	private OptionsPanel selectorPane;
	private GridBagConstraints graphConstraints;
	private JSplitPane mainPanel;
	private EntityLibrary library;
	
	// startup code
	public void initialiseOWLView() throws Exception{
		
		setLayout(new BorderLayout());
		try {
			OWLModelManager manager = getOWLModelManager();
			owlModel = manager.getActiveOntology();
			library = new EntityLibrary(owlModel);
			// initialize default variables:
			graphComponent = new GraphComponent(new GraphModel());
			selectorPane = new OptionsPanel(owlModel, library);
			// build toolBar
			toolBar = buildToolBar();
			// now build main panel, make use of everything we've initialized so far
			mainPanel = buildMainPanel();
			
			removeAll();
			add(mainPanel, BorderLayout.CENTER);
			repaint();
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
		}
	}
	
	private JSplitPane buildMainPanel() {
		JSplitPane mainPanel = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT);
		
		JPanel rightPanel = new JPanel(new GridBagLayout());
		GridBagConstraints toolBarConstraints = new GridBagConstraints();
		graphConstraints = new GridBagConstraints();
		toolBarConstraints.fill = GridBagConstraints.BOTH;
		toolBarConstraints.gridx = 0;
		toolBarConstraints.gridy = 0;
		toolBarConstraints.gridwidth = 3;
		toolBarConstraints.gridheight = 1;
		toolBarConstraints.anchor = GridBagConstraints.CENTER;
		
		graphConstraints.fill = GridBagConstraints.BOTH;
		graphConstraints.gridx = 0;
		graphConstraints.gridy = 1;
		graphConstraints.gridwidth = 3;
		graphConstraints.gridheight = 2;
		graphConstraints.anchor = GridBagConstraints.CENTER;
		graphConstraints.weightx = 1.0;
		graphConstraints.weighty = 1.0;
		
		rightPanel.add(toolBar, toolBarConstraints);
		rightPanel.add(graphComponent, graphConstraints);
		mainPanel.setDividerLocation(300);
		mainPanel.setResizeWeight(0.5);
		mainPanel.setLeftComponent(selectorPane);
		mainPanel.setRightComponent(rightPanel);
		return mainPanel;
	}
	
	private JPanel buildToolBar() {
        // toolbar Buttons
        JPanel buttonBar = new JPanel();
        buttonBar.setLayout(new FlowLayout(FlowLayout.TRAILING));
		Font font = new Font("Dialog", Font.PLAIN, 12);
		
		/** Build the buttons and their split pane **/
		
		// This button will show the schemas & roles inside each metaphor
		JButton showSchemasButton = new JButton("Show Schemas");
		showSchemasButton.setFont(font);
		showSchemasButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				GraphModel graphModel = (GraphModel) graphComponent.getGraph();
				Object[] cells = graphModel.getChildVertices(graphModel.getDefaultParent());
				graphModel.cellsFolded(cells, false, false, true);
				for (Object obj : graphModel.schemaBindingVertices) {
					mxCell vertex = (mxCell) obj;
					graphModel.getModel().setVisible(vertex, true);
				}
				for (Object obj : graphModel.schemaBindingEdges) {
					mxCell edge = (mxCell) obj;
					graphModel.getModel().setVisible(edge, true);
				}
			}
		});
		buttonBar.add(showSchemasButton);
		
		// This button will hide the schemas & roles inside each metaphor
		JButton hideSchemasButton = new JButton("Hide Schemas");
		hideSchemasButton.setFont(font);
		hideSchemasButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				GraphModel graphModel = (GraphModel) graphComponent.getGraph();
				Object[] cells = graphModel.getChildVertices(graphModel.getDefaultParent());
				graphModel.cellsFolded(cells, true, false, true);
				for (Object obj : graphModel.schemaBindingVertices) {
					mxCell vertex = (mxCell) obj;
					graphModel.getModel().setVisible(vertex, false);
				}
				for (Object obj : graphModel.schemaBindingEdges) {
					mxCell edge = (mxCell) obj;
					graphModel.getModel().setVisible(edge, false);
				}
			}
		});
		buttonBar.add(hideSchemasButton);
		
		// This button will expand schema relationships regardless of metaphors
		JButton expandSchemaDirect = new JButton("Schema Bindings (Direct)");
		expandSchemaDirect.setFont(font);
		expandSchemaDirect.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				GraphModel graphModel = (GraphModel) graphComponent.getGraph();
				for (Object obj : graphModel.getChildVertices(graphModel.getDefaultParent())) {
					for (Object obj2 : graphModel.getChildVertices(obj)) {
						if (!graphModel.getLabel(obj2).equals("")) {
							graphModel.expandSchemaOutgoing(obj2, false);
							graphComponent.reApplyLayout(graphModel.getDefaultParent(), obj2);
							graphModel.expandSchemaOutgoing(obj2, true);
						}
					}
				}
			}
		});
		buttonBar.add(expandSchemaDirect);
		
		// This button will only draw graph 1-level deep and manual expansion can be done by right clicking on each node
		JButton drawDirectButton = new JButton("Draw Graph (Direct Relationships)");
		drawDirectButton.setFont(font);
		drawDirectButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
					drawButtonAction(false);
			}
		});
		buttonBar.add(drawDirectButton);
		
		// This button will draw the entire graph and manual collapsing can be done by right clicking each node
		JButton drawAllButton = new JButton("Draw Graph (All Relationships)");
		drawAllButton.setFont(font);
		drawAllButton.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent e) {
					drawButtonAction(true);
			}
		});
		buttonBar.add(drawAllButton);
		
		return buttonBar;
	}
	
	private void drawButtonAction(boolean expandAll) {
		OWLNamedIndividual ind = selectorPane.getSelectedIndividual();
		Object[] metaphorRelations = selectorPane.getMetaphorRelations();
		Object[] schemaRelations = selectorPane.getSchemaRelations();
		boolean schema = true;
		if (selectorPane.individualTabs.getSelectedIndex() == 0) {
			schema = false;
		}
		JOptionPane frame = new JOptionPane();
		if (ind == null) {
			JOptionPane.showMessageDialog(frame,
				    "Please select either a Metaphor or a Schema",
				    "Inane error",
				    JOptionPane.ERROR_MESSAGE);
		} else {
			if (selectorPane.individualTabs.getSelectedIndex() == 0 && metaphorRelations == null) {
				JOptionPane.showMessageDialog(frame,
					    "Please choose at least 1 Metaphor Relationship.",
					    "Inane error",
					    JOptionPane.ERROR_MESSAGE);
			} else if (selectorPane.individualTabs.getSelectedIndex() == 1 && schemaRelations == null) {
				JOptionPane.showMessageDialog(frame,
					    "Please choose at least 1 Schema Relationship.",
					    "Inane error",
					    JOptionPane.ERROR_MESSAGE);
			} else {
				JPanel panel = (JPanel) mainPanel.getRightComponent();
				panel.remove(graphComponent);
				graphComponent = prepareGraph(ind, metaphorRelations, schemaRelations, expandAll, schema);
				//graphComponent = prepareGraph("Metaphor_ACQUIRING_IDEAS_IS_EATING", "isRelatedToMetaphor", false);
				panel.add(graphComponent, graphConstraints);
				mainPanel.setRightComponent(panel);
				mainPanel.setDividerLocation(300);
				mainPanel.setResizeWeight(0.5);
			}
		}
	}

	private GraphComponent prepareGraph(OWLNamedIndividual oIndividual, Object[] metaphorRelations, Object[] schemaRelations, boolean expand, boolean schema) {
		GraphModel graph = new GraphModel(owlModel, library, oIndividual, metaphorRelations, schemaRelations, expand, schema);
		GraphComponent graphComponent = new GraphComponent(graph);		
		return graphComponent;
	}

	@Override
	protected void disposeOWLView() {
		owlModel = null;
		graphComponent = null;
		toolBar = null;
		selectorPane = null;
		graphConstraints = null;
		mainPanel = null;
	}
}

