import numpy as np
import argparse
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from tkinter import filedialog
from loadmat import load_mat, view_save_as_html
from nilearn import datasets, surface, plotting
import matplotlib.pyplot as plt

body_colors = ['darkblue', 'blue', 'cyan', 'green', 'lawngreen', 'yellow', 'orange', 'red']
cont_body_cmap = LinearSegmentedColormap.from_list("cont_body_cmap", body_colors)
cont_body_cmap_r = cont_body_cmap.reversed()

disc_cmap = ListedColormap(body_colors, name='disc_cmap')
disc_cmap_r = disc_cmap.reversed()
disc_white_cmap = ListedColormap(['white'] + body_colors, name='disc_white_cmap')

red_cmap = ListedColormap(['red', 'red'], name='red_cmap')

colors = ['darkblue', 'blue', 'cyan', 'green', 'lawngreen', 'yellow', 'gold', 'orange', 'red', 'darkred']
cont_cmap = LinearSegmentedColormap.from_list("cont_cmap", colors)

cont_cmap_r = cont_cmap.reversed()

cyclic_colors = ['darkblue', 'blue', 'cyan', 'darkgreen', 'green', 'lime', 'orange', 'orangered', 'red', 'darkred',
                 'red', 'orangered', 'orange',
                 'goldenrod', 'gold', 'yellow', 'cyan', 'blue', 'darkblue']
cyclic_cont_cmap = LinearSegmentedColormap.from_list("cyclic_cont_cmap", cyclic_colors)

# rotate hsv such that the red and not cyan is in the middle
# get hsv cm, call it with a rotated list from 0-1 to return the color values
# and create from it a new colormap
rotated_hsv = ListedColormap(plt.colormaps['hsv'](np.flip(np.roll(np.linspace(0, 1, 256), 128))))

fsaverage = datasets.fetch_surf_fsaverage('fsaverage')

bg_map_lh = surface.load_surf_data('./data/lh.avg_curv')
bg_map_lh[bg_map_lh >= 0] = 0.75
bg_map_lh[bg_map_lh < 0] = 0.5
bg_map_lh[0] = 0
bg_map_lh[1] = 1

bg_map_rh = surface.load_surf_data('./data/rh.avg_curv')
bg_map_rh[bg_map_rh >= 0] = 0.75
bg_map_rh[bg_map_rh < 0] = 0.5
bg_map_rh[0] = 0
bg_map_rh[1] = 1

bg_maps = {'lh': bg_map_lh, 'rh': bg_map_rh}

side = {'lh': 'left', 'rh': 'right'}

def draw_data_map(mapName, hemi=None, fname=None, title='', cmap=cont_cmap, surf='multi', sigInd=None, interData=False,
                  vMin=None, vMax=None, threshold=0.00001, colorbar=True):
    if isinstance(mapName, str):
        if not mapName.endswith('gii'):
            mapNameWords = mapName.lower().replace('.', '_').replace('\\', '_').replace('/', '_').split('_')
            if hemi is None:
                if 'lh' in mapNameWords:
                    hemi = 'lh'
                if 'rh' in mapNameWords:
                    hemi = 'rh'

                if 'disc' in mapNameWords:
                    cmap = disc_cmap
                elif 'body' in mapNameWords:
                    cmap = cont_body_cmap

            xData = load_mat(mapName)
        else:
            xData = surface.load_surf_data(mapName)
    else:
        xData = mapName

    xData[np.isnan(xData)] = 0
    if sigInd is not None:
        xData[~sigInd] = 0
    else:
        sigInd = np.nonzero(xData)[0]
    if interData:
        xData[sigInd] = np.interp(xData[sigInd], (xData[sigInd].min(), xData[sigInd].max()), (1, 8))

    if vMin:
        if vMin > 0:
            xData[np.where((xData < vMin) & (xData > 0))] = vMin
        else:
            xData[xData < vMin] = vMin
    if threshold == -180.5:
        vMin = -180
        vMax = 180

    if vMax:
        xData[xData > vMax] = vMax
    if xData.min() < 0 and threshold == 0.00001:
        threshold = xData.min() - 1
        xData[xData == 0] = threshold - 0.1

    bg_map = bg_maps[hemi]

    if surf == 'multi':
        view = plotting.view_multi_surf(fsaverage, xData, colorbar_height=0.6, threshold=threshold, bg_map=bg_map,
                                        cmap=cmap, colorbar=colorbar, symmetric_cmap=False, title=title, vmax=vMax,
                                        vmin=vMin, side=side[hemi], darkness=None)
    else:
        view = plotting.view_surf(fsaverage[f'{surf}_{side[hemi]}'], xData, threshold=threshold, bg_map=bg_map,
                                  cmap=cmap, colorbar=colorbar, symmetric_cmap=False, title=title, side=side[hemi],
                                  colorbar_height=0.6, darkness=None)
    if fname is not None:
        view_save_as_html(view, f'{fname}.html')
    view.open_in_browser()


class getSigInd(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str) and 'mat' in values:
            tmp = load_mat(values)
            if tmp.max() != 1:
                sigInd = np.nonzero(tmp)[0]
            else:
                sigInd = tmp.astype(bool)
        else:
            sigInd = eval(values)
        setattr(namespace, self.dest, sigInd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='draw_data_map',
        description='Wrapper for draw_surface function. Draws a surface map of data')
    parser.add_argument('--mapName', help='Name of the map to draw')
    parser.add_argument('--hemi', help='Side of the brain', choices=['lh', 'rh'])
    parser.add_argument('--fname', help='Name of the file to save the map to')
    parser.add_argument('--cmap', help='Colormap to use', default='cont_cmap')
    parser.add_argument('--surf', help='Surface to draw on', default='multi', choices=['multi', 'infl', 'pial', 'flat'])
    parser.add_argument('--sigInd', help='Indices of significant voxels', action=getSigInd)
    parser.add_argument('--interData', help='Interpolate data to 1-8', action='store_true')
    parser.add_argument('--vMin', help='Minimum value of the colormap', type=float)
    parser.add_argument('--vMax', help='Maximum value of the colormap', type=float)
    parser.add_argument('--threshold', help='Threshold value for the colormap', default=0.00001, type=float)
    parser.add_argument('--title', help='Title of the map', default='')
    parser.add_argument('--colorbar', help='Draw a colorbar', action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    if args.mapName is None:
        args.mapName = filedialog.askopenfilename(title='Select map to draw', filetypes=[('Matlab files', '*.mat')],
                                                  initialdir='./')
        if args.fname is None:
            parser.print_help()
            exit()
    draw_data_map(args.mapName, hemi=args.hemi, fname=args.fname, cmap=eval(args.cmap), surf=args.surf,
                  sigInd=args.sigInd, interData=args.interData,
                  vMin=args.vMin, vMax=args.vMax, threshold=args.threshold, title=args.title, colorbar=args.colorbar)
