import overpy

api = overpy.Overpass()
result = api.query("""
[out:json];
area[name="Moscow"];
(
  way(area);
);
out geom;
""")

print([way.id for way in result.ways[:5]])

