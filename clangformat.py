from gi.repository import GObject, Gtk, Gedit, Gdk
from subprocess import Popen, PIPE

class ClangFormatPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "ClangFormatPlugin"

    window = GObject.property(type=Gedit.Window)
    _handlers = []

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        handler_id = self.window.connect('key-press-event', self.on_key_press_event)
        self._handlers.append(handler_id)

    def do_deactivate(self):
        for handler_id in self._handlers:
            self.window.disconnect(handler_id)

    def do_update_state(self):
        pass

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        if event.state & Gdk.ModifierType.CONTROL_MASK and key == 'F':
            self.format_document()
            return True

        return False

    #formats the current document's text using clang-format
    def format_document(self):
        doc = self.window.get_active_document()
        
        if not doc:
            return
        
        lang = doc.get_language() 
        if lang.get_name() in ("C", "C++", "C/C++/ObjC Header"):
            doc_text = doc.get_text(doc.get_start_iter(), doc.get_end_iter(),include_hidden_chars=True)
            enc_input = doc_text.encode('utf-8')
            p = Popen(['clang-format'], stdout=PIPE, stdin=PIPE)
            output = p.communicate(input=enc_input)[0]
            
            #begin single user action, as otherwise removing the old text and 
            #inserting the new text are counted as two separate undo actions
            doc.begin_user_action()
            doc.set_text(output.decode('utf-8'))
            doc.end_user_action()