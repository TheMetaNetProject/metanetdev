package edu.berkeley.icsi.metanet.owl2sql;

public class Basics {
	public static final String VERSION = "1.1";
	public static final String CLASS_PREFIX = "";
	public static final String JOIN_TABLE_PREFIX = "JoinTable_";
	public static final String OBJ_PROP_PREFIX = "";
	public static final String DATA_PROP_PREFIX = "";
	public static final String DEFAULT_CHAR_SET = "utf8";
	public static final String DEFAULT_COLLATE = "utf8_unicode_ci";
	public static final int DEFAULT_DATA_SIZE = 180;
	public static final String DEFAULT_SQL_DATATYPE = 
			"VARCHAR(" + DEFAULT_DATA_SIZE + ") BINARY " +
			"CHARACTER SET " + DEFAULT_CHAR_SET + 
			" COLLATE " + DEFAULT_COLLATE;
	public static final String DB_NAME = "owl2sql";
	public static final String[] REQ_PRIV_SET = {
		"CREATE", "DROP", "INSERT"
	};
}
