package edu.berkeley.icsi.metanet.wiki2owl;

import java.awt.event.ActionEvent;
import java.io.IOException;

import org.protege.editor.owl.ui.action.ProtegeOWLAction;
import javax.swing.JOptionPane;

/**
 * Implements the load from Persian wiki menubar item.
 * 
 * @author Jisup Hong <jhong@icsi.berkeley.edu>
 */
public class LoadFromRussianWiki extends ProtegeOWLAction {

    /**
     *
     */
    private static final long serialVersionUID = -5991650300986557024L;

    @Override
    public void initialise() throws Exception {
        // TODO Auto-generated method stub
    }

    @Override
    public void dispose() throws Exception {
        // TODO Auto-generated method stub
    }

    @Override
    public void actionPerformed(ActionEvent arg0) {
        try {
            WikiLoader wl = new WikiLoader(getOWLWorkspace());
            wl.load(WikiLoader.RU);
        } catch (IOException io) {
            JOptionPane.showMessageDialog(getOWLWorkspace(), io.getLocalizedMessage());
        }
    }
}
