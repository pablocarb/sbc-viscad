import svgwrite
from svgwrite import cm, mm
import xml.etree.ElementTree as ET

def cds(x=0, y=0, fill='red'):
    ox = 9-x
    oy = 35-y
    points = [ (x[0]-ox,x[1]-oy) for x in ( (9,65), (27,65), (42,50), (27,35), (9,35), (9,65) ) ]
    stroke = '#000000'
    stroke_width = '3'
    stroke_linecap = 'round'
    stroke_linejoin = 'round'
    pid = 'poly1'
    out = svgwrite.shapes.Polygon(points=points,
                                  id=pid,
                                  stroke=stroke,
                                  stroke_width=stroke_width,
                                  stroke_linecap=stroke_linecap,
                                  stroke_linejoin=stroke_linejoin,
                                  fill=fill
                              )
    return out
    
fname = 'test/test.svg'
dwg = svgwrite.Drawing(filename=fname, debug=True)
dwg.add( cds() )
dwg.viewbox(width=50, height=100)
dwg.stretch()
dwg.save()

