""" Provides some helper functions for test.
"""
import random
import tempfile
import os
import osmium

def _complete_object(o):
    """Takes a hash with an incomplete OSM object description and returns a
       complete one.
    """
    if o['type'] == 'C':
        ret = { 'created_at' : "2005-04-09T19:54:13Z",
                'num_changes' : 2, 'closed_at' : "2005-04-09T20:54:39Z",
                'open' : "false", 'min_lon' : -0.1465242,
                'min_lat' : 51.5288506, 'max_lon' : -0.1464925,
                'max_lat' : 51.5288620, 'user' : "Steve", 'uid' : "1",
                'tags' : None
        }
    else:
        ret = { 'version' : '1', 'timestamp': "2012-05-01T15:06:20Z",
                'changeset' : "11470653", 'uid' : "122294", 'user' : "foo",
                'tags' : {}
        }
    ret.update(o)
    if ret['type'] == 'N':
        if 'lat' not in ret:
            ret['lat'] = random.random()*180 - 90
        if 'lon' not in ret:
            ret['lon'] = random.random()*360 - 180
    return ret

def _write_osm_obj(fd, obj):
    if obj['type'] == 'N':
        fd.write(('<node id="%(id)d" lat="%(lat).8f" lon="%(lon).8f" version="%(version)s" timestamp="%(timestamp)s" changeset="%(changeset)s" uid="%(uid)s" user="%(user)s"'% obj).encode('utf-8'))
        if obj['tags'] is None:
            fd.write('/>\n'.encode('utf-8'))
        else:
            fd.write('>\n'.encode('utf-8'))
            for k,v in iter(obj['tags'].items()):
                fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
            fd.write('</node>\n'.encode('utf-8'))
    elif obj['type'] == 'W':
        fd.write(('<way id="%(id)d" version="%(version)s" changeset="%(changeset)s" timestamp="%(timestamp)s" user="%(user)s" uid="%(uid)s">\n' % obj).encode('utf-8'))
        for nd in obj['nodes']:
            fd.write(('<nd ref="%s" />\n' % (nd,)).encode('utf-8'))
        for k,v in iter(obj['tags'].items()):
            fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
        fd.write('</way>\n'.encode('utf-8'))
    elif obj['type'] == 'R':
        fd.write(('<relation id="%(id)d" version="%(version)s" changeset="%(changeset)s" timestamp="%(timestamp)s" user="%(user)s" uid="%(uid)s">\n' % obj).encode('utf-8'))
        for mem in obj['members']:
            fd.write(('  <member type="%s" ref="%s" role="%s"/>\n' % mem).encode('utf-8'))
        for k,v in iter(obj['tags'].items()):
            fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
        fd.write('</relation>\n'.encode('utf-8'))
    elif obj['type'] == 'C':
        fd.write(('<changeset id="%(id)d" created_at="%(created_at)s" num_changes="%(num_changes)d" closed_at="%(closed_at)s" open="%(open)s" min_lon="%(min_lon).8f" min_lat="%(min_lat).8f" max_lon="%(max_lon).8f" max_lat="%(max_lat).8f"  user="%(user)s" uid="%(uid)s"' % obj).encode('utf-8'))
        if obj['tags'] is None:
            fd.write('/>\n'.encode('utf-8'))
        else:
            fd.write('>\n'.encode('utf-8'))
            for k,v in iter(obj['tags'].items()):
                fd.write(('  <tag k="%s" v="%s"/>\n' % (k, v)).encode('utf-8'))
            fd.write('</changeset>\n'.encode('utf-8'))



def create_osm_file(data):
    """Creates a temporary osm XML file. The data is a list of OSM objects,
       each described by a hash of attributes. Most attributes are optional
       and will be filled with sensitive values, if missing. Mandatory are
       only `type` and `id`. For ways, nodes are obligatory and for relations
       the memberlist.
    """
    data.sort(key=lambda x:('NWR'.find(x['type']), x['id']))
    with tempfile.NamedTemporaryFile(dir='/tmp', suffix='.osm', delete=False) as fd:
        fname = fd.name
        fd.write("<?xml version='1.0' encoding='UTF-8'?>\n".encode('utf-8'))
        fd.write('<osm version="0.6" generator="test-pyosmium" timestamp="2014-08-26T20:22:02Z">\n'.encode('utf-8'))
        fd.write('\t<bounds minlat="-90" minlon="-180" maxlat="90" maxlon="180"/>\n'.encode('utf-8'))

        for obj in data:
            _write_osm_obj(fd, _complete_object(obj))

        fd.write('</osm>\n'.encode('utf-8'))

    return fname

def osmobj(kind, **args):
    ret = dict(args)
    ret['type'] = kind
    return ret


class HandlerTestBase:

    apply_locations = False
    apply_idx = 'sparse_mem_array'

    def test_func(self):
        fn = create_osm_file(self.data)
        try:
            self.Handler().apply_file(fn, self.apply_locations, self.apply_idx)
        finally:
            os.remove(fn)

