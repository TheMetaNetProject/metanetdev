.. java:import:: java.util.zip GZIPInputStream

Wiki.User
=========

.. java:package:: org.wikipedia
   :noindex:

.. java:type:: public class User implements Cloneable
   :outertype: Wiki

   Subclass for wiki users.

Constructors
------------
User
^^^^

.. java:constructor:: protected User(String username)
   :outertype: Wiki.User

   Creates a new user object. Does not create a new user on the wiki (we don't implement this for a very good reason). Shouldn't be called for anons.

   :param username: the username of the user

Methods
-------
blockLog
^^^^^^^^

.. java:method:: public LogEntry blockLog() throws IOException
   :outertype: Wiki.User

   Returns a log of the times when the user has been blocked.

   :return: records of the occasions when this user has been blocked

clone
^^^^^

.. java:method:: @Override public User clone()
   :outertype: Wiki.User

   Copies this user object.

   :return: the copy

contribs
^^^^^^^^

.. java:method:: public Revision contribs(int... ns) throws IOException
   :outertype: Wiki.User

   Fetches the contributions for this user in a particular namespace(s).

   :param ns: a list of namespaces to filter by, empty = all namespaces.
   :return: a revision array of contributions

countEdits
^^^^^^^^^^

.. java:method:: public int countEdits() throws IOException
   :outertype: Wiki.User

   Fetches the internal edit count for this user, which includes all live edits and deleted edits after (I think) January 2007. If you want to count live edits only, use the slower \ ``int count = user.contribs().length;``\ .

   :return: the user's edit count

equals
^^^^^^

.. java:method:: @Override public boolean equals(Object x)
   :outertype: Wiki.User

   Tests whether this user is equal to another one.

   :return: whether the users are equal

getUserInfo
^^^^^^^^^^^

.. java:method:: public HashMap<String, Object> getUserInfo() throws IOException
   :outertype: Wiki.User

   Gets various properties of this user. Groups and rights are cached for the current logged in user. Returns:

   .. parsed-literal::

      {
          "editcount" => 150000,                                // the user's edit count (int)
          "groups"    => { "users", "autoconfirmed", "sysop" }, // the groups the user is in (String[])
          "rights"    => { "edit", "read", "block", "email"},   // the stuff the user can do (String[])
          "emailable" => true,                                  // whether the user can be emailed through
                                                                // [[Special:Emailuser]] or emailUser() (boolean)
          "blocked"   => false,                                 // whether the user is blocked (boolean)
          "gender"    => Gender.MALE                            // the user's gender (Gender)
      }

   :return: (see above)

getUsername
^^^^^^^^^^^

.. java:method:: public String getUsername()
   :outertype: Wiki.User

   Gets this user's username.

   :return: this user's username

hashCode
^^^^^^^^

.. java:method:: @Override public int hashCode()
   :outertype: Wiki.User

   Returns a hashcode of this user.

   :return: see above

isA
^^^

.. java:method:: public boolean isA(String group) throws IOException
   :outertype: Wiki.User

   Returns true if the user is a member of the specified group. Uses the groups cache.

   :param group: a specific group
   :return: whether the user is in it

isAllowedTo
^^^^^^^^^^^

.. java:method:: public boolean isAllowedTo(String right) throws IOException
   :outertype: Wiki.User

   Returns true if the user is allowed to perform the specified action. Uses the rights cache. Read [[Special:Listgrouprights]] before using this!

   :param right: a specific action
   :return: whether the user is allowed to execute it

isBlocked
^^^^^^^^^

.. java:method:: public boolean isBlocked() throws IOException
   :outertype: Wiki.User

   Determines whether this user is blocked by looking it up on the IP block list.

   :return: whether this user is blocked

toString
^^^^^^^^

.. java:method:: @Override public String toString()
   :outertype: Wiki.User

   Returns a string representation of this user.

   :return: see above

