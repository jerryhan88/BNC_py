import os.path as opath
import sys
import json
from functools import reduce

from PyQt5.QtWidgets import QWidget, QApplication, QShortcut
from PyQt5.QtGui import QImage, QPainter, QPen, QKeySequence, QColor, QBrush, QPalette
from PyQt5.QtCore import Qt, QSize, QPoint, QRectF, QSizeF
from PyQt5.QtPrintSupport import QPrinter

from __path_organizer import exp_dpath
from SequencerWrapper import valid_TWs, get_travelTime, get_min_tt_seq

pallet = [
        "#ff0000",  # red
        "#0000ff",  # blue
        "#a52a2a",  # brown
        "#ff00ff",  # magenta
        "#008000",  # green
        "#4b0082",  # indigo
        "#f0e68c",  # khaki
        "#800000",  # maroon
        "#000080",  # navy
        "#ffa500",  # orange
        "#ffc0cb",  # pink
        "#808080",  # grey
]


mainFrameOrigin = (100, 100)
margin = 10
unit = 50
coX, coY = (margin * 1, margin * 1)
numGridLines = 9

SHOW_LABEL = True


class RoutineSequence(object):
    S_SIZE = 8

    def __init__(self, sL, sXY):
        self.seqPoints = [QPoint(x, y) for x, y in sXY]

    def draw(self, qp):
        s = RoutineSequence.S_SIZE
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(len(self.seqPoints) - 1):
            p0, p1 = self.seqPoints[i], self.seqPoints[i + 1]
            qp.drawLine(p0, p1)
        brush = QBrush(Qt.black)
        qp.setBrush(brush)
        for cp in self.seqPoints:
            qp.drawEllipse(cp, s / 2, s / 2)


class WareHouse(object):
    H_SIZE = 8

    def __init__(self, wid, cx, cy, clr="#000000"):
        self.pen = QPen(QColor(clr), 2, Qt.SolidLine)
        self.brush = QBrush(QColor(clr))
        self.cp = QPoint(cx, cy)
        s = WareHouse.H_SIZE
        self.rect = QRectF(cx - s / 2, cy - s / 2, s, s)

    def draw(self, qp):
        qp.setPen(self.pen)
        qp.setBrush(self.brush);
        qp.drawRect(self.rect)


class DeliveryPoint(object):
    N_SIZE = 6

    def __init__(self, did, cx, cy, clr="#000000", isValidTask=False):
        self.pen = QPen(QColor(clr), 1, Qt.SolidLine)
        self.brush = QBrush(QColor(clr))
        self.isValidTask = isValidTask
        self.cp = QPoint(cx, cy)
        s = DeliveryPoint.N_SIZE
        self.lu = QPoint(cx - s / 2, cy - s / 2)
        self.lb = QPoint(cx - s / 2, cy + s / 2)
        self.ru = QPoint(cx + s / 2, cy - s / 2)
        self.rb = QPoint(cx + s / 2, cy + s / 2)


    def draw(self, qp):
        qp.setPen(self.pen)
        if not self.isValidTask:
            qp.setBrush(Qt.NoBrush)
            qp.drawLine(self.lu, self.rb)
            qp.drawLine(self.lb, self.ru)
        else:
            qp.setBrush(self.brush)
            s = DeliveryPoint.N_SIZE
            qp.drawEllipse(self.cp, s / 2, s / 2)
        # pen = QPen(Qt.red, 1, Qt.DashDotLine)
        # qp.setPen(pen)
        # qp.drawLine(self.cp, self.wh.cp)


class Viz(QWidget):
    def __init__(self, prob):
        super().__init__()
        self.xLen = self.yLen = 10 * unit
        w, h = coX + self.xLen + margin * 1, coY + self.yLen + margin * 1
        self.canvasSize = (w, h)
        # self.image = QImage(w, h, QImage.Format_RGB32)
        # self.image.fill(Qt.white)
        # self.path = QPainterPath()
        # self.clearImage()
        #
        self.instances = []
        self.initInstances(prob)
        self.initUI(prob['problemName'])
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

    def initInstances(self, prob):
        sL, sXY = [], []
        for i in range(len(prob['S'])):
            sL.append('s%d' % i)
            sx, sy = prob['XY'][prob['S'][i]]
            sXY.append((coX + sx * self.xLen, coY + (1.0 - sy) * self.yLen))
        self.instances.append(RoutineSequence(sL, sXY))
        for i in range(len(prob['P'])):
            wid = 'w%d' % i
            nid = prob['P'][i]
            hx, hy = prob['XY'][nid]
            clr = pallet[nid % len(pallet)]
            wh = WareHouse(wid,
                         coX + hx * self.xLen,
                         coY + (1.0 - hy) * self.yLen,
                         clr)
            self.instances.append(wh)
        partialSeq = prob['S']
        al_i, be_i, t_ij, bu = [prob[k] for k in ['al_i', 'be_i', 't_ij', 'bu']]
        for k in range(len(prob['D'])):
            nid = 't%d' % k
            nx, ny = prob['XY'][prob['D'][k]]
            n0, n1 = prob['h_k'][k], prob['n_k'][k]
            clr = pallet[n0 % len(pallet)]
            isValidTask = None
            min_tt_seq = get_min_tt_seq(partialSeq, n0, n1, al_i, be_i, t_ij)
            if min_tt_seq is None:
                isValidTask = False
            else:
                tt = get_travelTime(min_tt_seq, al_i, be_i, t_ij)
                isValidTask = tt < bu
            self.instances.append(DeliveryPoint(nid,
                                coX + nx * self.xLen,
                                coY + (1.0 - ny) * self.yLen,
                                    clr, isValidTask))

    # def clearImage(self):
    #     self.path = QPainterPath()
    #     self.image.fill(Qt.white)
    #     self.update()

    def initUI(self, problemName):
        w, h = self.canvasSize
        self.setGeometry(mainFrameOrigin[0], mainFrameOrigin[1], w, h)
        self.setWindowTitle(problemName)
        self.setFixedSize(QSize(w, h))
        #
        self.image = QImage(w, h, QImage.Format_RGB32)
        self.image.fill(Qt.white)
        pal = self.palette()
        pal.setColor(QPalette.Background, Qt.white)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        #
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawCanvas(qp)
        qp.end()
        #
        qp = QPainter()
        qp.begin(self.image)
        self.drawCanvas(qp)
        qp.end()

    def save_img(self, img_fpath):
        if img_fpath.endswith('.png'):
            self.image.save(img_fpath, 'png')
        else:
            assert img_fpath.endswith('.pdf')
            w, h = self.canvasSize
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSizeMM(QSizeF(w / 15, h / 15))
            printer.setFullPage(True)
            printer.setPageMargins(0.0, 0.0, 0.0, 0.0, QPrinter.Millimeter)
            printer.setColorMode(QPrinter.Color)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(img_fpath)
            pixmap = self.grab().scaledToHeight(
                printer.pageRect(QPrinter.DevicePixel).size().toSize().height() * 2)
            painter = QPainter(printer)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()

    def drawCanvas(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        qp.setBrush(Qt.NoBrush)
        # Outer lines!
        qp.drawLine(coX, coY,
                    coX, coY + self.yLen)
        qp.drawLine(coX, coY + self.yLen,
                    coX + self.xLen, coY + self.yLen)
        qp.drawLine(coX + self.xLen, coY + self.yLen,
                    coX + self.xLen, coY)
        qp.drawLine(coX + self.xLen, coY,
                    coX, coY)
        #
        pen = QPen(Qt.gray, 1, Qt.DashLine)
        qp.setPen(pen)
        for i in range(numGridLines):
            qp.drawLine(coX + float(i + 1) / (numGridLines + 1) * self.xLen, coY,
                        coX + float(i + 1) / (numGridLines + 1) * self.xLen, coY + self.yLen)
            qp.drawLine(coX + self.xLen, coY + float(i + 1) / (numGridLines + 1) * self.yLen,
                        coX, coY + float(i + 1) / (numGridLines + 1) * self.yLen)
        #
        for ins in self.instances:
            ins.draw(qp)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        fpath = 'prob_nr004-np004-nd040-ca010-dt125-tw001-sn018.json'
    else:
        fpath = sys.argv[1]
    prob_fpath = reduce(opath.join, [exp_dpath, 'problem', fpath])
    prob = None
    with open(prob_fpath) as json_file:
        prob = json.load(json_file)
    assert prob is not None


    app = QApplication(sys.argv)
    viz = Viz(prob)
    viz.save_img('temp.png')
    sys.exit(app.exec_())