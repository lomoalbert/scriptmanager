# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# This file is in the public domain
### END LICENSE

from locale import gettext as _

import os
import glob
import os.path
import re
import cPickle

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('scriptmanager')

from scriptmanager_lib import Window
from scriptmanager.AboutScriptmanagerDialog import AboutScriptmanagerDialog
from scriptmanager.PreferencesScriptmanagerDialog import PreferencesScriptmanagerDialog

from scriptmanager_lib.scriptmanagerconfig import get_data_path


# See scriptmanager_lib.Window.py for more details about how this class works
class ScriptmanagerWindow(Window):
    __gtype_name__ = "ScriptmanagerWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        super(ScriptmanagerWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutScriptmanagerDialog
        self.PreferencesDialog = PreferencesScriptmanagerDialog
        
        self.list = builder.get_object('treeview1')
        self.liststore2 = builder.get_object('liststore1')
        self.entry1 = builder.get_object('entry1')
        self.entry2 = builder.get_object('entry2')
        self.textview1 = builder.get_object('textview1')
        self.bf=self.textview1.get_buffer()
        self.treeview_selection1 = builder.get_object('treeview-selection1')
        
        column = Gtk.TreeViewColumn('title', Gtk.CellRendererText(), text=0)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.list.append_column(column)

        column = Gtk.TreeViewColumn('tag', Gtk.CellRendererText(), text=1)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.list.append_column(column)
        
        '''column = Gtk.TreeViewColumn('script', Gtk.CellRendererText(), text=2)   
        column.set_clickable(True)   
        column.set_resizable(True)   
        self.list.append_column(column)'''
        self.init_db()
    

        
    def init_db(self):
        self.db_path=os.path.join(os.environ['HOME'],'.scriptdb')
        if not os.path.exists(self.db_path):
            with open(self.db_path,'w') as fi:
                cPickle.dump([],fi)
        fi = open(self.db_path)
        self.scriptdb=cPickle.load(fi)
        fi.close()
        for script in self.scriptdb:
            self.liststore2.append(script)
        
    def refresh(self):
        with open(self.db_path,'w') as fi:
            cPickle.dump(self.scriptdb,fi)

    def getscript(self):
        return [self.entry1.get_text() ,self.entry2.get_text() ,self.bf.get_text(self.bf.get_start_iter(),self.bf.get_end_iter(),True)]


    def button1_clicked_cb(self,widget):
        logging.info('button1_clicked_cb')
        title,tag,script = self.getscript()
        self.scriptdb[self.scriptdb.index(list(self.liststore2.get(self.treeview_selection1.get_selected()[1],0,1,2)))]=self.getscript()
        logging.info('save',0,title,1,tag,2,script)
        self.liststore2.set(self.treeview_selection1.get_selected()[1],0,title,1,tag,2,script)
        self.refresh()

    def button2_clicked_cb(self,widget):
        logging.info('button2_clicked_cb')
        self.liststore2.append(self.getscript())
        self.scriptdb.append(self.getscript())
        self.refresh()

        
    def button3_clicked_cb(self,widget):
        title,tag,script = self.liststore2.get(self.treeview_selection1.get_selected()[1],0,1,2)
        self.liststore2.remove(self.treeview_selection1.get_selected()[1])
        self.scriptdb.remove([title,tag,script])
        self.refresh()
        
    def treeview_selection1_changed_cb(self,widget):
        if widget.get_selected()[1]:
            title,tag,script = self.liststore2.get(widget.get_selected()[1],0,1,2)
        else:
            return
        self.entry1.set_text(title)
        self.entry2.set_text(tag)
        self.bf.set_text(script)
        
    def entry3_changed_cb(self,widget):
        self.search(widget.get_text())
        
    def entry3_activate_cb(self,widget):
        self.search(widget.get_text())
        
    def search(self,keyword):
        self.liststore2.clear()
        for script in self.scriptdb:
            if keyword in str(script):
                self.liststore2.append(script)
