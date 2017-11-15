import svgwrite
from svgwrite import cm, mm
import xml.etree.ElementTree as ET

class cds:
    def __init__(self, x=0, y=0, fill='red'):
        x1 = 9
        x2 = 27
        x3 = 42
        y1 = 35
        y2 = 50
        y3 = 65
        ox = x1-x
        oy = y1-y
        points = [ (x[0]-ox,x[1]-oy) for x in ( (x1,y3), (x2,y3), (x3,y2), (x2,y1), (x1,y1), (x1,y3) ) ]
        stroke = '#000000'
        stroke_width = '3'
        stroke_linecap = 'round'
        stroke_linejoin = 'round'
        pid = 'poly1'
        self.part = svgwrite.shapes.Polygon(points=points,
                                            id=pid,
                                            stroke=stroke,
                                            stroke_width=stroke_width,
                                            stroke_linecap=stroke_linecap,
                                            stroke_linejoin=stroke_linejoin,
                                            fill=fill
                                        )
        self.x = x
        self.y = y + y2 -y1
        self.width = x3 - x1
        self.height = y3 - y1

class connect:
    def __init__(self, part1, part2):
        start = (part1.x+part1.width, part1.y)
        end = (part2.x, part2.y)
        stroke = '#000000'
        stroke_width = '3'
        stroke_linecap = 'round'
        stroke_linejoin = 'round'
        pid = 'line1'
        self.part = svgwrite.shapes.Line(start=start, end=end,
                                         id=pid,
                                         stroke=stroke,
                                         stroke_width=stroke_width,
                                         stroke_linecap=stroke_linecap,
                                         stroke_linejoin=stroke_linejoin
                                     )
        self.x = start[0] 
        self.y = start[1]
        self.width = end[0] - start[0]
        self.height = end[1] - end[0]
                                         
class promoter:
    pass

class terminator:
    pass

class rbs:
    pass


    
fname = 'test/test.svg'
dwg = svgwrite.Drawing(filename=fname, debug=True)
base = 20
cds1 = cds(x=0, y=base)
cds2 = cds(x=2*cds1.width, y=base, fill='blue')
cds3 = cds(x=4*cds1.width, y=base, fill='green')
conn1 = connect(cds1, cds2)
conn2 = connect(cds2, cds3)
parts = [cds1, conn1, cds2, conn2, cds3]
w = 0
for p in parts:
    dwg.add( p.part )
    w += p.width
dwg.viewbox(width=w, height=100)
dwg.save()

