# Black-Doc
Formats the target Python repository with black, and add a generated docstring template to every function and every class 
in every Python file (or in the specified file) in the repository, if absent, following the Sphinx standard.

# To install

To install the repository you just need to clone in on your computer 
    
        git clone https://github.com/drasgo/Black-Doc.git
        cd Black-Doc
        python3 -m pip install -r requirements.txt --user

then either create your own wheel package and install it

        cd Black-Doc
        python3 setup.py bdist_wheel
        cd dist
        python3 -m pip install created_package --user

where `created_package` is the wheel package just generated.

Or install the pre-packaged version you can find in the `releases` folder
    
        cd Black-Doc/releases
        python3 -m pip install release_with_highest_version --user

where `release_with_highest_version` is the wheel package with the highest version among the ones present.

# To use

To use the `Black-Doc` library in its easiest form, you just need to go in the folder of the project you want to 
format and generate docstrings, and execute

        blackdoc --repo

This command "refactors" every file in the current folder, and recursively every Python file in every subfolder.

Moreover, there are some possible arguments that can be passed when executing blackdoc:

        optional arguments:
          -h, --help            show this help message and exit
          -r, --repo            If specified, the current folder is going to be
                                recursively black-ed and docstring-ed.
          -f FILE, --file FILE  If a single file is specified, then the 'black & doc'
                                process is executed only on the specified (Python)
                                file.
          --no_backup           If specified, it does not create a backup folder of
                                the current directory called 'blackdoc_backup' (NOTE:
                                if the backup is created and 'blackdoc_backup' already
                                exists, it overwrites it).
          --no_black            If specified, does not perform the black operations,
                                and only generates the docstring templates.
          --use_nlp             If specified, it will use NLP-based tools (e.g. text
                                segmentation) for describing the code elements in the
                                docstrings. (Experimental. Increases startup time and
                                overall processing time).
          -w WORKERS, --workers WORKERS
                                Number of workers that document the files in the
                                repository in parallel (Default=3).
        
        NOTE: Either -r/--repo or -f FILE/--file FILE need to be provided.


NOTE: Either -r/--repo or -f FILE/--file FILE need to be provided.


Finally, a configuration file with the name `blackdoc_configuration.toml` can be added in the current
folder, to specify the blacklist collection of the folders (i.e. the folders that should not be touched by Black-Doc)
and the whitelist collection of the folders (if the whitelist is EMPTY, every folder not part of the blacklist will be 
processed, if it is NOT EMPTY, then only the files in the folders in the whitelist are going to be "black-ed" and 
"docstring-ed").

An example of `blackdoc_configuration.toml` file can be found in the folder `examples`.