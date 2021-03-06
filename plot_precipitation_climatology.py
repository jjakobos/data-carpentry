import pdb
import argparse
import calendar
import warnings

import numpy
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import iris.coord_categorisation
import cmocean

import unit_convert

warnings.filterwarnings('ignore')


#pdb.set_trace  #use n to go to next line of code, c to continue normally


def read_data(fname, month):
    """Read an input data file"""
    
    cube = iris.load_cube(fname, 'precipitation_flux')
    
    iris.coord_categorisation.add_month(cube, 'time')
    cube = cube.extract(iris.Constraint(month=month))
    
    return cube


def plot_data(cube, month, gridlines=False,levels=None):
    """Plot the data."""
        
    plt.figure(figsize=[12,5])    
    iplt.contourf(cube, cmap=cmocean.cm.haline_r, levels=levels,extend='max')

    plt.gca().coastlines()
    if gridlines:
        plt.gca().gridlines()
    cbar = plt.colorbar()
    cbar.set_label(str(cube.units))
    
    title = '%s precipitation climatology (%s)' %(cube.attributes['model_id'], month)
    plt.title(title)

def apply_mask(cube,maskfile,realm):
    sf_cube = iris.load_cube(maskfile,'land_area_fraction')
    cube.data = numpy.ma.asarray(cube.data)
    if realm == 'land':
        cube.data.mask = numpy.where(sf_cube.data > 50, False, True)
    elif realm == 'ocean':
        cube.data.mask = numpy.where(sf_cube.data > 50, True, False)
    else:
        print('Not a valid realm, no mask applied.')
    return cube


def main(inargs):
    """Run the program."""

    cube = read_data(inargs.infile, inargs.month)    
    cube = unit_convert.convert_pr_units(cube)
    clim = cube.collapsed('time', iris.analysis.MEAN)
    if inargs.mask:
        sftlf_file, realm = inargs.mask
        clim = apply_mask(clim,sftlf_file,realm)
    plot_data(clim, inargs.month,gridlines=inargs.gridlines,levels=inargs.cbar_levels)
    plt.savefig(inargs.outfile)


if __name__ == '__main__':
    description='Plot the precipitation climatology for a given month.'
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("month", type=str, choices=calendar.month_abbr[1:], help="Month to plot")
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("-g","--gridlines",action="store_true",default=False,help="Include gridlines on the plot")
    parser.add_argument("--mask", type=str, nargs=2, metavar=('SFTLF_FILE', 'REALM'), default=None, help='Apply a land or ocean mask (specify the realm to mask)')

    parser.add_argument("-l","--cbar_levels",type=float,nargs='*',default=None,help="List of colorbar levels")

    args = parser.parse_args()
    
    main(args)
