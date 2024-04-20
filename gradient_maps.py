import numpy as np
from scipy import linalg
import matplotlib.pyplot as plt
import seaborn as sns
from gradient_utils import get_neighbors, draw_surface
from draw_data_map import rotated_hsv
from nilearn import datasets, surface
from loadmat import save_mat, save_fig, load_mat, set_folder


def draw_hist(angles, sigInd, title='', fname='histogram', plotRange=np.arange(-180, 181, 90), xLabel='Angle'):
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.histplot(angles[sigInd], kde=False, stat='count', bins=180, ax=ax, color='black')
    ax.set_xlabel(xLabel, fontdict={'size': 24})
    ax.set_ylabel('Count', fontdict={'size': 24})
    ax.set_title(title, fontdict={'size': 24})
    if plotRange is not None:
        ax.set_xticks(plotRange)
    ax.tick_params(labelsize=24)
    if fname is not None:
        save_fig(plt, fname)
    plt.show()
    # plt.close()


def calc_angles(xData, yData, sigInd, srfCoordinates, neighbors, normals):
    gradX = np.zeros_like(srfCoordinates)
    gradY = np.zeros_like(srfCoordinates)

    validInd = []
    for i in sigInd:
        # find neighbors of vertex
        listNeighbors = neighbors.get(i)
        # because we use only sigInd it is possible to get
        # 1. only neighbors which are outside the sigInd
        # 2. neighbors which are only on one side of region
        if np.sum(xData[listNeighbors]) == 0 or np.sum(yData[listNeighbors]) == 0 or \
                len(np.unique(xData[listNeighbors])) == 1 or len(np.unique(yData[listNeighbors])) == 1:
            continue

        if listNeighbors:
            norm = normals[i]

            # project all vertex in area onto a plane tangent to the surface at the main vertex's location.
            # normalize by the main vertex coordinates. Centralize all vertices values around the main vertex.
            # Calculate gradient by fitting a best-fit line via a linear regression model, considering the centralized values
            # and their 2D projected coordinates

            # project vertex to plane by projecting the vector from a vertex to the centroid onto the normal
            # multiply by the normal to find the projected vector onto the normal and subtract it from the vertex
            projCoor = srfCoordinates[listNeighbors] - norm * (srfCoordinates[listNeighbors] @ norm).reshape(-1, 1)
            iCoor = srfCoordinates[i] - norm * (srfCoordinates[i] @ norm).reshape(-1, 1)
            projCoor -= iCoor
            pinvCoor = linalg.pinv(projCoor.T @ projCoor) @ projCoor.T

            # relx/y is a 6 (or number of neighbors) components vector that each one is the
            # difference in sel\lat value between the neighbor and the center
            relX = xData[listNeighbors] - xData[i]
            gradX[i] = pinvCoor @ relX
            relY = yData[listNeighbors] - yData[i]
            gradY[i] = pinvCoor @ relY
            validInd.append(i)

    if len(validInd) == 0:
        return [], [], [], []
    validInd = np.array(validInd)
    # not sure if the next 2 lines are necessary
    gradX[~np.isin(np.arange(len(gradX)), validInd)] = 0
    gradY[~np.isin(np.arange(len(gradY)), validInd)] = 0

    # calc angles between two gradients between 0-180
    cross = np.cross(gradX, gradY)
    angles = np.degrees(np.arctan2(np.linalg.norm(cross, axis=1), np.sum(gradY * gradX, axis=1)))
    zero_cross = np.intersect1d(np.where(np.linalg.norm(cross, axis=1) == 0)[0], validInd)
    validInd = np.setdiff1d(validInd, zero_cross)

    # calc angles between -180-180
    direct = np.sign(np.sum(normals * cross, axis=1))
    direct[direct == 0] = 1
    angles = angles * direct

    return angles, validInd, gradX, gradY


def build_angle_maps(mapName, firstMapDict, secondMapDict, srfCoordinatesDict, normalsDict, saveMaps, hemiList):
    nGenNeighbors = 3

    plotRange = np.arange(-180, 181, 60)
    cmap = rotated_hsv

    for hemi in hemiList:
        firstMapName = firstMapDict.get(hemi)
        secondMapName = secondMapDict.get(hemi)

        xData = load_mat(f'./MapsCalculation/{firstMapName}')
        yData = load_mat(f'./MapsCalculation/{secondMapName}')
        sigInd = np.where(load_mat(f'./MapsCalculation/sigInd_{hemi}.mat'))[0]
        neighbors = get_neighbors(nGenNeighbors=nGenNeighbors, vertices=sigInd, hemi=hemi)

        angles, sigInd, gradX, gradY = calc_angles(xData, yData, sigInd, srfCoordinatesDict[hemi], neighbors, normalsDict[hemi])

        # Set all vertices angles that with no data to -181
        angles[np.setdiff1d(np.arange(angles.shape[0]), sigInd)] = -181

        if saveMaps:
            save_mat(f'./{mapName}_{hemi}.mat', {'angles': angles})
            saveName = f'./{mapName}_{hemi}'
        else:
            saveName = None

        draw_surface(angles, hemi=hemi, title=f'{mapName} {hemi}', cmap=cmap, threshold=-180.5,
                     saveName=saveName, show=True, colorbar=True, vmin=-180, vmax=180)

        draw_hist(angles, sigInd, f'{mapName} {hemi}', fname=saveName, plotRange=plotRange)


def main():
    set_folder('./MaxR/')  # RandomEffect or MaxR
    saveMaps = False
    fsaverage = datasets.fetch_surf_fsaverage('fsaverage')
    hemiList = ['lh', 'rh']
    side = {'lh': 'left', 'rh': 'right'}
    srfCoordinatesDict = {}
    normalsDict = {}
    for hemi in hemiList:
        srfCoordinatesDict[f'{hemi}'] = surface.load_surf_mesh(fsaverage[f'pial_{side[hemi]}'])[0]
        normalsDict[f'{hemi}'] = surface._vertex_outer_normals(fsaverage[f'pial_{side[hemi]}'])

    build_angle_maps(mapName=f'sel800-lat400', hemiList=hemiList, srfCoordinatesDict=srfCoordinatesDict,
                     normalsDict=normalsDict, saveMaps=saveMaps,
                     firstMapDict={'rh': f'sel_rh_800.mat', 'lh': f'sel_lh_800.mat'},
                     secondMapDict={'rh': f'lat_rh_400', 'lh': f'lat_lh_400.mat'})

    for surfMap, smooth in zip(['lat', 'sel'], [400, 800]):
        build_angle_maps(mapName=f'{surfMap}{smooth}-body200', hemiList=hemiList, srfCoordinatesDict=srfCoordinatesDict,
                         normalsDict=normalsDict, saveMaps=saveMaps,
                         firstMapDict={'rh': fr'body_rh_200.mat', 'lh': fr'body_lh_200.mat'},
                         secondMapDict={'rh': f'{surfMap}_rh_{smooth}.mat', 'lh': f'{surfMap}_lh_{smooth}.mat'})


if __name__ == "__main__":
    main()
