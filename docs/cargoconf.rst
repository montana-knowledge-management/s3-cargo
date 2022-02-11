******************
Configuration file
******************

=======
Options
=======

.. py:attribute:: projectid
   
   The project identifier in case there are multiple projects in 1 bucket.

   :type: str

   Example:

   .. code-block:: yaml

      options:
         projectid: example_project_1


.. py:attribute:: destination

   The location of the local working directory relative to the configuration
   file. Can be nested. If the directory doesn't exist then it will be created.
   The remote files will be synchronized into this location.

   :type: str

   Example:

   .. code-block:: yaml

      options:
         destination: resources

   .. code-block:: yaml

      options:
         destination: nested/path/to/workdir

.. py:attribute:: url

   The endpoint url of the s3 storage service.

   :type: str

   Example:

   .. code-block:: yaml

      options:
         url: https://s3.wasabisys.com


.. py:attribute:: bucket

   The name of the bucket that contains your projects.

   :type: str

   Example:

   .. code-block:: yaml

      options:
         bucket: my-projects
         

.. py:attribute:: user

   The name of the current user. Automatically set.

   :type: str
   :value: USER or USERNAME environment variable.


.. py:attribute:: cleanup_workdir

   :type: bool
   :value: False

   If true, the :attr:`destination` directory will be deleted at the beginning
   of the session.

   Example:

   .. code-block:: yaml

      options:
         cleanup_workdir: True


=========
Resources
=========

.. py:attribute:: selector

   Select a file from the remote resouce or use wildcard selection to select
   multiple files. The files can be selected only from the **input**,
   **shared**, **home** directories. No exception will be raised if the pattern
   is incorrect or the selected files don't exist.

   :type: str

   Examples:

   * Select file1.txt from the input directory:
   
      .. code-block:: yaml

         resources:
            - input/file1.txt

   * Select all txt files from your remote home directory. **Note**: You don't
     have to specify the user in the home directory because it will be resolved
     automatically.
     
      .. code-block:: yaml

         resources:
            - home/*.txt

   * Select a nested file from shared:

      .. code-block:: yaml

         resources:
            - shared/nested/directory/image_01.png



.. py:attribute:: mode

   Set the selected items mode to either `persistent` or `transient`.

   `persistent`
      In this mode, successive sessions will not overwrite or download again the
      files if they are already present under :attr:`destination`.

   `transient`
      In this mode, successive sessions will download and overwrite the selected
      files. It doesn't matter if the files are present or not.

   :type: str
   :value: "persistent"

   Examples:

   Select all textfile from input in transient mode because a textprocessing
   pipeline needs to be tested:

   .. code-block:: yaml

      resources:
         - home/*.txt:
               mode: transient

.. py:attribute:: bind

   Create a subdirectory under :attr:`destination` and place the selected files
   under it.

   :type: str

   Examples:

   .. code-block:: yaml

      options:
        destination: workdir

      resources:
      - input/july/vacation_1.mp4:
            bind: vacation/videos

   The result will be: :code:`workdir/vacation/videos/input/july/vacation_1.mp4` under the local
   working directory. See :attr:`unravel` to get rid of the path before the
   remote file.


.. py:attribute:: unpack

   If the selected file(s) is an archive then you can uncompress it with this
   option. Supported file formats: :code:`zip, tar.bz2`.

   :type: bool
   :value: False

.. py:attribute:: unravel

   Download the selected remote files without their preceding path. If the
   :attr:`bind` option is not set, then the files will be placed under the
   root of the local working directory.

   :type: bool
   :value: False

   Examples:

   * withour :attr:`bind`:

      .. code-block:: yaml

         options:
            destination: workdir
         resources:
         - input/july/vacation_1.mp4:
               unravel: true

      Result: :code:`workdir/vacation_1.mp4`

   * with :attr:`bind`:

      .. code-block:: yaml

         options:
            destination: workdir

         resources:
            - input/july/vacation_1.mp4:
               unravel: true
               bind: vacationvideos

      Result: :code:`workdir/vacationvideos/vacation_1.mp4`


.. =======
.. Futures
.. =======


.. .. py:attribute:: name

.. .. py:attribute:: compress

.. .. py:attribute:: selector

.. .. py:attribute:: emit
