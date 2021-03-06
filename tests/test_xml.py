from vprgen._xml import XMLGenerator

try:
    from io import BytesIO as StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

def test_basic():
    stream = StringIO()
    with XMLGenerator(stream) as xg:
        with xg.element("root"):
            xg.element_leaf("element", {"key": "value"}, "plain text")
    assert stream.getvalue() == b'<root><element key="value">plain text</element></root>'
