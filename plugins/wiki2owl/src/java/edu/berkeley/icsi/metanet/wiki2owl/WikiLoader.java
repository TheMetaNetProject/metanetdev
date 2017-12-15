package edu.berkeley.icsi.metanet.wiki2owl;

import java.awt.BorderLayout;
import java.awt.Frame;
import java.awt.GridLayout;
import java.awt.event.WindowEvent;
import java.awt.event.WindowListener;
import java.awt.event.WindowStateListener;
import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.IOException;
import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.Collections;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JLabel;

import org.protege.editor.owl.model.OWLModelManager;
import org.semanticweb.owlapi.io.RDFXMLOntologyFormat;
import org.semanticweb.owlapi.model.AddImport;
import org.semanticweb.owlapi.model.IRI;
import org.semanticweb.owlapi.model.OWLNamedIndividual;
import org.semanticweb.owlapi.model.OWLOntology;
import org.semanticweb.owlapi.model.OWLOntologyCreationException;
import org.semanticweb.owlapi.model.OWLOntologyFormat;
import org.semanticweb.owlapi.model.OWLOntologyManager;
import org.semanticweb.owlapi.util.DefaultPrefixManager;
import org.semanticweb.owlapi.util.OWLEntityRemover;

import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JPasswordField;
import javax.swing.JProgressBar;
import javax.swing.JTextField;
import javax.swing.SwingUtilities;
import javax.swing.SwingWorker;
import org.protege.editor.owl.model.OWLWorkspace;
import org.semanticweb.owlapi.util.SimpleIRIMapper;

/**
 * Class that adds importation from MetaNet Wiki to Protege 4.x.  It
 * pops up a window to retrieve login information and displays a
 * progress bar while the download and conversion are in progress. 
 * 
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class WikiLoader implements PropertyChangeListener, WindowListener {

    private static Logger logger = Logger.getLogger(WikiLoader.class
            .getSimpleName());
    public static final String EN = "en";
    public static final String ES = "es";
    public static final String FA = "fa";
    public static final String RU = "ru";
    public static final String TEST = "test";
    private static final String WIKI_SERVER = "ambrosia.icsi.berkeley.edu:2080";
    private static final String WIKI_SCRIPTPATH_PREFIX = "/dev/";
    private static final String ONTOLOGY_URL = "https://metaphor.icsi.berkeley.edu/metaphor/MetaphorOntology.owl";
    private static final String ONTOLOGY_BASE = "https://metaphor.icsi.berkeley.edu";
    private static final String REPO_FILE = "MetaphorRepository.owl";
    private static String wikiuser = "";
    private static String wikipw = "";
    private String lang;
    private OWLWorkspace ws;
    private OWLModelManager mm;
    private OWLOntologyManager om;
    private OWLOntology repo;
    private WikiParser wikip;
    private JDialog progressDialog;
    private JProgressBar progressBar;
    private JLabel progressLabel;

    public WikiLoader(OWLWorkspace w) {
        ws = w;
        mm = ws.getOWLModelManager();
        om = mm.getOWLOntologyManager();
        wikip = new WikiParser();
        progressDialog = new JDialog((JFrame) null, "Load from Wiki", false);
        progressDialog.setAlwaysOnTop(true);
        progressBar = new JProgressBar(0, 100);
        progressBar.setIndeterminate(false);
        progressBar.setValue(0);
        progressDialog.add(BorderLayout.CENTER, progressBar);
        progressLabel = new JLabel("Connecting to the wiki...");
        progressDialog.add(BorderLayout.NORTH, progressLabel);
        progressDialog.setSize(300, 75);
        progressDialog.setLocationRelativeTo(ws);
        progressDialog.setVisible(false);
        progressDialog.addWindowListener(this);
        wikip.addPropertyChangeListener(this);

    }

    public void load(String lang) throws IOException {

        String iriStr = getRepositoryIRIString(lang);
        IRI repIRI = IRI.create(iriStr);
        IRI ontoIRI = IRI.create(ONTOLOGY_URL);

        // see if we already have this repository loaded. if yes, then abort: don't clobber
        repo = om.getOntology(repIRI);
        if (repo != null) {
            throw new IOException("Ontology " + iriStr + " is already loaded.  Please unload before reloading.");
        }

        // collect login information, with possibility of canceling
        if (getWikiLoginInfo() != 0) {
            // if hit cancel, abort without error
            return;
        }
        // show progress bar
        progressDialog.setVisible(true);
        progressBar.setValue(0);

        SimpleIRIMapper rmapper = new SimpleIRIMapper(repIRI, IRI.generateDocumentIRI());
        om.addIRIMapper(rmapper);

        // Load the general metaphor ontology if it isn't already loaded
        OWLOntology metaont = om.getOntology(ontoIRI);
        if (metaont == null) {
            try {
                // Let's hope that the loader handles UTF-8 correctly.
                setProgressMessage("Loading metaphor ontology...");
                metaont = om.loadOntology(ontoIRI);
                progressBar.setValue(1);
            } catch (OWLOntologyCreationException ex) {
                logger.log(Level.SEVERE, "Error loading remote ontology", ex);
                throw new IOException(ex);
            }
        }

        // Create new ontology for repository data
        setProgressMessage("Preparing to load repository...");
        try {
            // Let's hope that the loader handles UTF-8 correctly.
            repo = om.createOntology(repIRI);
        } catch (OWLOntologyCreationException ex) {
            logger.log(Level.SEVERE, "Error loading remote ontology", ex);
            throw new IOException(ex);
        }

        // Add import of MetaphorOntology
        setProgressMessage("Creating link to metaphor ontology...");
        AddImport ai = new AddImport(repo, om.getOWLDataFactory().getOWLImportsDeclaration(IRI.create(ONTOLOGY_URL)));
        om.applyChange(ai);
        om.getImports(repo);

        // Delete any individuals that are already in there
		/*OWLEntityRemover remover = new OWLEntityRemover(om,
         Collections.singleton(metanet));
         for (OWLNamedIndividual i : metanet.getIndividualsInSignature()) {
         i.accept(remover);
         }
         om.applyChanges(remover.getChanges());
         remover.reset();
         */

        // Use same format
        RDFXMLOntologyFormat ofm = new RDFXMLOntologyFormat();
        ofm.setPrefix("metanet", ONTOLOGY_URL + "#");
        ofm.setDefaultPrefix(iriStr + "#");
        om.setOntologyFormat(repo, ofm);

        // Set up the Wiki Parser
        wikip.setWikiServer(WIKI_SERVER);
        wikip.setWikiLogin(wikiuser, wikipw);
        wikip.setLanguage(lang);
        wikip.setWikiBase(WIKI_SCRIPTPATH_PREFIX+lang);
        wikip.setLogLevel(Level.INFO);
        wikip.setOntology(metaont, "metanet");
        wikip.setRepository(repo);

        /*
         * Do wiki page parsing and population of OWL model
         */
        try {
            wikip.initializeWiki();
            setProgressMessage("Executing import...");
            wikip.execute();
        } catch (Exception ex) {
            mm.removeOntology(repo);
            progressDialog.setVisible(false);
            throw new IOException(ex);
        }

    }

    private static String getRepositoryIRIString(String lang) {
        return ONTOLOGY_BASE + "/" + lang + "/" + REPO_FILE;
    }

    private static int getWikiLoginInfo() {
        //Using a JPanel as the message for the JOptionPane
        JPanel userPanel = new JPanel();
        userPanel.setLayout(new GridLayout(2, 2));

        //Labels for the textfield components        
        JLabel usernameLbl = new JLabel("Wiki Username: ");
        JLabel passwordLbl = new JLabel("Password: ");
        usernameLbl.setHorizontalAlignment(usernameLbl.RIGHT);
        passwordLbl.setHorizontalAlignment(usernameLbl.RIGHT);

        JTextField username = new JTextField(6);
        JPasswordField passwordFld = new JPasswordField(6);

        username.setText(wikiuser);
        passwordFld.setText(wikipw);

        //Add the components to the JPanel        
        userPanel.add(usernameLbl);
        userPanel.add(username);
        userPanel.add(passwordLbl);
        userPanel.add(passwordFld);

        //As the JOptionPane accepts an object as the message
        //it allows us to use any component we like - in this case 
        //a JPanel containing the dialog components we want
        int input = JOptionPane.showConfirmDialog(null, userPanel,
                "MetaNet Wiki Login",
                JOptionPane.OK_CANCEL_OPTION,
                JOptionPane.QUESTION_MESSAGE);

        if (input == 0) {
            wikiuser = username.getText();
            wikipw = new String(passwordFld.getPassword());
        }
        return input;
    }

    public void setProgressMessage(String msg) {
        progressLabel.setText(msg);
    }

    @Override
    public void propertyChange(PropertyChangeEvent evt) {
        if ("progress" == evt.getPropertyName()) {
            final int progress = (Integer) evt.getNewValue();
            setProgressMessage(wikip.getProgressMessage());
            SwingUtilities.invokeLater(new Runnable(){
            	public void run() {
            		progressBar.setValue(progress);
            	}
            });
            if (progress == 100) {
                mm.setActiveOntology(repo);
                progressDialog.setVisible(false);
            }
        }
    }

    @Override
    public void windowOpened(WindowEvent e) {
    }

    @Override
    public void windowClosing(WindowEvent e) {
        wikip.cancel(true);
        mm.removeOntology(repo);
        progressDialog.setVisible(false);
        JOptionPane.showMessageDialog((JFrame) null,"Import canceled.");
    }

    @Override
    public void windowClosed(WindowEvent e) {
    }

    @Override
    public void windowIconified(WindowEvent e) {
    }

    @Override
    public void windowDeiconified(WindowEvent e) {
    }

    @Override
    public void windowActivated(WindowEvent e) {
    }

    @Override
    public void windowDeactivated(WindowEvent e) {
    }
        
}
