import xbmc
import xbmcgui


class DialogSelect(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listing = kwargs.get("listing")
        self.title = kwargs.get("title")
        self.totalitems = 0
        self.result = None

    def autofocus_listitem(self):
        pass

    def close_dialog(self, cancelled=False):
        if cancelled:
            self.result = False
        else:
            self.result = self.list_control.getSelectedItem()
        self.close()

    def onInit(self):
        self.list_control = self.getControl(6)
        self.getControl(3).setVisible(False)
        self.list_control.setEnabled(True)
        self.list_control.setVisible(True)
        self.set_cancel_button()
        self.getControl(5).setVisible(False)
        self.getControl(1).setLabel(self.title)
        self.list_control.addItems(self.listing)
        self.setFocus(self.list_control)
        self.totalitems = len(self.listing)
        self.autofocus_listitem()

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216, 247, 257, 275, 61467, 61448, ):
            self.close_dialog(True)
        if (action.getId() == 7 or action.getId() == 100) and xbmc.getCondVisibility(
                "Control.HasFocus(3) | Control.HasFocus(6)"):
            self.close_dialog()

    def onClick(self, controlID):
        if controlID == 5:
            self.result = True
            self.close()
        else:
            self.close_dialog(True)

    def set_cancel_button(self):
        try:
            self.getControl(7).setLabel(xbmc.getLocalizedString(222))
            self.getControl(7).setVisible(True)
            self.getControl(7).setEnabled(True)
        except Exception:
            pass
