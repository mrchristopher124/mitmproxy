import cStringIO, time
import libpry
from libmproxy import proxy, controller, utils, dump, flow


class u_read_chunked(libpry.AutoTree):
    def test_all(self):
        s = cStringIO.StringIO("1\r\na\r\n0\r\n")
        libpry.raises(IOError, proxy.read_chunked, s, None)

        s = cStringIO.StringIO("1\r\na\r\n0\r\n\r\n")
        assert proxy.read_chunked(s, None) == "a"

        s = cStringIO.StringIO("\r\n")
        libpry.raises(IOError, proxy.read_chunked, s, None)

        s = cStringIO.StringIO("1\r\nfoo")
        libpry.raises(IOError, proxy.read_chunked, s, None)

        s = cStringIO.StringIO("foo\r\nfoo")
        libpry.raises(proxy.ProxyError, proxy.read_chunked, s, None)


class Dummy: pass

class u_read_http_body(libpry.AutoTree):
    def test_all(self):

        d = Dummy()
        h = flow.Headers()
        s = cStringIO.StringIO("testing")
        assert proxy.read_http_body(s, d, h, False, None) == ""

        h["content-length"] = ["foo"]
        s = cStringIO.StringIO("testing")
        libpry.raises(proxy.ProxyError, proxy.read_http_body, s, d, h, False, None)

        h["content-length"] = [5]
        s = cStringIO.StringIO("testing")
        assert len(proxy.read_http_body(s, d, h, False, None)) == 5
        s = cStringIO.StringIO("testing")
        libpry.raises(proxy.ProxyError, proxy.read_http_body, s, d, h, False, 4)


        h = flow.Headers()
        s = cStringIO.StringIO("testing")
        assert len(proxy.read_http_body(s, d, h, True, 4)) == 4
        s = cStringIO.StringIO("testing")
        assert len(proxy.read_http_body(s, d, h, True, 100)) == 7


class u_parse_request_line(libpry.AutoTree):
    def test_simple(self):
        libpry.raises(proxy.ProxyError, proxy.parse_request_line, "")

        u = "GET ... HTTP/1.1"
        libpry.raises("invalid url", proxy.parse_request_line, u)

        u = "GET http://foo.com:8888/test HTTP/1.1"
        m, s, h, po, pa, minor = proxy.parse_request_line(u)
        assert m == "GET"
        assert s == "http"
        assert h == "foo.com"
        assert po == 8888
        assert pa == "/test"
        assert minor == 1

    def test_connect(self):
        u = "CONNECT host.com:443 HTTP/1.0"
        expected = ('CONNECT', None, 'host.com', 443, None, 0)
        ret = proxy.parse_request_line(u)
        assert expected == ret

    def test_inner(self):
        u = "GET / HTTP/1.1"
        assert proxy.parse_request_line(u) == ('GET', None, None, None, '/', 1)


class uFileLike(libpry.AutoTree):
    def test_wrap(self):
        s = cStringIO.StringIO("foobar\nfoobar")
        s = proxy.FileLike(s)
        s.flush()
        assert s.readline() == "foobar\n"
        assert s.readline() == "foobar"
        # Test __getattr__
        assert s.isatty



class uProxyError(libpry.AutoTree):
    def test_simple(self):
        p = proxy.ProxyError(111, "msg")
        assert repr(p)


tests = [
    uProxyError(),
    uFileLike(),
    u_parse_request_line(),
    u_read_chunked(),
    u_read_http_body(),
]
