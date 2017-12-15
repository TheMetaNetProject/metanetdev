package edu.berkeley.icsi.metanet.wikifileapi;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.logging.Logger;

public class WikiFileApi {
	
	private static final java.util.logging.Logger logger = Logger.getLogger("WikiFileApi");
	private String rootDir;
	
	/**
	 * Given a namespace string, returns all the names of pages in that
	 * namespace.  The page names returned include the namespace
	 * itself.
	 * 
	 * @param namespace
	 * @return	list of page names
	 */
	public List<String> getNamespaceMembers(String namespace) {
		File nsDirectory = new File(rootDir + namespace);
		File[] flist = nsDirectory.listFiles();
		List<String> pageNames = new ArrayList<String>();
		if (flist == null) {
			return pageNames;
		}
		for (File file : flist) {
			pageNames.add(namespace+':'+file.getName().replace("___", "/"));
		}
		return pageNames;
	}
	

	public String getPageText(String pagename) throws IOException {
		String path = rootDir + pagename.replace("/", "___").replace(":", "/").replace(" ", "_");
		byte[] encoded = Files.readAllBytes(Paths.get(path));
		String content = new String(encoded, StandardCharsets.UTF_8);
		return content;
	}
	
	public WikiFileApi(String rootDirectory) {
		rootDir = rootDirectory;
		if (!rootDir.endsWith("/")) {
			rootDir += "/";
		}
	}

	public static void main(String[] args)
	{
		WikiFileApi wikip = new WikiFileApi(args[0]);
		List<String> l = wikip.getNamespaceMembers(args[1]);
	}
}
