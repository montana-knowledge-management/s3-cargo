
# Project structure

Multiple projects can be located under 1 bucket. This is useful when multiple
projects are related to each other. A project has the following structure:
``` shell
.
└── example_project
    ├── home
    │   ├── dev_1
    │   ├── dev_2
    │   └── dev_3
    ├── input
    ├── project_results
    └── shared
```
On top, there is the project root `example_project` this also the project ID
that needs to be specified in the configuration file. Next, the `input`
directory holds every data/file/resource that needs to be used during the
project. This is a "read-only" directory which means, **assuming normal use**, there
is no way that you write this directory from your code.
The `home` directory contains your personal workspace. The selection is based on
the `user` option in the configuration file. This is done automatically, no need
to specify it. Normally, you can only see your home directory and not others. If
you want to share files with others you can put them under the `shared`
directory.
The `project_results` folder, as the name suggests, contains the end results of
the project, that is going to be deployed to clients.
