import os

def main():
    rootdir = '/home/ywkim/seaside/geotiff/earthquake/utm'
    outdir = '/home/ywkim/seaside/geotiff/earthquake/geo'

    for file in os.listdir(rootdir):
        infile = os.path.join(rootdir, file)
        outfile = os.path.join(outdir, file)
        cmdline = 'gdalwarp ' + infile + " " + outfile + "- t_srs \"+proj=longlat +ellps=WGS84\""
        os.sys(cmdline)
        print(os.path.join(rootdir), file)


if __name__ == "__main__":
    main()