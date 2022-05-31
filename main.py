import sys
from PyQt5.QtWidgets import *
import random
from gui import Ui_MainWindow
from PyQt5 import QtGui, QtCore,QtWidgets
from coloring import Coloring
items = []
graph = {}
class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.scene = Scene()
        self.graphicsView.setScene(self.scene)
        self.len = 0
        self.pushButton.clicked.connect(self.addEdge)
        self.pushButton_3.clicked.connect(self.colorEdges)

    def addEdge(self):
        item = CustomItem(left=True)
        items.append(item)
        self.scene.addItem(item)



    def colorEdges(self):
        sortedGraph = []
        for i in sorted(list(graph.keys())):
            sortedGraph.append(graph[i])
        colors = {}
        setSolors = Coloring(sortedGraph)
        coloring = setSolors.greedyColoring()
        for color in set(coloring):
            colors[color] = [random.randint(0, 255),random.randint(0, 255),random.randint(0, 255)]
        for edge in range(len(coloring)):
            numColor = coloring[edge]
            colorRGB = colors[numColor]
            items[edge].setBrush(QtGui.QBrush(QtGui.QColor(colorRGB[0], colorRGB[1],colorRGB[2])))
        self.plainTextEdit.setPlainText(f'Z(G) = {len(set(coloring))}')

class Connection(QtWidgets.QGraphicsLineItem):
    def __init__(self, start, p2):
        super().__init__()
        self.start = start
        self.end = None
        self._line = QtCore.QLineF(start.scenePos(), p2)
        self.setLine(self._line)


    def controlPoints(self):
        return self.start, self.end

    def setP2(self, p2):
        self._line.setP2(p2)
        self.setLine(self._line)

    def setStart(self, start):
        self.start = start
        self.updateLine()

    def setEnd(self, end):


        self.end = end
        self.updateLine(end)

    def updateLine(self, source):
        if source == self.start:
            self._line.setP1(source.scenePos())
        else:
            self._line.setP2(source.scenePos())
        self.setLine(self._line)


class ControlPoint(QtWidgets.QGraphicsEllipseItem):
    def __init__(self, parent, onLeft):
        super().__init__(-50, -50, 100, 100, parent)

        self.onLeft = onLeft
        self.lines = []
        # this flag **must** be set after creating self.lines!
        self.setFlags(self.ItemSendsScenePositionChanges)

    def addLine(self, lineItem):
        for existing in self.lines:
            if existing.controlPoints() == lineItem.controlPoints():
                # another line with the same control points already exists
                return False
        self.lines.append(lineItem)
        return True

    def removeLine(self, lineItem):
        for existing in self.lines:
            if existing.controlPoints() == lineItem.controlPoints():
                self.scene().removeItem(existing)
                self.lines.remove(existing)
                return True
        return False

    def itemChange(self, change, value):
        for line in self.lines:
            line.updateLine(self)
        return super().itemChange(change, value)


class CustomItem(QtWidgets.QGraphicsItem):
    pen = QtGui.QPen(QtCore.Qt.white, 2)
    penControl = QtGui.QPen(QtCore.Qt.black, 2)
    brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
    controlBrush = QtGui.QBrush(QtGui.QColor(0,0, 0))
    rect = QtCore.QRectF(50, -15, 100, 100)


    def __init__(self, left=False, right=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setFlags(self.ItemIsMovable)


        self.controls = []
        for onLeft, create in enumerate((right, left)):
            if create:
                self.control = ControlPoint(self, onLeft)
                self.controls.append(self.control)
                self.control.setPen(self.pen)
                self.control.setBrush(self.controlBrush)
                if onLeft:
                    self.control.setX(100)
                self.control.setY(35)

    def boundingRect(self):
        adjust = self.pen.width()
        return self.rect.adjusted(-adjust, -adjust, adjust, adjust)

    def paint(self, painter, option, widget=None):
        painter.save()

        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        painter.drawRoundedRect(self.rect, 4, 4)


        painter.restore()

    def setBrush(self, brush):
        self.control.setBrush(brush)






class Scene(QtWidgets.QGraphicsScene):
    startItem = newConnection = None
    def controlPointAt(self, pos):
        mask = QtGui.QPainterPath()
        mask.setFillRule(QtCore.Qt.WindingFill)
        for item in self.items(pos):
            if mask.contains(pos):
                # ignore objects hidden by others
                return
            if isinstance(item, ControlPoint):
                return item
            if not isinstance(item, Connection):
                mask.addPath(item.shape().translated(item.scenePos()))

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            item = self.controlPointAt(event.scenePos())
            if item:
                self.startItem = item
                self.newConnection = Connection(item, event.scenePos())
                self.addItem(self.newConnection)
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if (item and item != self.startItem and
                self.startItem.onLeft != item.onLeft):
                    p2 = item.scenePos()
            else:
                p2 = event.scenePos()
            self.newConnection.setP2(p2)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.newConnection:
            item = self.controlPointAt(event.scenePos())
            if item and item != self.startItem:
                self.newConnection.setEnd(item)


                if self.startItem.addLine(self.newConnection):
                    for i in range(0,len(items)):
                        if items[i] == item.parentItem() :
                            u = i
                        if items[i] == self.startItem.parentItem():
                            v = i
                    if u in graph.keys():
                        graph[u].append(v)
                    else:
                        graph[u] = [v]
                    if v in graph.keys():
                        graph[v].append(u)
                    else:
                        graph[v] = [u]
                    global sortedGraph

                    item.addLine(self.newConnection)
                else:

                    self.startItem.removeLine(self.newConnection)
                    self.removeItem(self.newConnection)
            else:
                self.removeItem(self.newConnection)
        self.startItem = self.newConnection = None
        super().mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)



    view = MainWindow()
    view.setMouseTracking(True)

    view.show()

    sys.exit(app.exec_())


