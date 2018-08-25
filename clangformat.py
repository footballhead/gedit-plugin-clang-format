from gi.repository import GObject, Gtk, Gedit, Gdk
from subprocess import Popen, PIPE
import random
import string
import json
import os.path

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
            
            pos = doc.props.cursor_position
            
            enc_input = doc_text.encode('utf-8')
            doc_path = doc.get_location().get_path()
            popen_cwd = os.path.split(doc_path)[0]
            p = Popen(['clang-format', '-style=file', '-cursor=%d' % (pos)],
                      stdout=PIPE, stdin=PIPE, cwd=popen_cwd)
            output = p.communicate(input=enc_input)[0].decode('utf-8')
            
            #get new cursor position
            (cursor_str,formatted_text) = output.split('\n', 1)
            pos =  json.loads(cursor_str)['Cursor']

            #begin single user action
            doc.begin_user_action()
            doc.set_text(formatted_text)
            cursor_iter = doc.get_iter_at_offset(pos)
            doc.place_cursor(cursor_iter)
            doc.end_user_action()
