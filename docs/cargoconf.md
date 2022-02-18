# Configuration file

The configuration file is a simple `yaml` file that can have any name. In this
file you describe the environment you want to see in a declarative way and let
Cargo figure out how to make it happen.

The configuration file does not handle s3 service credentials for obvious
reasons. The keys should be placed in the `~/.aws/credentials` file.
Example `credentials` file:
``` txt
[default]
aws_access_key_id=EXAMPLE_PUBLIC_KEY
aws_secret_access_key=EXAMPLE_PRIVATE_KEY
```

Environment variables can and should be used to not leak anything sensitive into
the version control repository. Use environment variables with caution and only
from trusted sources.

The configuration file consists of 3 sections: `options`, `resources`,
`futures`. `options` is a required section, the other 2 can be omitted based on
the use case.


## Options

### projectid

The project identifier in case there are multiple projects in 1 bucket.

Example:

``` yaml
options:
   projectid: example_project_1
```

### destination

The location of the local working directory relative to the configuration
file. Can be nested. If the directory doesn't exist then it will be created.
The remote files will be synchronized into this location.

!!! note

    If the `destination` is located in a git repository, then it is preferable if
    you add it to your `.gitignore`.

Example:

``` yaml
options:
   destination: resources
```
```yaml
options:
   destination: nested/path/to/workdir
```

### url

The endpoint url of the s3 storage service.

Example:

``` yaml
options:
   url: https://s3.wasabisys.com
```

### bucket

The name of the bucket that contains your projects.

Example:

``` yaml
options:
   bucket: my-projects
```

### user

The name of the current user. Automatically set.

value: `USER` or `USERNAME` environment variable.


### cleanup_workdir


If true, the `destination` directory will be deleted at the beginning
of the session. Default value is `False`.

Example:

``` yaml
options:
   cleanup_workdir: True
```

## Resources

### selector

Select a file from the remote resouce or use wildcard selection to select
multiple files. The files can be selected only from the **input**,
**shared**, **home** directories. No exception will be raised if the pattern
is incorrect or the selected files don't exist.

!!! note

    * When you write selectors you should not include the `projectid` in the path.
    * You don't have to specify the user in the home directory because it will
      be resolved automatically. See examples.

Examples:

* Select file1.txt from the input directory:
   ```yaml
   resources:
      - input/file1.txt
   ```

* Select all txt files from your remote home directory.

   ```yaml
   resources:
      - home/*.txt
   ```

* Select a nested file from shared:
   ``` yaml
   resources:
      - shared/nested/directory/image_01.png
   ```

### mode

Set the selected items mode to either `persistent` or `transient`. Default value
is `persistent`.

`persistent`
   In this mode, successive sessions will not overwrite or download again the
   files if they are already present under :attr:`destination`.

`transient`
   In this mode, successive sessions will download and overwrite the selected
   files. It doesn't matter if the files are present or not.


Examples:

Select all textfile from input in transient mode because a textprocessing
pipeline needs to be tested:

``` yaml
resources:
   - home/*.txt:
         mode: transient
```


### bind

Create a subdirectory under :attr:`destination` and place the selected files
under it.

Examples:

``` yaml
options:
   destination: workdir

resources:
- input/july/vacation_1.mp4:
      bind: vacation/videos
```

The result will be: `workdir/vacation/videos/input/july/vacation_1.mp4` under the local
working directory. See `unravel` to get rid of the path before the
remote file.


### unpack

If the selected file(s) is an archive then you can uncompress it with this
option. Supported file formats: `zip, tar.bz2`. Default value is `False`.

!!! note

    If `True`, the file will be downloaded regardless of the `mode` option and
    the contents of the archive will overwrite any existing file in the local
    worworking directory.



### unravel

Download the selected remote files without their preceding path. If the
`bind` option is not set, then the files will be placed under the
root of the local working directory. Default value is `False`.


Examples:

* without `bind`:
   ``` yaml
   options:
      destination: workdir
   resources:
   - input/july/vacation_1.mp4:
         unravel: true
   ```
   Result: `workdir/vacation_1.mp4`

* with `bind`:

   ``` yaml
   options:
      destination: workdir

   resources:
      - input/july/vacation_1.mp4:
         unravel: true
         bind: vacationvideos
   ```

   Result: `workdir/vacationvideos/vacation_1.mp4`


## Futures

### name
Handling the name is dependent on the `compress` option. If `compress` is not
set, then the `name` will be handled as a directory name, otherwise `name` will
be the resulting archives name.

Examples:

* A text processing result is located here
  `workdir/processed/transformed_file.txt`. This file needs to be uploaded into
  the bucket and shared with others. Under the shared directory there is a
  `training_data` folder where the preprocessed files need to be collected.
  ``` yaml
  options:
    destination: workdir
  futures:
    - name: training_data
        selector:
          - processed/transformed_file.txt
        emit:
          - shared
  ```
  Result in the bucket: `<projectid>/shared/training_data/transformed_file.txt`.


### compress
Compress can be set to either `zip` or `bz2`. The selected files will be
compressed into the specified format __without their path__.

Examples:

Select all text files from the local `workdir/processed/` directory and compress them into
`bz2` format then place the result into the `shared` remote folder.

``` yaml
options:
   destination: workdir
futures:
   - name: compressed_training_data
      compress: 'bz2'
      selector:
         - processed/*.txt
      emit:
         - shared
```
Result in the bucket: `<projectid>/shared/compressed_training_data.tar.bz2`


### selector
A list of [glob](https://en.wikipedia.org/wiki/Glob_(programming)) patterns
selecting files from the local working directory.

Example:

``` yaml
options:
   destination: workdir

futures:
   - name: training_data
      selector:
         - processed/uppercased/f-*.txt
         - processed/uppercased/e-*.txt
         - processed/uppercased/a-*.txt
      emit:
         - shared
```
Result in the bucket:
``` shell
<projectid>/shared/training_data/f-01.txt
<projectid>/shared/training_data/f-02.txt
<projectid>/shared/training_data/f-03.txt
<projectid>/shared/training_data/e-13.txt
<projectid>/shared/training_data/e-45.txt
<projectid>/shared/training_data/a-00.txt
```

### emit
A list of remote location where the selected files will be uploaded. Can be
nested. It must start with either `shared`, `project_results` or `home`. In any
other case the files will be placed under `home/<user>/<emit_path>`.

Example:

Upload a video file into multiple location:
``` yaml
options:
   destination: workdir

futures:
   - name: videos
       selector:
         - processed/shaded/video_snippet_1.mp4
       emit:
         - shared
         - home/shaded
```
Result in the bucket:
```shell
<projectid>/shared/videos/video_snippet_1.mp4
<projectid>/home/<user>/shaded/video_snippet_1.mp4
```
