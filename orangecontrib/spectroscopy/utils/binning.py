import numpy as np

from Orange.data import Domain, Table

from orangecontrib.spectroscopy.utils import index_values, values_to_linspace, \
    get_hypercube, NanInsideHypercube, InvalidAxisException
from orangecontrib.spectroscopy.utils.skimage.shape import view_as_blocks

def get_coords(data, xat, yat):
    ndom = Domain([xat, yat])
    datam = Table(ndom, data)
    coorx = datam.X[:, 0]
    coory = datam.X[:, 1]

    lsx = values_to_linspace(coorx)
    lsy = values_to_linspace(coory)
    # lsz = data.X.shape[1]

    if lsx is None:
        raise InvalidAxisException("x")
    if lsy is None:
        raise InvalidAxisException("y")

    # set data
    coords = np.ones((lsy[2], lsx[2], 2)) * np.nan

    xindex = index_values(coorx, lsx)
    yindex = index_values(coory, lsy)
    coords[yindex, xindex] = datam.X

    if np.any(np.isnan(coords)):
        raise NanInsideHypercube(np.sum(np.isnan(coords)))
    else:
        return coords

def bin_mean(data, bin_sqrt, n_attrs):
    view = view_as_blocks(data, block_shape=(bin_sqrt, bin_sqrt, n_attrs))
    flatten_view = view.reshape(view.shape[0], view.shape[1], -1, n_attrs)
    mean_view = np.mean(flatten_view, axis=2)
    return mean_view

def bin_hypercube(in_data, xat, yat, bin_sqrt):
    hypercube, lsx, lsy = get_hypercube(in_data, xat, yat)
    n_attrs = len(in_data.domain.attributes)
    assert n_attrs == hypercube.shape[2]      # maybe -1?
    mean_view = bin_mean(hypercube, bin_sqrt, n_attrs)

    coords = get_coords(in_data, xat, yat)
    mean_coords = bin_mean(coords, bin_sqrt, 2)

    table_view = mean_view.reshape(-1, n_attrs)
    table_view_coords = mean_coords.reshape(-1, 2)

    domain = Domain(in_data.domain.attributes, metas=[xat, yat])
    return Table(domain, table_view, metas=table_view_coords)
