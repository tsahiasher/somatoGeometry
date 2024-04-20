import numpy as np
from nilearn import datasets, plotting, surface
from loadmat import load_mat, pickle_load, pickle_dump, view_save_as_html, path_exists
from draw_data_map import cont_cmap, cyclic_cont_cmap, bg_maps

NUM_OF_VERTICES = 163842

fsaverage = datasets.fetch_surf_fsaverage('fsaverage')

side = {'lh': 'left', 'rh': 'right'}


def get_parc_vertices(hemi, parcAreas):
    vert = []
    parc = load_mat(f'./data/HCP_180_POIs_{hemi}.mat', use_main_folder=False)
    areaNames = [i[0].item() for i in parc[:, 4]]
    for n in parcAreas:
        vert.extend(parc[areaNames.index(f'{hemi[0].upper()}_{n}_ROI'), 1].squeeze())
    return np.array(vert)

# get nGenNeighbors gen of vertex out of neighbors list
# exclude vertices of lower gen than nGenNeighbors
# exclude vertices that are not in vertices list
def get_vertex_neighbors(vertex, nGenNeighbors, neighbors, vertices):
    vertexNeighbors = [vertex]
    removeList = np.array([vertex])
    for j in range(nGenNeighbors):
        tmpList = np.array([]).astype(np.int32)
        for k in vertexNeighbors:
            tmpList = np.concatenate((tmpList, np.array(neighbors[k])))

        if j < nGenNeighbors - 1:
            removeList = np.concatenate((removeList, tmpList))
        vertexNeighbors = np.unique(tmpList)

    removeList = np.unique(removeList)
    # return only the Neighbors vertices that are in vertices list and NOT in removeList
    if vertices is None:
        return list(vertexNeighbors[np.invert(np.isin(vertexNeighbors, removeList))])
    else:
        return list(vertexNeighbors[np.logical_and(np.isin(vertexNeighbors, vertices),
                                                   np.invert(np.isin(vertexNeighbors, removeList)))])


# get nGenNeighbors gen of vertex out of neighbors list
# include vertices of lower gen than nGenNeighbors
# exclude vertices that are not in vertices list
def get_vertex_neighbors_no_remove(vertex, nGenNeighbors, neighbors, vertices):
    # vertexNeighbors hold gen i of neighbors. start with i = 0
    vertexNeighbors = [vertex]
    fullList = np.array([]).astype(np.int32)
    for j in range(nGenNeighbors):
        tmpList = np.array([]).astype(np.int32)
        # create a list with all neighbors of neighbors
        for k in vertexNeighbors:
            tmpList = np.concatenate((tmpList, np.array(neighbors[k])))
        # add neighbors of neighbors to full list
        fullList = np.unique(np.concatenate((fullList, vertexNeighbors)))
        # to save the time, we do not need next gen neighbors in the last loop
        if j < nGenNeighbors - 1:
            # next gen neighbors. Take only new neighbors from tmpList
            # np.unique([x for x in tmpList if x not in fullList]).astype(np.int)
            vertexNeighbors = np.unique(tmpList[np.invert(np.isin(tmpList, fullList))]).astype(np.int32)
    # add last gen of neighbors
    fullList = np.unique(np.concatenate((fullList, tmpList)))
    # remove main vertex
    fullList = np.delete(fullList, np.argwhere(fullList == vertex).squeeze())
    # return full list indices only if exist in vertices list
    # [x for x in fullList if x in vertices]
    if vertices is None:
        return list(fullList)
    else:
        return list(fullList[np.isin(fullList, vertices)])


def get_neighbors(nGenNeighbors=1, vertices=None, hemi='lh', name=''):
    NZ_str = 'NZ' if vertices is not None else ''
    use_main_folder = True if vertices is not None else False
    if vertices is None:
        name = ''
    fname = f'{name}{NZ_str}neighbors{nGenNeighbors}_{hemi}.pklz'
    if path_exists(fname, use_main_folder):
        return pickle_load(fname, use_main_folder)

    neighbors = pickle_load('./data/neighbors.pklz', use_main_folder=False)
    if vertices is not None:
        findNeighbors = vertices
        for i in neighbors:
            addVertexNeighbors = np.array(neighbors[i])
            addVertexNeighbors = addVertexNeighbors[np.isin(addVertexNeighbors, vertices)]
            neighbors[i] = addVertexNeighbors
    else:
        findNeighbors = neighbors
    genNeighbors = {}

    for i in findNeighbors:
        genNeighbors[i] = get_vertex_neighbors_no_remove(i, nGenNeighbors, neighbors, vertices)

    pickle_dump(fname, genNeighbors,
                True, use_main_folder)

    return genNeighbors


def draw_surface(surfData, hemi='lh', surf='multi', scale=False, cmap=cyclic_cont_cmap, colorbar_height=0.6, title='',
                 saveName=None, show=True, threshold=None, return_info=False, bg_map=None, colorbar=True, dtype=np.int8,
                 vmax=None, vmin=None,
                 darkness=None):
    if isinstance(surfData, str):
        if not surfData.endswith('gii'):
            surfData = load_mat(surfData).astype(dtype)
        else:
            surfData = surface.load_surf_data(surfData)

    if scale:
        surfData[np.nonzero(surfData)] = np.interp(surfData[np.nonzero(surfData)],
                                                   (np.min(surfData[np.nonzero(surfData)]), surfData.max()), (-1, 1))

    if bg_map is None:
        bg_map = bg_maps[hemi]

    if threshold is None:
        threshold = 0.000001

    if surf == 'multi':
        view = plotting.view_multi_surf(fsaverage, surfData, colorbar_height=colorbar_height, threshold=threshold,
                                        bg_map=bg_map, cmap=cmap, colorbar=colorbar, symmetric_cmap=False, title=title,
                                        return_info=return_info, vmax=vmax, vmin=vmin, side=side[hemi],
                                        darkness=darkness)
    else:
        view = plotting.view_surf(fsaverage[f'{surf}_{side[hemi]}'], surfData, threshold=threshold, bg_map=bg_map,
                                  cmap=cmap, colorbar=colorbar, symmetric_cmap=False,
                                  title=title, side=side[hemi], colorbar_height=colorbar_height,
                                  return_info=return_info, darkness=darkness)
    if return_info:
        return view
    if show:
        view.open_in_browser()
    if saveName is not None:
        view_save_as_html(view, f'{saveName}.html')


def add_map(info, surfMap, hemi='lh', cmap='binary', threshold=0.000001, return_info=False, saveName=None,
            colorbar=False):
    if surfMap.size:
        view = plotting.add_map(info, surfMap, side[hemi], threshold=threshold, cmap=cmap, symmetric_cmap=False,
                                return_info=return_info,
                                colorbar=colorbar, colorbar_height=0.6, vmin=None, vmax=None)
    else:
        if return_info:
            return info
        view = plotting.info_to_view(info, side[hemi])

    if return_info:
        return view
    else:
        view.open_in_browser()
        if saveName is not None:
            view_save_as_html(view, f'{saveName}.html')

def clusterize(hemi, mask, minSize, cmap=cont_cmap):
    sigInd = mask.astype(bool)
    clusters = np.zeros_like(sigInd, dtype='uint32')
    neighbors = get_neighbors(hemi=hemi, name='')
    next_cluster = 1
    freeClusters = []
    for i in range(NUM_OF_VERTICES):
        if sigInd[i]:
            if clusters[i]:
                cur_cluster = clusters[i]
            else:
                if len(freeClusters):
                    cur_cluster = freeClusters.pop()
                else:
                    cur_cluster = next_cluster
                    next_cluster += 1
                clusters[i] = cur_cluster
            for j in neighbors[i]:
                if sigInd[j]:
                    if clusters[j]:
                        if cur_cluster < clusters[j]:
                            freeClusters.append(clusters[j])
                            clusters[clusters == clusters[j]] = cur_cluster
                        elif cur_cluster > clusters[j]:
                            freeClusters.append(cur_cluster)
                            clusters[clusters == cur_cluster] = clusters[j]
                            cur_cluster = clusters[j]
                    else:
                        clusters[j] = cur_cluster

    num = []
    j = 0
    for i in np.sort(np.unique(clusters)):
        if np.sum(clusters == i) < minSize:
            num.append(np.sum(clusters == i))
            sigInd[clusters == i] = 0
        else:
            j += 1
    draw_surface(sigInd, hemi, cmap=cmap)
    return sigInd


def smooth_map(hemi, surfMap, repeat):
    neighbors = pickle_load('./data/neighbors.pklz', use_main_folder=False)
    sigInd = load_mat(rf'./sigInd_{hemi}.mat').astype(bool)
    zeroInd = np.where(surfMap == 0)[0]
    # need a vertex with zero value
    if zeroInd.size:
        zeroIdx = zeroInd[0]
    else:
        zeroIdx = 0
        surfMap[0] = 0

    newNeighborsList = []
    # add vertexid to the vertex neighbors list as first index (location is important)
    # all lists should be length of 6 so if vertex had only 5
    # add to end of the list a vertex with value 0
    for i in np.where(sigInd)[0]:
        temp = [i]
        temp.extend(neighbors[i])
        if len(neighbors[i]) == 5:
            temp.extend([zeroIdx])
        newNeighborsList.append(temp)
    neighbors = np.array(newNeighborsList)
    delta = []
    for i in range(repeat):
        newMap = np.zeros_like(surfMap)
        # mean of all non zero values
        newMap[neighbors[:, 0]] = np.sum(surfMap[neighbors], axis=1) / np.sum(surfMap[neighbors] != 0, axis=1)
        newMap[~sigInd] = 0
        newMap[np.isnan(newMap)] = 0
        surfMap = newMap
    return surfMap