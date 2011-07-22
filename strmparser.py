import os, re, math, struct

srtm_name = re.compile(r"([NS])(\d{2})([EW])(\d{3})\.hgt")

def _get_offset(x, y, size):
    return (x + size * (size - y - 1)) * 2

def get_elevation(lat, lon):
    #Prepare lat and lon variables.
    #SRTM filenames use directions, find which dir our lat,lon
    #values belong to.
    lon_dir = 'w' if lon < 0 else 'e'
    lat_dir = 's' if lat < 0 else 'n'
    int_lat = int(lat)
    int_lon = int(lon)
    frac_lat = int_lat - lat
    frac_lon = int_lon - lon
    srtm_path = 'data/%s%02d%s%03d.hgt' % (lat_dir, abs(int_lat), lon_dir, abs(int_lon))
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
    
            x = abs(frac_lon * data_size)
            y = abs(frac_lat * data_size)
            print "x: %s, y: %s" % (x,y)
            int_x = int(x)
            frac_x = x - int_x
            int_y = int(y)
            frac_y = y - int_y
            print "Offset is %s" % _get_offset(int_x, int_y, data_size)

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
