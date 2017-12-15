package edu.berkeley.icsi.metanet.metavisual;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLIndividual;
import org.semanticweb.owlapi.model.OWLLiteral;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLOntology;

import com.mxgraph.model.mxCell;
import com.mxgraph.model.mxGeometry;
import com.mxgraph.util.mxRectangle;
import com.mxgraph.view.mxCellState;
import com.mxgraph.view.mxGraph;
import com.mxgraph.view.mxStylesheet;

public class GraphModel extends mxGraph {
	
	private OWLOntology owlModel;
	private mxStylesheet styles;
	private OWLNamedIndividual rootIndividual;
	protected Set<OWLObjectProperty> metaphorRelations;
	protected Set<OWLObjectProperty> schemaRelations;
	protected Set<Object> schemaBindingVertices;
	protected Set<Object> schemaBindingEdges;
	protected HashMap<Object, Object[]> schemaToRoles;
	private Set<OWLNamedIndividual> schemaSet;
	private Set<OWLNamedIndividual> metaphorSet;
	private boolean expandAll = false;
	private EntityLibrary library;
	
	public GraphModel() {
		super();
	}

	public GraphModel(OWLOntology owlModel, EntityLibrary library, OWLNamedIndividual individual, Object[] metaphorRelations, Object[] schemaRelations, boolean expandAll, boolean schema) {
		// Setting class variables
		this.owlModel = owlModel;
		this.expandAll = expandAll;	
		this.library = library;
		this.metaphorRelations = new HashSet<OWLObjectProperty>();
		this.schemaRelations = new HashSet<OWLObjectProperty>();
		schemaBindingVertices = new HashSet<Object>();
		schemaBindingEdges = new HashSet<Object>();
		schemaToRoles = new HashMap<Object, Object[]>();
		rootIndividual = individual;
		if (metaphorRelations != null) {
			for (Object obj : metaphorRelations) {
				String relationName = (String) obj;
				this.metaphorRelations.add(library.getObjectProperties().get(relationName));
			}
		}
		if (schemaRelations != null) {
			for (Object obj : schemaRelations) {
				String relationName = (String) obj;
				this.schemaRelations.add(library.getObjectProperties().get(relationName));
			}
		}
		schemaSet = new HashSet<OWLNamedIndividual>();
		metaphorSet = new HashSet<OWLNamedIndividual>();
		
		// Start drawing graph & set graph properties
		setProperties();
		setGraphStyles();
		if (schema) {
			drawSchemaGraph();
		} else {
			drawGraph();
		}
	}
	
	/** METHODS THAT TAKE CARE OF DRAWING VARIOUS PARTS OF THE GRAPH **/
	
	private void drawSchemaGraph() {
		GraphVertexItem vertexObj = new GraphVertexItem(rootIndividual, getName(rootIndividual), "Schema");
		Object vertexRootCell = insertVertex(getDefaultParent(), null, vertexObj, 0, 0, 0, 0, "schemaMovable;fillColor=#ddbf2a");
		schemaSet.add(rootIndividual);
		updateChildrenCount(vertexObj, schemaRelations);
		redrawVertexBox(vertexRootCell);
		includeRoles(vertexRootCell);
		expandSchemaOutgoing(vertexRootCell, false);
		expandSchemaIncoming(vertexRootCell, false);
	}

	private void drawGraph() {
		GraphVertexItem vertexObj = new GraphVertexItem(rootIndividual, getName(rootIndividual), "Metaphor");
		Object vertexRootCell = insertVertex(getDefaultParent(), null, vertexObj, 0, 0, 0, 0, "fillColor=#ddbf2a");
		metaphorSet.add(rootIndividual);
		updateChildrenCount(vertexObj, metaphorRelations);
		redrawVertexBox(vertexRootCell);
		insertSchemaToMetaphor(vertexRootCell);
		expandMetaphorOutgoing(rootIndividual, vertexRootCell);
		expandMetaphorIncoming(rootIndividual, vertexRootCell);
	}
	
	public void expandMetaphorIncoming(OWLNamedIndividual currentMetaphor, Object source) {
		for (OWLObjectProperty edgeProperty : metaphorRelations) {
			Set<OWLNamedIndividual> subjects = library.getSubjectsSet().get(edgeProperty.getIRI().getFragment() + currentMetaphor.getIRI().getFragment());
			if (subjects != null) {
				for (OWLNamedIndividual indie : subjects) {
					if (!metaphorSet.contains(indie)) {
						metaphorSet.add(indie);
						GraphVertexItem subjectVal = new GraphVertexItem(indie, getName(indie), "Metaphor"); // create new DESTINATION OWLVertex for Graph
						Object target = insertVertex(getDefaultParent(), null, subjectVal, 0, 0, 0, 0);
						GraphEdgeItem edge = new GraphEdgeItem(edgeProperty); // create new OWLEdge for Graph
						Object e = insertEdge(getDefaultParent(), null, edge, source, target, "reverseEdge");
						moveEdgeToBack(e);
						updateChildrenCount(subjectVal, metaphorRelations);
						redrawVertexBox(target);
						insertSchemaToMetaphor(target);
						if (expandAll) {
							expandMetaphorOutgoing(indie, target);
							expandMetaphorIncoming(indie, target);
						}
					}
				}
			}
		}
	}

	public void expandMetaphorOutgoing(OWLNamedIndividual currentMetaphor, Object subject) {
		for (OWLObjectProperty edgeProperty : metaphorRelations) {
			Set<OWLIndividual> objects = currentMetaphor.getObjectPropertyValues(edgeProperty, owlModel);
			for (OWLIndividual it : objects) {
				OWLNamedIndividual indie = it.asOWLNamedIndividual();
				if (!metaphorSet.contains(indie)) {
					metaphorSet.add(indie);
					GraphVertexItem objectVal = new GraphVertexItem(indie, getName(indie), "Metaphor"); // create new DESTINATION OWLVertex for Graph
					Object object = insertVertex(getDefaultParent(), null, objectVal, 0, 0, 0, 0);
					// inserts Edge and takes care of inverse properties
					edgeInserterWithInverse(subject, object, edgeProperty, metaphorRelations);
					updateChildrenCount(objectVal, metaphorRelations);
					redrawVertexBox(object);
					insertSchemaToMetaphor(object);
					if (expandAll) {
						expandMetaphorOutgoing(indie, object);
						expandMetaphorIncoming(indie, object);
					}
				}
			}
		}
		// Sets expanded flag inside vertex to TRUE
		GraphVertexItem v = (GraphVertexItem) ((mxCell)subject).getValue();
		v.setExpandState(true);
		((mxCell)subject).setValue(v);
	}
	
	public void expandSchemaIncoming(Object source, boolean secondPass) {
		GraphVertex sourceVertex = new GraphVertex(source);
		Object[] roles = getChildVertices(source);
		for (OWLObjectProperty edgeProperty : schemaRelations) {
			Set<OWLNamedIndividual> subjects = library.getSubjectsSet().get(edgeProperty.getIRI().getFragment() + sourceVertex.getIndie().getIRI().getFragment());
			if (subjects != null) {
				for (OWLNamedIndividual indie : subjects) {
					if (!schemaSet.contains(indie)) {
						schemaSet.add(indie);
						GraphVertexItem objectVal = new GraphVertexItem(indie, getName(indie), "Schema");
						Object object = insertVertex(getDefaultParent(), null, objectVal, 0, 0, 0, 0, "schemaMovable");
						schemaBindingVertices.add(object);
						GraphEdgeItem edge = new GraphEdgeItem(edgeProperty); // create new OWLEdge for Graph
						Object e = insertEdge(getDefaultParent(), null, edge, source, object, "schemaBinding;rotation=180");
						moveEdgeToFront(e);
						schemaBindingEdges.add(e);
						updateChildrenCount(objectVal, schemaRelations);
						redrawVertexBox(object);
						includeRoles(object);
						roleBindings(schemaToRoles.get(object), roles, indie);
					}
				}
			}
		}
	}
	
	public void expandSchemaOutgoing(Object source, boolean secondPass) {
		GraphVertex sourceVertex = new GraphVertex(source);
		Object[] roles = getChildVertices(source);
		for (OWLObjectProperty edgeProperty : schemaRelations) {
			Set<OWLIndividual> objects = sourceVertex.getIndie().getObjectPropertyValues(edgeProperty, owlModel);
			for (OWLIndividual it : objects) {
				OWLNamedIndividual indie = it.asOWLNamedIndividual();
				if (!schemaSet.contains(indie)) {
					schemaSet.add(indie);
					GraphVertexItem objectVal = new GraphVertexItem(indie, getName(indie), "Schema");
					Object object = insertVertex(getDefaultParent(), null, objectVal, 0, 0, 0, 0, "schemaMovable");
					schemaBindingVertices.add(object);
					edgeInserterWithInverse(source, object, edgeProperty, schemaRelations);
					updateChildrenCount(objectVal, schemaRelations);
					redrawVertexBox(object);
					includeRoles(object);
					roleBindings(roles, schemaToRoles.get(object), sourceVertex.getIndie());
				} if (secondPass) {
					for (Object obj : schemaBindingVertices) {
						GraphVertex vertex = new GraphVertex(obj);
						if (vertex.getIndie() == indie) {
							edgeInserterWithInverse(source, obj, edgeProperty, schemaRelations);
							roleBindings(roles, schemaToRoles.get(obj), sourceVertex.getIndie());
						}
					}
				}
			}
		}
		// Sets expanded flag inside vertex to TRUE
		GraphVertexItem v = (GraphVertexItem) ((mxCell)source).getValue();
		v.setExpandState(true);
		((mxCell)source).setValue(v);
	}
	
	public void roleBindings(Object[] sourceRoles, Object[] targetRoles, OWLNamedIndividual sourceSchema) {
		// role lookup property for bindings
		OWLObjectProperty hasBoundRole1 = library.getObjectProperties().get("hasBoundRole1");
		OWLObjectProperty hasBoundRole2 = library.getObjectProperties().get("hasBoundRole2");
		OWLObjectProperty hasBindings = library.getObjectProperties().get("hasBindings");
		// create set of bindings individuals
		Set<OWLIndividual> bindings = sourceSchema.getObjectPropertyValues(hasBindings, owlModel);
		// first we build the hashes for quicker lookup later
		HashMap<String, Object> rolesHash = new HashMap<String, Object>();
		for (Object obj : sourceRoles) {
			GraphVertex source = new GraphVertex(obj);
			rolesHash.put(source.getIndie().getIRI().getFragment(), obj);
		}
		for (Object obj : targetRoles) {
			GraphVertex target = new GraphVertex(obj);
			rolesHash.put(target.getIndie().getIRI().getFragment(), obj);
		}
		for (OWLIndividual bind : bindings) {
			Set<OWLIndividual> boundRoles1 = bind.getObjectPropertyValues(hasBoundRole1, owlModel);
			Set<OWLIndividual> boundRoles2 = bind.getObjectPropertyValues(hasBoundRole2, owlModel);
			for (OWLIndividual ind : boundRoles1) {
				OWLNamedIndividual boundRole1 = ind.asOWLNamedIndividual();
				if (rolesHash.containsKey(boundRole1.getIRI().getFragment())) {
					Object boundRoleSource = rolesHash.get(boundRole1.getIRI().getFragment());
					for (OWLIndividual ind2 : boundRoles2) {
						OWLNamedIndividual boundRole2 = ind2.asOWLNamedIndividual();
						if (rolesHash.containsKey(boundRole2.getIRI().getFragment())) {
							Object boundRoleTarget = rolesHash.get(boundRole2.getIRI().getFragment());
							GraphEdgeItem edge = new GraphEdgeItem(hasBindings);
							Object e = insertEdge(getDefaultParent(), null, edge, boundRoleSource, boundRoleTarget, "rolesBinding");
							moveEdgeToFront(e);
							schemaBindingEdges.add(e);
							rolesHash.remove(boundRole1.getIRI().getFragment());
							rolesHash.remove(boundRole2.getIRI().getFragment());
						}
					}
				}
			}
		}
	}
	
	public void edgeInserterWithInverse(Object subject, Object object, OWLObjectProperty property, Set<OWLObjectProperty> relations) {
		GraphEdgeItem edge = new GraphEdgeItem(property); // create new OWLEdge for Graph
		if (relations == metaphorRelations) {
			Object e = insertEdge(getDefaultParent(), null, edge, subject, object);
			moveEdgeToBack(e);
		} else {
			Object e = insertEdge(getDefaultParent(), null, edge, subject, object, "schemaBinding");
			moveEdgeToFront(e);
			schemaBindingEdges.add(e);
		}
		// begins checking for inverse
		mxCell subjectCell = (mxCell) subject;
		mxCell objectCell = (mxCell) object;
		OWLNamedIndividual subjectInd = ((GraphVertexItem)subjectCell.getValue()).getIndividual();
		OWLNamedIndividual objectInd = ((GraphVertexItem)objectCell.getValue()).getIndividual();
		/*
		 * We know that the relationship goes Subject -> Property -> Object
		 * We are now checking to see if we have a relationship that goes Object -> InverseProperty -> Subject
		 * Because the current database's check for inverse property is broken, we have to brute-force through this process
		 * Basically for each Object, we iterate through the selected properties to see if there is a Object -> Property -> Subject
		 * Will catch inverse property if those assertions exist, or just a normal relationship between Object -> Subject
		 */
		for (OWLObjectProperty prop : relations) {
			Set<OWLNamedIndividual> inverseSet = library.getSubjectsSet().get(prop.getIRI().getFragment() + subjectInd.getIRI().getFragment());
			if (inverseSet != null) {
				if (inverseSet.contains(objectInd)) {
					GraphEdgeItem inverseEdge = new GraphEdgeItem(prop);
					if (relations == metaphorRelations) {
						Object e2 = insertEdge(getDefaultParent(), null, inverseEdge, subject, object, "reverseEdge");
						moveEdgeToBack(e2);
					} else {
						Object e2 = insertEdge(getDefaultParent(), null, inverseEdge, subject, object, "schemaBinding;rotation=180");
						moveEdgeToFront(e2);
						schemaBindingEdges.add(e2);
					}
				}
			}
		}
	}
	
	public void collapseVertex(Object origin, boolean isRoot) {
		mxCell vertex = (mxCell) origin;
		GraphVertexItem targetVertex = (GraphVertexItem) vertex.getValue();
		OWLNamedIndividual individual = targetVertex.getIndividual();
		Object[] removeMe = new Object[1];
		removeMe[0] = vertex;
		for (Object v : getOutgoingEdges(vertex)) {
			mxCell edge = (mxCell) v;
			collapseVertex(edge.getTarget(), false);
		}
		if (!isRoot) {
			metaphorSet.remove(individual);
			removeCells(removeMe, true);
		} else {
			targetVertex.setExpandState(false);
		}
	}
	
	public void collapseSchema(Object origin, boolean isRoot) {
		mxCell cell = (mxCell) origin;
		Object[] removeMe = new Object[1];
		GraphVertex vertex = new GraphVertex(origin);
		if (isRoot) {
			vertex.getOWLVertex().setExpandState(false);
			for (Object e : getOutgoingEdges(origin)) {
				mxCell edge = (mxCell) e;
				mxCell target = (mxCell) edge.getTarget();
				if (target.getParent() == getDefaultParent()) {
					schemaBindingEdges.remove(e);
					removeMe[0] = edge;
					removeCells(removeMe);
					collapseSchema(target, false);
				}
			}
		} else {
			if (getIncomingEdges(origin).length == 0) {
				System.out.println(getLabel(origin));
				for (Object e : getOutgoingEdges(origin)) {
					mxCell edge = (mxCell) e;
					mxCell target = (mxCell) edge.getTarget();
					schemaBindingEdges.remove(e);
					removeMe[0] = edge;
					removeCells(removeMe);
					collapseSchema(target, false);
				}
				schemaBindingVertices.remove(origin);
				schemaSet.remove(vertex.getIndie());
				removeMe[0] = origin;
				removeCells(removeMe);
			}
		}
	}
	
	
	private void insertSchemaToMetaphor(Object metaphorCell) {
		OWLObjectProperty hasTargetSchema = library.getObjectProperties().get("hasTargetSchema");
		OWLObjectProperty hasSourceSchema = library.getObjectProperties().get("hasSourceSchema");
		mxCell cell = (mxCell) metaphorCell;
		GraphVertexItem vertex = (GraphVertexItem) cell.getValue();
		OWLNamedIndividual individual = (OWLNamedIndividual) vertex.getIndividual();
		Set<OWLIndividual> sourceSchema = individual.getObjectPropertyValues(hasSourceSchema, owlModel);
		Set<OWLIndividual> targetSchema = individual.getObjectPropertyValues(hasTargetSchema, owlModel);
		mxRectangle bounds = getView().getState(metaphorCell).getLabelBounds();
		double startingHeight = bounds.getHeight();
		if (sourceSchema.size() > 0 && targetSchema.size() > 0) {
			for (OWLIndividual ind : targetSchema) {
				OWLNamedIndividual indie = ind.asOWLNamedIndividual();
				//schemaSet.add(indie);
				String indName = getName(indie);
				GraphVertexItem schemaVertex = new GraphVertexItem(indie, indName, "Schema");
				Object v = insertVertex(metaphorCell, null, schemaVertex, 10, startingHeight + 10, 150, 50, "schema");
				//schemaBindingVertices.add(v);
				updateChildrenCount(schemaVertex, schemaRelations);
			}
			for (OWLIndividual ind : sourceSchema) {
				OWLNamedIndividual indie = ind.asOWLNamedIndividual();
				//schemaSet.add(indie);
				String indName = getName(indie);
				GraphVertexItem schemaVertex = new GraphVertexItem(indie, indName, "Schema");
				Object v = insertVertex(metaphorCell, null, schemaVertex, 230, startingHeight + 10, 150, 50, "schema");
				//schemaBindingVertices.add(v);
				updateChildrenCount(schemaVertex, schemaRelations);
			}
			// insert connector node for schema mapping
			Object v = insertVertex(metaphorCell, null, "", 187.5, startingHeight + 10, 15, 15, "schemaMappingConnector");
			// insert edge
			Object source = cell.getChildAt(1);
			Object target = cell.getChildAt(0);
			Object e1 = insertEdge(metaphorCell, null, "", source, v, "schemaMappingEdgeFirst");
			Object e2 = insertEdge(metaphorCell, null, "", v, target, "schemaMappingEdgeSecond");
			moveEdgeToFront(e1);
			moveEdgeToFront(e2);
			// Insert the roles with mappings
			rolesWithMappings(metaphorCell, source, target, startingHeight + 8);
			// resize the cell to make it look nice after we've inserted the schemas
			mxGeometry geo = cell.getGeometry();
			geo.setHeight(geo.getHeight() + 20);
			geo.setWidth(geo.getWidth() + 10);
			cell.setGeometry(geo);
		}
	}
	
	private void rolesWithMappings(Object metaphor, Object sourceSchema, Object targetSchema, double circleHeight) {
		OWLObjectProperty hasRoles = library.getObjectProperties().get("hasRoles");
		OWLObjectProperty hasMappings = library.getObjectProperties().get("hasMappings");
		OWLObjectProperty hasSourceRole = library.getObjectProperties().get("hasSourceRole");
		OWLObjectProperty hasTargetRole = library.getObjectProperties().get("hasTargetRole");
		// The following numbers are used for spacing out roles inside the schemas
		circleHeight += 40;
		int sourceYPos = 20;
		int targetYPos = 20;
		// Extracting individual from Metaphor
		GraphVertex metaphorNode = new GraphVertex(metaphor);
		// Extracting individual from Source Schema
		GraphVertex sourceSchemaNode = new GraphVertex(sourceSchema);
		// Extracting individual from Target Schema
		GraphVertex targetSchemaNode = new GraphVertex(targetSchema);
		// Build HashMap and set of hasRoles and hasMappings values
		HashMap<String, OWLNamedIndividual> sourceSchemaRoles = library.indieHashSet(sourceSchemaNode.getIndie(), hasRoles);
		HashMap<String, OWLNamedIndividual> targetSchemaRoles = library.indieHashSet(targetSchemaNode.getIndie(), hasRoles);
		Set<OWLIndividual> roleMappings = metaphorNode.getIndie().getObjectPropertyValues(hasMappings, owlModel);
		// Begin the checking and inserting process
		//ArrayList sourceRoles = new ArrayList();
		//ArrayList targetRoles = new ArrayList();
		if (roleMappings != null) {
			for (OWLIndividual map : roleMappings) {
				OWLNamedIndividual mapping = map.asOWLNamedIndividual();
				Set<OWLIndividual> sourceRole = mapping.getObjectPropertyValues(hasSourceRole, owlModel);
				Set<OWLIndividual> targetRole = mapping.getObjectPropertyValues(hasTargetRole, owlModel);
				// We assume that both set are non-empty since a mapping MUST have a sourceRole and a targetRole
				for (OWLIndividual ind : sourceRole) {
					OWLNamedIndividual sourceRoleIndie = ind.asOWLNamedIndividual();
					OWLNamedIndividual sourceSchemaRole = sourceSchemaRoles.get(sourceRoleIndie.getIRI().getFragment());
					if (sourceSchemaRole != null) {
						for (OWLIndividual indy : targetRole) {
							OWLNamedIndividual targetRoleIndie = indy.asOWLNamedIndividual();
							OWLNamedIndividual targetSchemaRole = targetSchemaRoles.get(targetRoleIndie.getIRI().getFragment());
							if (targetSchemaRole != null) {
								// First insert the circle that's part of the mapping edge
								Object circle = insertVertex(metaphor, null, "", 187.5, circleHeight, 15, 15, "schemaMappingConnector;fillColor=#c66565");
								circleHeight += 60;
								// Insert the source role, retain the returned object
								Object sourceSchemaCell = insertRole(sourceRoleIndie, sourceSchema, sourceYPos);
								//sourceRoles.add(sourceSchemaCell);
								sourceYPos += 60;
								// Insert the target role, retain the returned object
								Object targetSchemaCell = insertRole(targetRoleIndie, targetSchema, targetYPos);
								//targetRoles.add(targetSchemaCell);
								targetYPos += 60;
								// Now insert the edge mapping between these two roles
								insertEdge(metaphor, null, "Mapping", sourceSchemaCell, circle, "schemaMappingEdgeFirst;strokeColor=#c66565");
								insertEdge(metaphor, null, "Mapping", circle, targetSchemaCell, "schemaMappingEdgeSecond;strokeColor=#c66565");
								// Remove the roles from their respective sets so that we can insert all the remaining roles later
								sourceSchemaRoles.remove(sourceRoleIndie.getIRI().getFragment());
								targetSchemaRoles.remove(targetRoleIndie.getIRI().getFragment());
							}
						}
					}
				}
			}
		}
		// We're done checking for mappings between roles, now we can insert the remaining roles without a care
		if (!sourceSchemaRoles.isEmpty())
			for (OWLNamedIndividual sourceRoleIndie : sourceSchemaRoles.values()) {
				Object v = insertRole(sourceRoleIndie, sourceSchema, sourceYPos);
				//sourceRoles.add(v);
				sourceYPos += 60;
			}
		if (!targetSchemaRoles.isEmpty())
			for (OWLNamedIndividual targetRoleIndie : targetSchemaRoles.values()) {
				Object v = insertRole(targetRoleIndie, targetSchema, targetYPos);
				//targetRoles.add(v);
				targetYPos += 60;
			}
//		if (!schemaToRoles.containsKey(sourceSchema)) {
//			schemaToRoles.put(sourceSchema, sourceRoles.toArray());
//		}
//		if (!schemaToRoles.containsKey(targetSchema)) {
//			schemaToRoles.put(targetSchema, targetRoles.toArray());
//		}
		mxGeometry sourceSchemaNodeGeo = sourceSchemaNode.getCell().getGeometry();
		sourceSchemaNodeGeo.setHeight(sourceSchemaNodeGeo.getHeight() + 10);
		sourceSchemaNode.getCell().setGeometry(sourceSchemaNodeGeo);
		mxGeometry targetSchemaNodeGeo = targetSchemaNode.getCell().getGeometry();
		targetSchemaNodeGeo.setHeight(targetSchemaNodeGeo.getHeight() + 10);
		targetSchemaNode.getCell().setGeometry(targetSchemaNodeGeo);
	}
	
	private Object insertRole(OWLNamedIndividual role, Object schema, int yPos) {
		GraphVertexItem roleVertex = new GraphVertexItem(role, getName(role), "Role");
		Object v = insertVertex(schema, null, roleVertex, 10, yPos, 130, 50, "role;fillColor=#6599b1");
		return v;
	}
	
	private void includeRoles(Object parentSchema) {
		OWLObjectProperty hasRoles = library.getObjectProperties().get("hasRoles");
		mxCell parentCell = (mxCell) parentSchema;
		GraphVertexItem parentVertex = (GraphVertexItem) parentCell.getValue();
		OWLNamedIndividual parentIndividual = (OWLNamedIndividual) parentVertex.getIndividual();
		Set<OWLIndividual> schemaRoles = parentIndividual.getObjectPropertyValues(hasRoles, owlModel);
		if (schemaRoles != null) {
			int yPos = 20;
			ArrayList roles = new ArrayList();
			for (OWLIndividual ind : schemaRoles) {
				OWLNamedIndividual indie = ind.asOWLNamedIndividual();
				String indName = getName(indie);
				GraphVertexItem roleVertex = new GraphVertexItem(indie, indName, "Role");
				@SuppressWarnings("unused")
				Object v = insertVertex(parentSchema, null, roleVertex, 10, yPos, 130, 50, "role");
				roles.add(v);
				yPos += 60;
			}
			schemaToRoles.put(parentSchema, roles.toArray());
			mxGeometry geo = parentCell.getGeometry();
			geo.setHeight(geo.getHeight() + 10);
			geo.setWidth(geo.getWidth() + 10);
			parentCell.setGeometry(geo);
		}
	}
	
	/** HELPER FUNCTIONS AND SOME OVERRIDES FOR AESTHETICS **/
	
	public void redrawVertexBox(Object obj) {
		Object[] vertices = new Object[1];
		mxRectangle[] rects = new mxRectangle[1];
		mxCell vertex = (mxCell) obj;
		if (vertex.getChildCount() == 0) {
			mxRectangle bounds = getView().getState(vertex).getLabelBounds();
			bounds.setHeight(bounds.getHeight() + 5);
			bounds.setWidth(bounds.getWidth() + 30);
			rects[0] = bounds;
			vertices[0] = obj;
			vertex.getGeometry().setAlternateBounds(bounds);
		}
		cellsResized(vertices, rects);
	}
	
	private void setProperties() {
		setEnabled(false);
		setCellsEditable(false);
		setCellsResizable(false);
		setConstrainChildren(true);
		setDisconnectOnMove(false);
		setDropEnabled(false);
		setHtmlLabels(true);
		setAllowNegativeCoordinates(false);
	}
	
	private void updateChildrenCount(GraphVertexItem v, Set<OWLObjectProperty> relations) {
		OWLNamedIndividual individual = v.getIndividual();
		for (OWLObjectProperty edgeProperty : relations) {
			Set<OWLIndividual> objects = individual.getObjectPropertyValues(edgeProperty, owlModel);
			Set<OWLNamedIndividual> subjects = library.getSubjectsSet().get(edgeProperty.getIRI().getFragment() + individual.getIRI().getFragment());
			for (OWLIndividual it : objects) {
				OWLNamedIndividual indie = it.asOWLNamedIndividual();
				if (!metaphorSet.contains(indie) && !schemaSet.contains(indie)) {
					v.increaseCount();
				}
			}
			if (subjects != null) {
				for (OWLNamedIndividual it : subjects) {
					if (!metaphorSet.contains(it) && !schemaSet.contains(it)) {
						v.increaseCount();
					}
				}
			}
		}
	}
	
	public void moveEdgeToBack(Object edge) {
		Object[] edges = new Object[1];
		edges[0] = edge;
		cellsOrdered(edges, true);
	}
	
	public void moveEdgeToFront(Object edge) {
		Object[] edges = new Object[1];
		edges[0] = edge;
		cellsOrdered(edges, false);
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
	
	private void setGraphStyles() {
		// Inserting AVis JGraph styles into the stylesheet
		styles = getStylesheet();
		GraphStyles myStyles = new GraphStyles();
		styles.setDefaultEdgeStyle(myStyles.defaultEdgeStyle());
		styles.setDefaultVertexStyle(myStyles.defaultVertexStyle());
		styles.putCellStyle("reverseEdge", myStyles.reverseEdgeStyle());
		styles.putCellStyle("schema", myStyles.schemaStyle());
		styles.putCellStyle("schemaMovable", myStyles.schemaMovableStyle());
		styles.putCellStyle("role", myStyles.roleStyle());
		styles.putCellStyle("schemaMappingEdgeFirst", myStyles.schemaMappingEdgeFirst());
		styles.putCellStyle("schemaMappingEdgeSecond", myStyles.schemaMappingEdgeSecond());
		styles.putCellStyle("schemaMappingConnector", myStyles.schemaMappingConnector());
		styles.putCellStyle("schemaBinding", myStyles.schemaBinding());
		styles.putCellStyle("rolesBinding", myStyles.rolesBinding());
		setStylesheet(styles);
	}
	
	@Override
	public boolean isCellSelectable(Object cell) {
		mxCellState state = getView().getState(cell);
		if (state != null) {
			Map<String, Object> style = state.getStyle();
			Object value = style.get("selectable");
			return isCellsSelectable() && !isCellLocked(cell) && value != "0";
		}
		return true;
	}
}
