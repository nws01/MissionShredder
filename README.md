# MissionShredder
Generates HuginOS Mission Plans based on user input

- Enter Named Area of Interest Co-ordinates (generates mission plan with this waypoint in the center of the survey patttern)
- Select mission type
  - Initial search for standard survey pattern
  - Reacquire for Cathx/low altitude/short linespacings (optimises line order for 30m turn radius)
  - Must set vehicle settings in HOS (altitudes, safe/critical depths, payload configurations)

Dependencies:
- Python3
- pip install PyQT5
- pip install pyproj
