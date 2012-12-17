=============
fix-svn-props
=============

I'm sure it must have been a good idea to allow .jpg to register as
text. It's probably not what *you* need though. It might happen that
you inherit a svn repository with bad associations and properties. If
you do, I hope that this script helps you get back to sanity.

*Note*: This was written with posix-systems in mind, I'm guessing it
won't play nicely on Windows.

Use
---

To assess the svn tree in your current directory:

::

    > python fix-svn-props.py --mime --eol --test .

``--mime``
    fixes mime-types

``--eol``
    normalizes eol settings

``--test``
    turns the command into a no-op, displaying what the script would have done

I *strongly* recommend running the ``--test`` flag on your initial
run.

File associations
-----------------

Hardcoded! This is pretty clumsy. If I get enough interest, I'll
separate out these hardcoded values into something a little more
configurable.

::

    MIME = {
      '.bash': 'text/plain',
      '.css': 'text/css',
      '.gif': 'image/gif',
      '.htm': 'text/html',
      '.html': 'text/html',
      '.java': 'text/plain',
      '.jj': 'text/plain',
      '.jpeg': 'image/jpeg',
      '.jpg': 'image/jpg',
      '.js': 'text/js',
      '.pl': 'text/plain',
      '.pm': 'text/plain',
      '.png': 'image/png',
      '.properties': 'text/plain',
      '.py': 'text/plain',
      '.rb': 'text/plain',
      '.sh': 'text/plain',
      '.sql': 'text/plain',
      '.txt': 'text/plain',
      '.wsdd': 'text/xml',
      '.wsdl': 'text/xml',
      '.xml': 'text/xml',
      '.xsd': 'text/xml',
      '.xsl': 'text/xml'
    }	    
    EOL = {
      '.css': 'native',
      '.html': 'native',
      '.java': 'native',
      '.jj': 'native',
      '.js': 'native',
      '.pl': 'native',
      '.pm': 'native',
      '.properties': 'native',
      '.py': 'native',
      '.rb': 'native',
      '.sh': 'native',
      '.sql': 'native',
      '.txt': 'native',
      '.wsdl': 'native',
      '.xml': 'native',
      '.xsd': 'native',
      '.xsl': 'native'
    }
				
