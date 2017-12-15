.. java:import:: java.util.zip GZIPInputStream

Wiki.Revision
=============

.. java:package:: org.wikipedia
   :noindex:

.. java:type:: public class Revision implements Comparable<Revision>
   :outertype: Wiki

   Represents a contribution and/or a revision to a page.

Constructors
------------
Revision
^^^^^^^^

.. java:constructor:: public Revision(long revid, Calendar timestamp, String title, String summary, String user, boolean minor, boolean bot, boolean rvnew, int size)
   :outertype: Wiki.Revision

   Constructs a new Revision object.

   :param revid: the id of the revision (this is a long since {{NUMBEROFEDITS}} on en.wikipedia.org is now (January 2012) ~25% of \ ``Integer.MAX_VALUE``\
   :param timestamp: when this revision was made
   :param title: the concerned article
   :param summary: the edit summary
   :param user: the user making this revision (may be anonymous, if not use \ ``User.getUsername()``\ )
   :param minor: whether this was a minor edit
   :param bot: whether this was a bot edit
   :param rvnew: whether this revision created a new page
   :param size: the size of the revision

Methods
-------
compareTo
^^^^^^^^^

.. java:method:: public int compareTo(Wiki.Revision other)
   :outertype: Wiki.Revision

   Compares this revision to another revision based on the recentness of their timestamps.

   :param other: the revision to compare
   :return: whether this object is equal to

diff
^^^^

.. java:method:: public String diff(Revision other) throws IOException
   :outertype: Wiki.Revision

   Returns a HTML rendered diff table; see the table at the \ `example <http://en.wikipedia.org/w/index.php?diff=343490272>`_\ .

   :param other: another revision on the same page.
   :return: the difference between this and the other revision

diff
^^^^

.. java:method:: public String diff(String text) throws IOException
   :outertype: Wiki.Revision

   Returns a HTML rendered diff table between this revision and the given text. Useful for emulating the "show changes" functionality. See the table at the \ `example <http://en.wikipedia.org/w/index.php?diff=343490272>`_\ .

   :param text: some wikitext
   :return: the difference between this and the the text provided

diff
^^^^

.. java:method:: public String diff(long oldid) throws IOException
   :outertype: Wiki.Revision

   Returns a HTML rendered diff table; see the table at the \ `example <http://en.wikipedia.org/w/index.php?diff=343490272>`_\ .

   :param oldid: the oldid of a revision on the same page. NEXT_REVISION, PREVIOUS_REVISION and CURRENT_REVISION can be used here for obvious effect.
   :return: the difference between this and the other revision

diff
^^^^

.. java:method:: protected String diff(long oldid, String text) throws IOException
   :outertype: Wiki.Revision

   Fetches a HTML rendered diff table; see the table at the \ `example <http://en.wikipedia.org/w/index.php?diff=343490272>`_\ .

   :param oldid: the id of another revision; (exclusive) or
   :param text: some wikitext to compare against
   :return: a difference between oldid or text

equals
^^^^^^

.. java:method:: @Override public boolean equals(Object o)
   :outertype: Wiki.Revision

   Determines whether this Revision is equal to another object.

   :param o: an object
   :return: whether o is equal to this object

getPage
^^^^^^^

.. java:method:: public String getPage()
   :outertype: Wiki.Revision

   Returns the page to which this revision was made.

   :return: the page

getRcid
^^^^^^^

.. java:method:: public long getRcid()
   :outertype: Wiki.Revision

   Gets the \ ``rcid``\  of this revision for patrolling purposes.

   :return: the rcid of this revision (long)

getRenderedText
^^^^^^^^^^^^^^^

.. java:method:: public String getRenderedText() throws IOException
   :outertype: Wiki.Revision

   Gets the rendered text of this revision. WARNING: fails if the revision is deleted.

   :return: the rendered contents of the appropriate article at \ ``timestamp``\

getRevid
^^^^^^^^

.. java:method:: public long getRevid()
   :outertype: Wiki.Revision

   Returns the oldid of this revision. Don't confuse this with \ ``rcid``\

   :return: the oldid (long)

getRollbackToken
^^^^^^^^^^^^^^^^

.. java:method:: public String getRollbackToken()
   :outertype: Wiki.Revision

   Gets the rollback token for this revision. Can be null, and often for good reasons: cannot rollback or not top revision.

   :return: the rollback token

getSize
^^^^^^^

.. java:method:: public int getSize()
   :outertype: Wiki.Revision

   Gets the size of this revision in bytes.

   :return: see above

getSummary
^^^^^^^^^^

.. java:method:: public String getSummary()
   :outertype: Wiki.Revision

   Returns the edit summary for this revision. WARNING: returns null if the summary was RevisionDeleted.

   :return: the edit summary

getText
^^^^^^^

.. java:method:: public String getText() throws IOException
   :outertype: Wiki.Revision

   Fetches the contents of this revision. WARNING: fails if the revision is deleted.

   :return: the contents of the appropriate article at \ ``timestamp``\

getTimestamp
^^^^^^^^^^^^

.. java:method:: public Calendar getTimestamp()
   :outertype: Wiki.Revision

   Gets the time that this revision was made.

   :return: the timestamp

getUser
^^^^^^^

.. java:method:: public String getUser()
   :outertype: Wiki.Revision

   Returns the user or anon who created this revision. You should pass this (if not an IP) to \ ``getUser(String)``\  to obtain a User object. WARNING: returns null if the user was RevisionDeleted.

   :return: the user or anon

hashCode
^^^^^^^^

.. java:method:: @Override public int hashCode()
   :outertype: Wiki.Revision

   Returns a hash code of this revision.

   :return: a hash code

isBot
^^^^^

.. java:method:: public boolean isBot()
   :outertype: Wiki.Revision

   Determines whether this revision was made by a bot.

   :return: (see above)

isMinor
^^^^^^^

.. java:method:: public boolean isMinor()
   :outertype: Wiki.Revision

   Checks whether this edit was marked as minor. See [[Help:Minor edit]] for details.

   :return: whether this revision was marked as minor

isNew
^^^^^

.. java:method:: public boolean isNew()
   :outertype: Wiki.Revision

   Determines whether this revision created a new page.  WARNING: Will return false for all revisions prior to 2007 (I think?) -- this is a MediaWiki problem. WARNING: Returning true does not imply this is the bottommost revision on the page due to histmerges. WARNING: Not accessible through getPageHistory() -- a MW problem.

   :return: (see above)

rollback
^^^^^^^^

.. java:method:: public void rollback() throws IOException, LoginException
   :outertype: Wiki.Revision

   Reverts this revision using the rollback method. See \ ``Wiki.rollback()``\ .

rollback
^^^^^^^^

.. java:method:: public void rollback(boolean bot, String reason) throws IOException, LoginException
   :outertype: Wiki.Revision

   Reverts this revision using the rollback method. See \ ``Wiki.rollback()``\ .

   :param bot: mark this and the reverted revision(s) as bot edits
   :param reason: (optional) a custom reason

setRcid
^^^^^^^

.. java:method:: public void setRcid(long rcid)
   :outertype: Wiki.Revision

   Sets the \ ``rcid``\  of this revision, used for patrolling. This parameter is optional. This is publicly editable for subclassing.

   :param rcid: the rcid of this revision (long)

setRollbackToken
^^^^^^^^^^^^^^^^

.. java:method:: public void setRollbackToken(String token)
   :outertype: Wiki.Revision

   Sets a rollback token for this revision.

   :param token: a rollback token

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: Wiki.Revision

   Returns a string representation of this revision.

   :return: see above

