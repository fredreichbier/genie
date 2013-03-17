import os.path

def normpath(filename):
    """
        Return a normalized, absolute filename.

        On case-insensitive systems, this also converts the
        filename to lowercase.
    """
    return os.path.normcase(os.path.abspath(filename))

class Cabinet(object):
    """
        Just a helper class taking care of your files. It can close them
        if you wish.
    """
    def __init__(self):
        self._files = {}

    def get_file(self, filename):
        """
            Return a file object. Load the file if necessary.
        """
        filename = normpath(filename)
        if filename not in self._files:
            self._load_file(filename)
        return self._files[filename]

    def _load_file(self, filename):
        """
            Load a file in my cabinet. The filename is already normalized.
        """
        self._files[filename] = open(filename, 'rb')

    def close_files(self):
        """
            Close all open files. NOW.
        """
        while self._files:
            self.close_file(self._files.keys()[0])

    def close_file(self, filename):
        """
            Close a certain file.
        """
        filename = normpath(filename)
        self._files.pop(filename).close()

