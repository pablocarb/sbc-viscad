import svgwrite
from svgwrite import cm, mm
import xml.etree.ElementTree as ET

class Part:
    _partid = 0
    def __init__(self, **kwargs):
        self.__class__._partid += 1
        """ Default style """
        self.kwargs = {
            'stroke': '#000000',
            'stroke_width': '3',
            'stroke_linecap': 'round',
            'stroke_linejoin': 'round'
            }
        for key in kwargs:
            self.kwargs[key] = kwargs[key]
            

class Cds(Part):
    def __init__(self, x=0, y=0, **kwargs):
        Part.__init__(self, **kwargs)
        x1 = 9
        x2 = 27
        x3 = 42
        y1 = 35
        y2 = 50
        y3 = 65
        ox = x1-x
        oy = y1-y
        points = [ (x[0]-ox,x[1]-oy) for x in ( (x1,y3), (x2,y3), (x3,y2), (x2,y1), (x1,y1), (x1,y3) ) ]
        pid = 'poly' + str(self._partid)

        self.part = [svgwrite.shapes.Polygon(points=points,
                                            id=pid,
                                            **self.kwargs
                                        )]
        self.x = x
        self.y = y + y2 -y1
        self.width = x3 - x1
        self.height = y3 - y1

class Promoter(Part):
    def __init__(self, x=0, y=0, **kwargs):
        Part.__init__(self, **kwargs)
        self.part = []
        """ Arrow head """
        x1 = 31.5
        x2 = 40
        y0 = 15.5
        y1 = 23
        y2 = 30.3333
        ox = x1-x
        oy = y2-y
        points =  [  (x[0]-ox,x[1]-oy) for x in ( (x1, y0), (x2, y1), (x1, y2) ) ]
        pid = 'proma' + str(self._partid)

        self.part.append( svgwrite.shapes.Polyline(points=points,
                                            id=pid,fill='none',
                                            **self.kwargs
                                        )
                          )
        """ Main line """
        X1 = 10
        X2 = 39
        Y1 = 23
        Y2 = 50
        ox = x1-x
        oy = y2-y
        points = [  (x[0]-ox,x[1]-oy) for x in  ( (X1, Y2), (X1, Y1), (X2, Y1) ) ]
        pid = 'proml' + str(self._partid)

        self.part.append( svgwrite.shapes.Polyline(points=points,
                                                   id=pid, fill='none',
                                                   **self.kwargs
                                               ))

        self.x = x
        self.y = y
        self.width = x2 - X1
        self.height = Y2 - y0


class connect(Part):
    def __init__(self, part1, part2, **kwargs):
        Part.__init__(self, **kwargs)
        start = (part1.x+part1.width, part1.y)
        end = (part2.x, part2.y)
        pid = 'line' + str(self._partid)
        self.part = [svgwrite.shapes.Line(start=start, end=end,
                                         id=pid,
                                         **self.kwargs
                                     )]
        self.x = start[0] 
        self.y = start[1]
        self.width = end[0] - start[0]
        self.height = end[1] - end[0]
                                         

class Terminator:
    pass

class Rbs:
    pass

    
fname = 'test/test.svg'
dwg = svgwrite.Drawing(filename=fname, debug=True)
base = 20
cds1 = Cds(x=0, y=base, fill='red')
cds2 = Cds(x=2*cds1.width, y=base, fill='blue')
cds3 = Cds(x=4*cds1.width, y=base, fill='green')
conn1 = connect(cds1, cds2)
conn2 = connect(cds2, cds3)
prom1 = Promoter(x=6*cds1.width, y=base)
parts = []
parts =  [cds1, conn1, cds2, conn2, cds3, prom1]
w = 0
for pc in parts:
    for p in pc.part:
        dwg.add( p )
    w += pc.width
dwg.viewbox(width=w, height=100)
dwg.save()

