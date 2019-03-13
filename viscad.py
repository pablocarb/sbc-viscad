'''
viscad (c) University of Manchester 2018

viscad is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  Pablo Carbonell, SYNBIOCHEM
@description: DoE-based pathway libraries visualisation
@usage: viscad.py design.j0 -i design.txt -v2
'''
import svgwrite
from svgwrite import cm, mm
import xml.etree.ElementTree as ET
import re
import math
import os
import argparse
import subprocess
import sys
import csv
import pandas as pd
import numpy as np

RESISTANCE = True
ORIGIN = True


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
        self.part = []


class Title(Part):
    def __init__(self, title, x=0, y=0, width=0, partid=None, **kwargs):
        Part.__init__(self, **kwargs)
        if partid is None:
            pid = 'title' + str(self._partid)
        else:
            pid = partid
        self.x = x 
        self.y = y
        self.width = width
        self.height = 0
        self.i = self.x
        self.o = self.x + self.width 
        g = svgwrite.container.Group(id=pid, **self.kwargs)
        g.add( svgwrite.text.Text(title, insert=( self.x, self.y), stroke='none', fill='#000000', font_size='24') )
        self.part.append( g )
        

class Cds(Part):
    def __init__(self, x=0, y=0, partid=None, **kwargs):
        x1 = 9
        x2 = 27
        x3 = 42
        y1 = 35
        y2 = 50
        y3 = 65
        Part.__init__(self, **kwargs)
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
        g.add( svgwrite.text.Text(pid, insert=( self.x-50, self.y + 40), stroke='none', fill=self.kwargs['stroke']) )


class Rbs:
    pass


def readExample(f, f2=None, v2=True):
    """ Read the DoE file """
    lib = []
    libid = []
    # Improved version containing all the information in a single file
    if f2 is None:
        with open(f) as h:
            csr = csv.reader(h)
            for row in csr:
                r1 = []
                r2 = []
                cid = row[0]
                r1.append( cid )
                r2.append( cid )
                for part in row[1:]:
                    sbcid, partinfo = part.split(':')
                    if len(sbcid) == 0:
                        sbcid = None
                    r1.append(sbcid)
                    r2.append(partinfo)
                lib.append( r2 )
                libid.append( r1 )
        return lib, libid

    with open(f) as handler:
        for row in handler:
            ll = []
            for x in row.rstrip().split('\t'):
                # if x.startswith( 'promoter' ):
                #     a, b = x.split( '_' )
                #     if re.search( '.*(\d+)', a):
                #         v = re.search( '.*(\d+)', a).groups()[0]
                #         if int(v) > 3 and int(b) >=3:
                #             x = None
                ll.append( x )
            lib.append( ll )
    if not v2:
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
    else:
        if os.path.exists(f2):
            with open(f2) as handler:
                i = 0
                for row in handler:
                    line = row.rstrip()
                    ll = line.split('\t')
                    lli = []
                    j = 0
                    for x in lib[i]:
                        #### PATCH: to be changed by directly reading the excel file ####
                        try:
                            y = ll[j]
                        except:
                            y = None
                        if x.startswith( 'promoter' ):
                            a, b = x.split( '_' )
                            if re.search( '.*(\d+)', a):
                                # promoter number
                                v = re.search( '[^\d]*(\d+)$', a).groups()[0]
                                if int(v) > 3 and int(b) >=3:
                                    y = None
                                    j -= 1
                                    continue
                        j += 1
                        lli.append( y )
                    libid.append( lli )
                    i += 1
    return lib, libid

            

def addNewConstruct(dwg, constructIdentifier, construct, base, cell, slot, dlibid, cmap={}, cv=False):
    """ Mapping improvement. """
    parts = []
    colors = ['red', 'blue', 'green', 'chartreuse', 'magenta', 'grey', 'cyan', 'darksalmon', 'lavender', 'orange']
    cid = constructIdentifier
    if cid in dlibid:
        cid = dlibid[cid]
    title = Title( cid, cell, base+0.5*slot, cell )
    parts.append( title )
    base += slot
    cursor = 1
    for i in range(0, len(construct)):
        try:
            partid = dlibid[ construct[i] ]
        except:
            continue
        x = construct[i].split('_')
        level = int(x[-1])
        w = re.split('([0-9]+)$', x[0])
        ptype = w[0]
        pnum = int( math.floor( int(w[1]) / 2 )  - 2 )
        if partid is None or partid == 'None':
            if ptype == 'promoter':
                cursor += 4
            else:
                cursor += 2
            continue
        if ptype == 'plasmid':
            prom1 = Promoter(x=len(parts)*cell, y=base, partid=partid)
            parts.append( prom1 )
            cursor += 1

        if ptype == 'origin' and ORIGIN:
            pcolor = colors [ level - 1]
            ori1 = Origin(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            parts.append( ori1 )
            cursor += 2

        if ptype == 'resistance' and RESISTANCE:

            pcolor = colors[ pnum ]
            cds1 = Cds(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            conn1 = connect(parts[-1], cds1)
            parts.append(conn1)
            parts.append(cds1)
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
#            if partid in cmap:
#            pcolor = colors[ cmap[partid] % len(colors) ]
#            else:
            if cv:
                pcolor = colors[ (pnum + level - 1 ) % len(colors)]
            else:
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



def mapnewParts(dlib, dlibid):
    """ Assign a unique index to each part """
    cmap = {}
    for libi in sorted(dlib):
        try:
            constructid = dlibid[libi]
        except:
            construct = libi
        cmap[construct] = len(cmap)
        for p in dlib[libi]:
            if p not in cmap:
                cmap[p] = len(cmap)
    return cmap


def fromDesign(M):
    dlib1 = {}
    df = pd.DataFrame(M)
    for j in np.arange(3,df.shape[1],2):
        n = len( df.iloc[:,j].unique() )
        for z in np.arange(n/2,n):
            dlib1['promoter{}_{}'.format(j+2,int(z)+1)] = None
    dlib = {}
    for i in np.arange(M.shape[0]):
        plasmid = []
        plasmid.append( 'origin{}_{}'.format(1,int(M[i,0]+1) ) )
        plasmid.append( 'resistance{}_{}'.format(2,1) )
        for j in np.arange(1,M.shape[1],2):
            plasmid.append( 'promoter{}_{}'.format(j+2,int(M[i,j]+1) ) )
            plasmid.append( 'gene{}_{}'.format(j+3,int(M[i,j]+1) ) )
        dlib[ 'PLASMID%02d' % (i+1,) ] = plasmid
    for p in dlib:
        for x in dlib[p]:
            if x not in dlib1:
                dlib1[x] = x
    return dlib, dlib1
    
        
             
def createnewCad(f1=None, f2=None, outfile=None, v2=True, M=None, colvariants=False):
    if M is None:
        f1j0 = re.sub('.txt', '.j0', f1)
        f1ji0 = re.sub('.j0', '.ji0', f1j0)
        dlib = readLibrary(f1j0)
        dlib1 = mapLibrary(dlib, f1ji0)
    else:
        dlib, dlib1 = fromDesign(M)
    ncmap = mapnewParts(dlib, dlib1)
    dwg = svgwrite.Drawing(filename=outfile, debug=True)
    slot = 100
    cell = 50
    i = 1
    w = cell
    for libi in sorted(dlib):
        try:
            constructid = dlib1[libi]
        except:
            constructid = libi
        parts = addNewConstruct(dwg, constructid, construct=dlib[libi], base=(2*i+0.5)*slot,
                                cell=cell, slot=slot, dlibid=dlib1, cmap=ncmap, cv=colvariants)
        i += 1
        for pc in parts:
            for p in pc.part:
                dwg.add( p )
        w = max(w, pc.x+pc.width)                         
    dwg.viewbox(width=w+cell, height=slot*(2*i+0.5))
    dwg.save()


def readLibrary(infoFile, abbvr=False):
    dlib = {}
    for l in open(infoFile):
        m = l.rstrip().split('\t')
        sbcid = m[0]
        try:
            sbcid = str(int(re.sub('SBC', '', sbcid)))
        except:
            pass
        mm = []
        for x in m:
            if abbvr:
                x = re.sub('plasmid', 'l', x)
                x = re.sub('promoter', 'p', x)
                x = re.sub('gene', 'g', x)
            mm.append(x)
        dlib[sbcid] = mm[1:]
    return dlib

def mapLibrary(dlib, equiv):
    """ Get the ids of each part. """
    eqlib = {}
    for line in open(equiv):
        construct = []
        line = line.rstrip()
        ids = line.split()
        plasmid = ids[0]
        l = 16
        ll = len(ids[1])
        for i in range(0, len(line)):
            if line[i:(i+ll)] == ids[1]:
                break
        while i < len(line):
            construct.append( line[i:(i+l)].rstrip() )
            i += l
        for j in range(0, len(dlib[plasmid])):
            try:
                if construct[j] == '':
                    construct[j] = 'None'
                if dlib[plasmid][j] in eqlib and construct[j] == 'None':
                    # do not update if it is not empty (see comment below)
                    continue
                eqlib[dlib[plasmid][j]] = construct[j]
            except:
                # This can happen because some parts are removed
                # in one of the constructs, prioritize assigning 
                # a value if somewhere happens in the library
                if dlib[plasmid][j] not in eqlib:
                    eqlib[dlib[plasmid][j]] = 'None'
            
    return eqlib



def makeReport(pdfile, design='SBC', size=10):
    texfile = re.sub('\.pdf$', '_report.tex', pdfile)
    mask = {'design': design, 'comment': 'Library size={}'.format(size)}
    with open('template.tex') as handler, open(texfile, 'w') as h2:
        for line in handler:
            for x in mask:
                line = re.sub('{{'+x+'}}', mask[x], line)
            if line.startswith('\end{document}'):
                for i in range(0, 1+size / 10):
                    d = ((10 - size) % 10 ) % 10
                    y1 = max(0, 1500*( (size/10) - i ) - d * 1500/10)
                    y2 = 1500*i
                    tx = '\\includegraphics[width=\\textwidth, trim={{ 0 {y1} 0 {y2} }}, clip]{{{pdf}}}\n'
                    h2.write(tx.format(y1=y1,
                                       y2=y2,
                                       pdf=os.path.basename(pdfile)))
            h2.write( line )
    p = subprocess.Popen( ['pdflatex', os.path.abspath(texfile)], cwd=os.path.dirname( pdfile ) )
            
def makePDF(outfile, outpdfile):
    p = subprocess.call( ['/usr/bin/inkscape', outfile, '-A', outpdfile] )


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
    parser.add_argument('-r', action='store_true',
                        help='Report')
    parser.add_argument('-d', default=None,
                        help='Design')
    parser.add_argument('-s', default=None,
                        help='Size')
    parser.add_argument('-x', default='',
                        help='Add extension to output files')
    parser.add_argument('-v2', action='store_true',
                        help='Use new version with txt file (still not working)')
    return parser


def runViscad(args=None):
    parser = arguments()
    if args is None:
        arg = parser.parse_args()
    else:
        arg = parser.parse_args(args)
    name = re.sub( '\.[^.]+$', '', os.path.basename(arg.doeFile) )
    if arg.O is not None:
        outfile = os.path.join(arg.O, name+arg.x+'.svg')
        outpdfile = os.path.join(arg.O, name+arg.x+'.pdf')
    else:
        outfile = os.path.join(os.path.dirname(arg.doeFile), name+arg.x+'.svg')
        outpdfile = os.path.join(os.path.dirname(arg.doeFile), name+arg.x+'.pdf')
    try:
        v2 = arg.v2
    except:
        v2 = False

    createnewCad(f1=arg.doeFile, f2=arg.i, outfile=outfile, v2=v2)
    if arg.p:
        makePDF(outfile, outpdfile)
        if arg.r:
            try:
                makeReport( outpdfile, arg.d, int(arg.s) )
            except:
                pass
            
    if arg.l is not None:
        with open(arg.l, 'a') as handler:
            if args is None:
                handler.write(' '.join(['"{}"'.format(x) for x in sys.argv])+'\n')
            else:
                handler.write('"viscad.py"'+' '.join(['"{}"'.format(x) for x in args])+'\n')

if __name__ == '__main__':
    runViscad()


#########################

# Previous version of the code: it had some issues with file parsing

def createCad(f1, f2, outfile, v2=True):
    lib, libid = readExample(f1, f2, v2)
    cmap = mapParts(lib,libid)

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
            
        parts = addConstruct(dwg, construct, base=(2*i+0.5)*slot, cell=cell, slot=slot, constructid=constructid, cmap=cmap)
        i += 1
        for pc in parts:
            for p in pc.part:
                dwg.add( p )
        w = max(w, pc.x+pc.width)                         
    dwg.viewbox(width=w+cell, height=slot*(2*i+0.5))
    dwg.save()


def mapParts(lib, libid):
    """ Assign a unique index to each part """
    cmap = {}
    for i in range(0, len(lib)):
        construct = lib[i]
        try:
            constructid = libid[i]
        except:
            constructid = lib[i]
        for p in constructid:
            if p not in cmap:
                cmap[p] = len(cmap)
    return cmap


def addConstruct(dwg, construct, base, cell, slot, constructid=None, cmap={}):
    parts = []
    colors = ['red', 'blue', 'green', 'chartreuse', 'magenta', 'grey', 'cyan', 'darksalmon', 'lavender', 'orange']
    try:
        cid = constructid[0]
    except:
        cid = construct[0]
    title = Title( cid, cell, base+0.5*slot, cell )
    parts.append( title )
    base += slot
    cursor = 1
    for i in range(1, len(construct)):
        try:
            partid = constructid[i]
        except:
            continue
        x = construct[i].split('_')
        level = int(x[-1])
        w = re.split('([0-9]+)$', x[0])
        ptype = w[0]
        pnum = int( math.floor( int(w[1]) / 2 )  - 2 )
        if partid is None:
            if ptype == 'promoter':
                cursor += 4
            else:
                cursor += 2
            continue
        if ptype == 'plasmid':
            prom1 = Promoter(x=len(parts)*cell, y=base, partid=partid)
            parts.append( prom1 )
            cursor += 1

        if ptype == 'origin' and ORIGIN:
            pcolor = colors [ level - 1]
            ori1 = Origin(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            parts.append( ori1 )
            cursor += 2

        if ptype == 'resistance' and RESISTANCE:

            pcolor = colors[ pnum ]
            cds1 = Cds(x=cursor*cell, y=base, partid=partid, fill=pcolor)
            conn1 = connect(parts[-1], cds1)
            parts.append(conn1)
            parts.append(cds1)
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
#            if partid in cmap:
#            pcolor = colors[ cmap[partid] % len(colors) ]
#            else:
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
