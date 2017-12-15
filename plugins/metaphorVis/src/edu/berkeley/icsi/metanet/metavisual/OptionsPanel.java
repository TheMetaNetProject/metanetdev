package edu.berkeley.icsi.metanet.metavisual;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.event.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Set;

import javax.swing.*;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;

import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;

public class OptionsPanel extends JPanel {
	private static final long serialVersionUID = 3689599666043501512L;

	private OWLOntology owlModel;
	private OWLNamedIndividual selectedIndividual;
	private Object[] metaphorRelations;
	private Object[] schemaRelations;
	private JList metaphorList;
	private JList schemaList;
	private JList metaphorRelationsList;
	private JList schemaRelationsList;
	private JList selectedItems;
	protected JTabbedPane individualTabs;
	private EntityLibrary library;
	
	public OWLNamedIndividual getSelectedIndividual() {
		return selectedIndividual;
	}
	
	public Object[] getMetaphorRelations() {
		return metaphorRelations;
	}
	
	public Object[] getSchemaRelations() {
		return schemaRelations;
	}
	
	public OptionsPanel(OWLOntology owlModel, EntityLibrary library) {
		this.owlModel = owlModel;
		this.library = library;
		setLayout(new BoxLayout(this, BoxLayout.PAGE_AXIS));
		
		// adding top & bottom components respectively
		JPanel listWithHeader = individualSelectionPane();
		JPanel propListWithHeader = propertySelectionPane();
		JPanel infoPanel = infoPanel();
		
		add(infoPanel);
		add(listWithHeader);
		add(propListWithHeader);
	}
	
	private JPanel infoPanel() {
		DefaultListModel infoModel = new DefaultListModel();
		infoModel.addElement("Currently Selected Metaphor:");
		infoModel.addElement("None");
		infoModel.addElement("");
		
		selectedItems = new JList(infoModel);
		selectedItems.setEnabled(false);
		selectedItems.setVisibleRowCount(3);
		
		JScrollPane selectedScroll = new JScrollPane(selectedItems, JScrollPane.VERTICAL_SCROLLBAR_NEVER, JScrollPane.HORIZONTAL_SCROLLBAR_NEVER);
		selectedScroll.setPreferredSize(new Dimension(300, selectedItems.getPreferredSize().height));
		
		JPanel infoPanel = new JPanel(new FlowLayout());
		infoPanel.add(selectedScroll);
		return infoPanel;
	}
	
	private JPanel individualSelectionPane() {
		/** Work on the Individual listing + setting pane **/
		// build individuals list
		DefaultListModel individualListModel = new DefaultListModel();
		// Populates list with METAPHORS
		for (OWLIndividual ind : library.getClasses().get("Metaphor").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			individualListModel.addElement(item);
		}
		for (OWLIndividual ind : library.getClasses().get("VettedMetaphor").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			individualListModel.addElement(item);
		}
		for (OWLIndividual ind : library.getClasses().get("AutoMetaphor").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			individualListModel.addElement(item);
		}
		metaphorList = new JList(individualListModel);
		metaphorList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		metaphorList.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				if (e.getValueIsAdjusting() == false) {
					int index = metaphorList.getSelectedIndex();
					if (index > -1) {
						OptionsListItem selectedInd = (OptionsListItem)metaphorList.getSelectedValue();
						selectedIndividual = selectedInd.individual();
						DefaultListModel listModel = (DefaultListModel)selectedItems.getModel();
						listModel.set(1, selectedInd);
					}
				}
			}
		});
		
		// BUILDING SCHEMA LIST
		DefaultListModel schemaListModel = new DefaultListModel();
		// Populates list with METAPHORS
		for (OWLIndividual ind : library.getClasses().get("Schema").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			schemaListModel.addElement(item);
		}
		for (OWLIndividual ind : library.getClasses().get("VettedSchema").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			schemaListModel.addElement(item);
		}
		for (OWLIndividual ind : library.getClasses().get("AutoSchema").getIndividuals(owlModel)) {
			OWLNamedIndividual indie = ind.asOWLNamedIndividual();
			OptionsListItem item = new OptionsListItem(getName(indie), indie);
			schemaListModel.addElement(item);
		}
		schemaList = new JList(schemaListModel);
		schemaList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		schemaList.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				if (e.getValueIsAdjusting() == false) {
					int index = schemaList.getSelectedIndex();
					if (index > -1) {
						OptionsListItem selectedInd = (OptionsListItem)schemaList.getSelectedValue();
						selectedIndividual = selectedInd.individual();
						DefaultListModel listModel = (DefaultListModel)selectedItems.getModel();
						listModel.set(1, selectedInd);
					}
				}
			}
		});
		
		JScrollPane metaphorListScroll = new JScrollPane(metaphorList);
		metaphorListScroll.setPreferredSize(new Dimension(300, 225));
		JScrollPane schemaListScroll = new JScrollPane(schemaList);
		schemaListScroll.setPreferredSize(new Dimension(300, 225));
		
		individualTabs = new JTabbedPane();
		individualTabs.addTab("Metaphors", metaphorListScroll);
		individualTabs.setMnemonicAt(0, KeyEvent.VK_1);
		individualTabs.addTab("Schemas", schemaListScroll);
		individualTabs.setMnemonicAt(1, KeyEvent.VK_2);
		
		JPanel listWithHeader = componentWithHeader(individualTabs, "Metaphor Selection");
		
		return listWithHeader;
	}
	
	private JPanel propertySelectionPane() {
		/** Work on the Property Listing + setting pane **/
		// now build the property list similarly
		metaphorRelationsList = new JList(buildMetaphorRelationsList());
		metaphorRelationsList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
		metaphorRelationsList.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				if (e.getValueIsAdjusting() == false) {
					Object[] selections = metaphorRelationsList.getSelectedValues();
					if (selections.length > 0) {
						metaphorRelations = selections;
					}
				}
			}
		});
		schemaRelationsList = new JList(buildSchemaRelationsList());
		schemaRelationsList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
		schemaRelationsList.addListSelectionListener(new ListSelectionListener() {
			public void valueChanged(ListSelectionEvent e) {
				if (e.getValueIsAdjusting() == false) {
					Object[] selections = schemaRelationsList.getSelectedValues();
					if (selections.length > 0) {
						schemaRelations = selections;
					}
				}
			}
		});
		JScrollPane metaphorScroll = new JScrollPane(metaphorRelationsList);
		metaphorScroll.setPreferredSize(new Dimension(300, 225));
		JScrollPane schemaScroll = new JScrollPane(schemaRelationsList);
		schemaScroll.setPreferredSize(new Dimension(300, 225));
		
		JTabbedPane tabbedPane = new JTabbedPane();
		tabbedPane.addTab("Metaphors", metaphorScroll);
		tabbedPane.setMnemonicAt(0, KeyEvent.VK_1);
		tabbedPane.addTab("Schemas", schemaScroll);
		tabbedPane.setMnemonicAt(1, KeyEvent.VK_2);
		
		JPanel propListWithHeader = componentWithHeader(tabbedPane, "Relationships Selection (1 or more)");
		
		return propListWithHeader;
	}
	
	private DefaultListModel buildMetaphorRelationsList() {
		DefaultListModel metaphorRelationsListModel = new DefaultListModel();
		HashMap<String, OWLObjectProperty> hash = library.getObjectProperties();
		metaphorRelationsListModel.addElement(hash.get("isRelatedToMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("entailsMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isEntailedByMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isRelatedToMetaphorBySource").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isRelatedToMetaphorByTarget").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isSubcaseOfMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isSourceSubcaseOfMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isTargetSubcaseOfMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isSupercaseOfMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("isUsedByMetaphor").getIRI().getFragment());
		metaphorRelationsListModel.addElement(hash.get("makesUseOfMetaphor").getIRI().getFragment());
		return metaphorRelationsListModel;
	}
	
	private DefaultListModel buildSchemaRelationsList() {
		DefaultListModel schemaRelationsListModel = new DefaultListModel();
		HashMap<String, OWLObjectProperty> hash = library.getObjectProperties();
		schemaRelationsListModel.addElement(hash.get("isRelatedToSchema").getIRI().getFragment());
		schemaRelationsListModel.addElement(hash.get("isSubcaseOfSchema").getIRI().getFragment());
		schemaRelationsListModel.addElement(hash.get("isSupercaseOfSchema").getIRI().getFragment());
		schemaRelationsListModel.addElement(hash.get("isUsedBySchema").getIRI().getFragment());
		schemaRelationsListModel.addElement(hash.get("makesUseOfSchema").getIRI().getFragment());
		return schemaRelationsListModel;
	}
	
	private JPanel componentWithHeader(JComponent component, String panelName) {
		JLabel panelLabel = new JLabel(panelName);
		JPanel headerPane = new JPanel();
		Dimension d = headerPane.getMaximumSize();
		d.height = 100;
		headerPane.setMaximumSize(d);
		headerPane.setLayout(new BorderLayout());
		headerPane.add(panelLabel, BorderLayout.LINE_START);
		JPanel listWithHeader = new JPanel();
		listWithHeader.setLayout(new BoxLayout(listWithHeader, BoxLayout.PAGE_AXIS));
		listWithHeader.add(headerPane);
		listWithHeader.add(component);
		
		return listWithHeader;
	}
	
	private String getName(OWLNamedIndividual individual) {
		OWLDataProperty name = library.getDataProperties().get("hasName");
		Set<OWLLiteral> lits = individual.getDataPropertyValues(name, owlModel);
		String indName = "";
		for (OWLLiteral lit : lits) {
			indName = lit.getLiteral();
		}
		return indName;
	}
	
}
