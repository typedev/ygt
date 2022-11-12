import sys
import uuid
# import ygPreferences
from .macfuncDialog import macfuncDialog
from .ygModel import (ygSet,
                      ygParams,
                      ygPoint,
                      ygPointSorter,
                      ygHint,
                      hint_type_nums,
                      ygCaller,
                      ygFunction,
                      ygMacro,
                      ygGlyph)

from PyQt6.QtCore import (
    Qt,
    QPoint,
    QPointF,
    QSize,
    QSizeF,
    QRect,
    QRectF,
    pyqtSignal,
    QLine,
    QLineF
)
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
    QColor,
    QPolygonF,
    QAction
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QGraphicsRectItem,
    QGraphicsLineItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QMenu,
    QLabel,
    QSizePolicy,
    QDialog
)
from fontTools import ttLib
from fontTools.pens.basePen import BasePen
import inspect


HINT_ARROW_WIDTH =               3
HINT_ARROWHEAD_WIDTH =           1
HINT_ANCHOR_WIDTH =              3
HINT_LINK_WIDTH =                1
SET_WIDTH =                      2
HINT_COLLECTION_COLOR =          QColor(0,255,0,128)
HINT_COLLECTION_SELECT_COLOR =   QColor(0,205,0,128)
HINT_ANCHOR_COLOR =              QColor(255,0,255,128)
HINT_ANCHOR_SELECT_COLOR =       QColor(175,0,175,128)
HINT_STEM_COLOR =                QColor(255,0,0,128)
HINT_STEM_SELECT_COLOR =         QColor(205,0,0,128)
HINT_SHIFT_COLOR =               QColor(100,100,255,128)
HINT_SHIFT_SELECT_COLOR =        QColor(0,0,150,128)
HINT_ALIGN_COLOR =               QColor(0,255,0,128)
HINT_ALIGN_SELECT_COLOR =        QColor(0,205,0,128)
HINT_LINK_COLOR =                QColor(127,127,255,255)
HINT_LINK_SELECT_COLOR =         QColor(87,87,215,255)
HINT_FUNC_COLOR =                QColor(0,205,0,128)
HINT_FUNC_SELECT_COLOR =         QColor(0,105,0,128)
HINT_INTERPOLATE_COLOR =         QColor(255,127,0,128)
HINT_INTERPOLATE_SELECT_COLOR =  QColor(215,87,0,128)
SET_COLOR =                      QColor(128,128,128,128)
SET_SELECT_COLOR =               QColor(128,128,128,225)
POINT_OFFCURVE_SELECTED =        QColor(127,127,255,255)
POINT_ONCURVE_OUTLINE =          QColor("red")
POINT_OFFCURVE_FILL =            QColor("white")
POINT_ONCURVE_FILL =             QColor("white")
POINT_OFFCURVE_OUTLINE =         QColor(127,127,255,255)
POINT_OFFCURVE_SELECTED =        QColor(127,127,255,255)
POINT_ONCURVE_SELECTED =         QColor(127,127,255,255)
PREVIEW_BASE_COLOR =             QColor(64,33,31,255)
POINT_OUTLINE_WIDTH =            1
POINT_ANCHORED_OUTLINE_WIDTH =   3
CHAR_OUTLINE_WIDTH =             1
FUNC_BORDER_WIDTH =              2
GLYPH_WIDGET_MARGIN =            50
POINT_ONCURVE_DIA =              8
POINT_OFFCURVE_DIA =             6

HINT_COLOR = {"anchor":      HINT_ANCHOR_COLOR,
              "align":       HINT_ALIGN_COLOR,
              "shift":       HINT_SHIFT_COLOR,
              "interpolate": HINT_INTERPOLATE_COLOR,
              "stem":        HINT_STEM_COLOR,
              "whitespace":  HINT_STEM_COLOR,
              "blackspace":  HINT_STEM_COLOR,
              "grayspace":   HINT_STEM_COLOR,
              "move":        HINT_STEM_COLOR,
              "macro":       HINT_FUNC_COLOR,
              "function":    HINT_FUNC_COLOR,
              "set":         SET_COLOR}

SELECTED_HINT_COLOR = {"anchor":      HINT_ANCHOR_SELECT_COLOR,
                       "align":       HINT_ALIGN_SELECT_COLOR,
                       "shift":       HINT_SHIFT_SELECT_COLOR,
                       "interpolate": HINT_INTERPOLATE_SELECT_COLOR,
                       "stem":        HINT_STEM_SELECT_COLOR,
                       "whitespace":  HINT_STEM_SELECT_COLOR,
                       "blackspace":  HINT_STEM_SELECT_COLOR,
                       "grayspace":   HINT_STEM_SELECT_COLOR,
                       "move":        HINT_STEM_SELECT_COLOR,
                       "macro":       HINT_FUNC_SELECT_COLOR,
                       "function":    HINT_FUNC_SELECT_COLOR,
                       "set":         SET_SELECT_COLOR}

# Classes in this file:

# QtPen (BasePen): copied from fontTools so we could drop a reference to Qt5.
# GlyphWidget(QWidget): Displays glyph outline.
# ygSelectable: inherited by objects that can be selected.
# ygHintView(QGraphicsItem, ygSelectable): Interface with a hint (ygModel.ygHint)
# ygGraphicalHintComponent: Superclass for a visible piece of a hint.
# ArrowHead(QGraphicsPolygonItem, ygGraphicalHintComponent):
#                    Arrowhead component of a visible hint.
# ygBorderLine(QGraphicsLineItem, ygGraphicalHintComponent):
#                    Borderline around certain hints.
# HintArrowLine(QGraphicsPathItem, ygGraphicalHintComponent):
#                    Stem of a visible hint
# HintPointMarker(QGraphicsEllipseItem, ygGraphicalHintComponent):
#                    Thickens and adds color to a point.
# ygPointable: superclass for objects that an arrow can point at.
# ygPointCollectionView(QGraphicsItem, ygGraphicalHintComponent, ygPointable):
#                    Visible representation of a collection of points.
# ygSetView(QGraphicsItem, ygGraphicalHintComponent):
#                    Visible representation of a set (of points).
# ygSelection: Keeps track of selected objects.
# ygPointView(QGraphicsEllipseItem, ygSelectable, ygPointable):
#                    Visual representation of a point.
# SelectionRect(QGraphicsRectItem): For making marquee selections.
# ygGlyphViewer(QGraphicsScene): Visual representation of a glyph (with points,
#                    ygHintView objects, etc.)
# MyView(QGraphicsView): Container for ygGlyphViewer; receives (some) events

class QtPen(BasePen):
    """ Copied from fontTools so we can get rid of the reference to Qt5
        (we're using Qt6). The fontTools library was issued under the MIT license:

        MIT License

        Copyright (c) 2017 Just van Rossum

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction, including without limitation the rights
        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
        copies of the Software, and to permit persons to whom the Software is
        furnished to do so, subject to the following conditions:

        The above copyright notice and this permission notice shall be included in all
        copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
        SOFTWARE.
    """

    def __init__(self, glyphSet, path=None):
        BasePen.__init__(self, glyphSet)
        if path is None:
            path = QPainterPath()
        self.path = path

    def _moveTo(self, p):
        self.path.moveTo(*p)

    def _lineTo(self, p):
        self.path.lineTo(*p)

    def _curveToOne(self, p1, p2, p3):
        self.path.cubicTo(*p1, *p2, *p3)

    def _qCurveToOne(self, p1, p2):
        self.path.quadTo(*p1, *p2)

    def _closePath(self):
        self.path.closeSubpath()

# "View" classes are for making visual representations of data from the model.
# We keep lists and indexes of "View" classes for easy lookup, but otherwise
# data should never be stored as "View" objects--only as "Model" objects.
# Likewise, data shouldn't be manipulated here, but only in the model. This
# file can send requests to the Model to perform certain editing tasks. Then
# the model will send a signal that the display should be refreshed.


class GlyphWidget(QWidget):
    """ Widget for displaying glyph outline.

        This is not interactive at all, but displayed like a background. The
        points and hints you interact with are in ygGlyphViewer (the
        QGraphicsScene). This class also stores translation info so other
        widgets can position their stuff correctly, and provides a convenience
        function for converting font coordinates to Qt coordinates.

        Redo this so that this widget is sized according to the dimensions in the
        head table and doesn't change from glyph to glyph.

    """
    def _calc_canvas_size(self, yg_font):
        f = yg_font.ft_font
        x_size = abs(f['head'].xMin) + abs(f['head'].xMax) + (GLYPH_WIDGET_MARGIN * 2)
        y_size = abs(f['head'].yMin) + abs(f['head'].yMax) + (GLYPH_WIDGET_MARGIN * 2)
        zero_x = abs(f['head'].xMin) + GLYPH_WIDGET_MARGIN
        zero_y = abs(f['head'].yMax) + GLYPH_WIDGET_MARGIN
        return x_size, y_size, zero_x, zero_y

    def __init__(self, viewer, yg_font, yg_glyph):
        super().__init__()
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.preferences = yg_glyph.preferences
        self.ft_glyph = yg_glyph.ft_glyph
        self.ft_glyph.recalcBounds(yg_font.ft_font['glyf'])
        self.canvas_size = self._calc_canvas_size(yg_font)
        self.adv, self.lsb = yg_font.ft_font['hmtx'].metrics[yg_glyph.glyph_name()]
        self.setMinimumSize(self.canvas_size[0], self.canvas_size[1])
        self.xTranslate = self.canvas_size[2]
        self.yTranslate = self.canvas_size[3]
        glyph_set = {yg_glyph.glyph_name(): self.ft_glyph}
        self.path = QPainterPath()
        self.qt_pen = QtPen(glyph_set, path=self.path)
        self.ft_glyph.draw(self.qt_pen, yg_font.ft_font['glyf'])
        self.center_x = self.xTranslate + round(self.adv / 2)

    def paintEvent(self, event):
        painter = QPainter(self)

        brush = QBrush()
        brush.setColor(QColor('white'))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QRect(0, 0, self.width(), self.height())
        painter.fillRect(rect, brush)

        painter.scale(1.0, -1.0)
        painter.translate(QPointF(self.xTranslate, self.yTranslate * -1))

        pen = painter.pen()

        if self.preferences["show_metrics"]:
            pen.setWidth(1)
            pen.setColor(QColor(50,50,50,50))
            painter.setPen(pen)
            painter.drawLine(QLine(-abs(self.xTranslate),0,self.width(),0))
            ya = -abs(self.yTranslate)
            painter.drawLine(QLine(0,ya,0,self.height()))
            painter.drawLine(QLine(self.adv,ya,self.adv,self.height()))

        pen.setWidth(CHAR_OUTLINE_WIDTH)
        pen.setColor(QColor("gray"))
        painter.setPen(pen)
        painter.drawPath(self.path)
        painter.end()

    def _font2Qt(self, x, y, onCurve=False):
        """ Converts font coordinate system to Qt, for positioning points

            The font coordinate system has zero at the baseline and
            higher y values towards the top. The Qt system has 0,0
            at the top left of the canvas and higher y values towards
            the bottom.
        """
        thisx = x + self.xTranslate
        thisy = (y * -1) + abs(self.yTranslate)
        if onCurve:
            adjust = POINT_ONCURVE_DIA / 2
        else:
            adjust = POINT_OFFCURVE_DIA / 2
        # These are the coordinates for the points
        # print("x: " + str(thisx - adjust))
        # print("y: " + str(thisy - adjust))
        return QPointF(thisx - adjust, thisy - adjust)



class ygSelectable:

    def _prepare_graphics(self):
        pass

    def update(self):
        pass

    def _is_yg_selected(self):
        pass

    def yg_select(self):
        pass

    def yg_unselect(self):
        pass



class ygHintView(QGraphicsItem, ygSelectable):
    """ Wrapper for a ygModel.ygHint object.

    """
    def __init__(self, *args, **kwargs):
        """ Constructor for ygHintView

            Parameters:
            args[0] (ygGlyphViewer): The scene that owns this. We can't always
            call scene() because we sometimes need that reference before this
            is added to the scene.

            args[1] (ygModel.ygHint): a hint from the ygModel

            args[2]: either a component of the graphical hint or a list of them.

        """
        super().__init__()
        self._is_selected = False
        self.yg_glyph_view = args[0]
        self.yg_hint = args[1]
        self.label = None
        self.label_proxy = None
        self.description = self._set_description()
        if len(args) >= 3:
            # graphical_hint may arrive as an irregularly nested list.
            # flatten it into a simple list
            self.graphical_hint = list(self._traverse(args[2]))
            for g in self.graphical_hint:
                g.setParentItem(self)

    def _set_description(self):
        result = self.yg_hint.hint_type()
        if hasattr(self.yg_hint, "cvt"):
            result += " (" + str(self.yg_hint.cv()) + ")"
        # Tooltip not yet. By default, the tooltip appears when the mouse is
        # anywhere in a widget's bounding rect. For hints that is not helpful.
        # *** There is a way to change this behavior: figure it out later.
        # self.setToolTip(result)
        return result

    def _set_name(self, name):
        self.yg_hint.name = name
        self.label = QLabel()
        self.label.setStyleSheet("QLabel {background-color: transparent; color: gray;}")
        self.label.setText(name)
        self.label_proxy = self.yg_glyph_view.addWidget(self.label)
        rect = self.boundingRect()
        self.label.move(round(rect.topLeft().x()), round(rect.topLeft().y() - self.label.height()))

    def _remove_labels(self):
        if self.label_proxy:
            self.yg_glyph_view.removeItem(self.label_proxy)
        for g in self.graphical_hint:
            if hasattr(g, "_remove_labels"):
                g._remove_labels()

    # Adapted from https://stackoverflow.com/questions/6340351/iterating-through-list-of-list-in-python
    # Presumed public domain.
    def _traverse(self, o):
        if isinstance(o, list):
            for value in o:
                for subvalue in self._traverse(value):
                    yield subvalue
        else:
            yield o

    def paint(self, painter, option, widget):
        """ Got to be here, but it doesn't have to do anything.

        """
        pass

    def boundingRect(self):
        if len(self.graphical_hint) >= 1:
            resultRect = None
            for g in self.graphical_hint:
                if resultRect == None:
                    resultRect = g.boundingRect()
                else:
                    resultRect = g.boundingRect().united(resultRect)
            return resultRect
        else:
            return None # This shouldn't happen. Behavior undefined if it does.

    def contains(self, pt):
        if len(self.graphical_hint) >= 1:
            for g in self.graphical_hint:
                if g.contains(pt):
                    return True
        return False

    def mouse_over_point(self, pt):
        """ In ygHintView. Returns a HintPointMarker.
        """
        if len(self.graphical_hint) >= 1:
            for g in self.graphical_hint:
                if type(g) is HintPointMarker and g.contains(pt):
                    return g
        return None

    def get_scene(self):
        return self.yg_glyph_view

    def _target_list(self):
        """ Returns a list of target points for this hint.

        """
        mpt = self.yg_glyph_view.resolve_point_identifier(self.yg_hint.main_target())
        mypoints = []
        if type(mpt) is ygSet:
            for p in mpt.point_list():
                # pp = self.yg_glyph_view.resolve_point_identifier(p)
                mypoints.append(p)
        elif type(mpt) is ygParams:
            mypoints.extend(self._get_macfunc_targets(mpt))
        elif type(mpt) is not list:
            mypoints.append(self.yg_glyph_view.resolve_point_identifier(mpt))
        return mypoints

    def _update_touches(self):
        self._remove_touches()
        self._touch_all_points()

    def _get_macfunc_targets(self, p):
        """ p should be the point_dict from a ygParams object. Survey all the
            point params in a macro or function definition and touch any marked
            as "target."

        """
        macfunc_name = self.yg_hint.name
        plist = []
        if macfunc_name != None:
            try:
                if self.yg_hint.hint_type() == "macro":
                    macfunc = self.yg_glyph_view.yg_glyph.yg_font.macros[macfunc_name]
                elif self.yg_hint.hint_type() == "function":
                    macfunc = self.yg_glyph_view.yg_glyph.yg_font.functions[macfunc_name]
                else:
                    raise Exception(str(macfunc_name) + " not function or macro!")
                k = p.point_dict.keys();
                for kk in k:
                    if kk in macfunc and "subtype" in macfunc[kk] and macfunc[kk]["subtype"] == "target":
                        plist.append(p.point_dict[kk])
            except Exception as e:
                print("Exception in _get_macfunc_targets")
                print(e)
        return plist

    def _touch_untouch(self, point_list, touch):
        """ Touch or untouch the points in point_list. When touch=False,
            remove self from the owners list, and mark the point as untouched
            only if there are no other owners.

        """
        ptindex = self.yg_glyph_view.yg_point_view_index
        for p in point_list:
            if type(p) is ygSet:
                self._touch_untouch(p.point_list(), touch)
            elif type(p) is ygParams:
                self._touch_untouch(self._get_macfunc_targets(p))
            else:
                if touch:
                    try:
                        ptindex[p.id].touched = True
                        ptindex[p.id].owners.append(self)
                    except Exception:
                        pass
                else:
                    try:
                        ptindex[p.id].owners.remove(self)
                        if len(ptindex[p.id].owners) == 0:
                            ptindex[p.id].touched = False
                    except Exception:
                        pass

    def _touch_all_points(self):
        """ Mark each point affected by this hint as 'touched,' and record
            this hint as an owner in its 'owners" list. To orient new hints
            correctly, we need to be accurate about which points are touched.

        """
        self._touch_untouch(self._target_list(), True)

    def _remove_touches(self):
        """ Remove reference to this hint from the "owners" list for each
            point, and if the owner's list is empty afterwards, mark the
            point as untouched.

        """
        self._touch_untouch(self._target_list(), False)

    def _process_click_on_hint(self, obj, with_shift, is_left):
        # Not yet doing different things for shift. Need to take care of that.
        if is_left:
            if with_shift:
                self.yg_glyph_view.yg_selection._toggle_object(self)
            else:
                self.yg_glyph_view.yg_selection._add_object(self, False)

    def _prepare_graphics(self):
        if len(self.graphical_hint) >= 1:
            for c in self.graphical_hint:
                if isinstance(c, ygGraphicalHintComponent):
                    c._prepare_graphics(is_selected=self._is_selected, hint_type=self.yg_hint.hint_type())

    def _is_yg_selected(self):
        return self._is_selected

    def update(self):
        if len(self.graphical_hint) >= 1:
            for c in self.graphical_hint:
                c.update()
        super().update()

    def yg_select(self):
        self._is_selected = True
        self._prepare_graphics()
        self.update()

    def yg_unselect(self):
        self._is_selected = False
        self._prepare_graphics()
        self.update()



class ygGraphicalHintComponent:

    def _prepare_graphics(self, **kwargs):
        pass



class ArrowHead(QGraphicsPolygonItem, ygGraphicalHintComponent):
    """ Arrowhead to mount on the end of a line

        A reference should be kept only in ygHintView.

        This is separate from the line (HintArrowLine) it goes with, chiefly so that
        it can be clickable.
    """
    def __init__(self, tip, direction, hint_type, id, parent=None):
        super().__init__()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.direction = direction
        self.hint_type = hint_type
        self.parent = parent
        self.id = id
        tp = QPointF(0,0)
        qpolygon = QPolygonF([tp,tp,tp])
        # Perhaps the directions should be "positive" and "negative" to keep
        # this as neutral as possible about whether the vector is x or y.
        if direction == "down":
            self.tip = QPointF(8, 8)
            pt1 = QPointF(self.tip.x() - 6, self.tip.y() - 8)
            pt2     = QPointF(self.tip.x() + 6, self.tip.y() - 8)
            qpolygon = QPolygonF([
                self.tip, # 8,8
                pt1,
                pt2
            ])
        elif direction == "up":
            self.tip = QPointF(8, 0)
            pt1 = QPointF(self.tip.x() - 6, self.tip.y() + 8)
            pt2 = QPointF(self.tip.x() + 6, self.tip.y() + 8)
            qpolygon = QPolygonF([
                self.tip, # 8,0
                pt1,
                pt2
            ])
        elif direction == "left":
            self.tip = QPointF(0, 8)
            pt1 = QPointF(self.tip.x() + 8, self.tip.y() + 6)
            pt2 = QPointF(self.tip.x() + 8, self.tip.y() - 6)
            qpolygon = QPolygonF([
                self.tip, # 0,8
                pt1,
                pt2
            ])
        elif direction == "right":
            self.tip = QPointF(8, 8)
            pt1 = QPointF(self.tip.x() - 8, self.tip.y() - 6)
            pt2 = QPointF(self.tip.x() - 8, self.tip.y() + 6)
            qpolygon = QPolygonF([
                pt1,
                pt2,
                self.tip # 8,8
            ])
        self.setPolygon(qpolygon)
        self._prepare_graphics(is_selected=False, hint_type=self.hint_type)

    def _prepare_graphics(self, **kwargs):
        # For ArrowHead
        is_selected = kwargs["is_selected"]
        hint_type = kwargs["hint_type"]
        if is_selected:
            pen_color = SELECTED_HINT_COLOR[hint_type]
        else:
            pen_color = HINT_COLOR[hint_type]
        pen = QPen(pen_color)
        pen.setWidth(SET_WIDTH)
        brush = QBrush(pen_color)
        self.setPen(pen)
        self.setBrush(brush)

    def setPos(self, qpf):
        # These little offsets were made by experimentation.  But see if they
        # can be abstracted somehow.
        if self.direction == "down":
            nqp = QPointF(qpf.x() - 8, qpf.y() - 6)
        elif self.direction == "up":
            nqp = QPointF(qpf.x() - 8, qpf.y() - 2)
        elif self.direction == "left":
            nqp = QPointF(qpf.x() - 4, qpf.y() - 8)
        else:
            nqp = QPointF(qpf.x() - 6, qpf.y() - 8)
        super().setPos(nqp)

    def mousePressEvent(self, event):
        # In ArrowHead
        with_shift = (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
        is_left = event.button() == Qt.MouseButton.LeftButton
        self.parentItem()._process_click_on_hint(self, with_shift, is_left)



class ygBorderLine(QGraphicsLineItem, ygGraphicalHintComponent):
    def __init__(self, line, hint_type):
        super().__init__()
        self.hint_type = hint_type
        self.line = line
        self.setLine(self.line)

    def _prepare_graphics(self, **kwargs):
        is_selected = kwargs["is_selected"]
        hint_type = kwargs["hint_type"]
        if is_selected:
            pen_color = SELECTED_HINT_COLOR[hint_type]
        else:
            pen_color = HINT_COLOR[hint_type]
        pen = QPen(pen_color)
        pen.setWidth(FUNC_BORDER_WIDTH)
        pen.setDashPattern([1,2])
        brush = QBrush(pen_color)
        self.setPen(pen)

    def mousePressEvent(self, event):
        # in yBorderLine
        with_shift = (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
        is_left = event.button() == Qt.MouseButton.LeftButton
        self.parentItem()._process_click_on_hint(self, with_shift, is_left)



class HintArrowLine(QGraphicsPathItem, ygGraphicalHintComponent):
    """ Line for connecting related points

    The connecting line with arrow represents a hint. There are different kinds,
    which will be represented by different colors.
    (A (linked) set will be indicated by thinner lines without arrows.)
    """
    def __init__(self, p1, p2, vector, hint_type, id=None, parent=None):
        # "vector" param not used. Get rid of it.
        super().__init__()
        #
        # This class looks very messy. Clean it up!
        #
        # p1 and p2 must be ygPointable objects (ygPointView, ygPointCollectionView).
        #
        # p1 is the beginning of the line; p2 is the end (where we will put
        # the arrowhead). vector is 0 for y, 1 for x
        # start by figuring out the rectangle that will contain this line.
        #
        self.vector = vector
        # id setup not needed:
        if id:
            self.id = id
        else:
            self.id = uuid.uuid1()
        # parent setup not needed
        self.parent = parent
        self.setCursor(Qt.CursorShape.CrossCursor)
        begin_a = p1.attachment_point(p2.center_point)
        begin_x = begin_a.x()
        begin_y = begin_a.y()
        end_a = p2.attachment_point(begin_a)
        end_x = end_a.x()
        end_y = end_a.y()
        xdistance = abs(begin_x - end_x)
        ydistance = abs(begin_y - end_y)
        self.hint_type = hint_type
        # Shouldn't need a ref to the arrowhead here, but only in ygHintView.
        self.arrowhead = None
        try:
            box_ratio = xdistance / ydistance
        except ZeroDivisionError:
            box_ratio = 0
        # Generate a keyword to describe the shape of the box.
        if xdistance == 0 and ydistance == 0:
            self.shape = "invisible"
            self.arrow_vector = None
        elif xdistance == 0:
            self.shape = "y only"
            self.arrow_vector = "y"
        elif ydistance == 0:
            self.shape = "x only"
            self.arrow_vector = "x"
        elif box_ratio < 0.3333:
            self.shape = "tall"
            self.arrow_vector = "y"
        elif box_ratio > 3:
            self.shape = "flat"
            self.arrow_vector = "x"
        elif ydistance > xdistance:
            self.shape = "tallish"
            self.arrow_vector = "y"
        else:
            self.shape = "flattish"
            self.arrow_vector = "x"
        self.arrowhead_direction = None
        # Should these direction words be "positive" and "negative"?
        if self.arrow_vector == "x":
            if begin_x < end_x:
                self.arrowhead_direction = "right"
            if begin_x > end_x:
                self.arrowhead_direction = "left"
        if self.arrow_vector == "y":
            if begin_y < end_y:
                self.arrowhead_direction = "down"
            if begin_y > end_y:
                self.arrowhead_direction = "up"
        # These little adjustments are for getting the line aligned exactly
        # with the center of the points. See if they can be abstracted, and
        # change with the point diameter.
        self.leftadjust = [12, 4]
        self.rightadjust = [-4, 4]
        self.topadjust = [4, 12]
        self.bottomadjust = [4, -4]
        if self.arrow_vector == "x":
            if min(begin_x, end_x) == begin_x:
                self.lineBegin = self._adjustPoint(self.leftadjust, begin_x, begin_y)
                self.lineEnd = self._adjustPoint(self.rightadjust, end_x, end_y)
                leftPoint = self.lineBegin
                rightPoint = self.lineEnd
            else:
                self.lineEnd = self._adjustPoint(self.leftadjust, end_x, end_y)
                self.lineBegin = self._adjustPoint(self.rightadjust, begin_x, begin_y)
                rightPoint = self.lineBegin
                leftPoint = self.lineEnd
        else:
            if min(begin_y, end_y) == begin_y:
                self.lineBegin = self._adjustPoint(self.topadjust, begin_x, begin_y)
                self.lineEnd = self._adjustPoint(self.bottomadjust, end_x, end_y)
                topPoint = self.lineBegin
                bottomPoint = self.lineEnd
            else:
                self.lineEnd = self._adjustPoint(self.topadjust, end_x, end_y)
                self.lineBegin = self._adjustPoint(self.bottomadjust, begin_x, begin_y)
                bottomPoint = self.lineBegin
                topPoint = self.lineEnd
        # The "0.33" that governs the length of the handles for the cubic drawing
        # needs to be abstracted, so it can change with the shape of the box.
        partial_y_distance = ydistance * 0.33
        partial_x_distance = xdistance * 0.33
        if self.shape == "invisible":
            path = QPainterPath()
        elif self.shape in ["y only", "x only"]:
            path = QPainterPath(self.lineBegin)
            path.lineTo(self.lineEnd)
        elif self.shape in ["tall", "tallish"]:
            handle1 = QPointF(topPoint.x(), topPoint.y() + partial_y_distance)
            handle2 = QPointF(bottomPoint.x(), bottomPoint.y() - partial_y_distance)
            if self.arrowhead_direction == "up":
                path = QPainterPath(bottomPoint)
                path.cubicTo(handle2, handle1, topPoint)
            else:
                path = QPainterPath(topPoint)
                path.cubicTo(handle1, handle2, bottomPoint)
        elif self.shape in ["flat", "flattish"]:
            handle1 = QPointF(leftPoint.x() + partial_x_distance, leftPoint.y())
            handle2 = QPointF(rightPoint.x() - partial_x_distance, rightPoint.y())
            if self.arrowhead_direction == "left":
                path = QPainterPath(rightPoint)
                path.cubicTo(handle2, handle1, leftPoint)
            else:
                path = QPainterPath(leftPoint)
                path.cubicTo(handle1, handle2, rightPoint)
        else:
            print("What's going on?")
        self.setPath(path)
        self._prepare_graphics(is_selected=False, hint_type=self.hint_type)

    def _prepare_graphics(self, **kwargs):
        # For HintArrowLine
        is_selected = kwargs["is_selected"]
        hint_type = kwargs["hint_type"]
        pen = QPen()
        pen.setWidth(HINT_ARROW_WIDTH)
        if is_selected:
            pen.setColor(SELECTED_HINT_COLOR[hint_type])
        else:
            pen.setColor(HINT_COLOR[hint_type])
        if hint_type == "whitespace":
            pen.setDashPattern([2,2])
        if hint_type == "grayspace":
            pen.setDashPattern([4,2])
        self.setPen(pen)

    def _adjustPoint(self, adjustment, x, y):
        return QPointF(x + adjustment[0], y + adjustment[1])

    def endPoint(self):
        return self.lineEnd

    def mousePressEvent(self, event):
        # In HintArrowLine
        with_shift = (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
        is_left = event.button() == Qt.MouseButton.LeftButton
        self.parentItem()._process_click_on_hint(self, with_shift, is_left)



class HintPointMarker(QGraphicsEllipseItem, ygGraphicalHintComponent):
    """ pt has got to be a ygPointView.
    """
    def __init__(self, viewer, pt, hint_type, name=None, id=None, parent=None):
        self.pt = pt
        self.name = name
        self.label = None
        # This is "placed" when user has associated it with a point.
        self.placed = False
        self.x = self.pt.glocation.x() - 1
        self.y = self.pt.glocation.y() - 1
        self.glocation = QPointF(self.x, self.y)
        if self.pt.yg_point.on_curve:
            self.diameter = POINT_ONCURVE_DIA + 2
        else:
            self.diameter = POINT_OFFCURVE_DIA + 2
        super().__init__(QRectF(self.glocation, QSizeF(self.diameter, self.diameter)))
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._prepare_graphics(is_selected=False, hint_type=hint_type)
        self.label_proxy = None
        if self.name != None:
            self._prepare_label()
            self.label_proxy = viewer.addWidget(self.label)
        self.viewer = viewer

    def _prepare_label(self):
        self.label = QLabel()
        self.label.setStyleSheet("QLabel {background-color: transparent; color: gray;}")
        self.label.setText(str(self.name))
        self.label.move(round(self.x + self.diameter), round(self.y + self.diameter))

    def _get_model_point(self):
        return self.pt.yg_point

    def _get_view_point(self):
        return self.pt

    def _remove_labels(self):
        if self.label_proxy:
            self.viewer.removeItem(self.label_proxy)

    def _prepare_graphics(self, **kwargs):
        # For HintPointMarker
        is_selected = kwargs["is_selected"]
        hint_type = kwargs["hint_type"]
        pen = QPen()
        pen.setWidth(HINT_ANCHOR_WIDTH)
        if is_selected:
            pen.setColor(SELECTED_HINT_COLOR[hint_type])
            if self.label:
                self.label.show()
        else:
            pen.setColor(HINT_COLOR[hint_type])
            if self.label:
                self.label.hide()
        self.setPen(pen)

    def get_scene(self):
        return self.viewer

    def mousePressEvent(self, event):
        # In HintPointMarker
        with_shift = (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
        is_left = event.button() == Qt.MouseButton.LeftButton
        self.parentItem()._process_click_on_hint(self, with_shift, is_left)



class ygPointable:
    """ For getting the point that a hint line should attach to. For points,
        this is very simple. For sets, not so much.

    """

    def attachment_point(self, pt):
        pass

    def center_point(self):
        pass


class ygPointCollectionView(QGraphicsItem, ygGraphicalHintComponent, ygPointable):
    """ A graphical representation of the points that are among the params for
        a macro or function, and also the clickable bounding rectangle.

        Parameters:
        viewer (ygGlyphViewer): The scene for this editing pane

        yg_params (ygModel.ygParams): The collection of params for a function
        or macro

        hint_type (str): The type of this hint (it must be "function" or
        "macro")

    """
    def __init__(self, viewer, *args):
        super().__init__()
        self.yg_viewer = viewer
        self.point_dict = {}
        if type(args[0]) is ygParams:
            self.yg_params = args[0]
            kk = self.yg_params.point_dict.keys()
            for k in kk:
                self.point_dict[k] = viewer.resolve_point_identifier(self.yg_params.point_dict[k])
            self.hint_type = self.yg_params.hint_type
        else:
            point_list = args[0]
            self.hint_type = args[1]
            for p in point_list:
                pp = viewer.resolve_point_identifier(p)
                if type(pp) is ygPoint:
                    self.point_dict[pp.preferred_label()] = pp
                elif type(pp) is ygSet:
                    self.point_dict[pp.main_point().preferred_label()] = pp.main_point()
        self.point_markers = self._make_point_markers()
        lines, self.rect = self._boundingLines()
        self.borders = []
        for l in lines:
            self.borders.append(ygBorderLine(l, self.hint_type))
        self._prepare_graphics(is_selected=False, hint_type=self.hint_type)

    def _prepare_graphics(self, **kwargs):
        # For ygPointCollectionView
        is_selected = kwargs["is_selected"]
        hint_type = kwargs["hint_type"]
        if is_selected:
            pen_color = SELECTED_HINT_COLOR[hint_type]
        else:
            pen_color = HINT_COLOR[hint_type]
        pen = QPen(pen_color)
        pen.setWidth(FUNC_BORDER_WIDTH)
        pen.setDashPattern([1,2])
        for b in self.borders:
            b.setPen(pen)
            b.update()
        ppen = QPen(pen_color)
        ppen.setWidth(HINT_ANCHOR_WIDTH)
        for m in self.point_markers:
            m.setPen(ppen)
            m.update()

    def visible_objects(self):
        return self.point_markers + self.borders

    def _make_point_markers(self):
        kk = self.point_dict.keys()
        marker_list = []
        zcounter = 10
        for k in kk:
            p = self.point_dict[k]
            if type(p) is ygSet:
                p = p.main_point()
            ptv = self.yg_viewer.yg_point_view_index[p.id]
            h = HintPointMarker(self.yg_viewer, ptv, self.hint_type, name=k)
            zcounter += 1
            marker_list.append(h)
        return marker_list

    def paint(self, painter, option, widget):
        """ Got to be here, but it doesn't have to do anything.

        """
        pass

    def boundingRect(self):
        return self.rect

    def height(self):
        return self.rect.height()

    def width(self):
        return self.rect.width()

    def _boundingLines(self):
        # Four visible lines for border, plus the bounding rect
        markers = self.point_markers
        min_x = max_x = min_y = max_y = None
        for m in markers:
            if not min_x:
                min_x = m.x
            else:
                min_x = min(min_x,m.x)
            if not min_y:
                min_y = m.y
            else:
                min_y = min(min_y, m.y)
            if not max_x:
                max_x = m.x
            else:
                max_x = max(max_x, m.x)
            if not max_y:
                max_y = m.y
            else:
                max_y = max(max_y, m.y)
        min_x -= 5
        min_y -= 5
        max_x += 15
        max_y += 15
        lines = []
        lines.append(QLineF(min_x, min_y, max_x, min_y))
        lines.append(QLineF(max_x, min_y, max_x, max_y))
        lines.append(QLineF(max_x, max_y, min_x, max_y))
        lines.append(QLineF(min_x, min_y, min_x, max_y))
        rect = QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
        return lines, rect

    def attachment_point(self, pt):
        if pt.x() < self.rect.x() - 1:
            x = self.rect.x() - 1
            if pt.y() < self.rect.y() - 1:
                return QPointF(x, self.rect.y() - 4)
            elif pt.y() > self.rect.y() + self.rect.height():
                return QPointF(x, self.rect.y() + self.rect.height() - 3)
            else:
                return QPointF(x, self.rect.y() + (self.rect.height() / 2) - 3)
        elif pt.x() > self.rect.x() + self.rect.width() + 1:
            x = self.rect.x() + self.rect.width() + 1
            if pt.y() < self.rect.y() - 1:
                return QPointF(x, self.rect.y() - 4)
            elif pt.y() > self.rect.y() + self.rect.height():
                return QPointF(x, self.rect.y() + self.rect.height() - 3)
            else:
                return QPointF(x, self.rect.y() + (self.rect.height() / 2) - 3)
        else:
            x = self.rect.x() + self.rect.width() / 2
            if pt.y() < self.rect.y() + (self.rect.height() / 2):
                return QPointF(x, self.rect.y() - 4)
            else:
                return QPointF(x, self.rect.y() + self.height() - 3)

    def center_point(self):
        return QPointF(self.x() + (self.width() / 2), self.y() + (self.height() / 2))

    def contains(self, pt):
        for p in self.point_markers:
            if p.contains(pt):
                return True
        for b in self.borders:
            if b.contains(pt):
                return True
        return False

    def mousePressEvent(self, event):
        # In ygPointCollectionView
        with_shift = (QApplication.keyboardModifiers() & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier
        is_left = event.button() == Qt.MouseButton.LeftButton
        self.parentItem()._process_click_on_hint(self, with_shift, is_left)




class ygSetView(ygPointCollectionView):
    """ A graphical representation of a list of points.

    """
    def __init__(self, viewer, yg_set, hint_type):
        super().__init__(viewer, yg_set.point_list(), hint_type)
        self.viewer = viewer
        self.hint_type = hint_type


class ygSelection:
    """ A list of selected objects (points, hints, or both).

        The class has functions for manipulating the list.
    """
    def __init__(self, viewer):
        self.selected_objects = []
        self.viewer = viewer

    def get_scene(self):
        return self.viewer

    def _cancel_selection(self):
        for p in self.selected_objects:
            if p._is_yg_selected:
                p.yg_unselect()
                p._prepare_graphics()
                p.update()
        self.selected_objects = []
        self.viewer.update()

    def _add_object(self, obj, add_to_selection):
        if not add_to_selection:
            self._cancel_selection()
        if obj.isVisible():
            obj.yg_select()
            self.selected_objects.append(obj)
            obj._prepare_graphics()
            obj.update()

    def _cancel_object(self, obj):
        obj.yg_unselect()
        self.selected_objects.remove(obj)
        obj._prepare_graphics()
        obj.update()

    def _toggle_object(self, obj):
        if not obj.isVisible():
            return
        if obj._is_yg_selected():
            obj.yg_unselect()
            self.selected_objects.remove(obj)
        else:
            obj.yg_select()
            self.selected_objects.append(obj)
        obj._prepare_graphics()
        obj.update()

    def _add_rect(self, rect, add_to_selection):
        """ This method of selecting doesn't work on hints.
        """
        if not add_to_selection:
            self._cancel_selection()
        for ptv in self.viewer.yg_point_view_list:
            if ptv.isVisible() and rect.contains(ptv.glocation):
                ptv.yg_select()
                self.selected_objects.append(ptv)
                ptv._prepare_graphics()
                ptv.update()

    def _toggle_rect(self, rect):
        """ This method of selecting doesn't work on hints.
        """
        for ptv in self.viewer.yg_point_view_list:
            if ptv.isVisible() and rect.contains(ptv.glocation):
                if ptv._is_yg_selected():
                    ptv.yg_unselect()
                else:
                    ptv.yg_select()
                if ptv._is_yg_selected():
                    self.selected_objects.append(ptv)
                else:
                    self.selected_objects.remove(ptv)
                ptv._prepare_graphics()
                ptv.update()



class ygPointView(QGraphicsEllipseItem, ygSelectable, ygPointable):
    """ A visible point

    """

    def __init__(self, viewer, yg_point, gwidget):
        self._is_selected = False
        self.yg_point = yg_point
        if yg_point.on_curve:
            self.diameter = POINT_ONCURVE_DIA
        else:
            self.diameter = POINT_OFFCURVE_DIA
        # glocation is a QPointF
        self.glocation = gwidget._font2Qt(self.yg_point.font_x, self.yg_point.font_y, self.yg_point.on_curve)
        super().__init__(QRectF(self.glocation, QSizeF(self.diameter, self.diameter)))
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.border_width = 1
        self.index = -1
        self.touched = False
        self.viewer = viewer
        self.point_number_label = None
        self.point_number_label_proxy = None
        # These are the ygHintView objects that touch this point. When a hint
        # is removed from ygGlyphViewer, remove the reference from this list.
        # If a hint being removed makes this list empty, remove the "touched"
        # flag from this ygPointView.
        self.owners = []

    def attachment_point(self, pt):
        return self.glocation

    def center_point(self):
        return self.glocation

    def _prepare_graphics(self):
        if self._is_yg_selected():
            if self.yg_point.on_curve:
                brushColor = POINT_ONCURVE_SELECTED
            else:
                brushColor = POINT_OFFCURVE_SELECTED
        else:
            brushColor = POINT_ONCURVE_FILL
        if self.yg_point.on_curve:
            penColor = POINT_ONCURVE_OUTLINE
        else:
            penColor = POINT_OFFCURVE_OUTLINE
        pen = QPen(penColor)
        pen.setWidth(self.border_width)
        brush = QBrush(brushColor)
        self.setBrush(brush)
        self.setPen(pen)

    def get_scene(self):
        return self.viewer

    def add_label(self):
        if self.point_number_label:
            self.del_label()
        self.point_number_label = QLabel()
        self.point_number_label.setStyleSheet("QLabel {background-color: transparent; color: red; font-size: 90%}")
        self.point_number_label.setText(str(self.yg_point.preferred_label()))
        self.point_number_label_proxy = self.viewer.addWidget(self.point_number_label)
        label_x = self.glocation.x() + self.diameter
        label_y = self.glocation.y() - self.point_number_label.height()
        self.point_number_label.move(round(label_x), round(label_y))

    def del_label(self):
        if self.point_number_label:
            self.viewer.removeItem(self.point_number_label_proxy)
            self.point_number_label = None
            self.point_number_label_proxy = None

    def update(self):
        pass

    def _is_yg_selected(self):
        return self._is_selected

    def yg_select(self):
        self._is_selected = True
        self._prepare_graphics()
        self.update()

    def yg_unselect(self):
        self._is_selected = False
        self._prepare_graphics()
        self.update()

    def mousePressEvent(self, event):
        # In ygPointView
        # Select when clicked, eiher adding to or replacing current selection.
        modifier = QApplication.keyboardModifiers()
        if (modifier & Qt.KeyboardModifier.ShiftModifier) == Qt.KeyboardModifier.ShiftModifier:
            if event.button() == Qt.MouseButton.LeftButton:
                self.viewer.yg_selection._toggle_object(self)
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.viewer.yg_selection._add_object(self, False)



class SelectionRect(QGraphicsRectItem):
    """ The rubber band that appears while dragging to select points.
    """
    def __init__(self, qr):
        super(SelectionRect, self).__init__(qr)
        self.setRect(qr)



class ygGlyphViewer(QGraphicsScene):
    """ The workspace.

    Holds all the visible items and a good bit of the data required for editing
    hints.

    """

    sig_new_hint = pyqtSignal(object)
    sig_viewer_ready = pyqtSignal()
    sig_reverse_hint = pyqtSignal(object)
    sig_change_hint_color = pyqtSignal(object)
    sig_off_curve_visibility = pyqtSignal()
    sig_make_macfunc = pyqtSignal(object)
    sig_assign_macfunc_point = pyqtSignal(object)
    sig_edit_macfunc_params = pyqtSignal(object)
    sig_change_cv = pyqtSignal(object)
    sig_round_hint = pyqtSignal(object)
    sig_swap_macfunc_points = pyqtSignal(object)
    sig_macfunc_target = pyqtSignal(object)
    sig_macfunc_ref = pyqtSignal(object)
    sig_toggle_point_numbers = pyqtSignal()

    def __init__(self, preferences, yg_glyph):
        """ yg_glyph is a ygGlyph object from ygModel.
        """
        self.preferences = preferences
        self.yg_point_view_index = {}
        self.yg_point_view_list = []
        self.yg_hint_view_index = {}
        self.yg_hint_view_list = []
        super(ygGlyphViewer, self).__init__()
        self.yg_glyph = yg_glyph
        self.vector = self.yg_glyph.current_vector()
        # Try to get rid of ref to this scene in the model's ygGlyph class.
        self.yg_glyph.glyph_viewer = self
        self.glyphwidget = GlyphWidget(self, self.yg_glyph.yg_font, self.yg_glyph)
        self.glyphwidget.move(0,0)
        self.addWidget(self.glyphwidget)
        self.selectionRect = None          # The rubber band. None when no selection is underway.
        self.dragBeginPoint = QPointF(0,0) # Set whenever left mouse button is pressed, in case of rubber band selection
        self.yg_selection = ygSelection(self)
        self.off_curve_points_showing = self.preferences.show_off_curve_points()
        self.point_numbers_showing = self.preferences.show_point_numbers()
        for p in self.yg_glyph.points():
            yg_point_view = ygPointView(self, p, self.glyphwidget)
            self.yg_point_view_index[p.id] = yg_point_view
            self.yg_point_view_list.append(yg_point_view)
            yg_point_view._prepare_graphics()
            self.addItem(yg_point_view)
            if not yg_point_view.yg_point.on_curve and not self.off_curve_points_showing:
                yg_point_view.hide()
            if yg_point_view.isVisible() and self.point_numbers_showing:
                yg_point_view.add_label()


        self.sig_new_hint.connect(self.add_hint)
        self.sig_change_cv.connect(self.change_cv)
        self.sig_reverse_hint.connect(self.reverse_hint)
        self.sig_swap_macfunc_points.connect(self.swap_macfunc_points)
        self.sig_change_hint_color.connect(self.change_hint_color)
        self.sig_edit_macfunc_params.connect(self.edit_macfunc_params)
        self.sig_off_curve_visibility.connect(self.toggle_off_curve_visibility)
        self.sig_make_macfunc.connect(self.make_macfunc)
        self.sig_macfunc_target.connect(self.macfunc_target)
        self.sig_macfunc_ref.connect(self.macfunc_ref)
        self.sig_toggle_point_numbers.connect(self.toggle_point_numbers)
        self.sig_round_hint.connect(self.toggle_hint_rounding)

        # We've drawn the points on the screen. Now get and display the hints.

        self.install_hints(self.yg_glyph.hints())

    def edit_macfunc_params(self, hint):
        ed_dialog = macfuncDialog(hint)
        r = ed_dialog.exec()
        if r == QDialog.DialogCode.Accepted:
            hint.yg_hint.hint_has_changed(hint.yg_hint)

    def change_axis(self):
        # And do the things necessary to switch it: make sure the hints for
        # the current vector are stored, and what else?
        if self.vector == "x":
            self.vector = "y"
        else:
            self.vector = "x"

    def toggle_off_curve_visibility(self):
        self.off_curve_points_showing = not self.off_curve_points_showing
        self.preferences.set_show_off_curve_points(self.off_curve_points_showing)
        for p in self.yg_point_view_list:
            if not p.yg_point.on_curve:
                if self.off_curve_points_showing:
                    p.show()
                    if self.point_numbers_showing:
                        p.add_label()
                else:
                    p.hide()
                    if self.point_numbers_showing:
                        p.del_label()

    def make_set(self):
        """ In the hint model, the target can be either a ygPoint or a ygSet.
            This function takes the current selection, a ygPoint, and turns it
            into a ygSet, which it substitutes for the ygPoint. Note that
            exactly one selected point must be touched, and at least one
            selected point must be untouched.

        """
        selected_points = self.selectedObjects(True)
        touched_points = []
        untouched_points = []
        for s in selected_points:
            if s.touched:
                touched_points.append(s)
            else:
                untouched_points.append(s)
        if len(untouched_points) < 1 or len(touched_points) != 1:
            return
        touched_point = touched_points[0]
        hint = touched_point.owners[0]
        hint_model = hint.yg_hint
        if not hint_model.hint_type() in ["shift", "align", "interpolate"]:
            return
        new_list = []
        for p in selected_points:
            new_list.append(self._model_point(p))
        sorter = ygPointSorter(self.vector)
        sorter.sort(new_list)
        set = ygSet(new_list)
        set._main_point = touched_point.yg_point
        hint_model.set_main_target(set.id_list())
        hint._update_touches()
        self.yg_glyph.hint_changed(hint_model)

    def get_scene(self):
        """ Returns the current scene (always this object!)

            Returns:
            ygGlyphViewer: this scene
        """
        return self

    def _mouse_over_point(self, qp):
        """ In ygGlyphViewer. Determines whether the mouse is positioned over a point.

            Parameters:
            qp (QPos): The current position of the mouse

            Returns:
            bool: True if the mouse is over a point; False otherwise

        """
        pt_keys = self.yg_point_view_index.keys()
        for pk in pt_keys:
            if self.yg_point_view_index[pk].contains(qp):
                return self.yg_point_view_index[pk]
        return None

    def _mouse_over_hint(self, qp):
        """ Determines whether the mouse is positioned over a hint.

            Parameters:
            qp (QPos): The current position of the mouse

            Returns:
            bool: True if the mouse is over a hint; False otherwise
        """
        for h in self.yg_hint_view_list:
            if h.contains(qp):
                return h
        return None

    def change_hint_color(self, _params):
        _params["hint"].yg_hint.change_hint_color(_params["color"])

    def toggle_hint_rounding(self, hint):
        self._model_hint(hint).toggle_rounding()

    def toggle_point_numbers(self):
        self.point_numbers_showing = not self.point_numbers_showing
        self.preferences.set_show_point_numbers(self.point_numbers_showing)
        for p in self.yg_point_view_list:
            if self.point_numbers_showing:
                if p.isVisible():
                    p.add_label()
            else:
                p.del_label()

    def swap_macfunc_points(self, data):
        hint = data["hint"].yg_hint
        new_pt_name = data["new_pt"]
        old_pt_name = data["old_pt"]
        hint.swap_macfunc_points(new_pt_name, old_pt_name)

    def reverse_hint(self, h):
        """ Recipient of a signal for reversing a hint. Communicates to the
            model that a hint must be added to the hint tree.

            Parameters:
            h (ygModel.ygHint): the hint to be reversed

        """
        h.reverse_hint(h)

    def macfunc_target(self, _params):
        hint = _params["hint"]
        pt = _params["pt"]
        hint.yg_hint.set_target(pt)

    def macfunc_ref(self, _params):
        hint = _params["hint"]
        pt = _params["pt"]
        hint.yg_hint.set_ref(pt)

    def change_cv(self, param_dict):
        """ Recipient of a signal for adding or changeing a control value.

            Parameters:
            param_dict (dict): A dictionary containing "hint" (the affected
            hint, ygHintView) and "cv" (the new cv)

        """
        if type(param_dict["hint"]) is ygHintView:
            param_dict["hint"].yg_hint.set_cv(param_dict["cv"])

    def add_hint(self, h):
        """ Recipient of a signal for adding a hint. Communicates to the model
            that a hint must be added to the hint tree.

            Parameters:
            h (ygModel.ygHint): the hint to add to the tree

        """
        if type(h) is ygHint:
            h.add_hint(h)
        elif type(h) is ygHintView:
            h.add_hint(h.yg_hint)

    def _adjust_rect(self, current_point):
        """ Flips points around to account for rubber band rotating around
            the origin point.

            Parameters:
            current_point: The fixed point at which the selection began

            Returns:
            QRectF: The adjusted selection rect
        """
        qr = QRectF(0,0,0,0)
        current_x = current_point.x()
        current_y = current_point.y()
        origin_x = self.dragBeginPoint.x()
        origin_y = self.dragBeginPoint.y()
        if current_x > origin_x and current_y > origin_y:
            qr.setCoords(origin_x, origin_y, current_x, current_y)
        elif current_x < origin_x and current_y > origin_y:
            qr.setCoords(current_x, origin_y, origin_x, current_y)
        elif current_x > origin_x and current_y < origin_y:
            qr.setCoords(origin_x, current_y, current_x, origin_y)
        elif current_x < origin_x and current_y < origin_y:
            qr.setCoords(current_x, current_y, origin_x, origin_y)
        else:
            qr.setCoords(origin_x, origin_y, origin_x, origin_y)
        return qr

    def selectedObjects(self, points_only):
        """ Get a list of objects (points and hints) selected by the user.

            Parameters:
            point_only (bool): if true, return only selected points (not hints)

            Returns:
            A list of all selected objects

        """
        if not points_only:
            return self.yg_selection.selected_objects
        result = []
        for o in self.yg_selection.selected_objects:
            if type(o) is ygPointView:
                result.append(o)
        return result

    def install_hints(self, hint_list):
        """ Installs a collection of hints sent from the model.

            Parameters:
            hint_tree (ygModel.ygHintNode): All the hints for either the y
            or the x vector for this glyph, in a tree structure.

        """
        # Remove the old hints (destroying the ygHintView wrappers) and empty
        # out the list storing them.
        for h in self.yg_hint_view_list:
            h._remove_touches()
            if h in self.items():
                h._remove_labels()
                self.removeItem(h)
        self.yg_hint_view_list.clear()
        # The hints we get from the model are ygModel.ygHint objects, using
        # any legal Xgridfit identifier for the points. Wrap each one in a
        # ygHintView object.
        for h in hint_list:
            vh = self._make_visible_hint(h)
            self.yg_hint_view_list.append(vh)
        self.update()

    def get_hint_type_num(self, htype):
        """ Translates the string description of the hint type (e.g. 'stem')
            into an int used by the program for deciding the shape of the
            visible hint.

            Parameters:
            htype (str): The string that describes the hint

            Returns:
            int: 0: no reference point; 1: one reference point; any number of
            targets; 2: two reference points; any number of targets; 3: one
            reference point; one target; 4:

        """
        return hint_type_nums[htype]

    def resolve_point_identifier(self, pt, kwargs=None):
        """ Gets a ygModel.ygPoint object.

            Parameters:
            pt: A ygModel.ygPoint or ygPointView object, or any kind of idenfifier
            accepted by Xgridfit.

            Returns: A ygModel.ygPoint object.

        """
        if type(pt) is ygPointView:
            return pt.yg_point
        return self.yg_glyph.resolve_point_identifier(pt)

    def _make_visible_hint(self, hint):
        """ Builds ygHintView objects from ygHint objects and adds them to
            this ygGlyphViewer (a QGraphicsScene).

            Parameters:
            hint (ygHint): The hint from the model

            Returns:
            ygHintView: The graphical hint, if one has been made (None if not)

        """
        # Make sure we've got the hint type
        hint_type = hint.hint_type()
        hint_type_num = self.get_hint_type_num(hint_type)

        # Build the visible hints
        if hint_type_num == 0:
            # 0 = draw a circle around a point.
            target = self.resolve_point_identifier(hint.main_target())
            if type(target) is ygSet:
                target = target.main_point()
            gtarget = self.yg_point_view_index[target.id]
            hpm = HintPointMarker(self, gtarget, "anchor")
            yg_hint_view = ygHintView(self, hint, hpm)
            yg_hint_view._touch_all_points()
            yg_hint_view._prepare_graphics()
            self.addItem(yg_hint_view)
        elif hint_type_num in [1, 3]:
            # With type 1, the target can be a set.
            target = self.resolve_point_identifier(hint.main_target())
            if type(target) is ygSet:
                gtarget = ygSetView(self, target, hint_type)
            else:
                gtarget = self.yg_point_view_index[target.id]
            # If this is going to crash, need to catch it and recover. Maybe
            # mark the hint as invalid and skip it when drawing or compiling? ***
            if hint.main_ref() == None:
                print("Warning: ref is None (target is " + str(target.index) + ")")
            ref = self.resolve_point_identifier(hint.main_ref())
            gref = self.yg_point_view_index[ref.id]
            ha = HintArrowLine(gref, gtarget, 0, hint_type, parent=self)
            ah = ArrowHead(ha.endPoint(), ha.arrowhead_direction, hint_type, ha.id, parent=self)
            ah.setPos(ha.endPoint())
            glist = [ha, ah]
            if type(gtarget) is ygSetView:
                glist.extend(gtarget.visible_objects())
            yg_hint_view = ygHintView(self, hint, glist)
            yg_hint_view._touch_all_points()
            yg_hint_view._prepare_graphics()
            self.addItem(yg_hint_view)
        elif hint_type_num == 2:
            # 2 = arrows from two reference points to one interpolated point or set
            target = self.resolve_point_identifier(hint.main_target())
            if type(target) is ygSet:
                gtarget = ygSetView(self, target, hint_type)
            else:
                gtarget = self.yg_point_view_index[target.id]
            ref_list = hint.main_ref()
            if type(ref_list) is list:
                ref_list = ygSet(ref_list)
            if len(ref_list.point_list()) < 2:
                # This could come up with faulty code from the box, so handle it
                # with an error dialog.
                raise Exception("There must be two reference points for an interpolation hint")
            gref = []
            ref_one = self.resolve_point_identifier(ref_list.point_list()[0])
            ref_two = self.resolve_point_identifier(ref_list.point_list()[1])
            gref.append(self.yg_point_view_index[ref_one.id])
            gref.append(self.yg_point_view_index[ref_two.id])
            ha1 = HintArrowLine(gref[0], gtarget, 0, hint_type, parent=self)
            ha2 = HintArrowLine(gref[1], gtarget, 0, hint_type, parent=self)
            ah1 = ArrowHead(ha1.endPoint(), ha1.arrowhead_direction, hint_type, ha1.id, parent=self)
            ah2 = ArrowHead(ha2.endPoint(), ha2.arrowhead_direction, hint_type, ha2.id, parent=self)
            ah1.setPos(ha1.endPoint())
            ah2.setPos(ha2.endPoint())
            glist = [ha1, ah1, ha2, ah2]
            if type(gtarget) is ygSetView:
                glist.extend(gtarget.visible_objects())
            yg_hint_view = ygHintView(self, hint, glist)
            yg_hint_view._touch_all_points()
            yg_hint_view._prepare_graphics()
            self.addItem(yg_hint_view)
        elif hint_type_num == 4:
            # Green anchors, surrounded by green border
            gtarget = self.resolve_point_identifier(hint.main_target())
            if type(gtarget) is ygParams:
                gtarget.name = hint.macfunc_name()
                gtarget.hint_type = hint_type
                gtarget.other_params = hint.macfunc_other_args()
                yg_params_view = ygPointCollectionView(self, gtarget)
                yg_hint_view = ygHintView(self, hint, yg_params_view.visible_objects())
                yg_hint_view._set_name(gtarget.name)
                yg_hint_view._touch_all_points()
                yg_hint_view._prepare_graphics()
                self.addItem(yg_hint_view)
            else:
                raise Exception("Something went wrong with gtarget in _make_visible_hint")
        else:
            raise Exception("Unknown hint type " + str(hint_type_num))
        self.yg_hint_view_index[hint.id] = yg_hint_view
        self.yg_hint_view_list.append(yg_hint_view)
        return yg_hint_view

    def _ptcoords(self, p):
        if self.vector == "y":
            return p.yg_point.font_y
        else:
            return p.yg_point.font_x

    def make_macfunc(self, _params):
        hint_type = _params["hint_type"]
        name = _params["name"]
        self.make_macfunc_from_selection(hint_type, name=name)
        # Called function will send the signal to the model.

    def _model_hint(self, h):
        if type(h) is ygHintView:
            return(h.yg_hint)
        return h

    def _model_point(self, p):
        if type(p) is ygPointView:
            return p.yg_point
        return p

    def make_hint_from_selection(self, a):
        """ Make a hint based on selection in the editing panel.

            Should we be making ygModel.ygHint instances here? Since
            we're making valid yaml source, wouldn't it be better to
            pass that with the signal?
        """
        menu_to_hint_type = {"Anchor (A)": "anchor",
                             "Align (L)": "align",
                             "Shift (S)": "shift",
                             "Interpolate (I)": "interpolate",
                             "White Distance (W)": "whitespace",
                             "Black Distance (B)": "blackspace",
                             "Gray Distance (G)": "grayspace"}
        hint_type = menu_to_hint_type[self.sender().text()]
        hint_type_num = self.get_hint_type_num(hint_type)
        pp = self.selectedObjects(True)
        pplen = len(pp)
        new_yg_hint = None
        if hint_type_num == 0:
            if pplen >= 1:
                h = {"ptid": self._model_point(pp[0]).preferred_label()}
                new_yg_hint = ygHint(self.yg_glyph, h)
                self.sig_new_hint.emit(new_yg_hint)
        if hint_type_num in [1, 3]:
            if pplen >= 2:
                # ref should be a touched point and target an untouched point.
                # If it's the other way around, reverse them.
                if pp[1].touched and not pp[0].touched:
                    pp[0], pp[1] = pp[1], pp[0]
                target_name = self._model_point(pp[1]).preferred_label()
                ref_name = self._model_point(pp[0]).preferred_label()
                h = {"ptid": target_name, "ref": ref_name, "rel": hint_type}
                new_yg_hint = ygHint(self.yg_glyph, h)
                self.sig_new_hint.emit(new_yg_hint)
        if hint_type_num == 2:
            if pplen >= 3:
                if pplen > 3:
                    del pp[3:]
                # If two of the three selected points are touched, they are the
                # reference points, and the unselected point is the target.
                # Otherwise, sort the points by x or y position: the middle one
                # is the target, and the ones on the ends are reference points.
                # If the program makes the wrong choice, user can rearrange
                # things in the editor.
                touched_points = []
                untouched_points = []
                for t in pp:
                    if type(t) is ygPointView:
                        if t.touched:
                            touched_points.append(self._model_point(t))
                        else:
                            untouched_points.append(self._model_point(t))
                if len(touched_points) == 2 and len(untouched_points) == 1:
                    touched_names  = [touched_points[0].preferred_label(),
                                      touched_points[1].preferred_label()]
                    untouched_name = untouched_points[0].preferred_label()
                    h = {"ptid": untouched_name, "ref": touched_names, "rel": hint_type}
                    new_yg_hint = ygHint(self.yg_glyph, h)
                else:
                    newlist = []
                    for p in pp:
                        newlist.append(self._model_point(p))
                    sorter = ygPointSorter(self.yg_glyph.current_vector())
                    sorter.sort(newlist)
                    target = newlist.pop(1)
                    ref_names = [newlist[0].preferred_label(),
                                 newlist[1].preferred_label()]
                    target_name = target.preferred_label()
                    h = {"ptid": target_name, "ref": ref_names, "rel": hint_type}
                    new_yg_hint = ygHint(self.yg_glyph, h)
                self.sig_new_hint.emit(new_yg_hint)

    def make_macfunc_from_selection(self, hint_type, **kwargs):
        hint_type_num = self.get_hint_type_num(hint_type)
        pp = self.selectedObjects(True)
        if hint_type_num == 4:
            name = kwargs["name"]
            if hint_type == "function":
                fu = ygFunction(name, self.yg_glyph.yg_font)
                pt_names = fu.required_point_list() + fu.optional_point_list()
                other_params = {"nm": name}
            else:
                ma = ygMacro(name, self.yg_glyph.yg_font)
                pt_names = ma.required_point_list() + ma.optional_point_list()
                other_params = {"nm": name}

            # Got to have param names associated with these points. Gonna make
            # arbitrary assignments, which user must clean up. First assign the
            # required params, then the optional ones.
            pt_dict = {}
            counter = 0
            for p in pt_names:
                try:
                    ppp = pp[counter]
                    if type(ppp) is ygPointView:
                        ppp = self.yg_glyph.points_to_labels(ppp.yg_point)
                    pt_dict[p] = ppp
                    counter += 1
                except IndexError:
                    break

            h = {"ptid": pt_dict, hint_type: other_params}
            yg_hint = ygHint(self.yg_glyph, h)

            self.sig_new_hint.emit(yg_hint)


    def delete_selected_hints(self):
        oo = self.selectedObjects(False)
        hh = []
        for o in oo:
            if type(o) is ygHintView:
                hh.append(o.yg_hint)
        if len(hh) > 0:
            # Call a function in the model.
            hh[0].delete_hints(hh)

    def mousePressEvent(self, event):
        # In ygGlyphViewer
        super().mousePressEvent(event)
        modifier = QApplication.keyboardModifiers()
        if event.button() == Qt.MouseButton.LeftButton:
            if not self._mouse_over_point(event.scenePos()) and not self._mouse_over_hint(event.scenePos()):
                if (modifier & Qt.KeyboardModifier.ShiftModifier) != Qt.KeyboardModifier.ShiftModifier:
                    self.yg_selection._cancel_selection()
                self.dragBeginPoint = event.scenePos()
                self.selectionRect = SelectionRect(QRectF(self.dragBeginPoint, QSizeF(0,0)))
                self.addItem(self.selectionRect)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.selectionRect != None:
            thisx = abs(self.dragBeginPoint.x() - event.scenePos().x())
            thisy = abs(self.dragBeginPoint.y() - event.scenePos().y())
            if thisy > 4 or thisx > 4:
                self.selectionRect.setRect(self._adjust_rect(event.scenePos()))
                self.selectionRect.setPen(QPen(QColor("gray")))
                if self.selectionRect.isVisible():
                    self.selectionRect.update()
                else:
                    self.selectionRect.show()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.selectionRect == None:
            return
        if self.selectionRect.rect().isNull() or self.selectionRect.rect().height() == 0 or self.selectionRect.rect().width() == 0:
            self.removeItem(self.selectionRect)
            self.selectionRect = None
            return
        modifier = QApplication.keyboardModifiers()
        if (modifier & Qt.KeyboardModifier.ShiftModifier) != Qt.KeyboardModifier.ShiftModifier:
            self.yg_selection._add_rect(self.selectionRect.rect(), False)
        else:
            self.yg_selection._toggle_rect(self.selectionRect.rect())
        self.removeItem(self.selectionRect)
        self.selectionRect = None

    def contextMenuEvent(self, event):
        """ This seems horrible, but the most stable procedure (so far) seems
            to be to build every possible menu item and disable/hide the ones
            we don't want.

            Checklist of features:
                Toggle visibility of off-curve poihts: Done
                Toggle point numbers: Done
                Round touched point: Done
                Set control value: Done
                Set distance type for stem hints: Done
                Reverse stem hint: Done
                Additional parameters for functions and macros: Done
                Rearrange function/macro point params: Done
                Add point to function call: Not yet started
                Convert target point to target set in function/macro: Not yet started
                Set target and reference points for function/macro: Done
                Make set: Doesn't yet work for functions/macros
                Create function call: Done
                Create macro call: Done

        """

        cmenu = QMenu()
        selected_points = self.selectedObjects(True)

        # This should be on a "view" top menu (when I get around to that)

        if self.off_curve_points_showing:
            toggle_off_curve_visibility = cmenu.addAction("Hide off-curve points")
        else:
            toggle_off_curve_visibility = cmenu.addAction("Show off-curve points")

        # Show/hide point numbers

        if self.point_numbers_showing:
            toggle_point_number_visibility = cmenu.addAction("Hide point numbers")
        else:
            toggle_point_number_visibility = cmenu.addAction("Show point numbers")

        # "hint" will be None if the mouse pointer is not over a hint

        hint = self._mouse_over_hint(QPointF(event.scenePos()))
        try:
            ntype = hint_type_nums[hint.yg_hint.hint_type()]
        except Exception:
            ntype = 10

        cv_anchor_action_list = []
        cv_stem_action_list = []
        point_param_list = []
        black_space = white_space = gray_space = None

        cmenu.addSeparator()

        # Round point (any ntype but 4)

        round_hint = QAction("Round target point", checkable=True)
        cmenu.addAction(round_hint)
        if hint == None or ntype == 4:
            round_hint.setEnabled(False)
            round_hint.setVisible(False)
        else:
            if self._model_hint(hint).rounded():
                round_hint.setChecked(True)

        # Set control value for anchor hint (ntype == 0)

        set_anchor_cv = cmenu.addMenu("Set control value...")
        cv_list = self.yg_glyph.yg_font.cvt.get_list("pos", self.vector)
        cv_list.sort()
        if len(cv_list) > 0:
            for c in cv_list:
                cv_anchor_action_list.append(set_anchor_cv.addAction(c))
        if hint == None or ntype != 0:
            for c in cv_anchor_action_list:
                c.setEnabled(False)
                c.setVisible(False)
            a = set_anchor_cv.menuAction()
            a.setEnabled(False)
            a.setVisible(False)

        # Set control value for stem hint (ntype == 3)

        set_stem_cv = cmenu.addMenu("Set control value...")
        cv_list = self.yg_glyph.yg_font.cvt.get_list("dist", self.vector)
        cv_list.sort()
        if len(cv_list) > 0:
            for c in cv_list:
                ccv = QAction(c, self, checkable=True)
                if hint and (c == hint.yg_hint.cv()):
                    ccv.setChecked(True)
                set_stem_cv.addAction(ccv)
                cv_stem_action_list.append(ccv)
        if hint == None or ntype != 3:
            for c in cv_stem_action_list:
                c.setEnabled(False)
                c.setVisible(False)
            a = set_stem_cv.menuAction()
            a.setEnabled(False)
            a.setVisible(False)

        # Color. We don't recommend setting the "color" bits directly,
        # but rather set "rel" to blackspace, whitespace, etc.

        hint_color_menu = cmenu.addMenu("Set distance type...")

        no_color_menu = hint == None or ntype != 3

        black_space = QAction("Black", self, checkable=True)
        if hint != None:
            if hint.yg_hint.hint_type() in ["stem", "blackspace"]:
                black_space.setChecked(True)
        hint_color_menu.addAction(black_space)
        if no_color_menu:
            black_space.setEnabled(False)
            black_space.setVisible(False)

        white_space = QAction("White", self, checkable=True)
        if hint != None:
            if hint.yg_hint.hint_type() == "whitespace":
                white_space.setChecked(True)
        hint_color_menu.addAction(white_space)
        if no_color_menu:
            white_space.setEnabled(False)
            white_space.setVisible(False)

        gray_space = QAction("Gray", self, checkable=True)
        if hint != None:
            if hint.yg_hint.hint_type() == "grayspace":
                gray_space.setChecked(True)
        hint_color_menu.addAction(gray_space)
        if no_color_menu:
            gray_space.setEnabled(False)
            gray_space.setVisible(False)

        if no_color_menu:
            a = hint_color_menu.menuAction()
            a.setEnabled(False)
            a.setVisible(False)


        # Reverse a stem (simple arrow) hint

        reverse_hint = cmenu.addAction("Reverse hint")
        if hint == None or not ntype in [1, 3]:
            reverse_hint.setEnabled(False)
            reverse_hint.setVisible(False)

        # Other (non-point) parameters for functions and macros

        add_params = cmenu.addAction("Other parameters...")
        # Hide if no hint selected or hint is the wrong type or it has no non-
        # point parameters.
        if hint == None or ntype != 4 or len(ygCaller(hint.yg_hint.hint_type(),
                                                                hint.yg_hint.name,
                                                                self.yg_glyph.yg_font).non_point_params()) == 0:
            add_params.setEnabled(False)
            add_params.setVisible(False)

        # Rearrange point params for functions and macros

        disable_point_params = False
        # target_point will be HintPointMarker. The pt attribute for that is
        # a ygPointView object.
        target_point = None
        swap_old_name = None
        point_list = []
        try:
            # mouse_over_point actually returns a HintPointMarker.
            target_point = hint.mouse_over_point(QPointF(event.scenePos()))
            if hint.yg_hint.hint_type() == "macro":
                mafu = ygMacro(hint.yg_hint.name, self.yg_glyph.yg_font)
                point_list = mafu.point_list()
            else:
                mafu = ygFunction(hint.yg_hint.name, self.yg_glyph.yg_font)
                point_list = mafu.point_list()
            swap_old_name = target_point.name
            point_list.remove(swap_old_name)
        except Exception as e:
            disable_point_params = True
        point_param_menu = cmenu.addMenu("Point params")
        for p in point_list:
            point_param_list.append(point_param_menu.addAction(p))
        if hint == None or disable_point_params or ntype != 4 or len(point_list) == 0:
            for p in point_list:
                try:
                    p.setEnabled(False)
                    p.setVisible(False)
                except Exception as e:
                    pass
            a = point_param_menu.menuAction()
            a.setEnabled(False)
            a.setVisible(False)

        # Set a target or reference point for a function or macro. Only for use in ordering
        # hints: it has no effect on the rendering otherwise.

        if hint:
            target_point = hint.mouse_over_point(QPointF(event.scenePos()))
            if target_point != None:
                target_point = target_point._get_model_point()
        else:
            target_point = None
        new_target = target_point
        macfunc_target = QAction("Target", checkable=True)
        cmenu.addAction(macfunc_target)
        macfunc_ref = QAction("Reference point", checkable=True)
        cmenu.addAction(macfunc_ref)

        def tgt_pt_check(pt):
            if pt == None:
                return False
            return self.resolve_point_identifier(pt) == target_point

        if hint and tgt_pt_check(self._model_hint(hint).alt_target()):
            macfunc_target.setChecked(True)
            new_target = None
        if hint and tgt_pt_check(self._model_hint(hint).alt_ref()):
            macfunc_ref.setChecked(True)
            new_target = None
        if hint == None or ntype != 4:
            macfunc_target.setEnabled(False)
            macfunc_target.setVisible(False)
            macfunc_ref.setEnabled(False)
            macfunc_ref.setVisible(False)

        # Make a set. Pointer can be anywhere for this.

        # Test whether user can make a set. The rules are:
        #    1. More than one point must be selected.
        #    2. One selected point must be touched by a shift, align or
        #       interpolate instruction (types 1 and 2).
        touched_point = None
        num_of_selected_points = len(selected_points)
        try:
            if num_of_selected_points >= 2:
                for p in selected_points:
                    if p.touched and len(p.owners) >= 1:
                        if hint_type_nums[p.owners[0].yg_hint.hint_type()] in [1, 2]:
                            touched_point = p
                            break
        except Exception:
            pass

        # Functions and macros. Each is marked for which params are points, which are control
        # values, and which are others. For each count up the point params and show only those
        # for which that number falls within the range of possible point counts.

        functions = []
        all_functions = self.yg_glyph.yg_font.functions.keys()
        for f in all_functions:
            if num_of_selected_points in ygFunction(f, self.yg_glyph.yg_font).point_params_range():
                functions.append(f)
        macros = []
        all_macros = self.yg_glyph.yg_font.macros.keys()
        for f in all_macros:
            if num_of_selected_points in ygMacro(f, self.yg_glyph.yg_font).point_params_range():
                macros.append(f)

        function_menu = cmenu.addMenu("Functions")
        function_actions = []
        if len(functions) > 0:
            for f in functions:
                qa = QAction(f, self)
                function_actions.append(qa)
                function_menu.addAction(qa)
        else:
            a = function_menu.menuAction()
            a.setEnabled(False)
            a.setVisible(False)

        macro_menu = cmenu.addMenu("Macros")
        macro_actions = []
        if len(macros) > 0:
            for m in macros:
                qa = QAction(m, self)
                macro_actions.append(qa)
                macro_menu.addAction(qa)
        else:
            a = macro_menu.menuAction()
            a.setEnabled(False)
            a.setVisible(False)

        action = cmenu.exec(event.screenPos())

        if action == toggle_off_curve_visibility:
            self.sig_off_curve_visibility.emit()
        if action == toggle_point_number_visibility:
            self.sig_toggle_point_numbers.emit()
        if hint and (action == reverse_hint):
            self.sig_reverse_hint.emit(hint.yg_hint)
        if hint and action in cv_anchor_action_list:
            self.sig_change_cv.emit({"hint": hint, "cv": action.text()})
        if hint and action in cv_stem_action_list:
            self.sig_change_cv.emit({"hint": hint, "cv": action.text()})
        if hint and ntype == 3 and (action == black_space):
            self.sig_change_hint_color.emit({"hint":  hint, "color": "blackspace"})
        if hint and ntype == 3 and (action == white_space):
            self.sig_change_hint_color.emit({"hint":  hint, "color": "whitespace"})
        if hint and ntype == 3 and (action == gray_space):
            self.sig_change_hint_color.emit({"hint":  hint, "color": "grayspace"})
        if hint and ntype == 4 and (action == add_params):
            self.sig_edit_macfunc_params.emit(hint)
        if action in macro_actions:
            self.sig_make_macfunc.emit({"hint_type": "macro", "name": action.text()})
        if action in function_actions:
            self.sig_make_macfunc.emit({"hint_type": "function", "name": action.text()})
        if action in point_param_list:
            self.sig_swap_macfunc_points.emit({"hint": hint, "new_pt": action.text(), "old_pt": swap_old_name})
        if action == macfunc_target:
            self.sig_macfunc_target.emit({"hint": hint, "pt": new_target})
        if action == macfunc_ref:
            self.sig_macfunc_ref.emit({"hint": hint, "pt": new_target})
        if hint != None and action == round_hint:
            self.sig_round_hint.emit(hint)



class MyView(QGraphicsView):
    """ The container for the graphical hint editor.

        It holds and displays an instance of ygGlyphViewer; it will hold various
        buttons and controls, plus (I hope) a preview of the hinted glyph.

        Parameters:
        viewer (ygGlyphView): The QGraphicsScene that the user interacts with.

        font (ygModel.ygFont): The font object, including both a fontTools Font
        object and the yaml file (as read by the Python yaml module). Has
        convenience functions supplying various kinds of information about the
        font.

        parent: Is this used at all?
    """

    sig_goto = pyqtSignal(object)

    def __init__(self, preferences, viewer, font, parent=None):
        super(MyView, self).__init__(viewer, parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
        self.viewer = viewer
        self.original_transform = self.transform()
        self.yg_font = font
        self.preferences = preferences

    def setup_goto_signal(self, o):
        self.sig_goto.connect(o)

    def _current_index(self):
        return self.yg_font.glyph_index[self.viewer.yg_glyph.gname]

    def go_to_glyph(self, g):
        self.sender().disconnect()
        self.parent().parent().disconnect_glyph_pane()
        try:
            self.yg_font.glyph_index[g]
            self.switch_to(g)
        except Exception as e:
            print(e)
            self.preferences.top_window().show_error_message(["Warning", "Warning", "Can't load requested glyph."])
        self.parent().parent().setup_glyph_pane_connections()

    def next_glyph(self, a):
        self.sender().disconnect()
        self.parent().parent().disconnect_glyph_pane()
        current_index = self._current_index()
        if current_index < len(self.yg_font.glyph_list) - 1:
            gname = self.yg_font.glyph_list[current_index + 1][1]
        self.switch_to(gname)
        self.parent().parent().setup_glyph_pane_connections()

    def previous_glyph(self, a):
        self.parent().parent().disconnect_glyph_pane()
        self.sender().disconnect()
        current_index = self._current_index()
        if current_index > 0:
            gname = self.yg_font.glyph_list[current_index - 1][1]
        self.switch_to(gname)
        self.parent().parent().setup_glyph_pane_connections()

    def switch_from_font_viewer(self, gname):
        self.parent().parent().disconnect_glyph_pane()
        self.switch_to(gname)
        self.parent().parent().setup_glyph_pane_connections()

    def switch_to(self, gname):
        self.viewer.yg_glyph.save_source()
        new_glyph = ygGlyph(self.preferences, self.yg_font, gname)
        self.viewer = ygGlyphViewer(self.preferences, new_glyph)
        self.preferences.set_current_glyph(self.yg_font.full_name(), gname)
        self.setScene(self.viewer)
        self.centerOn(self.viewer.glyphwidget.center_x, self.sceneRect().center().y())
        self.parent().parent().set_window_title()
        ed = self.preferences.top_window().source_editor
        new_glyph.set_yaml_editor(ed)

    def switch_to_x(self):
        if self.viewer:
            self.viewer.yg_glyph.switch_to_vector("x")
            self.parent().parent().set_window_title()

    def switch_to_y(self):
        if self.viewer:
            self.viewer.yg_glyph.switch_to_vector("y")
            self.parent().parent().set_window_title()

    def set_background(self):
        self.setBackgroundBrush(QBrush(QColor(200,200,200,255)))

    def zoom(self, a):
        """ Called by signal.
        """
        self.sender().disconnect()
        sender_text = self.sender().text()
        if sender_text == "Original Size":
            self.setTransform(self.original_transform)
        elif sender_text == "Zoom In":
            self.scale(1.5, 1.5)
        elif sender_text == "Zoom Out":
            self.scale(0.75, 0.75)
        self.parent().parent().setup_zoom_connections()

    def keyPressEvent(self, event):
        if event.key() in [16777219, 16777223]:
            self.viewer.delete_selected_hints()
