from math import *

def IsPoint(p):
	return p and p.x and type(p.x) == "number" and (p.y and type(p.y) == "number")

def Round(v):
	return v < 0 and ceil(v - 0.5) or floor(v + 0.5)

def ClosestPointOnSegment(s1, s2, pt)
	ab = s2.sub(s1)
	t = ((pt.x - s1.x) * ab.x + (pt.y - s1.y) * ab.y) / (ab.x * ab.x + ab.y * ab.y)
	return t < 0 and s1 or (t > 1 and s2 or s1.add(t).scale(ab))
