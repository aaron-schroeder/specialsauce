"""Creates .tcx file for a fake activity with user-defined features."""
import math
import datetime

import lxml.etree as ET


def time_from_timestring(timestring):
    """Converts .tcx - formatted time string into a datetime object."""
    return datetime.datetime.strptime(timestring[0:19],'%Y-%m-%dT%H:%M:%S')


def timestring_from_time(time):
    """Converts datetime into a formatted string for .tcx file."""
    #return time.strftime('%Y-%m-%dT%H:%M:%S-06:00')
    return time.strftime('%Y-%m-%dT%H:%M:%S.00-06:00')


if __name__ == '__main__':

    # User input.
    file_dir = './activity_files/'
    fname_in = 'template.tcx'
    pace = 8.0  # mins/mile
    grade = 0.00  # decimal grade

    duration = 60.0  # mins
    hr = 130  # bpm
    cadence = 180  # footfalls/min

    mins = math.floor(pace)
    #minstring = '%02d' % int(mins)
    secs = 60*(pace - mins)
    #secstring = '%02d' % int(secs)
    #gradestring = '%02d' % int(grade*100)
    if grade < 0:
        fname_out = '%02dmin_%02d%02d%03d_alt.tcx' % (duration, mins, secs, 100*grade)
    else:
        fname_out = '%02dmin_%02d%02d_%02d_alt.tcx' % (duration, mins, secs, 100*grade)

    # Read in template .tcx file as an etree, which will
    # allow creation of a similar file with fake data.
    tree = ET.parse(file_dir+fname_in)
    root = tree.getroot()  # needed?
    ns = "{%s}" % root.nsmap[None]
    act = root.find(ns+'Activities').find(ns+'Activity')

    # Spoof the date so strava doesn't see a conflict.
    time_0 = datetime.datetime.strptime('1991-05-31T00:00:00',
        '%Y-%m-%dT%H:%M:%S') 
    #time_0 = datetime.datetime.strptime('1991-06-01T00:00:00',
        #'%Y-%m-%dT%H:%M:%S') + datetime.timedelta(int(pace-5))
    date_elem = act.find(ns+'Id')
    date_elem.text = timestring_from_time(time_0)

    # Spoof the name so strava will actually listen to my elevation data.
    # (https://developers.strava.com/docs/uploads/)
    name = act.find(ns+"Creator").find(ns+"Name")
    if 'with barometer' not in name.text:
        name.text = name.text + " with barometer"

    #pt_0 = act.find(ns+'Lap').find(ns+'Track').find(ns+'Trackpoint')
    #time_0 = get_time_tcx(pt_0.find(ns+'Time').text)

    """
    # Read in data from each trackpoint.
    time = [] 
    hr = [] 
    for lap in act.iterfind(ns+'Lap'):
        trk = lap.find(ns+'Track')
        for ix,pt in enumerate(trk.iterfind(ns+'Trackpoint')):
            time_string = pt.find(ns+"Time").text
            time.append((get_time_tcx(time_string) - time_0).total_seconds())
            hr_elem = pt.find(ns+"HeartRateBpm")
            if hr_elem is not None:
                hr_string = hr_elem.find(ns+"Value").text
                hr.append(int(hr_string))
            else:
                hr.append(0)
    """

    ET.strip_elements(act, ns+'Trackpoint')

    # Insert fake elevation and speed data into etree.
    speed_ms = 1609.34/(pace*60.0)
    elev_0 = 6000.0  # initial elevation, meters.

    for lap_index,lap in enumerate(act.iterfind(ns+'Lap')):
        lap.find(ns+'TotalTimeSeconds').text = str(round(duration*60.0,1))
        lap.find(ns+'DistanceMeters').text = str(round(duration*45.0*speed_ms,2))
        lap.find(ns+'MaximumSpeed').text = str(speed_ms)
        lap.attrib['StartTime'] = timestring_from_time(time_0)
        trk = lap.find(ns+'Track')
        distance_total = 0.0
        speeds_ms = []
        grades = []
        #for pt_index,pt in enumerate(trk.iterfind(ns+'Trackpoint')):
        for t in range(0, int(60*duration)+1):
            # Generate a trackpoint at the given time after activity start.
            pt = ET.Element(ns+'Trackpoint')
            time = ET.Element(ns+'Time')
            time.text = timestring_from_time(time_0 + datetime.timedelta(0,t))
            pt.append(time)

            # Determine distance from start, 5 mins moving and 5 mins stopped.
            if math.floor(t/300) % 2 == 0:
                distance_total = distance_total + speed_ms
            else:
                distance_total = distance_total + 0.5*speed_ms
            distance_element = ET.Element(ns+'DistanceMeters')
            distance_element.text = str(distance_total)
            pt.append(distance_element)

            # Spoof that elevation.
            elev_element = ET.Element(ns+'AltitudeMeters')
            elev_element.text = str(elev_0 + distance_total*grade)
            pt.append(elev_element)

            # # Add some data fields to be convincing.
            # hr_element = ET.Element(ns+'HeartRateBpm')
            # value_element = ET.Element(ns+'Value')
            # value_element.text = str(hr)
            # hr_element.append(value_element)
            # pt.append(hr_element)

            # # Create extension element that can contain 
            # # speed and cadence.
            # extensions_element = ET.Element(ns+"Extensions")
            # tpx_element = ET.Element(ns+"TPX")
            # tpx_element.attrib['xmlns'] = root.nsmap['ns3']

            # # Insert a fake cadence value, half of actual value.
            # cadence_element = ET.Element(ns+"RunCadence")
            # cadence_element.text = str(int(0.5*cadence))
            # tpx_element.append(cadence_element)

            # Insert a fake speed value. Steady-state speed in m/s.
            #speed_element = ET.Element(ns+"Speed")
            if math.floor(t/300) % 2 == 0:
                #speed_element.text = str(speed_ms)
                speeds_ms.append(speed_ms)
                grades.append(grade)
            else:
                #speed_element.text = str(0.0)
                speeds_ms.append(0.5*speed_ms)
                grades.append(grade)
            #tpx_element.append(speed_element)

            # extensions_element.append(tpx_element)
            # pt.append(extensions_element)
        
            # distance_element = ET.Element(ns+'DistanceMeters')
            # distance_element.text = str(distances[t])

            # # Plug in the elevation value at this spot
            # elev_element = ET.Element(ns+"AltitudeMeters")
            # elev_element.text = str(round(elevs[lap_index][pt_index],1))
            # pt.append(elev_element)

            trk.append(pt)

    # Write a new file that can fool strava/trainingpeaks/garmin/goldencheetah.
    tree.write(file_dir+fname_out, pretty_print=True, xml_declaration=True,encoding='UTF-8')
