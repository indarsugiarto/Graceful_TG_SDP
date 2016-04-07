from PyQt4 import Qt, QtGui

CHIP_LIST_48_0 = [[0,0],[1,0],[2,0],[3,0],[4,0],\
                  [0,1],[1,1],[2,1],[3,1],[4,1],[5,1],\
                  [0,2],[1,2],[2,2],[3,2],[4,2],[5,2],[6,2],\
                  [0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3],[7,3],\
                        [1,4],[2,4],[3,4],[4,4],[5,4],[6,4],[7,4],\
                              [2,5],[3,5],[4,5],[5,5],[6,5],[7,5],\
                                    [3,6],[4,6],[5,6],[6,6],[7,6],\
                                          [4,7],[5,7],[6,7],[7,7]]

CHIP_LIST_48_1 = [[0,0],[1,0],[2,0],[3,0],[4,0],[5,1],[6,2],\
                  [0,1],[1,1],[2,1],[3,1],[4,1],[5,2],[7,3],\
                  [0,2],[1,2],[2,2],[3,2],[4,2],[6,3],[7,4],\
                  [1,3],[2,3],[3,3],[4,3],[5,3],[6,4],[7,5],\
                  [0,3],[2,4],[3,4],[4,4],[5,4],[6,5],[7,6],\
                  [1,4],[3,5],[4,5],[4,6],[5,5],[6,6],[7,7],\
                  [2,5],[3,6],[4,7],[5,7],[5,6],[6,7]]

class visWidget(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        QtGui.QGraphicsView.__init__(self, parent)
        self.scene = QtGui.QGraphicsScene()
        #self.scene.addText("Test")

        self.drawLayout(mode=0)
        #self.drawLayout(mode=1)    # it will produce messy connection!!!
        #self.scene.addRect(0,0,100,100)

        self.setScene(self.scene)
        #self.view = QtGui.QGraphicsView(self.scene, self)
        #self.view.show()


    def drawLayout(self, mode):
        # Draw Spin5 chip layout
        w = 85
        h = 85
        xoffset = 125
        yoffset = -125
        hspace = xoffset-85
        if mode==0:
            # draw as logical layout
            self.chipIDTxt = [QtGui.QGraphicsTextItem() for _ in range(48)]
            self.edges = [[QtGui.QGraphicsLineItem() for _ in range(6)] for _ in range(48)]
            pen = QtGui.QPen()
            pen.setWidth(2)
            for i in range(48):
                x = CHIP_LIST_48_0[i][0]
                y = CHIP_LIST_48_0[i][1]
                self.scene.addRect(x*xoffset,y*yoffset,w,h,pen)
                self.chipIDTxt[i].setPos(x*xoffset+30,y*yoffset+30)
                txt = "%d,%d" % (CHIP_LIST_48_0[i][0], CHIP_LIST_48_0[i][1])
                self.chipIDTxt[i].setPlainText(txt)
                # put edge-0
                x1 = x*xoffset+w
                y1 = y*yoffset+h/2
                x2 = x1+hspace/2
                y2 = y1
                self.edges[i][0].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][0])
                # put edge-1
                x1 = x*xoffset+w
                y1 = y*yoffset
                x2 = x1+hspace/2
                y2 = y1-hspace/2
                self.edges[i][1].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][1])
                # put edge-2
                x1 = x*xoffset+w/2
                y1 = y*yoffset
                x2 = x1
                y2 = y1-hspace/2
                self.edges[i][2].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][2])
                # put edge-3
                x1 = x*xoffset
                y1 = y*yoffset+h/2
                x2 = x1-hspace/2
                y2 = y1
                self.edges[i][3].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][3])
                # put edge-4
                x1 = x*xoffset
                y1 = y*yoffset+h
                x2 = x1-hspace/2
                y2 = y1+hspace/2
                self.edges[i][4].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][4])
                # put edge-5
                x1 = x*xoffset+w/2
                y1 = y*yoffset+h
                x2 = x1
                y2 = y1+hspace/2
                self.edges[i][5].setLine(x1,y1,x2,y2)
                self.scene.addItem(self.edges[i][5])
                for j in range(6):
                    self.edges[i][j].setPen(pen)
                self.scene.addItem(self.chipIDTxt[i])
        #self.scene.addLine(0,0,70,70)
        else:
            # draw as physical layout
            self.chipIDTxt = [QtGui.QGraphicsTextItem() for _ in range(48)]
            self.edges = [[QtGui.QGraphicsLineItem() for _ in range(6)] for _ in range(48)]
            for x in range(7):
                for y in range(7):
                    i = y*7+x;
                    if i < 48:
                        self.scene.addRect(x*xoffset,y*yoffset,w,h)
                        self.chipIDTxt[i].setPos(x*xoffset+30,y*yoffset+30)
                        txt = "%d,%d" % (CHIP_LIST_48_1[i][0], CHIP_LIST_48_1[i][1])
                        self.chipIDTxt[i].setPlainText(txt)
                        self.scene.addItem(self.chipIDTxt[i])

