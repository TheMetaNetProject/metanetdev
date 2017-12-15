.. java:import:: java.util.zip GZIPInputStream

Wiki
====

.. java:package:: org.wikipedia
   :noindex:

.. java:type:: public class Wiki implements Serializable

   This is a somewhat sketchy bot framework for editing MediaWiki wikis. Requires JDK 1.6 (6.0) or greater. Uses the \ `MediaWiki API <http://www.mediawiki.org/wiki/API:Main_page>`_\  for most operations. It is recommended that the server runs the latest version of MediaWiki (1.20), otherwise some functions may not work.

   Extended documentation is available \ `here <http://code.google.com/p/wiki-java/wiki/ExtendedDocumentation>`_\ . All wikilinks are relative to the English Wikipedia and all timestamps are in your wiki's time zone.

   Please file bug reports \ `here <http://en.wikipedia.org/w/index.php?title=User_talk:MER-C&action=edit&section=new>`_\  (fast) or at the \ `Google code bug tracker <http://code.google.com/p/wiki-java/issues/list>`_\  (slow).

   :author: MER-C and contributors

Fields
------
ALL_LOGS
^^^^^^^^

.. java:field:: public static final String ALL_LOGS
   :outertype: Wiki

   Denotes all logs.

ALL_NAMESPACES
^^^^^^^^^^^^^^

.. java:field:: public static final int ALL_NAMESPACES
   :outertype: Wiki

   Denotes all namespaces.

ASSERT_BOT
^^^^^^^^^^

.. java:field:: public static final int ASSERT_BOT
   :outertype: Wiki

   Assert that we have a bot flag (i.e. 2).

ASSERT_LOGGED_IN
^^^^^^^^^^^^^^^^

.. java:field:: public static final int ASSERT_LOGGED_IN
   :outertype: Wiki

   Assert that we are logged in (i.e. 1).

ASSERT_NONE
^^^^^^^^^^^

.. java:field:: public static final int ASSERT_NONE
   :outertype: Wiki

   Use no assertions (i.e. 0).

ASSERT_NO_MESSAGES
^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int ASSERT_NO_MESSAGES
   :outertype: Wiki

   Assert that we have no new messages. Not defined in Assert Edit, but some bots have this.

BLOCK_LOG
^^^^^^^^^

.. java:field:: public static final String BLOCK_LOG
   :outertype: Wiki

   Denotes the block log.

CATEGORY_NAMESPACE
^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int CATEGORY_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for category description pages. Has the prefix "Category:".

CATEGORY_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int CATEGORY_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages regarding categories. Has the prefix "Category talk:".

CURRENT_REVISION
^^^^^^^^^^^^^^^^

.. java:field:: public static final long CURRENT_REVISION
   :outertype: Wiki

   In \ ``Revision.diff()``\ , denotes the current revision.

DELETION_LOG
^^^^^^^^^^^^

.. java:field:: public static final String DELETION_LOG
   :outertype: Wiki

   Denotes the deletion log.

FILE_NAMESPACE
^^^^^^^^^^^^^^

.. java:field:: public static final int FILE_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for image/file description pages. Has the prefix prefix "File:". Do not create these directly, use upload() instead. (This namespace used to have the prefix "Image:", hence the name.)

FILE_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int FILE_TALK_NAMESPACE
   :outertype: Wiki

   Denotes talk pages for image description pages. Has the prefix "File talk:".

FULL_PROTECTION
^^^^^^^^^^^^^^^

.. java:field:: public static final int FULL_PROTECTION
   :outertype: Wiki

   Denotes full protection (i.e. only admins can edit this page) [edit=sysop;move=sysop].

HELP_NAMESPACE
^^^^^^^^^^^^^^

.. java:field:: public static final int HELP_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for help pages, given the prefix "Help:".

HELP_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int HELP_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages regarding help pages, given the prefix "Help talk:".

HIDE_ANON
^^^^^^^^^

.. java:field:: public static final int HIDE_ANON
   :outertype: Wiki

   In queries against the recent changes table, this would mean we don't fetch anonymous edits.

HIDE_BOT
^^^^^^^^

.. java:field:: public static final int HIDE_BOT
   :outertype: Wiki

   In queries against the recent changes table, this would mean we don't fetch edits made by bots.

HIDE_MINOR
^^^^^^^^^^

.. java:field:: public static final int HIDE_MINOR
   :outertype: Wiki

   In queries against the recent changes table, this would mean we don't fetch minor edits.

HIDE_PATROLLED
^^^^^^^^^^^^^^

.. java:field:: public static final int HIDE_PATROLLED
   :outertype: Wiki

   In queries against the recent changes table, this would mean we don't fetch patrolled edits.

HIDE_SELF
^^^^^^^^^

.. java:field:: public static final int HIDE_SELF
   :outertype: Wiki

   In queries against the recent changes table, this would mean we don't fetch by the logged in user.

IMAGE_NAMESPACE
^^^^^^^^^^^^^^^

.. java:field:: @Deprecated public static final int IMAGE_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for image/file description pages. Has the prefix prefix "File:". Do not create these directly, use upload() instead. (This namespace used to have the prefix "Image:", hence the name.)

IMAGE_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^^

.. java:field:: @Deprecated public static final int IMAGE_TALK_NAMESPACE
   :outertype: Wiki

   Denotes talk pages for image description pages. Has the prefix "File talk:".

IMPORT_LOG
^^^^^^^^^^

.. java:field:: public static final String IMPORT_LOG
   :outertype: Wiki

   Denotes the page importation log.

MAIN_NAMESPACE
^^^^^^^^^^^^^^

.. java:field:: public static final int MAIN_NAMESPACE
   :outertype: Wiki

   Denotes the main namespace, with no prefix.

MEDIAWIKI_NAMESPACE
^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int MEDIAWIKI_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for (wiki) system messages, given the prefix "MediaWiki:".

MEDIAWIKI_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int MEDIAWIKI_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages relating to system messages, given the prefix "MediaWiki talk:".

MEDIA_NAMESPACE
^^^^^^^^^^^^^^^

.. java:field:: public static final int MEDIA_NAMESPACE
   :outertype: Wiki

   Denotes the namespace of images and media, such that there is no description page. Uses the "Media:" prefix.

MOVE_LOG
^^^^^^^^

.. java:field:: public static final String MOVE_LOG
   :outertype: Wiki

   Denotes the move log.

MOVE_PROTECTION
^^^^^^^^^^^^^^^

.. java:field:: public static final int MOVE_PROTECTION
   :outertype: Wiki

   Denotes move protection (i.e. only admins can move this page) [move=sysop]. We don't define semi-move protection because only autoconfirmed users can move pages anyway.

NEXT_REVISION
^^^^^^^^^^^^^

.. java:field:: public static final long NEXT_REVISION
   :outertype: Wiki

   In \ ``Revision.diff()``\ , denotes the next revision.

NO_PROTECTION
^^^^^^^^^^^^^

.. java:field:: public static final int NO_PROTECTION
   :outertype: Wiki

   Denotes a non-protected page.

PATROL_LOG
^^^^^^^^^^

.. java:field:: public static final String PATROL_LOG
   :outertype: Wiki

   Denotes the edit patrol log.

PREVIOUS_REVISION
^^^^^^^^^^^^^^^^^

.. java:field:: public static final long PREVIOUS_REVISION
   :outertype: Wiki

   In \ ``Revision.diff()``\ , denotes the previous revision.

PROJECT_NAMESPACE
^^^^^^^^^^^^^^^^^

.. java:field:: public static final int PROJECT_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for pages relating to the project, with prefix "Project:". It also goes by the name of whatever the project name was.

PROJECT_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int PROJECT_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages relating to project pages, with prefix "Project talk:". It also goes by the name of whatever the project name was, + "talk:".

PROTECTED_DELETED_PAGE
^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int PROTECTED_DELETED_PAGE
   :outertype: Wiki

   Denotes protected deleted pages [create=sysop].

PROTECTION_LOG
^^^^^^^^^^^^^^

.. java:field:: public static final String PROTECTION_LOG
   :outertype: Wiki

   Denotes the protection log.

SEMI_AND_MOVE_PROTECTION
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int SEMI_AND_MOVE_PROTECTION
   :outertype: Wiki

   Denotes move and semi-protection (i.e. autoconfirmed editors can edit the page, but you need to be a sysop to move) [edit=autoconfirmed;move=sysop]. Naturally, this value (4) is equal to SEMI_PROTECTION (1) + MOVE_PROTECTION (3).

SEMI_PROTECTION
^^^^^^^^^^^^^^^

.. java:field:: public static final int SEMI_PROTECTION
   :outertype: Wiki

   Denotes semi-protection (i.e. only autoconfirmed users can edit this page) [edit=autoconfirmed;move=autoconfirmed].

SPECIAL_NAMESPACE
^^^^^^^^^^^^^^^^^

.. java:field:: public static final int SPECIAL_NAMESPACE
   :outertype: Wiki

   Denotes the namespace of pages with the "Special:" prefix. Note that many methods dealing with special pages may spew due to raw content not being available.

TALK_NAMESPACE
^^^^^^^^^^^^^^

.. java:field:: public static final int TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages relating to the main namespace, denoted by the prefix "Talk:".

TEMPLATE_NAMESPACE
^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int TEMPLATE_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for templates, given the prefix "Template:".

TEMPLATE_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int TEMPLATE_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for talk pages regarding templates, given the prefix "Template talk:".

UPLOAD_LOG
^^^^^^^^^^

.. java:field:: public static final String UPLOAD_LOG
   :outertype: Wiki

   Denotes the upload log.

UPLOAD_PROTECTION
^^^^^^^^^^^^^^^^^

.. java:field:: public static final int UPLOAD_PROTECTION
   :outertype: Wiki

   Denotes protected images where the corresponding image description page can be edited.

USER_CREATION_LOG
^^^^^^^^^^^^^^^^^

.. java:field:: public static final String USER_CREATION_LOG
   :outertype: Wiki

   Denotes the user creation log.

USER_NAMESPACE
^^^^^^^^^^^^^^

.. java:field:: public static final int USER_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for user pages, given the prefix "User:".

USER_RENAME_LOG
^^^^^^^^^^^^^^^

.. java:field:: public static final String USER_RENAME_LOG
   :outertype: Wiki

   Denotes the user renaming log.

USER_RIGHTS_LOG
^^^^^^^^^^^^^^^

.. java:field:: public static final String USER_RIGHTS_LOG
   :outertype: Wiki

   Denotes the user rights log.

USER_TALK_NAMESPACE
^^^^^^^^^^^^^^^^^^^

.. java:field:: public static final int USER_TALK_NAMESPACE
   :outertype: Wiki

   Denotes the namespace for user talk pages, given the prefix "User talk:".

logger
^^^^^^

.. java:field:: protected static final Logger logger
   :outertype: Wiki

query
^^^^^

.. java:field:: protected String query
   :outertype: Wiki

scriptPath
^^^^^^^^^^

.. java:field:: protected String scriptPath
   :outertype: Wiki

Constructors
------------
Wiki
^^^^

.. java:constructor:: public Wiki()
   :outertype: Wiki

   Creates a new connection to the English Wikipedia.

Wiki
^^^^

.. java:constructor:: public Wiki(String domain)
   :outertype: Wiki

   Creates a new connection to a wiki. WARNING: if the wiki uses a $wgScriptpath other than the default \ ``/w``\ , you need to call \ ``getScriptPath()``\  to automatically set it. Alternatively, you can use the constructor below if you know it in advance.

   :param domain: the wiki domain name e.g. en.wikipedia.org (defaults to en.wikipedia.org)

Wiki
^^^^

.. java:constructor:: public Wiki(String domain, String scriptPath)
   :outertype: Wiki

   Creates a new connection to a wiki with $wgScriptpath set to \ ``scriptPath``\ .

   :param domain: the wiki domain name
   :param scriptPath: the script path

Methods
-------
allUsers
^^^^^^^^

.. java:method:: public String allUsers(String start, int number) throws IOException
   :outertype: Wiki

   Gets the specified number of users (as a String) starting at the given string, in alphabetical order. Equivalent to [[Special:Listusers]].

   :param start: the string to start enumeration
   :param number: the number of users to return
   :return: a String[] containing the usernames

calendarToTimestamp
^^^^^^^^^^^^^^^^^^^

.. java:method:: protected String calendarToTimestamp(Calendar c)
   :outertype: Wiki

   Turns a calendar into a timestamp of the format yyyymmddhhmmss. Might be useful for subclasses.

   :param c: the calendar to convert
   :return: the converted calendar

checkErrors
^^^^^^^^^^^

.. java:method:: protected void checkErrors(String line, String caller) throws IOException, LoginException
   :outertype: Wiki

   Checks for errors from standard read/write requests.

   :param line: the response from the server to analyze
   :param caller: what we tried to do

checkRights
^^^^^^^^^^^

.. java:method:: protected boolean checkRights(int level, boolean move) throws IOException, CredentialException
   :outertype: Wiki

   Checks whether the currently logged on user has sufficient rights to edit/move a protected page.

   :param level: a protection level
   :param move: whether the action is a move
   :return: whether the user can perform the specified action

constructNamespaceString
^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void constructNamespaceString(StringBuilder sb, String id, int... namespaces)
   :outertype: Wiki

   Convenience method for converting a namespace list into String form.

   :param sb: the url StringBuilder to append to
   :param id: the request type prefix (e.g. "pl" for prop=links)
   :param namespaces: the list of namespaces to append

contribs
^^^^^^^^

.. java:method:: public Revision contribs(String user, int... ns) throws IOException
   :outertype: Wiki

   Gets the contributions of a user in a particular namespace. Equivalent to [[Special:Contributions]]. Be careful when using this method because the user may have a high edit count e.g. enWiki.contribs("MER-C",
   Wiki.MAIN_NAMESPACE).length > 30000.

   :param user: the user or IP to get contributions for
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the contributions of the user

contribs
^^^^^^^^

.. java:method:: public Revision contribs(String user, String prefix, Calendar offset, int... ns) throws IOException
   :outertype: Wiki

   Gets the contributions for a user, an IP address or a range of IP addresses. Equivalent to [[Special:Contributions]].

   :param user: the user to get contributions for
   :param offset: fetch edits no older than this date
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :param prefix: a prefix of usernames. Overrides \ ``user``\ .
   :return: contributions of this user

convertTimestamp
^^^^^^^^^^^^^^^^

.. java:method:: protected String convertTimestamp(String timestamp)
   :outertype: Wiki

   Converts a timestamp of the form used by the API (yyyy-mm-ddThh:mm:ssZ) to the form yyyymmddhhmmss, which can be fed into \ ``timestampToCalendar()``\ .

   :param timestamp: the timestamp to convert
   :return: the converted timestamp

decode
^^^^^^

.. java:method:: protected String decode(String in)
   :outertype: Wiki

   Strips entity references like " from the supplied string. This might be useful for subclasses.

   :param in: the string to remove URL encoding from
   :return: that string without URL encoding

delete
^^^^^^

.. java:method:: public synchronized void delete(String title, String reason) throws IOException, LoginException
   :outertype: Wiki

   Deletes a page. Does not delete any page requiring \ ``bigdelete``\ .

   :param title: the page to delete
   :param reason: the reason for deletion

edit
^^^^

.. java:method:: public void edit(String title, String text, String summary) throws IOException, LoginException
   :outertype: Wiki

   Edits a page by setting its text to the supplied value. This method is thread safe and blocks for a minimum time as specified by the throttle. The edit will be marked bot if \ ``isMarkBot() == true``\  and minor if \ ``isMarkMinor() == true``\ .

   :param text: the text of the page
   :param title: the title of the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.

edit
^^^^

.. java:method:: public void edit(String title, String text, String summary, Calendar basetime) throws IOException, LoginException
   :outertype: Wiki

   Edits a page by setting its text to the supplied value. This method is thread safe and blocks for a minimum time as specified by the throttle. The edit will be marked bot if \ ``isMarkBot() == true``\  and minor if \ ``isMarkMinor() == true``\ .

   :param text: the text of the page
   :param title: the title of the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.
   :param basetime: the timestamp of the revision on which \ ``text``\  is based, used to check for edit conflicts. \ ``null``\  disables this.

edit
^^^^

.. java:method:: public void edit(String title, String text, String summary, int section) throws IOException, LoginException
   :outertype: Wiki

   Edits a page by setting its text to the supplied value. This method is thread safe and blocks for a minimum time as specified by the throttle. The edit will be marked bot if \ ``isMarkBot() == true``\  and minor if \ ``isMarkMinor() == true``\ .

   :param text: the text of the page
   :param title: the title of the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.
   :param section: the section to edit. Use -1 to specify a new section and -2 to disable section editing.

edit
^^^^

.. java:method:: public void edit(String title, String text, String summary, int section, Calendar basetime) throws IOException, LoginException
   :outertype: Wiki

   Edits a page by setting its text to the supplied value. This method is thread safe and blocks for a minimum time as specified by the throttle. The edit will be marked bot if \ ``isMarkBot() == true``\  and minor if \ ``isMarkMinor() == true``\ .

   :param text: the text of the page
   :param title: the title of the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.
   :param section: the section to edit. Use -1 to specify a new section and -2 to disable section editing.
   :param basetime: the timestamp of the revision on which \ ``text``\  is based, used to check for edit conflicts. \ ``null``\  disables this.

edit
^^^^

.. java:method:: public synchronized void edit(String title, String text, String summary, boolean minor, boolean bot, int section, Calendar basetime) throws IOException, LoginException
   :outertype: Wiki

   Edits a page by setting its text to the supplied value. This method is thread safe and blocks for a minimum time as specified by the throttle.

   :param text: the text of the page
   :param title: the title of the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.
   :param minor: whether the edit should be marked as minor, See [[Help:Minor edit]].
   :param bot: whether to mark the edit as a bot edit (ignored if one does not have the necessary permissions)
   :param section: the section to edit. Use -1 to specify a new section and -2 to disable section editing.
   :param basetime: the timestamp of the revision on which \ ``text``\  is based, used to check for edit conflicts. \ ``null``\  disables this.

emailUser
^^^^^^^^^

.. java:method:: public synchronized void emailUser(User user, String message, String subject, boolean emailme) throws IOException, LoginException
   :outertype: Wiki

   Sends an email message to a user in a similar manner to [[Special:Emailuser]]. You and the target user must have a confirmed email address and the target user must have email contact enabled. Messages are sent in plain text (no wiki markup or HTML).

   :param user: a Wikipedia user with email enabled
   :param subject: the subject of the message
   :param message: the plain text message
   :param emailme: whether to send a copy of the message to your email address

equals
^^^^^^

.. java:method:: @Override public boolean equals(Object obj)
   :outertype: Wiki

   Determines whether this wiki is equal to another object.

   :param obj: the object to compare
   :return: whether this wiki is equal to such object

exists
^^^^^^

.. java:method:: public boolean[] exists(String... titles) throws IOException
   :outertype: Wiki

   Determines whether a series of pages exist. Requires the [[mw:Extension:ParserFunctions|ParserFunctions extension]].

   :param titles: the titles to check
   :return: whether the pages exist

export
^^^^^^

.. java:method:: public String export(String title) throws IOException
   :outertype: Wiki

   Exports the current revision of this page. Equivalent to [[Special:Export]].

   :param title: the title of the page to export
   :return: the exported text

export
^^^^^^

.. java:method:: public String export(List<String> titles) throws IOException
   :outertype: Wiki

   Exports the current revision of the list of pages. Equivalent to [[Special:Export]].

   :param titles: List of titles of pages to export
   :return: the exported text

fetch
^^^^^

.. java:method:: protected String fetch(String url, String caller) throws IOException
   :outertype: Wiki

   A generic URL content fetcher. This is only useful for GET requests, which is almost everything that doesn't modify the wiki. Might be useful for subclasses. Here we also check the database lag and wait if it exceeds \ ``maxlag``\ , see \ `here <https://mediawiki.org/wiki/Manual:Maxlag_parameter>`_\  for how this works.

   :param url: the url to fetch
   :param caller: the caller of this method

formatList
^^^^^^^^^^

.. java:method:: public static String formatList(String pages)
   :outertype: Wiki

   Formats a list of pages, say, generated from one of the query methods into something that would be editor-friendly. Does the exact opposite of \ ``parseList()``\ , i.e. { "Main Page", "Wikipedia:Featured picture candidates", "File:Example.png" } becomes the string:

   .. parsed-literal::

      *[[:Main Page]]
      *[[:Wikipedia:Featured picture candidates]]
      *[[:File:Example.png]]

   :param pages: an array of page titles
   :return: see above

getAssertionMode
^^^^^^^^^^^^^^^^

.. java:method:: public int getAssertionMode()
   :outertype: Wiki

   Gets the assertion mode. See [[mw:Extension:Assert Edit]] for what functionality this mimics. Assertion modes are bitmasks.

   :return: the current assertion mode

getCategories
^^^^^^^^^^^^^

.. java:method:: public String getCategories(String title) throws IOException
   :outertype: Wiki

   Gets the list of categories a particular page is in. Includes hidden categories. Capped at \ ``max``\  number of categories, there's no reason why there should be more than that.

   :param title: a page
   :return: the list of categories that page is in

getCategoryMembers
^^^^^^^^^^^^^^^^^^

.. java:method:: public String getCategoryMembers(String name, int... ns) throws IOException
   :outertype: Wiki

   Gets the members of a category.

   :param name: the name of the category (e.g. Candidates for speedy deletion, not Category:Candidates for speedy deletion)
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: a String[] containing page titles of members of the category

getCurrentDatabaseLag
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public int getCurrentDatabaseLag() throws IOException
   :outertype: Wiki

   Determines the current database replication lag.

   :return: the current database replication lag

getCurrentUser
^^^^^^^^^^^^^^

.. java:method:: public User getCurrentUser()
   :outertype: Wiki

   Gets the user we are currently logged in as. If not logged in, returns null.

   :return: the current logged in user

getDomain
^^^^^^^^^

.. java:method:: public String getDomain()
   :outertype: Wiki

   Gets the domain of the wiki, as supplied on construction.

   :return: the domain of the wiki

getDuplicates
^^^^^^^^^^^^^

.. java:method:: public String getDuplicates(String file) throws IOException
   :outertype: Wiki

   Gets duplicates of this file. Capped at \ ``max``\  number of duplicates, there's no good reason why there should be more than that. Equivalent to [[Special:FileDuplicateSearch]].

   :param file: the file for checking duplicates (without the File:)
   :return: the duplicates of that file

getFileMetadata
^^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, Object> getFileMetadata(String file) throws IOException
   :outertype: Wiki

   Gets the file metadata for a file. Note that \ ``getImage()``\  reads directly into a \ ``BufferedImage``\  object, so you won't be able to get all metadata that way. The keys are: * size (file size, Integer) * width (Integer) * height (Integer) * mime (MIME type, String) * plus EXIF metadata (Strings)

   :param file: the image to get metadata for, without the File: prefix
   :return: the metadata for the image

getFirstRevision
^^^^^^^^^^^^^^^^

.. java:method:: public Revision getFirstRevision(String title) throws IOException
   :outertype: Wiki

   Gets the first revision of a page, or null if the page does not exist.

   :param title: a page
   :return: the oldest revision of that page

getIPBlockList
^^^^^^^^^^^^^^

.. java:method:: public LogEntry getIPBlockList(String user) throws IOException
   :outertype: Wiki

   Looks up a particular user in the IP block list, i.e. whether a user is currently blocked. Equivalent to [[Special:Ipblocklist]].

   :param user: a username or IP (e.g. "127.0.0.1")
   :return: the block log entry

getIPBlockList
^^^^^^^^^^^^^^

.. java:method:: public LogEntry getIPBlockList(Calendar start, Calendar end) throws IOException
   :outertype: Wiki

   Lists currently operating blocks that were made in the specified interval. Equivalent to [[Special:Ipblocklist]].

   :param start: the start date
   :param end: the end date
   :return: the currently operating blocks that were made in that interval

getIPBlockList
^^^^^^^^^^^^^^

.. java:method:: protected LogEntry getIPBlockList(String user, Calendar start, Calendar end, int amount) throws IOException
   :outertype: Wiki

   Fetches part of the list of currently operational blocks. Equivalent to [[Special:Ipblocklist]]. WARNING: cannot tell whether a particular IP is autoblocked as this is non-public data (see also [[bugzilla:12321]] and [[foundation:Privacy policy]]). Don't call this directly, use one of the two above methods instead.

   :param user: a particular user that might have been blocked. Use "" to not specify one. May be an IP (e.g. "127.0.0.1") or a CIDR range (e.g. "127.0.0.0/16") but not an autoblock (e.g. "#123456").
   :param start: what timestamp to start. Use null to not specify one.
   :param end: what timestamp to end. Use null to not specify one.
   :param amount: the number of blocks to retrieve. Use \ ``Integer.MAX_VALUE``\  to not specify one.
   :return: a LogEntry[] of the blocks

getImage
^^^^^^^^

.. java:method:: public byte[] getImage(String title) throws IOException
   :outertype: Wiki

   Fetches an image file and returns the image data in a \ ``byte[]``\ . To recover the old behavior (BufferedImage), use \ ``ImageIO.read(new ByteArrayInputStream(getImage("Example.jpg")));``\

   :param title: the title of the image (i.e. Example.jpg, not File:Example.jpg)
   :return: the image data

getImage
^^^^^^^^

.. java:method:: public byte[] getImage(String title, int width, int height) throws IOException
   :outertype: Wiki

   Fetches a thumbnail of an image file and returns the image data in a \ ``byte[]``\ . To recover the old behavior (BufferedImage), use \ ``ImageIO.read(new ByteArrayInputStream(getImage("Example.jpg")));``\

   :param title: the title of the image without the File: prefix (i.e. Example.jpg, not File:Example.jpg)
   :param width: the width of the thumbnail (use -1 for actual width)
   :param height: the height of the thumbnail (use -1 for actual height)
   :return: the image data

getImageHistory
^^^^^^^^^^^^^^^

.. java:method:: public LogEntry getImageHistory(String title) throws IOException
   :outertype: Wiki

   Returns the upload history of an image. This is not the same as getLogEntries(null, null, Integer.MAX_VALUE, Wiki.UPLOAD_LOG,
   title, Wiki.FILE_NAMESPACE), as the image may have been deleted. This returns only the live history of an image.

   :param title: the title of the image, excluding the File prefix
   :return: the image history of the image

getImagesOnPage
^^^^^^^^^^^^^^^

.. java:method:: public String getImagesOnPage(String title) throws IOException
   :outertype: Wiki

   Gets the list of images used on a particular page. Capped at \ ``max``\  number of images, there's no reason why there should be more than that.

   :param title: a page
   :return: the list of images used in the page

getInterWikiBacklinks
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getInterWikiBacklinks(String prefix) throws IOException
   :outertype: Wiki

   Fetches all pages that use interwiki links to the specified wiki and the page on that wiki that is linked to. For example,
   getInterWikiBacklinks("testwiki") may return:

   .. parsed-literal::

      {
          { "Spam", "testwiki:Blah" },
          { "Test", "testwiki:Main_Page" }
      }

   Here the page [[Spam]] contains the interwiki link [[testwiki:Blah]] and the page [[Test]] contains the interwiki link [[testwiki:Main_Page]]. This does not resolve nested interwiki prefixes, e.g. [[wikt:fr:Test]].

   For WMF wikis, see \ `the interwiki map <http://meta.wikimedia.org/wiki/Interwiki_map>`_\ for where some prefixes link to.

   :param prefix: the interwiki prefix that denotes a wiki
   :return: all pages that contain interwiki links to said wiki

getInterWikiBacklinks
^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public String getInterWikiBacklinks(String prefix, String title) throws IOException
   :outertype: Wiki

   Fetches all pages that use interwiki links with a certain \ ``prefix``\  and \ ``title``\ . \ ``prefix``\  refers to the wiki being linked to and \ ``title``\  refers to the page on said wiki being linked to. In wiki syntax, this is [[prefix:title]]. This does not resolve nested prefixes, e.g. [[wikt:fr:Test]].

   Example: If [[Test]] and [[Spam]] both contain the interwiki link [[testwiki:Blah]] then getInterWikiBacklinks("testwiki", "Blah");
   will return (sorted by \ ``title``\ )

   .. parsed-literal::

      {
          { "Spam", "testwiki:Blah" },
          { "Test", "testwiki:Blah" }
      }

   For WMF wikis, see \ `the interwiki map <http://meta.wikimedia.org/wiki/Interwiki_map>`_\ for where some prefixes link to.

   :param prefix: the interwiki prefix to search
   :param title: the title of the page on the other wiki to search for (optional, use "|" to not specify one). Warning: "" is a valid interwiki target!
   :return: a list of all pages that use interwiki links satisfying the parameters given

getInterwikiLinks
^^^^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, String> getInterwikiLinks(String title) throws IOException
   :outertype: Wiki

   Gets the list of interwiki links a particular page has. The returned map has the format language code => the page on the external wiki linked to.

   :param title: a page
   :return: a map of interwiki links that page has

getLinksOnPage
^^^^^^^^^^^^^^

.. java:method:: public String getLinksOnPage(String title) throws IOException
   :outertype: Wiki

   Gets the list of links used on a particular page. Patch somewhat by wim.jongman

   :param title: a page
   :return: the list of links used in the page

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(int amount) throws IOException
   :outertype: Wiki

   Gets the most recent set of log entries up to the given amount. Equivalent to [[Special:Log]].

   :param amount: the amount of log entries to get
   :return: the most recent set of log entries

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(User user) throws IOException
   :outertype: Wiki

   Gets log entries for a specific user. Equivalent to [[Special:Log]].

   :param user: the user to get log entries for
   :return: the set of log entries created by that user

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(String target) throws IOException
   :outertype: Wiki

   Gets the log entries representing actions that were performed on a specific target. Equivalent to [[Special:Log]].

   :param target: the target of the action(s).
   :return: the specified log entries

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(Calendar start, Calendar end) throws IOException
   :outertype: Wiki

   Gets all log entries that occurred between the specified dates. WARNING: the start date is the most recent of the dates given, and the order of enumeration is from newest to oldest. Equivalent to [[Special:Log]].

   :param start: what timestamp to start. Use null to not specify one.
   :param end: what timestamp to end. Use null to not specify one.
   :return: the specified log entries

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(int amount, String type) throws IOException
   :outertype: Wiki

   Gets the last how ever many log entries in the specified log. Equivalent to [[Special:Log]] and [[Special:Newimages]] when \ ``type.equals(UPLOAD_LOG)``\ .

   :param amount: the number of entries to get
   :param type: what log to get (e.g. DELETION_LOG)
   :return: the specified log entries

getLogEntries
^^^^^^^^^^^^^

.. java:method:: public LogEntry getLogEntries(Calendar start, Calendar end, int amount, String log, User user, String target, int namespace) throws IOException
   :outertype: Wiki

   Gets the specified amount of log entries between the given times by the given user on the given target. Equivalent to [[Special:Log]]. WARNING: the start date is the most recent of the dates given, and the order of enumeration is from newest to oldest.

   :param start: what timestamp to start. Use null to not specify one.
   :param end: what timestamp to end. Use null to not specify one.
   :param amount: the amount of log entries to get. If both start and end are defined, this is ignored. Use Integer.MAX_VALUE to not specify one.
   :param log: what log to get (e.g. DELETION_LOG)
   :param user: the user performing the action. Use null not to specify one.
   :param target: the target of the action. Use "" not to specify one.
   :param namespace: filters by namespace. Returns empty if namespace doesn't exist.
   :return: the specified log entries

getMaxLag
^^^^^^^^^

.. java:method:: public int getMaxLag()
   :outertype: Wiki

   Gets the maxlag parameter. See [[mw:Manual:Maxlag parameter]].

   :return: the current maxlag, in seconds

getOldImage
^^^^^^^^^^^

.. java:method:: public byte[] getOldImage(LogEntry entry) throws IOException
   :outertype: Wiki

   Gets an old image revision and returns the image data in a \ ``byte[]``\ . You will have to do the thumbnailing yourself.

   :param entry: the upload log entry that corresponds to the image being uploaded
   :return: the image data that was uploaded, as long as it is still live or null if the image doesn't exist

getPageHistory
^^^^^^^^^^^^^^

.. java:method:: public Revision getPageHistory(String title) throws IOException
   :outertype: Wiki

   Gets the entire revision history of a page. Be careful when using this method as some pages (such as [[Wikipedia:Administrators' noticeboard/Incidents]] have ~10^6 revisions.

   :param title: a page
   :return: the revisions of that page

getPageHistory
^^^^^^^^^^^^^^

.. java:method:: public Revision getPageHistory(String title, Calendar start, Calendar end) throws IOException
   :outertype: Wiki

   Gets the revision history of a page between two dates.

   :param title: a page
   :param start: the date to start enumeration (the latest of the two dates)
   :param end: the date to stop enumeration (the earliest of the two dates)
   :return: the revisions of that page in that time span

getPageInfo
^^^^^^^^^^^

.. java:method:: public HashMap<String, Object> getPageInfo(String page) throws IOException
   :outertype: Wiki

   Gets various page info. Returns:

   .. parsed-literal::

      {
          "displaytitle" => "iPod"         , // the title of the page that is actually displayed (String)
          "protection"   => NO_PROTECTION  , // the protection level of the page (Integer)
          "token"        => "\+"           , // an edit token for the page, must be logged
                                             // in to be non-trivial (String)
          "exists"       => true           , // whether the page exists (Boolean)
          "lastpurged"   => 20110101000000 , // when the page was last purged (Calendar), null if the
                                             // page does not exist
          "lastrevid"    => 123456789L     , // the revid of the top revision (Long), -1L if the page
                                             // does not exist
          "size"         => 5000           , // the size of the page (Integer), -1 if the page does
                                             // not exist
          "cascade"      => false          , // whether this page is cascade protected (Boolean)
          "timestamp"    => makeCalendar() , // when this method was called (Calendar)
          "watchtoken"   => "\+"             // watchlist token (String)
      }

   :param page: the page to get info for
   :return: (see above)

getPageText
^^^^^^^^^^^

.. java:method:: public String getPageText(String title) throws IOException
   :outertype: Wiki

   Gets the raw wikicode for a page. WARNING: does not support special pages. Check [[User talk:MER-C/Wiki.java#Special page equivalents]] for fetching the contents of special pages. Use \ ``getImage()``\  to fetch an image.

   :param title: the title of the page.
   :return: the raw wikicode of a page.

getProtectionLevel
^^^^^^^^^^^^^^^^^^

.. java:method:: public int getProtectionLevel(String title) throws IOException
   :outertype: Wiki

   Gets the protection status of a page.

   :param title: the title of the page
   :return: one of the various protection levels (i.e,. NO_PROTECTION, SEMI_PROTECTION, MOVE_PROTECTION, FULL_PROTECTION, SEMI_AND_MOVE_PROTECTION, PROTECTED_DELETED_PAGE)

getRawWatchlist
^^^^^^^^^^^^^^^

.. java:method:: public String getRawWatchlist() throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Fetches the list of titles on the currently logged in user's watchlist. Equivalent to [[Special:Watchlist/raw]].

   :return: the contents of the watchlist

getRawWatchlist
^^^^^^^^^^^^^^^

.. java:method:: public String getRawWatchlist(boolean cache) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Fetches the list of titles on the currently logged in user's watchlist. Equivalent to [[Special:Watchlist/raw]].

   :param cache: whether we should use the watchlist cache (no online activity, if the cache exists)
   :return: the contents of the watchlist

getRenderedText
^^^^^^^^^^^^^^^

.. java:method:: public String getRenderedText(String title) throws IOException
   :outertype: Wiki

   Gets the contents of a page, rendered in HTML (as opposed to wikitext). WARNING: only supports special pages in certain circumstances, for example getRenderedText("Special:Recentchanges")
   returns the 50 most recent change to the wiki in pretty-print HTML. You should test any use of this method on-wiki through the text \ ``{{Special:Specialpage}}``\ . Use \ ``getImage()``\  to fetch an image. Be aware of any transclusion limits, as outlined at [[Wikipedia:Template limits]].

   :param title: the title of the page
   :return: the rendered contents of that page

getRevision
^^^^^^^^^^^

.. java:method:: public Revision getRevision(long oldid) throws IOException
   :outertype: Wiki

   Gets a revision based on a given oldid. Automatically fills out all attributes of that revision except \ ``rcid``\ .

   :param oldid: a particular oldid
   :return: the revision corresponding to that oldid. If a particular revision has been deleted, returns null.

getScriptPath
^^^^^^^^^^^^^

.. java:method:: public String getScriptPath() throws IOException
   :outertype: Wiki

   Detects the $wgScriptpath wiki variable and sets the bot framework up to use it. You need not call this if you know the script path is \ ``/w``\ . See also [[mw:Manual:$wgScriptpath]].

   :return: the script path, if you have any use for it

getSectionMap
^^^^^^^^^^^^^

.. java:method:: public LinkedHashMap<String, String> getSectionMap(String page) throws IOException
   :outertype: Wiki

   Gets the list of sections on a particular page. The returned map pairs the section numbering as in the table of contents with the section title, as in the following example: 1 => How to nominate 1.1 => Step 1 - Evaluate 1.2 => Step 2 - Create subpage 1.2.1 => Step 2.5 - Transclude and link 1.3 => Step 3 - Update image ...

   :param page: the page to get sections for
   :return: the section map for that page

getSectionText
^^^^^^^^^^^^^^

.. java:method:: public String getSectionText(String title, int number) throws IOException
   :outertype: Wiki

   Gets the text of a specific section. Useful for section editing.

   :param title: the title of the relevant page
   :param number: the section number of the section to retrieve text for

getSiteStatistics
^^^^^^^^^^^^^^^^^

.. java:method:: public HashMap<String, Integer> getSiteStatistics() throws IOException
   :outertype: Wiki

   Fetches some site statistics, namely the number of articles, pages, files, edits, users and admins. Equivalent to [[Special:Statistics]].

   :return: a map containing the stats. Use "articles", "pages", "files" "edits", "users" or "admins" to retrieve the respective value

getStatusCheckInterval
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public int getStatusCheckInterval()
   :outertype: Wiki

   Gets the number of actions (edit, move, block, delete, etc) between status checks. A status check is where we update user rights, block status and check for new messages (if the appropriate assertion mode is set).

   :return: the number of edits between status checks

getTalkPage
^^^^^^^^^^^

.. java:method:: public String getTalkPage(String title) throws IOException
   :outertype: Wiki

   Returns the corresponding talk page to this page. Override to add custom namespaces.

   :param title: the page title
   :return: the name of the talk page corresponding to \ ``title``\  or "" if we cannot recognise it

getTemplates
^^^^^^^^^^^^

.. java:method:: public String getTemplates(String title, int... ns) throws IOException
   :outertype: Wiki

   Gets the list of templates used on a particular page that are in a particular namespace(s). Capped at \ ``max``\  number of templates, there's no reason why there should be more than that.

   :param title: a page
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the list of templates used on that page in that namespace

getThrottle
^^^^^^^^^^^

.. java:method:: public int getThrottle()
   :outertype: Wiki

   Gets the editing throttle.

   :return: the throttle value in milliseconds

getTopRevision
^^^^^^^^^^^^^^

.. java:method:: public Revision getTopRevision(String title) throws IOException
   :outertype: Wiki

   Gets the most recent revision of a page, or null if the page does not exist.

   :param title: a page
   :return: the most recent revision of that page

getUser
^^^^^^^

.. java:method:: public User getUser(String username) throws IOException
   :outertype: Wiki

   Gets the user with the given username. Returns null if it doesn't exist.

   :param username: a username
   :return: the user with that username

getUserAgent
^^^^^^^^^^^^

.. java:method:: public String getUserAgent()
   :outertype: Wiki

   Gets the user agent HTTP header to be used for requests. Default is "Wiki.java " + version.

   :return: useragent the user agent

hasNewMessages
^^^^^^^^^^^^^^

.. java:method:: public boolean hasNewMessages() throws IOException
   :outertype: Wiki

   Determines whether the current user has new messages. (A human would notice a yellow bar at the top of the page).

   :return: whether the user has new messages

hashCode
^^^^^^^^

.. java:method:: @Override public int hashCode()
   :outertype: Wiki

   Returns a hash code of this object.

   :return: a hash code

imageUsage
^^^^^^^^^^

.. java:method:: public String imageUsage(String image, int... ns) throws IOException
   :outertype: Wiki

   Returns a list of pages in the specified namespaces which use the specified image.

   :param image: the image (Example.png, not File:Example.png)
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the list of pages that use this image

initVars
^^^^^^^^

.. java:method:: protected void initVars()
   :outertype: Wiki

   Override/edit this if you need to change the API and human interface url configuration of the wiki. Some example uses: *Using HTTPS on Wikimedia sites *Server-side cache management (maxage and smaxage API parameters) \nWritten by Tedder

intersection
^^^^^^^^^^^^

.. java:method:: public static String intersection(String a, String b)
   :outertype: Wiki

   Determines the intersection of two lists of pages a and b. Such lists might be generated from the various list methods below. Examples from the English Wikipedia:

   .. parsed-literal::

      // find all orphaned and unwikified articles
      String[] articles = Wiki.intersection(wikipedia.getCategoryMembers("All orphaned articles", Wiki.MAIN_NAMESPACE),
          wikipedia.getCategoryMembers("All pages needing to be wikified", Wiki.MAIN_NAMESPACE));

      // find all (notable) living people who are related to Barack Obama
      String[] people = Wiki.intersection(wikipedia.getCategoryMembers("Living people", Wiki.MAIN_NAMESPACE),
          wikipedia.whatLinksHere("Barack Obama", Wiki.MAIN_NAMESPACE));

   :param a: a list of pages
   :param b: another list of pages
   :return: a intersect b (as String[])

isMarkBot
^^^^^^^^^

.. java:method:: public boolean isMarkBot()
   :outertype: Wiki

   Are edits are marked as bot by default?

   :return: whether edits are marked as bot by default

isMarkMinor
^^^^^^^^^^^

.. java:method:: public boolean isMarkMinor()
   :outertype: Wiki

   Are edits are marked as minor by default?

   :return: whether edits are marked as minor by default

isResolvingRedirects
^^^^^^^^^^^^^^^^^^^^

.. java:method:: public boolean isResolvingRedirects()
   :outertype: Wiki

   Checks whether API action=query dependencies automatically resolve redirects (default = false).

   :return: (see above)

isUsingCompressedRequests
^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public boolean isUsingCompressedRequests()
   :outertype: Wiki

   Checks whether we are using GZip compression for GET requests. Default: true.

   :return: (see above)

isWatched
^^^^^^^^^

.. java:method:: public boolean isWatched(String title) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Determines whether a page is watched. (Uses a cache).

   :param title: the title to be checked
   :return: whether that page is watched

linksearch
^^^^^^^^^^

.. java:method:: public ArrayList linksearch(String pattern) throws IOException
   :outertype: Wiki

   Searches the wiki for external links. Equivalent to [[Special:Linksearch]]. Returns two lists, where the first is the list of pages and the second is the list of urls. The index of a page in the first list corresponds to the index of the url on that page in the second list. Wildcards (*) are only permitted at the start of the search string.

   :param pattern: the pattern (String) to search for (e.g. example.com, *.example.com)
   :return: two lists - index 0 is the list of pages (String), index 1 is the list of urls (instance of \ ``java.net.URL``\ )

linksearch
^^^^^^^^^^

.. java:method:: public ArrayList linksearch(String pattern, String protocol, int... ns) throws IOException
   :outertype: Wiki

   Searches the wiki for external links. Equivalent to [[Special:Linksearch]]. Returns two lists, where the first is the list of pages and the second is the list of urls. The index of a page in the first list corresponds to the index of the url on that page in the second list. Wildcards (*) are only permitted at the start of the search string.

   :param pattern: the pattern (String) to search for (e.g. example.com, *.example.com)
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :param protocol: one of { http, https, ftp, irc, gopher, telnet, nntp, worldwind, mailto, news, svn, git, mms } or "" (equivalent to http)
   :return: two lists - index 0 is the list of pages (String), index 1 is the list of urls (instance of \ ``java.net.URL``\ )

listPages
^^^^^^^^^

.. java:method:: public String listPages(String prefix, int level, int namespace) throws IOException
   :outertype: Wiki

   Lists pages with titles containing a certain prefix with a certain protection level and in a certain namespace. Equivalent to [[Special:Allpages]], [[Special:Prefixindex]], [[Special:Protectedpages]] and [[Special:Allmessages]] (if namespace == MEDIAWIKI_NAMESPACE). WARNING: Limited to 500 values (5000 for bots), unless a prefix or protection level is specified.

   :param prefix: the prefix of the title. Use "" to not specify one.
   :param level: a protection level. Use NO_PROTECTION to not specify one. WARNING: it is not currently possible to specify a combination of both semi and move protection
   :param namespace: a namespace. ALL_NAMESPACES is not suppported, an UnsupportedOperationException will be thrown.
   :return: the specified list of pages

listPages
^^^^^^^^^

.. java:method:: public String listPages(String prefix, int level, int namespace, int minimum, int maximum) throws IOException
   :outertype: Wiki

   Lists pages with titles containing a certain prefix with a certain protection level and in a certain namespace. Equivalent to [[Special:Allpages]], [[Special:Prefixindex]], [[Special:Protectedpages]] [[Special:Allmessages]] (if namespace == MEDIAWIKI_NAMESPACE), [[Special:Shortpages]] and [[Special:Longpages]]. WARNING: Limited to 500 values (5000 for bots), unless a prefix, (max|min)imum size or protection level is specified.

   :param prefix: the prefix of the title. Use "" to not specify one.
   :param level: a protection level. Use NO_PROTECTION to not specify one. WARNING: it is not currently possible to specify a combination of both semi and move protection
   :param namespace: a namespace. ALL_NAMESPACES is not suppported, an UnsupportedOperationException will be thrown.
   :param minimum: the minimum size in bytes these pages can be. Use -1 to not specify one.
   :param maximum: the maximum size in bytes these pages can be. Use -1 to not specify one.
   :return: the specified list of pages

log
^^^

.. java:method:: protected void log(Level level, String text, String method)
   :outertype: Wiki

   Logs a successful result.

   :param text: string the string to log
   :param method: what we are currently doing
   :param level: the level to log at

login
^^^^^

.. java:method:: public synchronized void login(String username, char[] password) throws IOException, FailedLoginException
   :outertype: Wiki

   Logs in to the wiki. This method is thread-safe. If the specified username or password is incorrect, the thread blocks for 20 seconds then throws an exception.

   :param username: a username
   :param password: a password (as a char[] due to JPasswordField)

logout
^^^^^^

.. java:method:: public synchronized void logout()
   :outertype: Wiki

   Logs out of the wiki. This method is thread safe (so that we don't log out during an edit). All operations are conducted offline, so you can serialize this Wiki first.

logoutServerSide
^^^^^^^^^^^^^^^^

.. java:method:: public synchronized void logoutServerSide() throws IOException
   :outertype: Wiki

   Logs out of the wiki and destroys the session on the server. You will need to log in again instead of just reading in a serialized wiki. Equivalent to [[Special:Userlogout]]. This method is thread safe (so that we don't log out during an edit). WARNING: kills all concurrent sessions - if you are logged in with a browser this will log you out there as well.

logurl
^^^^^^

.. java:method:: protected void logurl(String url, String method)
   :outertype: Wiki

   Logs a url fetch.

   :param url: the url we are fetching
   :param method: what we are currently doing

longPages
^^^^^^^^^

.. java:method:: public String longPages(int cutoff) throws IOException
   :outertype: Wiki

   List pages above a certain size in the main namespace. Equivalent to [[Special:Longpages]].

   :param cutoff: the minimum size in bytes these long pages can be
   :return: pages above that size

longPages
^^^^^^^^^

.. java:method:: public String longPages(int cutoff, int namespace) throws IOException
   :outertype: Wiki

   List pages above a certain size in any namespace. Equivalent to [[Special:Longpages]].

   :param cutoff: the minimum size in nbytes these long pages can be
   :param namespace: a namespace
   :return: pages above that size

makeCalendar
^^^^^^^^^^^^

.. java:method:: public Calendar makeCalendar()
   :outertype: Wiki

   Creates a Calendar object with the current time. Wikimedia wikis use UTC, override this if your wiki is in another timezone.

   :return: see above

move
^^^^

.. java:method:: public void move(String title, String newTitle, String reason) throws IOException, LoginException
   :outertype: Wiki

   Moves a page. Moves the associated talk page and leaves redirects, if applicable. Equivalent to [[Special:MovePage]]. This method is thread safe and is subject to the throttle.

   :param title: the title of the page to move
   :param newTitle: the new title of the page
   :param reason: a reason for the move

move
^^^^

.. java:method:: public synchronized void move(String title, String newTitle, String reason, boolean noredirect, boolean movetalk, boolean movesubpages) throws IOException, LoginException
   :outertype: Wiki

   Moves a page. Equivalent to [[Special:MovePage]]. This method is thread safe and is subject to the throttle.

   :param title: the title of the page to move
   :param newTitle: the new title of the page
   :param reason: a reason for the move
   :param noredirect: don't leave a redirect behind. You need to be a admin to do this, otherwise this option is ignored.
   :param movesubpages: move the subpages of this page as well. You need to be an admin to do this, otherwise this will be ignored.
   :param movetalk: move the talk page as well (if applicable)

multipartPost
^^^^^^^^^^^^^

.. java:method:: protected String multipartPost(String url, Map<String, ?> params, String caller) throws IOException
   :outertype: Wiki

   Performs a multi-part HTTP POST.

   :param url: the url to post to
   :param params: the POST parameters. Supported types: UTF-8 text, byte[]. Text and parameter names must NOT be URL encoded.
   :param caller: the caller of this method
   :return: the server response

namespace
^^^^^^^^^

.. java:method:: public int namespace(String title) throws IOException
   :outertype: Wiki

   Returns the namespace a page is in. No need to override this to add custom namespaces, though you may want to define static fields e.g. \ ``public static final int PORTAL_NAMESPACE = 100;``\  for the Portal namespace on the English Wikipedia.

   :param title: the title of the page
   :return: one of namespace types above, or a number for custom namespaces or ALL_NAMESPACES if we can't make sense of it

namespaceIdentifier
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String namespaceIdentifier(int namespace) throws IOException
   :outertype: Wiki

   For a given namespace denoted as an integer, fetch the corresponding identification string e.g. \ ``namespaceIdentifier(1)``\  should return "Talk". (This does the exact opposite to \ ``namespace()``\ .

   :param namespace: an integer corresponding to a namespace. If it does not correspond to a namespace, we assume you mean the main namespace (i.e. return "").
   :return: the identifier of the namespace

newPages
^^^^^^^^

.. java:method:: public Revision newPages(int amount) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recently created pages in the main namespace. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then.

   :param amount: the number of pages to fetch
   :return: the revisions that created the pages satisfying the requirements above

newPages
^^^^^^^^

.. java:method:: public Revision newPages(int amount, int rcoptions) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recently created pages in the main namespace subject to the specified constraints. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Newpages]].

   :param rcoptions: a bitmask of HIDE_ANON etc that dictate which pages we return (e.g. exclude patrolled pages => rcoptions = HIDE_PATROLLED).
   :param amount: the amount of new pages to get
   :return: the revisions that created the pages satisfying the requirements above

newPages
^^^^^^^^

.. java:method:: public Revision newPages(int amount, int rcoptions, int... ns) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recently created pages in the specified namespace, subject to the specified constraints. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Newpages]].

   :param rcoptions: a bitmask of HIDE_ANON etc that dictate which pages we return (e.g. exclude patrolled pages => rcoptions = HIDE_PATROLLED).
   :param amount: the amount of new pages to get
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the revisions that created the pages satisfying the requirements above

newSection
^^^^^^^^^^

.. java:method:: public void newSection(String title, String subject, String text, boolean minor, boolean bot) throws IOException, LoginException
   :outertype: Wiki

   Creates a new section on the specified page. Leave \ ``subject``\  as the empty string if you just want to append.

   :param title: the title of the page to edit
   :param subject: the subject of the new section
   :param text: the text of the new section
   :param minor: whether the edit should be marked as minor (see [[Help:Minor edit]])

normalize
^^^^^^^^^

.. java:method:: public String normalize(String s)
   :outertype: Wiki

   Convenience method for normalizing MediaWiki titles. (Converts all spaces to underscores and makes the first letter caps).

   :param s: the string to normalize
   :return: the normalized string

parse
^^^^^

.. java:method:: public String parse(String markup) throws IOException
   :outertype: Wiki

   Renders the specified wiki markup by passing it to the MediaWiki parser through the API. (Note: this isn't implemented locally because I can't be stuffed porting Parser.php). One use of this method is to emulate the previewing functionality of the MediaWiki software.

   :param markup: the markup to parse
   :return: the parsed markup as HTML

parseAndCleanup
^^^^^^^^^^^^^^^

.. java:method:: protected String parseAndCleanup(String in) throws IOException
   :outertype: Wiki

   Same as \ ``parse()``\ , but also strips out unwanted crap. This might be useful to subclasses.

   :param in: the string to parse
   :return: that string without the crap

parseList
^^^^^^^^^

.. java:method:: public static String parseList(String list)
   :outertype: Wiki

   Parses a list of links into its individual elements. Such a list should be in the form:

   .. parsed-literal::

      * [[Main Page]]
      * [[Wikipedia:Featured picture candidates]]
      * [[:File:Example.png]]

   in which case { "Main Page", "Wikipedia:Featured picture
   candidates", "File:Example.png" } is the return value.

   :param list: a list of pages
   :return: an array of the page titles

parseLogEntry
^^^^^^^^^^^^^

.. java:method:: protected LogEntry parseLogEntry(String xml, int caller)
   :outertype: Wiki

   Parses xml generated by \ ``getLogEntries()``\ , \ ``getImageHistory()``\  and \ ``getIPBlockList()``\  into LogEntry objects. Override this if you want custom log types. NOTE: if RevisionDelete was used on a log entry, the relevant values will be null.

   :param xml: the xml to parse
   :param caller: 1 if ipblocklist, 2 if imagehistory
   :return: the parsed log entry

parseRevision
^^^^^^^^^^^^^

.. java:method:: protected Revision parseRevision(String xml, String title)
   :outertype: Wiki

   Parses stuff of the form title="L. Sprague de Camp"
   timestamp="2006-08-28T23:48:08Z" minor="" comment="robot  Modifying:
   [[bg:Blah]]" into useful revision objects. Used by \ ``contribs()``\ , \ ``watchlist()``\ , \ ``getPageHistory()``\  \ ``rangeContribs()``\  and \ ``recentChanges()``\ . NOTE: if RevisionDelete was used on a revision, the relevant values will be null.

   :param xml: the XML to parse
   :param title: an optional title parameter if we already know what it is (use "" if we don't)
   :return: the Revision encoded in the XML

populateNamespaceCache
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: protected void populateNamespaceCache() throws IOException
   :outertype: Wiki

   Populates the namespace cache.

post
^^^^

.. java:method:: protected String post(String url, String text, String caller) throws IOException
   :outertype: Wiki

   Does a text-only HTTP POST.

   :param url: the url to post to
   :param text: the text to post
   :param caller: the caller of this method
   :return: the server response

prefixIndex
^^^^^^^^^^^

.. java:method:: public String prefixIndex(String prefix) throws IOException
   :outertype: Wiki

   Lists pages that start with a given prefix. Equivalent to [[Special:Prefixindex]].

   :param prefix: the prefix
   :return: the list of pages with that prefix

prepend
^^^^^^^

.. java:method:: public void prepend(String title, String stuff, String summary, boolean minor, boolean bot) throws IOException, LoginException
   :outertype: Wiki

   Prepends something to the given page. A convenience method for adding maintainance templates, rather than getting and setting the page yourself.

   :param title: the title of the page
   :param stuff: what to prepend to the page
   :param summary: the edit summary. See [[Help:Edit summary]]. Summaries longer than 200 characters are truncated server-side.
   :param minor: whether the edit is minor

purge
^^^^^

.. java:method:: public void purge(boolean links, String... titles) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Purges the server-side cache for various pages.

   :param titles: the titles of the page to purge
   :param links: update the links tables

random
^^^^^^

.. java:method:: public String random() throws IOException
   :outertype: Wiki

   Fetches a random page in the main namespace. Equivalent to [[Special:Random]].

   :return: the title of the page

random
^^^^^^

.. java:method:: public String random(int... ns) throws IOException
   :outertype: Wiki

   Fetches a random page in the specified namespace. Equivalent to [[Special:Random]].

   :param ns: namespace(s)
   :return: the title of the page

rangeContribs
^^^^^^^^^^^^^

.. java:method:: public Revision rangeContribs(String range) throws IOException
   :outertype: Wiki

   Gets the contributions by a range of IP v4 addresses. Supported ranges are /8, /16 and /24. Do be careful with this, as calls such as enWiki.rangeContribs("152.163.0.0/16"); // let's get all the
   contributions for this AOL range! might just kill your program.

   :param range: the CIDR range of IP addresses to get contributions for
   :return: the contributions of that range

recentChanges
^^^^^^^^^^^^^

.. java:method:: public Revision recentChanges(int amount) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recent changes in the main namespace. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Recentchanges]].

   Note: Log entries in recent changes have a revid of 0!

   :param amount: the number of entries to return
   :return: the recent changes that satisfy these criteria

recentChanges
^^^^^^^^^^^^^

.. java:method:: public Revision recentChanges(int amount, int... ns) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recent changes in the specified namespace. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Recentchanges]].

   Note: Log entries in recent changes have a revid of 0!

   :param amount: the number of entries to return
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the recent changes that satisfy these criteria

recentChanges
^^^^^^^^^^^^^

.. java:method:: public Revision recentChanges(int amount, int rcoptions, int... ns) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recent changes in the specified namespace subject to the specified constraints. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Recentchanges]].

   Note: Log entries in recent changes have a revid of 0!

   :param amount: the number of entries to return
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :param rcoptions: a bitmask of HIDE_ANON etc that dictate which pages we return.
   :return: the recent changes that satisfy these criteria

recentChanges
^^^^^^^^^^^^^

.. java:method:: protected Revision recentChanges(int amount, int rcoptions, boolean newpages, int... ns) throws IOException
   :outertype: Wiki

   Fetches the \ ``amount``\  most recent changes in the specified namespace subject to the specified constraints. WARNING: The recent changes table only stores new pages for about a month. It is not possible to retrieve changes before then. Equivalent to [[Special:Recentchanges]].

   Note: Log entries in recent changes have a revid of 0!

   :param amount: the number of entries to return
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :param rcoptions: a bitmask of HIDE_ANON etc that dictate which pages we return.
   :param newpages: show new pages only
   :return: the recent changes that satisfy these criteria

relativeComplement
^^^^^^^^^^^^^^^^^^

.. java:method:: public static String relativeComplement(String a, String b)
   :outertype: Wiki

   Determines the list of articles that are in a but not b, i.e. a \ b. This is not the same as b \ a. Such lists might be generated from the various lists below. Some examples from the English Wikipedia:

   .. parsed-literal::

      // find all Martian crater articles that do not have an infobox
      String[] articles = Wiki.relativeComplement(wikipedia.getCategoryMembers("Craters on Mars"),
          wikipedia.whatTranscludesHere("Template:MarsGeo-Crater", Wiki.MAIN_NAMESPACE));

      // find all images without a description that haven't been tagged "no license"
      String[] images = Wiki.relativeComplement(wikipedia.getCategoryMembers("Images lacking a description"),
          wikipedia.getCategoryMembers("All images with unknown copyright status"));

   :param a: a list of pages
   :param b: another list of pages
   :return: a \ b

revisionsToWikitext
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String revisionsToWikitext(Revision revisions)
   :outertype: Wiki

   Turns a list of revisions into human-readable wikitext. Be careful, as slowness may result when copying large amounts of wikitext produced by this method, or by the wiki trying to parse it. Takes the form of:

   *(diff link) 2009-01-01 00:00 User (talk | contribs) (edit summary)

   :param revisions: a list of revisions
   :return: those revisions as wikitext

rollback
^^^^^^^^

.. java:method:: public void rollback(Revision revision) throws IOException, LoginException
   :outertype: Wiki

   Reverts a series of edits on the same page by the same user quickly provided that they are the most recent revisions on that page. If this is not the case, then this method does nothing. See [[mw:Manual:Parameters to index.php#Actions]] (look under rollback) for more information. The edit and reverted edits will be marked as bot if \ ``isMarkBot() == true``\ .

   :param revision: the revision to revert. \ ``revision.isTop()``\  must be true for the rollback to succeed

rollback
^^^^^^^^

.. java:method:: public synchronized void rollback(Revision revision, boolean bot, String reason) throws IOException, LoginException
   :outertype: Wiki

   Reverts a series of edits on the same page by the same user quickly provided that they are the most recent revisions on that page. If this is not the case, then this method does nothing. See [[mw:Manual:Parameters to index.php#Actions]] (look under rollback) for more information.

   :param revision: the revision to revert. \ ``revision.isTop()``\  must be true for the rollback to succeed
   :param bot: whether to mark this edit and the reverted revisions as bot edits (ignored if we cannot do this)
   :param reason: (optional) a reason for the rollback. Use "" for the default ([[MediaWiki:Revertpage]]).

search
^^^^^^

.. java:method:: public String search(String search, int... namespaces) throws IOException
   :outertype: Wiki

   Performs a full text search of the wiki. Equivalent to [[Special:Search]], or that little textbox in the sidebar. Returns an array of search results, where:

   .. parsed-literal::

      results[0] == page name
      results[1] == parsed section name (may be "")
      results[2] == snippet of page text

   :param search: a search string
   :param namespaces: the namespaces to search. If no parameters are passed then the default is MAIN_NAMESPACE only.
   :return: the search results

setAssertionMode
^^^^^^^^^^^^^^^^

.. java:method:: public void setAssertionMode(int mode)
   :outertype: Wiki

   Sets the assertion mode. See [[mw:Extension:Assert Edit]] for what this functionality this mimics. Assertion modes are bitmasks. Default is \ ``ASSERT_NONE``\ .

   :param mode: an assertion mode

setCookies
^^^^^^^^^^

.. java:method:: protected void setCookies(URLConnection u)
   :outertype: Wiki

   Sets cookies to an unconnected URLConnection and enables gzip compression of returned text.

   :param u: an unconnected URLConnection

setLogLevel
^^^^^^^^^^^

.. java:method:: @Deprecated public void setLogLevel(Level level)
   :outertype: Wiki

   Change the logging level of this object's Logger object.

   :param level: the new logging level

setMarkBot
^^^^^^^^^^

.. java:method:: public void setMarkBot(boolean markbot)
   :outertype: Wiki

   Sets whether edits are marked as bot by default (may be overridden specifically by edit()). Default = false. Works only if one has the required permissions.

   :param markbot: (see above)

setMarkMinor
^^^^^^^^^^^^

.. java:method:: public void setMarkMinor(boolean minor)
   :outertype: Wiki

   Sets whether edits are marked as minor by default (may be overridden specifically by edit()). Default = false.

   :param minor: (see above)

setMaxLag
^^^^^^^^^

.. java:method:: public void setMaxLag(int lag)
   :outertype: Wiki

   Sets the maxlag parameter. A value of less than 0s disables this mechanism. Default is 5s.

   :param lag: the desired maxlag in seconds

setResolveRedirects
^^^^^^^^^^^^^^^^^^^

.. java:method:: public void setResolveRedirects(boolean b)
   :outertype: Wiki

   Sets whether API action=query dependencies automatically resolve redirects (default = false).

   :param b: (see above)

setStatusCheckInterval
^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void setStatusCheckInterval(int interval)
   :outertype: Wiki

   Sets the number of actions (edit, move, block, delete, etc) between status checks. A status check is where we update user rights, block status and check for new messages (if the appropriate assertion mode is set). Default is 100.

   :param interval: the number of edits between status checks

setThrottle
^^^^^^^^^^^

.. java:method:: public void setThrottle(int throttle)
   :outertype: Wiki

   Sets the editing throttle. Read requests are not throttled or restricted in any way. Default is 10s.

   :param throttle: the new throttle value in milliseconds

setUserAgent
^^^^^^^^^^^^

.. java:method:: public void setUserAgent(String useragent)
   :outertype: Wiki

   Sets the user agent HTTP header to be used for requests. Default is "Wiki.java " + version.

   :param useragent: the new user agent

setUsingCompressedRequests
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. java:method:: public void setUsingCompressedRequests(boolean zipped)
   :outertype: Wiki

   Enables/disables GZip compression for GET requests. Default: true.

   :param zipped: whether we use GZip compression

shortPages
^^^^^^^^^^

.. java:method:: public String shortPages(int cutoff) throws IOException
   :outertype: Wiki

   List pages below a certain size in the main namespace. Equivalent to [[Special:Shortpages]].

   :param cutoff: the maximum size in bytes these short pages can be
   :return: pages below that size

shortPages
^^^^^^^^^^

.. java:method:: public String shortPages(int cutoff, int namespace) throws IOException
   :outertype: Wiki

   List pages below a certain size in any namespace. Equivalent to [[Special:Shortpages]].

   :param cutoff: the maximum size in bytes these short pages can be
   :param namespace: a namespace
   :return: pages below that size in that namespace

statusCheck
^^^^^^^^^^^

.. java:method:: protected void statusCheck() throws IOException, CredentialException
   :outertype: Wiki

   Performs a status check, including assertions.

timestampToCalendar
^^^^^^^^^^^^^^^^^^^

.. java:method:: protected final Calendar timestampToCalendar(String timestamp)
   :outertype: Wiki

   Turns a timestamp of the format yyyymmddhhmmss into a Calendar object. Might be useful for subclasses.

   :param timestamp: the timestamp to convert
   :return: the converted Calendar

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: Wiki

   Returns a string representation of this Wiki.

   :return: a string representation of this Wiki.

undo
^^^^

.. java:method:: public synchronized void undo(Revision rev, Revision to, String reason, boolean minor, boolean bot) throws IOException, LoginException
   :outertype: Wiki

   Undoes revisions, equivalent to the "undo" button in the GUI page history. A quick explanation on how this might work - suppose the edit history was as follows:

   ..

   * (revid=541) 2009-01-13 00:01 92.45.43.227
   * (revid=325) 2008-12-10 11:34 Example user
   * (revid=314) 2008-12-10 10:15 127.0.0.1
   * (revid=236) 2008-08-08 08:00 Anonymous
   * (revid=200) 2008-07-31 16:46 EvilCabalMember

   Then:

   .. parsed-literal::

      wiki.undo(wiki.getRevision(314L), null, reason, false); // undo revision 314 only
      wiki.undo(wiki.getRevision(236L), wiki.getRevision(325L), reason, false); // undo revisions 236-325

   This will only work if revision 541 or any subsequent edits do not clash with the change resulting from the undo.

   :param rev: a revision to undo
   :param to: the most recent in a range of revisions to undo. Set to null to undo only one revision.
   :param reason: an edit summary (optional). Use "" to get the default [[MediaWiki:Undo-summary]].
   :param minor: whether this is a minor edit
   :param bot: whether this is a bot edit

unwatch
^^^^^^^

.. java:method:: public void unwatch(String title) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Removes a page from the watchlist. You need to be logged in to use this. (Does not do anything if the page is not watched).

   :param title: the page to remove from the watchlist.

upload
^^^^^^

.. java:method:: public synchronized void upload(File file, String filename, String contents, String reason) throws IOException, LoginException
   :outertype: Wiki

   Uploads an image. Equivalent to [[Special:Upload]]. Supported extensions are (case-insensitive) "png", "jpg", "gif" and "svg". You need to be logged on to do this. Automatically breaks uploads into 2^\ ``LOG2_CHUNK_SIZE``\  byte size chunks. This method is thread safe and subject to the throttle.

   :param file: the image file
   :param filename: the target file name (Example.png, not File:Example.png)
   :param contents: the contents of the image description page, set to "" if overwriting an existing file
   :param reason: an upload summary (defaults to \ ``contents``\ , use "" to not specify one)

userExists
^^^^^^^^^^

.. java:method:: public boolean userExists(String username) throws IOException
   :outertype: Wiki

   Determines whether a specific user exists. Should evaluate to false for anons.

   :param username: a username
   :return: whether the user exists

version
^^^^^^^

.. java:method:: public String version() throws IOException
   :outertype: Wiki

   Gets the version of MediaWiki this wiki runs e.g. 1.20wmf5 (54b4fcb). See also http://gerrit.wikimedia.org/ .

   :return: the version of MediaWiki used

watch
^^^^^

.. java:method:: public void watch(String title) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Adds a page to the watchlist. You need to be logged in to use this.

   :param title: the page to add to the watchlist

watchInternal
^^^^^^^^^^^^^

.. java:method:: protected void watchInternal(String title, boolean unwatch) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Internal method for interfacing with the watchlist, since the API URLs for (un)watching are very similar.

   :param title: the title to (un)watch
   :param unwatch: whether we should unwatch this page

watchlist
^^^^^^^^^

.. java:method:: public Revision watchlist() throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Fetches the most recent changes to pages on your watchlist. Data is retrieved from the \ ``recentchanges``\  table and hence cannot be older than about a month.

   :return: list of changes to watched pages and their talk pages

watchlist
^^^^^^^^^

.. java:method:: public Revision watchlist(boolean allrev, int... ns) throws IOException, CredentialNotFoundException
   :outertype: Wiki

   Fetches recent changes to pages on your watchlist. Data is retrieved from the \ ``recentchanges``\  table and hence cannot be older than about a month.

   :param allrev: show all revisions to the pages, instead of the top most change
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: list of changes to watched pages and their talk pages

whatLinksHere
^^^^^^^^^^^^^

.. java:method:: public String whatLinksHere(String title, int... ns) throws IOException
   :outertype: Wiki

   Returns a list of all pages linking to this page. Equivalent to [[Special:Whatlinkshere]].

   :param title: the title of the page
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the list of pages linking to the specified page

whatLinksHere
^^^^^^^^^^^^^

.. java:method:: public String whatLinksHere(String title, boolean redirects, int... ns) throws IOException
   :outertype: Wiki

   Returns a list of all pages linking to this page within the specified namespaces. Alternatively, we can retrive a list of what redirects to a page by setting \ ``redirects``\  to true. Equivalent to [[Special:Whatlinkshere]].

   :param title: the title of the page
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :param redirects: whether we should limit to redirects only
   :return: the list of pages linking to the specified page

whatTranscludesHere
^^^^^^^^^^^^^^^^^^^

.. java:method:: public String whatTranscludesHere(String title, int... ns) throws IOException
   :outertype: Wiki

   Returns a list of all pages transcluding to a page within the specified namespaces.

   :param title: the title of the page, e.g. "Template:Stub"
   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: the list of pages transcluding the specified page

