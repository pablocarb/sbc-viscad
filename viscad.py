import svgwrite
from svgwrite import cm, mm
import xml.etree.ElementTree as ET
import re
import math
import os
import argparse
import subprocess
import sys


class Part:
    _partid = 0
    def __init__(self, **kwargs):
        self.__class__._partid += 1
        """ Default style """
        self.kwargs = {
            'stroke': '#000000',
            'stroke_width': '3',
            'stroke_linecap': 'round',
            'stroke_linejoin': 'round',
            'font-family': 'Verdana',
            'font-size': '16'
            }
        for key in kwargs:
            self.kwargs[key] = kwargs[key]
            

class Cds(Part):
    def __init__(self, x=0, y=0, partid=None, **kwargs):
        x1 = 9
        x2 = 27
        x3 = 42
        y1 = 35
        y2 = 50
        y3 = 65
        Part.__init__(self, **kwargs)
        self.part = []
        p1 = ( ('M', x1, y3), ('L', x2, y3), ('L', x3, y2), ('L', x2, y1), ('L', x1, y1), ('L', x1, y3), ('Z',) )
        pd1 = shiftPath(p1, x, y-y2)
        if partid is None:
            pid = 'cds' + str(self._partid)
        else:
            pid = partid
        g = svgwrite.container.Group(id=pid, **self.kwargs)
        g.add( svgwrite.path.Path( pd1 ) )
        self.part.append( g )
        self.x = x + x1
        self.y = y
        self.width = x3 - x1
        self.height = y3 - y1
        self.i = self.x
        self.o = self.x + self.width 
        g.add( svgwrite.text.Text(pid, insert=( self.x, self.y + 40), stroke='none') )


def shiftPath(p, x, y):
    pd = []
    for i in p:
        if len(i) >= 2:
            pd.append( (i[0], i[1]+x, i[2]+y) )
        else:
            pd.append( i )
    pa = []
    for x in pd:
        pa.append( ' '.join( map(str, x) ) )
    return ' '.join( pa )

class Promoter(Part):
    """ Define using path """
    def __init__(self, x=0, y=0, partid=None, **kwargs):
        Part.__init__(self, **kwargs)
        self.part = []
        p1 = ( ('M', 31.5, 15.5), ('L', 40, 23), ('L', 31.5, 30.333) )
        p2 = ( ('M', 10, 50), ('L', 10, 23), ('L', 39, 23) )
        pd1 = shiftPath(p1, x, y-50)
        pd2 = shiftPath(p2, x, y-50)
        if partid is None:
            pid = 'prom' + str(self._partid)
        else:
            pid = partid
        g = svgwrite.container.Group(id=pid, **self.kwargs)
        g.add( svgwrite.path.Path( pd1, fill='none') )
        g.add( svgwrite.path.Path( pd2, fill='none') )
        self.part.append( g )
        self.x = x 
        self.y = y 
        self.width = 40 - 10
        self.height = 50 - 15.5
        self.i = self.x
        self.o = self.x #+ self.width 
        g.add( svgwrite.text.Text(pid, insert=( self.x, self.y + 40), stroke='none', fill=self.kwargs['stroke']) )


class connect(Part):
    def __init__(self, part1, part2, **kwargs):
        Part.__init__(self, **kwargs)
        start = (part1.o, part1.y)
        end = (part2.i, part2.y)
        pid = 'line' + str(self._partid)
        self.part = [svgwrite.shapes.Line(start=start, end=end,
                                         id=pid,
                                         **self.kwargs
                                     )]
        self.x = start[0] 
        self.y = start[1]
        self.width = end[0] - start[0]
        self.height = end[1] - start[1]
        self.i = self.x
        self.o = self.x + self.width
                                         

class Terminator(Part):
    """ Define using path """
    def __init__(self, x=0, y=0, **kwargs):
        Part.__init__(self, **kwargs)
        self.part = []
        p1 = ( ('M', 25, 50), ('L', 25, 26) )
        p2 = ( ('M', 10, 25), ('L', 40, 25) )
        pd1 = shiftPath(p1, x, y-50)
        pd2 = shiftPath(p2, x, y-50)
        pid = 'term' + str(self._partid)
        g = svgwrite.container.Group(id=pid, **self.kwargs)
        g.add( svgwrite.path.Path( pd1, fill='none') )
        g.add( svgwrite.path.Path( pd2, fill='none') )
        self.part.append( g )
        self.x = x + 40
        self.y = y 
        self.width = 40 - 10
        self.height = 50 - 25
        self.i = self.x
        self.o = self.x



class Origin(Part):
    def __init__(self, x=0, y=0, partid=None, **kwargs):
        Part.__init__(self, **kwargs)
        self.part = []
        if partid is None:
            pid = 'prom' + str(self._partid)
        else:
            pid = partid
        g = svgwrite.container.Group(id=pid, **self.kwargs)
        g.add( svgwrite.shapes.Circle( center=(x+12,y), r=12) )
        self.part.append( g )
        self.x = x
        self.y = y
        self.width = 24 
        self.height = 24
        self.i = self.x
        self.o = self.x + self.width
        g.add( svgwrite.text.Text(pid, insert=( self.x, self.y + 40), stroke='none', fill=self.kwargs['stroke']) )


class Rbs:
    pass


def readExample(f, f2):
    """ Read the DoE file """
#    dn = '14'
#    f = '/mnt/syno/shared/Designs/SBCDE000%s/Design/SBCDE000%s_Doe_48lib_v4/SBCDE000%s_Doe_48lib_v4.j0' % (dn,dn,dn)
#    f2 = '/mnt/syno/shared/Designs/SBCDE000%s/Design/SBCDE000%s_Doe_48lib_v4/SBCDE000%s_Doe_48lib_v4.ji0' % (dn,dn,dn)
    lib = []
    libid = []
    with open(f) as handler:
        for row in handler:
            lib.append( row.rstrip().split('\t') )
    if os.path.exists(f2):
        with open(f2) as handler:
            for row in handler:
                line = row.rstrip()
                ll = []
                for i in range(0, len(line), 16):
                    pid = re.sub('\s', '', line[i:min(i+16, len(line))])
                    if len(pid) == 0:
                        ll.append( None )
                    else:
                        ll.append( pid )
                libid.append( ll )
    return lib, libid
            
def addConstruct(dwg, construct, base, cell, constructid=None):
    colors = ['red', 'blue', 'green', 'cyan', 'magenta', 'grey', 'lavender', 'darksalmon', 'chartreuse']
    cid = construct[0]
    parts = []
    cursor = 1
    for i in range(1, len(construct)):
        try:
            partid = constructid[i]
        except:
            continue
        if partid is None:
            cursor += 4
            continue
        x = construct[i].split('_')
        level = int(x[-1])
        w = re.split('([0-9]+)$', x[0])
        ptype = w[0]
        pnum = int( math.floor( int(w[1]) / 2 )  - 2 )
        if ptype == 'plasmid':
            prom1 = Promoter(x=len(parts)*cell, y=base, partid=partid)
            parts.append( prom1 )
            cursor += 1

        if ptype == 'origin':
            pcolor = colors [ level - 1]
            ori1 = Origin(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            parts.append( ori1 )
            cursor += 2
           

        if ptype == 'promoter':
            pcolor = colors[ level - 1 ]

            if len(parts) > 1:
                term1 = Terminator(x=cursor*cell, y=base, stroke=pcolor)
                conn1 = connect(parts[-1], term1)
                parts.append(conn1)
                parts.append(term1)
                cursor += 2

            prom1 = Promoter(x=cursor*cell, y=base, partid=partid, stroke=pcolor)
            if len(parts) >= 1:
                conn1 = connect(parts[-1], prom1)
                parts.append(conn1)
                parts.append(prom1)
                cursor += 2
            else:
                parts.append(prom1)
                cursor += 2
        if ptype == 'gene':

            pcolor = colors[ pnum ]
            cds1 = Cds(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            conn1 = connect(parts[-1], cds1)
            parts.append(conn1)
            parts.append(cds1)
            cursor += 2
    term1 = Terminator(x=cursor*cell, y=base)
    conn1 = connect(parts[-1], term1)
    parts.append(term1)
    parts.append(conn1)
    return parts

def createCad(f1, f2, outfile):
    lib, libid = readExample(f1, f2)
    dwg = svgwrite.Drawing(filename=outfile, debug=True)
    slot = 100
    cell = 50
    i = 1
    w = cell
    for i in range(0, len(lib)):
        construct = lib[i]
        try:
            constructid = libid[i]
        except:
            constructid = libid
        parts = addConstruct(dwg, construct, (i+1)*slot, cell, constructid)
        i += 1
        for pc in parts:
            for p in pc.part:
                dwg.add( p )
        w = max(w, pc.x+pc.width)                         
    dwg.viewbox(width=w+cell, height=slot*(i+1))
    dwg.save()

        
def arguments():
    parser = argparse.ArgumentParser(description='Visual DoE. Pablo Carbonell, SYNBIOCHEM, 2018')
    parser.add_argument('doeFile', 
                        help='Input DoE file')
    parser.add_argument('-i', default=None, 
                        help='Input DoE file with ICE number')
    parser.add_argument('-O',  default=None,
                        help='Output folder (default: same as input)')
    parser.add_argument('-p', action='store_false',
                        help='Do not generate pdf')
    parser.add_argument('-l', default=None,
                        help='Log file')
    return parser


def runViscad(args=None):
    parser = arguments()
    if args is None:
        arg = parser.parse_args()
    else:
        arg = parser.parse_args(args)
    name = re.sub( '\.[^.]+$', '', os.path.basename(arg.doeFile) )
    if arg.O is not None:
        outfile = os.path.join(arg.O, name+'.svg')
        outpdfile = os.path.join(arg.O, name+'.pdf')
    else:
        outfile = os.path.join(os.path.dirname(arg.doeFile), name+'.svg')
        outpdfile = os.path.join(os.path.dirname(arg.doeFile), name+'.pdf')        
    createCad(arg.doeFile, arg.i, outfile)
    if arg.p:
        p = subprocess.call( ['/usr/bin/inkscape', outfile, '-A', outpdfile] )
    if arg.l is not None:
        with open(arg.l, 'a') as handler:
            if args is None:
                handler.write(' '.join(['"{}"'.format(x) for x in sys.argv])+'\n')
            else:
                handler.write('"viscad.py"'+' '.join(['"{}"'.format(x) for x in args])+'\n')

if __name__ == '__main__':
    runViscad()
