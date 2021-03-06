from future.builtins import object
from future.utils import iteritems

from lxml.etree import xmlfile

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

# ----------------------------------------------------------------------------
# -- Stream-based XML Generator ----------------------------------------------
# ----------------------------------------------------------------------------
class XMLGenerator(object):
    """A XML Generator based on lxml.etree.

    Args:
        f (file-like object): the output stream
        pretty (:obj:`bool`): if the output XML should be nicely broken into multiple lines and indented
        skip_stringify (:obj:`bool`): assumes the dict passed into `element` and `element_leaf` are already converted
            to string objects
    """
    def __init__(self, f, pretty = False, skip_stringify = False):
        self.__f = f
        self.__pretty = pretty
        self.__skip_stringify = skip_stringify

    def __enter__(self):
        self.__context = xmlfile(self.__f, encoding='ascii')
        self._xf = self.__context.__enter__()
        self._depth = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.__context.__exit__(exc_type, exc_value, traceback)

    def _stringify(self, d):
        if self.__skip_stringify:
            return d
        else:
            return {k: '{:g}'.format(v) if isinstance(v, float) else str(v) for k, v in iteritems(d)} 

    def _indent(self):
        if self.__pretty and self._depth > 0:
            self._xf.write('\t' * self._depth)

    def _newline(self):
        if self.__pretty and self._depth > 0:
            self._xf.write('\n')

    class __XMLElementContextManager(object):
        """Context manager for an XML element."""
        def __init__(self, generator, tag, attrs):
            self.__gen = generator
            self.__tag = tag
            self.__attrs = attrs

        def __enter__(self):
            self.__gen._indent()
            self.__gen._depth += 1
            self.__context = self.__gen._xf.element(self.__tag, self.__attrs)
            ret = self.__context.__enter__()
            self.__gen._newline()
            return ret

        def __exit__(self, exc_type, exc_value, traceback):
            self.__gen._depth -= 1
            self.__gen._indent()
            ret = self.__context.__exit__(exc_type, exc_value, traceback)
            self.__gen._newline()
            return ret

    def element(self, tag, attrs = None):
        return self.__XMLElementContextManager(self, tag, self._stringify(attrs or {}))

    def element_leaf(self, tag, attrs = None, text = None):
        self._indent()
        with self._xf.element(tag, self._stringify(attrs or {})):
            if text:
                self._xf.write(text)
        self._newline()
