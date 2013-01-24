Simple Python scripts to tell how many font files and families 
were published in Google Web Fonts, by analysing revisions of 
the googlefontdirectory Mercurial repository.

Usage
----------

    GWF_REPO="/home/user/googlefontdirectory" python files-per-checkin.py;

This will output a file gwf_files.csv in the current working directory
similar to:

    date,files
    2010-05-26 16:03,63
    2010-06-04 17:54,63
    2010-06-07 15:02,63
    2010-06-23 16:12,63
    2010-08-04 11:10,63
    2010-08-06 11:15,65
    2010-08-24 14:49,65
    2010-09-18 10:49,73
    2010-09-08 15:50,67
    2010-09-18 10:51,76
    ...

Dependencies
--------------

[hglib](http://mercurial.selenic.com/wiki/PythonHglib) is required. 

To install it:

    cd ~/src/;
    hg clone http://selenic.com/repo/python-hglib;
    cd python-hglib;
    sudo python setup.py install;
    python -c 'import hglib';

The final command should cause no error if it installed successfully.