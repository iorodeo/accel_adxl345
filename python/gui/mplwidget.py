from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        self.axesDict= {}
        self.axesDict['x'] = self.fig.add_subplot(311)
        self.axesDict['y'] = self.fig.add_subplot(312)
        self.axesDict['z'] = self.fig.add_subplot(313)
        FigureCanvas.__init__(self,self.fig)
        FigureCanvas.setSizePolicy(
                self, 
                QtGui.QSizePolicy.Expanding, 
                QtGui.QSizePolicy.Expanding
                )
        FigureCanvas.updateGeometry(self)


class MplWidget(QtGui.QWidget):

    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.canvas = MplCanvas()
        self.vbl = QtGui.QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)

