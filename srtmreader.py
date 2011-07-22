import os, math, struct

def _get_offset(x, y, size):
    """
    Get x,y offset in bytes.
    """
    return (x + size * (size - y - 1)) * 2

def _weighted_avg(value1, value2, weight):
    return value2 * weight + value1 * (1 - weight)

def get_elevation(lat, lon, interpolation=False):
    """
    Read elevation data from SRTM file for a point (lat,lon). 
    """
    #Prepare lat and lon variables.
    #Find which directions our lat,lon values belong to.
    lon_dir = 'w' if lon < 0 else 'e'
    lat_dir = 's' if lat < 0 else 'n'
    int_lat = int(lat)
    int_lon = int(lon)
    frac_lat = int_lat - lat
    frac_lon = int_lon - lon
 
    srtm_path = 'data/%s%02d%s%03d.hgt' % (lat_dir, abs(math.floor(lat)), lon_dir, abs(math.floor(lon)))
    print "Search path: %s" % srtm_path
    print "lat: %s, lon: %s" % (lat, lon)
    print "int_lat: %s, int_lon: %s" % (int_lat, int_lon)
    print "frac_lat: %s, frac_lon: %s" % (frac_lat, frac_lon)

    #Check if file for lat,lon exists.
    if os.path.isfile(srtm_path):
        with open(srtm_path, 'rb') as f:
            f.seek(0, 2)
            file_size = f.tell()
            data_size = int(math.sqrt(file_size/2)) # 2 bytes per sample
            print "file_size: %s, data_size: %s" % (file_size, data_size)
            #Currently only SRTM3 is supported
            if data_size not in (1201,):
                return None
    
            if frac_lon > 0:
                x = (1 - frac_lon) * data_size 
            else:
                x = abs(frac_lon) * data_size

            if frac_lat > 0:
                y = (1 - frac_lat) * data_size
            else:
                y = abs(frac_lat) * data_size

            print "x: %s, y: %s" % (x,y)
            int_x = int(x)
            frac_x = x - int_x
            int_y = int(y)
            frac_y = y - int_y
            print "Offset is %f" % _get_offset(int_x, int_y, data_size)

            f.seek(_get_offset(int_x, int_y, data_size))
            #Read a big endian 16bit signed integer from file.
            s = struct.unpack('>h', f.read(2))[0]
            
            print "Fetched struct: %s, at %s.." % (s, f.tell())

            if interpolation:
                #Take weighted average of the 4 nearest observations
                f.seek(_get_offset(int_x + 1, int_y, data_size))
                i1 = struct.unpack('>h', f.read(2))[0]
                print "Interbjudd - x: %s y: %s - %s" % (int_x+1, int_y, i1)
                f.seek(_get_offset(int_x, int_y + 1, data_size))
                i2 = struct.unpack('>h', f.read(2))[0]
                print "Interbjudd - x: %s y: %s - %s" % (int_x, int_y+1, i2)
                f.seek(_get_offset(int_x + 1, int_y + 1, data_size))
                i3 = struct.unpack('>h', f.read(2))[0]
                print "Interbjudd - x: %s y: %s - %s" % (int_x+1, int_y+1, i3)
                s = _weighted_avg(_weighted_avg(s, i1, frac_x), _weighted_avg(i2, i3, frac_x), frac_y)

            return s
    else:
        print "File not found"
        return None

def test():
    """
    For all directions test all corners and a random point.
    """
    #Test South East (Requires s04e036.hgt)
    assert get_elevation(-3.2428,36.4761) in (2498, )
    assert get_elevation(-3.001,36.00) in (839, )
    assert get_elevation(-3.9999,36.00) in (1240, )
    assert get_elevation(-3.9999,36.9999) in (1141, )
    assert get_elevation(-3.0001,36.9999) in (1312, )
    #Test North East (Requires n47e009.hgt)
    assert get_elevation(47.2648,9.3515) in (1739, )
    assert get_elevation(47.0,9.0) in (2784, )
    assert get_elevation(47.9995,9.0) in (743, )
    assert get_elevation(47.9995,9.9990) in (649, )
    assert get_elevation(47.0005,9.9990) in (1121, )
    #Test North West (Requires n64e021.hgt)
    assert get_elevation(64.5407, -20.6408) in (1010, )
    assert get_elevation(64.0014, -20.001) in (103, )
    assert get_elevation(64.9995, -20.001) in (782, )
    assert get_elevation(64.9995, -20.9990) in (265, )
    assert get_elevation(64.0014, -20.9990) in (388, )
    #Test South West (Requires s32w70.hgt)
    assert get_elevation(-31.2030, -69.8537) in (4569, )
    assert get_elevation(-31.0005, -69.001) in (2223, )
    assert get_elevation(-31.9995, -69.001) in (2047, )
    assert get_elevation(-31.9995, -69.999) in (4780, )
    assert get_elevation(-31.0005, -69.999) in (3486, )

    print "Great Success!"
