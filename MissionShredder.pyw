"""
GUI application for control of Voysys 360° Camera System
"""
#12:52.0518S, 108:27.3424E
"""
To do:
- Add course and distance to lines
- Remove line end waypoints (goes off course and bearing)
- Add naming to transit lines
"""
import sys
import PyQt5 as Qt
from PyQt5 import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
import os
import datetime
import pyproj
from math import asin, atan2, cos, degrees, radians, sin, sqrt

########################FUNCTIONS###############################################################


if __name__ == '__main__':

    from math import asin, atan2, cos, degrees, radians, sin

    def generate_waypoint(lat1, lon1, d, bearing, R=6371):
        """
        lat: initial waypoint latitude, in decimal degrees
        lon: initial waypoint longitude, in  decimal degrees
        d: target distance from initial waypoint in km
        bearing: (true) bearing from initial waypoint in degrees
        R: optional radius of sphere, defaults to mean radius of earth

        Returns list of new lat/lon coordinate {d}km from initial, in degrees
        Utilises law of haversines from spherical trigonometry.
        """

        lat1 = radians(lat1)
        lon1 = radians(lon1)
        a = radians(bearing)
        lat2 = asin(sin(lat1) * cos(d/R) + cos(lat1) * sin(d/R) * cos(a))
        lon2 = lon1 + atan2(
            sin(a) * sin(d/R) * cos(lat1),
            cos(d/R) - sin(lat1) * sin(lat2)
        )
        lat2 = degrees(lat2)
        lon2 = degrees(lon2)
        result = [lat2, lon2]
        return result
    
    def course_and_distance(wp1, wp2):
        """
        Calculate the azimuth and distance between 2 wgs84 coordinates utilising pyproj
        """
        lat1 = wp1[0]
        lon1 = wp1[1]
        lat2 = wp2[0]
        lon2 = wp2[1]
        
        geodesic = pyproj.Geod(ellps='WGS84')
        course,back_azimuth,distance = geodesic.inv(lon1, lat1, lon2, lat2)  
        return distance, course
    

    def DM_to_DD(coord):
        """
        takes decimal minutes input in format "DD:MM.mmmm" and returns in Decimal Degrees "DD.dddddd"
        """
        coordSplit = coord.split(":")
        coordDegrees = coordSplit[0]
        coordMinutes = float(coordSplit[1])
        coordMinutes = round((coordMinutes/60), 6)
        coordMinutes = str(coordMinutes)
        coordMinutes = coordMinutes[1:]
        
        coordDD = coordDegrees + coordMinutes
        return coordDD
    
    def inverse_bearing(bearing):
        if bearing >= 180:
            inverseBearing = bearing - 180
            return inverseBearing

        if bearing < 180: 
            inverseBearing = bearing + 180
            return inverseBearing    
        
    def turn_bearing(bearing, direction):
        if direction == "Clockwise":
            turn1Bearing = (bearing + 90) % 360
            turn2Bearing = (bearing - 90) % 360
            return turn1Bearing, turn2Bearing

        if direction == "Anti Clockwise":
            turn1Bearing = (bearing - 90) % 360
            turn2Bearing = (bearing + 90) % 360
            return turn1Bearing, turn2Bearing
        
    def dd_to_dm(wpList):
        """
        Takes co-ordinates in -DD.ddddd list [lat1, lon1,....latn, lonn] and retruns in Kongsberg Maritime DD:MM.mmmmmS format
        """ 
        wpLATdd = str(wpList[0])
        wpLONdd = str(wpList[1])
        wpNS = wpLATdd[0]
        wpEW = wpLONdd[0]
        
        if wpNS =="-":
            wpNS = "S" 
        else:
            wpNS = "N"

        if wpEW == "-":
            wpEW = "W"
        else:
            wpEW = "E"

        wpLATdd = str(wpLATdd)
        wpLONdd = str(wpLONdd)
        wpLATdd = wpLATdd.strip("-")
        wpLONdd = wpLONdd.strip("-")
        wpLATdd = wpLATdd.split(".")
        wpLONdd = wpLONdd.split(".")
        LATdecimal = (wpLATdd[1])
        LONdecimal = (wpLONdd[1])
        LATdeg = str((wpLATdd[0]))
        LONdeg = str((wpLONdd[0]))

        latdecimal = str(LATdecimal)
        londecimal = str(LONdecimal)
        latdecimal = latdecimal.strip(".")
        londecimal = londecimal.strip(".")
        latdecimal = "0." + latdecimal
        londecimal = "0." + londecimal
        

        LATdecimal = float(latdecimal)*60
        LONdecimal = float(londecimal)*60
        LATdecimal = '{:.4f}'.format(LATdecimal)
        LONdecimal = '{:.4f}'.format(LONdecimal)

        LATmm = str(LATdecimal)
        LONmm = str(LONdecimal)

        wpLATdm = LATdeg + ":" + LATmm + wpNS
        wpLONdm = LONdeg + ":" + LONmm + wpEW

        wp = [wpLATdm, wpLONdm]

        return wp
    
    
    def write_transit(lat, lon, course, distance, surveyTitle):
        course = "(" + (str(course).zfill(3)) + ")"
        distance = "(" + str(distance) + ")"
        dm = dd_to_dm([lat, lon])
        lat = dm[0]
        lon = dm[1]

        tag1 = ":" 
        depth1 = "0.0"
        alt1 = "40"
        DMo1 = "T"
        Latitude1 = "-"
        Longitude1 = "-"
        course1 = "(000)"
        GMo1 = "C"
        Speed1 = "2.00"
        SMo1 = "S"
        Dur1 = "-"
        Dist1 = "-"
  

        tag = ":" 
        depth = "="
        alt = "="
        DMo = "="
        Latitude = str(lat)
        Longitude = str(lon)
        course = "(000)"
        GMo = "="
        Speed = "="
        SMo = "="
        Dur = "-"
        Dist = "-"

        Line1 = f"{tag1:10}"+f"{depth1:6}"+f"{alt1:6}"+f"{DMo1:4}"+f"{Latitude1:12}"+f"{Longitude1:13}"+f"{course1:7}"+f"{GMo1:3}"+f"{Speed1:5}"+f"{SMo1:5}"+f"{Dur1:7}"+f"{Dist1:8}"
        lineEntry = f"{tag:10}"+f"{depth:6}"+f"{alt:6}"+f"{DMo:4}"+f"{Latitude:12}"+f"{Longitude:13}"+f"{course:7}"+f"{GMo:3}"+f"{Speed:5}"+f"{SMo:5}"+f"{Dur:7}"+f"{Dist:8}"
        
        with open("Survey" + surveyTitle + ".mp", "a") as f:
            f.write(Line1 + "\n")
            f.write(lineEntry + "\n")
            f.write("# Lead-in to Survey Pattern \n")





    def write_leadin(lat, lon, course, distance, surveyTitle):
        course = "(" + (str(course).zfill(3)) + ")"
        distance = "(" + str(distance) + ")"
        dm = dd_to_dm([lat, lon])
        lat = dm[0]
        lon = dm[1]
  

        tag = ":leadin" 
        depth = "="
        alt = "="
        DMo = "="
        Latitude = str(lat)
        Longitude = str(lon)
        course = course
        GMo = "="
        Speed = "="
        SMo = "="
        Dur = "="
        Dist = distance
        lineEntry = f"{tag:10}"+f"{depth:6}"+f"{alt:6}"+f"{DMo:4}"+f"{Latitude:12}"+f"{Longitude:13}"+f"{course:7}"+f"{GMo:3}"+f"{Speed:5}"+f"{SMo:5}"+f"{Dur:7}"+f"{Dist:8}"

        with open("Survey" + surveyTitle + ".mp", "a") as f:
            f.write(lineEntry + "\n")



    def mp_generate(nai, surveyTitle, missionType, missionDirection, exitPoint, lineBearing, searchRadius, lineSpacing, runIn):
        """
        Generates a Kongsberg Maritime Mission Plan (.mp) file for loading to a Hugin AUV based on user inputs
        """

        #Far or near determines even/odd amount of lines (AUV to conclude survey on same or opposing side of the start point)
        timestamp = str(datetime.datetime.now())
        mpHeader = "MP1000\n#\n# Kongsberg Maritime AUV Mission Plan\n# Saved " + timestamp + " by MissionShredder" + "\n#\n\n#:Tag\tDepth\tAlt\tDMo\tLatitude\tLongitude\tCourse\tGMo\tSpeed\tSMo\tDur\tDist\tFlags\n#\n\n# Survey" + surveyTitle + "\n"
        lineName = "s" + surveyTitle

        #Format lat lon variables from line edit entry
        nai = nai.strip(" ")
        nai = nai.split(",")
        naiLAT = nai[0]
        naiLON = nai[1]
        naiNS = naiLAT[-1]
        naiEW = naiLON[-1]
        naiLAT = naiLAT.strip("S")
        naiLAT = naiLAT.strip("N")
        naiLON = naiLON.strip("E")
        naiLON = naiLON.strip("W")
        naiLAT = naiLAT.strip(" ")
        naiLON = naiLON.strip(" ")

        naiLATdd = (DM_to_DD(naiLAT))
        naiLONdd = (DM_to_DD(naiLON))

        lineBearing = int(lineBearing)
        searchRadius = int(searchRadius)
        lineSpacing = int(lineSpacing)
        runIn = int(runIn)
        surveyArea = searchRadius * 2

        if naiNS =="S":
            naiLATdd = "-" + naiLATdd

        if naiEW == "W":
            naiLONdd = "-" + naiLONdd

        naiLATdd = float(naiLATdd)
        naiLONdd = float(naiLONdd)

        lineLength = searchRadius*2+(runIn*2)
        startRange = lineLength/2/1000
        inverseLineBearing = inverse_bearing(lineBearing)
        wp_start = generate_waypoint(naiLATdd, naiLONdd, startRange, inverseLineBearing)
        



        #Calculate number of lines and adjust for near/far exit point
        lines = (surveyArea + lineSpacing)/lineSpacing

        if exitPoint == ("Near"):
            if (lines % 2) == 0:
                parallelShift = ((lines/2) * lineSpacing) + (lineSpacing/2)
                                
            if (lines %2) != 0:
                lines += 1
                parallelShift = ((lines/2) * lineSpacing) + (lineSpacing/2)
                
        if exitPoint == ("Far"):
            if (lines %2) != 0:
                parallelShift = ((lines/2) * lineSpacing) 
                lines = lines
            if (lines %2) == 0:
                lines += 1
                parallelShift = ((lines/2) * lineSpacing) 
                

        turn1Bearing, turn2Bearing = turn_bearing(lineBearing, missionDirection)
        totalLines = int(lines*2)
        
        if missionType == "Initial Search":
            turnBearing, turn2Bearing = turn_bearing(lineBearing, "Anti Clockwise")
            wp_start = generate_waypoint(wp_start[0], wp_start[1], (surveyArea/2/1000), turn2Bearing) #using turn2Bearing as inverse turn bearing. will not be used further in initial search pattern
            line = "survey"
            wp_list = [wp_start]
            sentinel = 0
            line_count = 1
            turn = 1
            next_line = "normal"
            surveyTurn = "survey"
            turny = "normal"

            #Create .mp file and write header
            with open("Survey" + surveyTitle + ".mp", "w") as f:
                f.writelines(mpHeader)
                f.close()

            leadIn = generate_waypoint(wp_start[0], wp_start[1], 2, inverseLineBearing)
            write_transit(leadIn[0], leadIn[1], lineBearing, 2000, surveyTitle)
            write_leadin(wp_start[0], wp_start[1], lineBearing, lineLength, surveyTitle)

            #Iterate through each line, generate the line, and append to the .mp file
            for i in range(1, totalLines):

                if surveyTurn == "survey":
                    line = lineName + str(line_count)
                    distance = lineLength
                    if next_line == "normal":
                        course = lineBearing
                        next_line = "inverse"
                    elif next_line == "inverse":
                        course = inverseLineBearing
                        next_line = "normal"
                    line_count +=1
                    surveyTurn = "turn"
                    
                    

                elif surveyTurn == "turn":
                    line = "turn"
                    course = turnBearing
                    turn += 1
                    distance = lineSpacing
                    surveyTurn = "survey"

                
                lat1 = float(wp_list[sentinel][0])
                lon1 = float(wp_list[sentinel][1])
                dist = distance/1000
                wp2 = generate_waypoint(lat1,lon1,dist,course)
                wp_list.append(wp2)
                mp_waypoint = dd_to_dm(wp2)
                             
                course = "(" + (str(course).zfill(3)) + ")"
                distance = "(" + str(distance) + ")"

    
                tag = ":" + str(line)
                depth = "="
                alt = "="
                DMo = "="
                Latitude = str(mp_waypoint[0])
                Longitude = str(mp_waypoint[1])
                course = course
                GMo = "="
                Speed = "="
                SMo = "="
                Dur = "="
                Dist = distance
                lineEntry = f"{tag:10}"+f"{depth:6}"+f"{alt:6}"+f"{DMo:4}"+f"{Latitude:12}"+f"{Longitude:13}"+f"{course:7}"+f"{GMo:3}"+f"{Speed:5}"+f"{SMo:5}"+f"{Dur:7}"+f"{Dist:8}"

                with open("Survey" + surveyTitle + ".mp", "a") as f:
                    f.write(lineEntry + "\n")
                    
            
                
                sentinel +=1
                
                    

            with open("Survey" + surveyTitle + ".mp", "a") as f:  
                f.write(":\n")
                f.close()



        



        if missionType == "Reacquire":
            line = "survey"
            wp_list = [wp_start]
            sentinel = 0
            line_count = 1
            turn = 1
            next_line = "normal"
            surveyTurn = "survey"
            turny = "normal"

            #Create .mp file and write header
            with open("Survey" + surveyTitle + ".mp", "w") as f:
                f.writelines(mpHeader)
                f.close()

            leadIn = generate_waypoint(wp_start[0], wp_start[1], 2, inverseLineBearing)
            write_transit(leadIn[0], leadIn[1], lineBearing, 2000, surveyTitle)
            write_leadin(wp_start[0], wp_start[1], lineBearing, lineLength, surveyTitle)

            #Iterate through each line, generate the line, and append to the .mp file
            for i in range(1, totalLines):

                if surveyTurn == "survey":
                    line = lineName + str(line_count)
                    distance = lineLength
                    if next_line == "normal":
                        course = lineBearing
                        next_line = "inverse"
                    elif next_line == "inverse":
                        course = inverseLineBearing
                        next_line = "normal"
                    line_count +=1
                    surveyTurn = "turn"
                    
                    

                elif surveyTurn == "turn":
                    line = "turn"
                    if turny == "normal":
                        course = turn1Bearing
                        turn += 1
                        turny = "inverse"
                        
                    elif turny == "inverse":
                        course = turn2Bearing
                        turn +=1
                        turny = "normal"


                    if (line_count % 2) == 0:
                        turnRange = (parallelShift - (lineSpacing/2))
                        distance = turnRange

                    if (line_count % 2) != 0:
                        turnRange = (parallelShift + (lineSpacing/2))
                        distance = turnRange
                    surveyTurn = "survey"

                
                lat1 = float(wp_list[sentinel][0])
                lon1 = float(wp_list[sentinel][1])
                dist = distance/1000
                wp2 = generate_waypoint(lat1,lon1,dist,course)
                wp_list.append(wp2)
                mp_waypoint = dd_to_dm(wp2)
                             
                course = "(" + (str(course).zfill(3)) + ")"
                distance = "(" + str(distance) + ")"

    
                tag = ":" + str(line)
                depth = "="
                alt = "="
                DMo = "="
                Latitude = str(mp_waypoint[0])
                Longitude = str(mp_waypoint[1])
                course = course
                GMo = "="
                Speed = "="
                SMo = "="
                Dur = "="
                Dist = distance
                lineEntry = f"{tag:10}"+f"{depth:6}"+f"{alt:6}"+f"{DMo:4}"+f"{Latitude:12}"+f"{Longitude:13}"+f"{course:7}"+f"{GMo:3}"+f"{Speed:5}"+f"{SMo:5}"+f"{Dur:7}"+f"{Dist:8}"

                with open("Survey" + surveyTitle + ".mp", "a") as f:
                    f.write(lineEntry + "\n")
                    
            
                
                sentinel +=1
                
                    

            with open("Survey" + surveyTitle + ".mp", "a") as f:  
                f.write(":\n")
                f.close()






                

            
            
       

            






        



    #######################INITIALISE GUI##################################################
    app = QApplication(sys.argv) #Create instance of QApplication, pass it sys.argv for command line arguments 
    window = QWidget()
    window.setWindowTitle('Mission Shredder')
    window.setGeometry(400, 100, 800, 500)
    missionGenerator = QWidget()


    ########################LIVE CONTROL MODULE####################################
    layout = QGridLayout()
    abspath = os.path.abspath(__file__) 
    dname = (os.path.dirname(abspath))
    os.chdir(dname)
    

    missionTypeList = ["Initial Search", "Reacquire"]
    mpDirectionList = ["Clockwise", "Anti Clockwise"]
    exitPointList = ["Far", "Near"]

    naiCoordLabel = QLabel("Enter NAI lat/lon in (DD:MM.mmmmS, DD:MM.mmmmE):" )
    naiCoordEntry = QLineEdit()
    surveyTitleLabel = QLabel("Enter Survey Title (e.g. 1a): ")
    surveyTitleEntry = QLineEdit()
    missionTypeLabel = QLabel("Select Mission Type: ")
    missionTypeComboBox = QComboBox()
    mpDirectionLabel = QLabel("Select Direction: ")
    mpDirectionComboBox = QComboBox()
    exitPointLabel = QLabel("Select exit type (near = same side as start point): ")
    exitPointComboBox = QComboBox()
    lineBearingLabel = QLabel("Enter first line bearing (°): ")
    lineBearingEntry = QLineEdit()
    searchRadiusLabel = QLabel("Enter Search Radius (m): ")
    searchRadiusEntry = QLineEdit()
    lineSpacingLabel = QLabel("Enter Line Spacing (m): ")
    lineSpacingEntry = QLineEdit()
    runInLabel = QLabel("Enter Run in/Run Out (m): ")
    runInEntry = QLineEdit("30")
        

    for i in missionTypeList:
        missionTypeComboBox.addItem(i)

    for i in mpDirectionList:
        mpDirectionComboBox.addItem(i)

    for i in exitPointList:
        exitPointComboBox.addItem(i)

   
    loadSurvey = QPushButton("Load Survey")
    generateMP = QPushButton("Generate Mission Plan")
    
 


    layout.addWidget(naiCoordLabel, 0, 0)
    layout.addWidget(naiCoordEntry, 0, 1)
    layout.addWidget(surveyTitleLabel, 1, 0)
    layout.addWidget(surveyTitleEntry, 1, 1)
    layout.addWidget(missionTypeLabel, 2, 0)
    layout.addWidget(missionTypeComboBox, 2, 1)
    layout.addWidget(mpDirectionLabel, 3, 0)
    layout.addWidget(mpDirectionComboBox, 3, 1)
    layout.addWidget(exitPointLabel, 4, 0)
    layout.addWidget(exitPointComboBox, 4, 1)
    layout.addWidget(lineBearingLabel, 5, 0)
    layout.addWidget(lineBearingEntry, 5, 1)
    layout.addWidget(searchRadiusLabel, 6, 0)
    layout.addWidget(searchRadiusEntry, 6, 1)
    layout.addWidget(lineSpacingLabel, 7, 0)
    layout.addWidget(lineSpacingEntry, 7, 1)
    layout.addWidget(runInLabel, 8, 0)
    layout.addWidget(runInEntry, 8, 1)
    layout.addWidget(generateMP, 9, 0, 1, 2)
    surveyName = surveyTitleEntry.text()

    generateMP.clicked.connect(lambda: mp_generate(naiCoordEntry.text(), surveyTitleEntry.text(), missionTypeComboBox.currentText(), mpDirectionComboBox.currentText(), exitPointComboBox.currentText(), lineBearingEntry.text(), searchRadiusEntry.text(), lineSpacingEntry.text(), runInEntry.text()))
    


    window.setLayout(layout)
    window.show()
    sys.exit(app.exec_())




