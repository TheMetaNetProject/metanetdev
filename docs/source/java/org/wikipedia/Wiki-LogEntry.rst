.. java:import:: java.util.zip GZIPInputStream

Wiki.LogEntry
=============

.. java:package:: org.wikipedia
   :noindex:

.. java:type:: public class LogEntry implements Comparable<LogEntry>
   :outertype: Wiki

   A wrapper class for an entry in a wiki log, which represents an action performed on the wiki.

Constructors
------------
LogEntry
^^^^^^^^

.. java:constructor:: protected LogEntry(String type, String action, String reason, User user, String target, String timestamp, Object details)
   :outertype: Wiki.LogEntry

   Creates a new log entry. WARNING: does not perform the action implied. Use Wiki.class methods to achieve this.

   :param type: the type of log entry, one of USER_CREATION_LOG, DELETION_LOG, BLOCK_LOG, etc.
   :param action: the type of action that was performed e.g. "delete", "unblock", "overwrite", etc.
   :param reason: why the action was performed
   :param user: the user who performed the action
   :param target: the target of the action
   :param timestamp: the local time when the action was performed. We will convert this back into a Calendar.
   :param details: the details of the action (e.g. the new title of the page after a move was performed).

Methods
-------
compareTo
^^^^^^^^^

.. java:method:: public int compareTo(Wiki.LogEntry other)
   :outertype: Wiki.LogEntry

   Compares this log entry to another one based on the recentness of their timestamps.

   :param other: the log entry to compare
   :return: whether this object is equal to

getAction
^^^^^^^^^

.. java:method:: public String getAction()
   :outertype: Wiki.LogEntry

   Gets a string description of the action performed, for example "delete", "protect", "overwrite", ... WARNING: returns null if the action was RevisionDeleted.

   :return: the type of action performed

getDetails
^^^^^^^^^^

.. java:method:: public Object getDetails()
   :outertype: Wiki.LogEntry

   Gets the details of this log entry. Return values are as follows:

   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | Log type                  | Return value                                                                                                                         |
   +===========================+======================================================================================================================================+
   | MOVE_LOG                  | The new page title                                                                                                                   |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | USER_RENAME_LOG           | The new username                                                                                                                     |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | BLOCK_LOG                 | new Object[] { boolean anononly, boolean nocreate, boolean noautoblock, boolean noemail, boolean nousertalk, String duration }       |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | USER_RIGHTS_LOG           | The new user rights (String[])                                                                                                       |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | PROTECTION_LOG            | action == "protect" or "modify" => the protection level (int, -2 if unrecognized), action == "move_prot" => the old title, else null |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+
   | Others or RevisionDeleted | null                                                                                                                                 |
   +---------------------------+--------------------------------------------------------------------------------------------------------------------------------------+

   Note that the duration of a block may be given as a period of time (e.g. "31 hours") or a timestamp (e.g. 20071216160302). To tell these apart, feed it into \ ``Long.parseLong()``\  and catch any resulting exceptions.

   :return: the details of the log entry

getReason
^^^^^^^^^

.. java:method:: public String getReason()
   :outertype: Wiki.LogEntry

   Gets the reason supplied by the perfoming user when the action was performed. WARNING: returns null if the reason was RevisionDeleted.

   :return: the reason the action was performed

getTarget
^^^^^^^^^

.. java:method:: public String getTarget()
   :outertype: Wiki.LogEntry

   Gets the target of the action represented by this log entry. WARNING: returns null if the content was RevisionDeleted.

   :return: the target of this log entry

getTimestamp
^^^^^^^^^^^^

.. java:method:: public Calendar getTimestamp()
   :outertype: Wiki.LogEntry

   Gets the timestamp of this log entry.

   :return: the timestamp of this log entry

getType
^^^^^^^

.. java:method:: public String getType()
   :outertype: Wiki.LogEntry

   Gets the type of log that this entry is in.

   :return: one of DELETION_LOG, USER_CREATION_LOG, BLOCK_LOG, etc.

getUser
^^^^^^^

.. java:method:: public User getUser()
   :outertype: Wiki.LogEntry

   Gets the user object representing who performed the action. WARNING: returns null if the user was RevisionDeleted.

   :return: the user who performed the action.

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: Wiki.LogEntry

   Returns a string representation of this log entry.

   :return: a string representation of this object

