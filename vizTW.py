import os.path as opath
import sys
import json
from functools import reduce

from PyQt5.QtWidgets import QWidget, QApplication, QShortcut
from PyQt5.QtGui import QImage, QPainterPath, QPainter, QPen, QKeySequence, QColor, QBrush, QPalette
from PyQt5.QtCore import Qt, QSize, QRectF, QSizeF
from PyQt5.QtPrintSupport import QPrinter

from __path_organizer import exp_dpath
from vizPos import pallet

mainFrameOrigin = (100, 80)
margin = 10
xUnit, yUnit = 50, 12
coX, coY = (margin * 1, margin * 1)
numGridLines = 9


class Viz(QWidget):
    def __init__(self, prob):
        super().__init__()
        numNodes = len(prob['al_i'])
        self.xLen = 10 * xUnit
        self.yLen = numNodes * yUnit
        w, h = coX + self.xLen + margin * 1, coY + self.yLen + margin * 1
        self.canvasSize = (w, h)
        #
        self.prob = prob
        self.initUI(prob['problemName'])
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

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
        qp.drawLine(coX, coY,
                    coX + self.xLen, coY)
        #
        pen = QPen(Qt.gray, 1, Qt.DashLine)
        qp.setPen(pen)
        nVerLine = len(self.prob['S']) * 2
        for i in range(nVerLine):
            qp.drawLine(coX + float(i + 1) / nVerLine * self.xLen, coY,
                        coX + float(i + 1) / nVerLine * self.xLen, coY + self.yLen)
        nHorLine = len(self.prob['al_i'])
        for i in range(nHorLine):
            qp.drawLine(coX, coY + float(i + 1) / nHorLine * self.yLen,
                        coX + self.xLen, coY + float(i + 1) / nHorLine * self.yLen)
        #
        pen = QPen(Qt.black, 1, Qt.SolidLine)
        qp.setPen(pen)
        brush = QBrush(Qt.black)
        qp.setBrush(brush)
        counter = 0
        h = yUnit - margin
        for nid in self.prob['S']:
            a, b = self.prob['al_i'][nid], self.prob['be_i'][nid]
            w = (b - a) / self.prob['TH'] * self.xLen
            x = a / self.prob['TH'] * self.xLen
            y = counter * yUnit
            qp.drawRect(QRectF(coX + x, coY + y, w, h))
            counter += 1
        for i in range(len(self.prob['P'])):
            nid = self.prob['P'][i]
            clr = pallet[nid % len(pallet)]
            pen = QPen(QColor(clr), 1, Qt.SolidLine)
            qp.setPen(pen)
            brush = QBrush(QColor(clr))
            qp.setBrush(brush)
            a, b = self.prob['al_i'][nid], self.prob['be_i'][nid]
            w = (b - a) / self.prob['TH'] * self.xLen
            x = a / self.prob['TH'] * self.xLen
            y = counter * yUnit
            qp.drawRect(QRectF(coX + x, coY + y, w, h))
            counter += 1
        for k in range(len(self.prob['D'])):
            nid = self.prob['D'][k]
            hid = self.prob['h_k'][k]
            clr = pallet[hid % len(pallet)]
            pen = QPen(QColor(clr), 1, Qt.SolidLine)
            qp.setPen(pen)
            qp.setBrush(Qt.NoBrush)

            a, b = self.prob['al_i'][nid], self.prob['be_i'][nid]
            w = (b - a) / self.prob['TH'] * self.xLen
            x = a / self.prob['TH'] * self.xLen
            y = counter * yUnit
            qp.drawRect(QRectF(coX + x, coY + y, w, h))
            counter += 1


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # fpath = 'prob_nr004-np002-nd020-ca050-dt150-tw001-sn003.json'
        # fpath = 'prob_nr004-np002-nd030-ca050-dt150-tw001-sn000.json'
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