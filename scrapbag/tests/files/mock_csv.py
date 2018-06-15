# -*- coding: utf-8 -*-
"""
Mock csv classes module
"""


class MockCell():
    """
    Class to mock excel cells..
    """
    def __init__(self, value):
        self.value = value


class MockSheet():
    """
    Class to mock excel cells..
    """

    def __init__(self, cells, merged_cells=None):

        self.cells = [[MockCell(xcell) for xcell in ycell] for ycell in cells]
        self.ncols = max([len(row) for row in self.cells])
        self.nrows = len(self.cells)
        self.merged_cells = [] if merged_cells is None else merged_cells

    def cell(self, x_cell, y_cell):
        """
        Cell getter
        Returns: value in the list corresponding to the parameters introduced.
        """
        return self.cells[x_cell][y_cell]
