import os, re, math, struct

srtm_name = re.compile(r"([NS])(\d{2})([EW])(\d{3})\.hgt")

def _get_offset(x, y, size):
    return (x + size * (size - y - 1)) * 2

def get_elevation(lat, lon):
    """
    """
    #Prepare lat and lon variables.
    #SRTM filenames use directions, find which dir our lat,lon
    #values belong to.
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
            s = struct.unpack('>h', f.read(2))
            
            #Byte calculations
            f.seek(_get_offset(int_x, int_y, data_size))
            b1 = struct.unpack('>b', f.read(1))
            b2 = struct.unpack('>b', f.read(1))

            print "Fetched struct: %s, at %s.. bytecalc: %s" % (s, f.tell(), (b1[0]*256 + b2[0]))

            return s
            #value00 = (x_int, y_int)
            #value10 = self.getPixelValue(x_int+1, y_int)
            #value01 = self.getPixelValue(x_int, y_int+1)
            #value11 = self.getPixelValue(x_int+1, y_int+1)
    
    else:
        print "File not found"
        return None

def test():
    #Test South East (Requires s04e036.hgt)
    assert get_elevation(-3.2428,36.4761)[0] in (2498, )
    assert get_elevation(-3.001,36.00)[0] in (839, )
    assert get_elevation(-3.9999,36.00)[0] in (1240, )
    assert get_elevation(-3.9999,36.9999)[0] in (1141, )
    assert get_elevation(-3.0001,36.9999)[0] in (1312, )
    #Test North East (Requires n47e009.hgt)
    assert get_elevation(47.2648,9.3515)[0] in (1739, )
    assert get_elevation(47.0,9.0)[0] in (2784, )
    assert get_elevation(47.9995,9.0)[0] in (743, )
    assert get_elevation(47.9995,9.9990)[0] in (649, )
    assert get_elevation(47.0005,9.9990)[0] in (1121, )
    #Test North West (Requires n64e021.hgt)
    assert get_elevation(64.5407, -20.6408)[0] in (1010, )
    assert get_elevation(64.0014, -20.001)[0] in (103, )
    assert get_elevation(64.9995, -20.001)[0] in (782, )
    assert get_elevation(64.9995, -20.9990)[0] in (265, )
    assert get_elevation(64.0014, -20.9990)[0] in (388, )
    #Test South West
    assert get_elevation(-31.2030, -69.8537)[0] in (4569, )
    assert get_elevation(-31.0005, -69.001)[0] in (2223, )
    assert get_elevation(-31.9995, -69.001)[0] in (2047, )
    assert get_elevation(-31.9995, -69.999)[0] in (4780, )
    assert get_elevation(-31.0005, -69.999)[0] in (3486, )

    print "Great Success!"
