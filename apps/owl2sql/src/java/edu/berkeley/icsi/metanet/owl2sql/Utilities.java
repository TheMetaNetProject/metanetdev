package edu.berkeley.icsi.metanet.owl2sql;

import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import org.semanticweb.owlapi.model.OWLClass;
import org.semanticweb.owlapi.model.OWLClassExpression;
import org.semanticweb.owlapi.model.OWLDataProperty;
import org.semanticweb.owlapi.model.OWLDataPropertyExpression;
import org.semanticweb.owlapi.model.OWLNamedObject;
import org.semanticweb.owlapi.model.OWLObjectProperty;
import org.semanticweb.owlapi.model.OWLObjectPropertyExpression;
import org.semanticweb.owlapi.model.OWLOntology;

/**
 * @author brandon
 *
 */
public class Utilities {
	
	/**
	 * Returns the set of all named subclasses of the given OWL class, including
	 * the given OWL class
	 * @param owlClass - the named OWL class
	 * @param ont - the ontology containing the OWL class
	 * @return the set of all named subclasses, including the given OWL class
	 */
	public static HashSet<OWLClass> getSubClasses(OWLClass owlClass, 
			Set<OWLOntology> ontClosure) {
		OWLClass subClass;
		
		HashSet<OWLClass> subClasses = new HashSet<OWLClass>();
		subClasses.add(owlClass);
		
		for (OWLClassExpression subClassEx : owlClass.getSubClasses(ontClosure)) {
			if (subClassEx.isAnonymous()) {
				continue;
			}
			subClass = subClassEx.asOWLClass();
			subClasses.addAll(getSubClasses(subClass, ontClosure));
		}
		return subClasses;
	}
	
	/**
	 * Returns the set of all named super-classes of the given OWL class, 
	 * including the given OWL class
	 * @param owlClass - the named OWL class
	 * @param ont - the ontology containing the OWL class
	 * @return the set of all named subclasses, including the given OWL class
	 */
	public static HashSet<OWLClass> getSuperClasses(OWLClass owlClass, 
			Set<OWLOntology> ontClosure) {
		OWLClass superClass;
		
		HashSet<OWLClass> superClasses = new HashSet<OWLClass>();
		superClasses.add(owlClass);
		
		for (OWLClassExpression superClassEx : 
				owlClass.getSuperClasses(ontClosure)) {
			if (superClassEx.isAnonymous()) {
				continue;
			}
			superClass = superClassEx.asOWLClass();
			superClasses.addAll(getSuperClasses(superClass, ontClosure));
		}
		return superClasses;
	}
	
	/**
	 * Returns the set of all named super-properties of the given object
	 * property, including the given object property itself
	 * @param objProp - the named OWL object property
	 * @param ont - the OWL ontology containing the object property
	 * @return the set of all named superproperties of the given object
	 * property, including the given object property itself
	 */
	public static HashSet<OWLObjectProperty> getSuperProps(
			OWLObjectProperty objProp, Set<OWLOntology> ontClosure) {
		OWLObjectProperty superproperty;
		
		HashSet<OWLObjectProperty> superproperties = 
				new HashSet<OWLObjectProperty>();
		superproperties.add(objProp);
		
		for (OWLObjectPropertyExpression superPropExp : 
				objProp.getSuperProperties(ontClosure)) {
			if (superPropExp.isAnonymous()) {
				System.out.println(superPropExp);
			} else {
				superproperty = superPropExp.asOWLObjectProperty();
				superproperties.addAll(getSuperProps(superproperty, ontClosure));
			}
		}
		
		return superproperties;
	}
	
	/**
	 * Returns the set of all named super-properties of the given data property 
	 * including the given data property itself
	 * @param dataProp - the named OWL data property
	 * @param ont - the OWL ontology containing the data property
	 * @return the set of all named superproperties of the given data property, 
	 * including the given data property itself
	 */
	public static HashSet<OWLDataProperty> getSuperProps(OWLDataProperty dataProp,
			Set<OWLOntology> ontClosure) {
		HashSet<OWLDataProperty> superproperties = 
				new HashSet<OWLDataProperty>();
		superproperties.add(dataProp);
		
		for (OWLDataPropertyExpression supPropExp : 
				dataProp.getSuperProperties(ontClosure)) {
			if (supPropExp.isAnonymous()) {
				// not currently handled
			} else {
				superproperties.addAll(getSuperProps(
						supPropExp.asOWLDataProperty(), ontClosure));
			}
		}
		
		return superproperties;
	}
	
	/**
	 * Returns a SQL INSERT statement for the given table and with the given
	 * values. Automatically truncates data values that are too long.
	 * @param tableName - name of the target table
	 * @param fieldValueMap - maps the name of each field to the string 
	 * representation of its value. If the value is itself a string, it should
	 * not be delimitted by apostrophes. For example, "value" rather than
	 * "'value'".
	 * @return a SQL INSERT statement
	 */
	public static String getInsertString(String tableName, 
			Map<String, String> fieldValueMap) {
		boolean isInteger;
		String fields = "";
		String values = "";
		String value;
		
		for (String field : fieldValueMap.keySet()) {
			if (!fields.isEmpty()) {
				fields += ", ";
				values += ", ";
			}
			fields += field;
			value = fieldValueMap.get(field).toString();
			
			try {
				Integer.parseInt(value);
				isInteger = true;
			} catch (NumberFormatException e) {
				isInteger = false;
			}
			
			if (!value.equals("true") && !value.equals("false") && !isInteger) {
				value = "'" + value + "'";
			}
			values += value;
		}
		return "INSERT INTO " + tableName + " (" + fields + ") VALUES (" + 
				values + ")";
	}
	
	public static String getUpdateString(String tableName, String pkName, 
			int pkValue, Map<String, String> fieldValueMap) {
		boolean isInteger;
		String setString = "";
		String value;
		
		for (String field : fieldValueMap.keySet()) {
			if (!setString.isEmpty()) {
				setString += ", ";
			}
			value = fieldValueMap.get(field);
			
			try {
				Integer.parseInt(value);
				isInteger = true;
			} catch (NumberFormatException e) {
				isInteger = false;
			}
			
			if (!value.equals("true") && !value.equals("false") && !isInteger) {
				value = "'" + value + "'";
			}
			setString += field + "=" + value;
		}
		return "UPDATE " + tableName + " SET " + setString + " WHERE " + 
				pkName + "=" + pkValue;
	}

	/**
	 * Returns the of disjunct OWL classes in the given OWLClassExpression. 
	 * Handles named OWL classes and disjunct anonymous classes but ignores
	 * other types of anonymous classes.
	 * @param owlClassExp
	 * @return the set of disjunct OWL classes in the given class expression
	 */
	public static HashSet<OWLClass> extractClasses(
			OWLClassExpression owlClassExp) {
		HashSet<OWLClass> owlClasses = new HashSet<OWLClass>();
		if (!owlClassExp.isAnonymous()) {
			owlClasses.add(owlClassExp.asOWLClass());
		} else if (!owlClassExp.asDisjunctSet().contains(owlClassExp)) {
			for (OWLClassExpression disjunctClassExp : 
					owlClassExp.asDisjunctSet()) {
				owlClasses.addAll(extractClasses(disjunctClassExp));
			}
		}
		return owlClasses;
	}
	
	/**
	 * Finds the human-readable name of an OWL object
	 * @param obj - A named OWL object
	 * @return
	 */
	public static String getName(OWLNamedObject obj) {
		return obj.getIRI().getFragment().toString().trim();
	}

	public static String getDatatype(int maxKeyLength, int keySize) {
		return "VARCHAR(" + maxKeyLength / keySize + ") BINARY " +
				"CHARACTER SET " + Basics.DEFAULT_CHAR_SET + 
				" COLLATE " + Basics.DEFAULT_COLLATE;
	}

	/**
	 * Takes the given string and returns it in a SQL-acceptable format (i.e.
	 * with escaped characters)
	 */
	public static String format(String str) {
		String out;
		
		out = str.replace("'", "\\'");
		str = str.replace("\"", "\\\"");
		return out;
	}

	/**
	 * Checks if the given string is a valid MySQL database name
	 * @param dbName - the proposed database name
	 * @return true if the name is valid, false if not
	 */
	public static boolean isValidDBName(String dbName) {
		if (!Pattern.matches(".*[^\\w\\$].*", dbName) && dbName.length() > 0) {
			return true;
		} else {
			return false;
		}
	}
}
