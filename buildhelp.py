#!/usr/bin/python
# ....

import os
import sys
import platform
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade

def get_deps_common():
    pass

class EnvCommon:
    arch = "32bit"
    is_current = False
    env_string = ""
    # TODO: Add all the options
    all_config_options = [
        "--with-gcc-speedup",
        "--with-system-libwpd",
        "--with-system-libwpg",
        "--with-system-libwps",
        "--without-junit",
        "--with-distro",
        "--enable-mysql-connector",
        "--with-libmysql-path",
        "--with-num-cpus",
        "--with-max-jobs",
        "--with-srcdir",
        "--with-mozilla-build",
        "--disable-mono",
        "--with-lang",
        "--with-poor-help-localizations",
        "--disable-build-mozilla",
        "--enable-minimizer",
        "--enable-presenter-console",
        "--enable-pdfimport",
        "--enable-wiki-publisher",
        "--enable-report-builder",
        "--with-google-docs",
        "--with-nlpsolver",
        "--with-ct2n",
        "--with-numbertext",
        "--with-languagetool",
        "--with-java-target-version",
        "--with-extension-integration"
    ]
    
    current_config = [
        "--disable-mono"
    ]

    def __init__(self):
        pass
    
    def get_status(self):
        return self.is_current

    def get_env_string(self):
        return self.env_string

    def get_all_configs(self):
        return self.all_config_options

    def get_cur_config(self):
        return self.current_config
    
    def set_cur_config(self, config):
        self.current_config = config

class EnvWindows(EnvCommon):
    cygwin = False
    default_cygwin_path = "c:\cygwin"

    def __init__(self):
        EnvCommon.__init__(self)
        if "cygwin" in platform.system().lower():
            self.cygwin = True
            self.is_current = True
        elif "windows" in platform.system().lower():
            is_current = True
        try:
            self.arch = platform.architecture()[0]
        except:
            pass
        self.env_string = "Win: "+self.arch
       
    # if windows then do check for
    # 1. mozilla build directory
    # 2. 
    def get_deps(self):
        pass
    
    # Check if python is running from inside cygwin or
    # as native application
    def get_git_path(self):
        return "/usr/bin/git"
        
# TODO: Somebody having a mac could complete this?
class EnvMac(EnvCommon):
    def __init__(self):
        EnvCommon.__init__(self)
        if "mac" in platform.system().lower():
            self.is_current = True
        self.arch = platform.architecture()[0]
        self.env_string = "Mac: "+self.arch
    
    def get_deps(self):
        pass

    def get_git_path(self):
        return "/usr/bin/git"

class EnvLinux(EnvCommon):
    default_config = [
        "--disable-mono",
        '--with-gcc-speedup="icecream,ccache"'
    ]
    def __init__(self):
        EnvCommon.__init__(self)
        if "linux" in platform.system().lower():
            self.is_current = True
        self.arch = platform.architecture()[0]
        self.env_string = "Linux: "+self.arch
        EnvCommon.set_cur_config(self, self.default_config)
    
    def get_deps(self):
        pass
    
    def get_git_path(self):
        return "/usr/bin/git"

class ConfigUI:
    def get_n_txtbox(self, n):
        for w in self.tableview.get_children():
            if w.get_name() == "txt:%d"%n:
                return w
        return None
    
    def destroy(self, widget):
        config = []
        for w in self.tableview.get_children():
            if "cb:" in w.get_name() and w.get_active():
                n = w.get_name().split(":")
                option = self.parent.cconfig.get_all_configs()[int(n[1])]
                t = self.get_n_txtbox(int(n[1]))
                if t != None and len(t.get_text()):
                    txt = t.get_text()
                    txt = txt.replace("'","")
                    txt = txt.replace('"',"")
                    option = option + '=' + txt + ''
                config.append(option)
        print config
        self.parent.cconfig.set_cur_config(config)
        self.parent.show()
    
    def __init__(self, parent):
        self.parent = parent
        if parent.cconfig == None:
            print "Unknown configuration!"
            parent.show()
            return
        self.configui = gtk.glade.XML("buildhelp/buildhelp.glade", "configui")
        dic = {"on_config_destroy": self.destroy
               }
        self.configui.signal_autoconnect(dic)
        self.tableview = self.configui.get_widget("configtable")
        self.tableview.resize(len(parent.cconfig.get_all_configs()), 3)
        for i in range(0,len(parent.cconfig.get_all_configs())):
            cb = gtk.CheckButton()
            cb.set_name("cb:%d" % i)
            self.tableview.attach(cb, 0,1,i,i+1)
            label = gtk.Label(parent.cconfig.get_all_configs()[i])
            label.set_justify(gtk.JUSTIFY_LEFT)
            self.tableview.attach(label, 1, 2, i, i+1)
            text = gtk.Entry()
            text.set_name("txt:%d" % i)
            self.tableview.attach(text, 2, 3, i, i+1)
        for i in parent.cconfig.get_cur_config():
            option = i.split("=")
            try:
                index = parent.cconfig.get_all_configs().index(option[0]) 
                if index >= 0:
                    for w in self.tableview.get_children():
                        if w.get_name() == "cb:%d" % index:
                            w.set_active(True)
                        if w.get_name() == "txt:%d" % index and len(option) > 1:
                            txt = option[1]
                            w.set_text(txt)
            except:
                pass
        self.tableview.show_all() 
        

class BuildUI:
    buildenvs = [EnvLinux(), EnvWindows(), EnvMac()]
    cconfig = None
    os_name = "Linux64"
    get_deps_local = None
    path = os.getcwd()
    
    def show(self, show=True):
        if show:
            self.buildui.get_widget("buildui").show_all()
        else:
            self.buildui.get_widget("buildui").hide_all()
    
    def check_cloned(self):
        cloned = False
        self.path = self.buildui.get_widget("path_label").get_text()
        if len(self.path) <= 0:
            self.path = os.getcwd()
        try:
            gitfile = open(self.path+"/.git/config")
            for line in gitfile:
                if "libreoffice/core" in line:
                    cloned = True
                    break
                gitfile.close()
        except:
                pass
        return cloned
    
    def execute_get_dependencies(self, widget):
        pass
    
    def execute_clone(self, widget):
        git = self.cconfig.get_git_path()
        if self.check_cloned():
            self.display_clone_error("Already clonned. Try git pull -r")
            return
        self.show(False)
        gtk.gdk.flush()
        os.system(git+" clone git://anongit.freedesktop.org/libreoffice/core "+self.path )
        self.show()
        
    def execute_set_config_options(self, widget):
        self.show(False)
        self.confwindow = ConfigUI(self)
    
    def display_clone_error(self, msg):
        a = gtk.MessageDialog(type = gtk.MESSAGE_ERROR, 
                      buttons = gtk.BUTTONS_OK, 
                      message_format=msg)
        a.run()
        a.destroy()
    
    def execute_pull(self, widget):
        if not self.check_cloned():
            self.display_clone_error("Please clone first...")
            return
        self.show(False)
        gtk.gdk.flush()
        cwd = os.getcwd()
        os.chdir(self.path)
        git = self.cconfig.get_git_path()
        os.system(git+" pull -r")
        os.chdir(cwd)
        self.show()

    def execute_help(self, widget):
        pass

    def execute_go(self, widget):
        if not self.check_cloned():
            self.display_clone_error("Please clone first...")
            return
        # TODO: Check if ./configure or ./autogen.sh needs to be run
        self.show(False)
        gtk.gdk.flush()
        cwd = os.getcwd()
        os.chdir(self.path)
        config = ""
        for c in self.cconfig.get_cur_config():
            config = config + " "+c
        #os.system("./autogen.sh "+config)
        #os.system("make")
        # Check if make succeeded
        #os.system("make dev-install")
        os.chdir(cwd)
        self.show()        
    
    def delete_event(self, widget, event, data=None):
        return False

    # Detect the path for the build (mostly if its the current directory
    # or $pwd/libo
    def detect_path(self):
        pass

    def destroy(self, widget, data=None):
        gtk.main_quit()
    
    
    def __init__(self):
        for e in self.buildenvs:
            if e.get_status:
                self.cconfig = e
                break
        if self.cconfig == None:
            print "Unable to detect platform: "+platform.system()+":"+platform.architecture()[0]
            print "Please report to the LibreOffice mailing list"
            sys.exit()

        self.buildui = gtk.glade.XML("buildhelp/buildhelp.glade", "buildui")
        dic = {"on_buildui_destroy": self.destroy,
               "on_exit_clicked": self.destroy,
               "on_config_clicked":self.execute_set_config_options,
               "on_gitpull_clicked":self.execute_pull,
               "on_go_clicked":self.execute_go,
               "on_help_clicked":self.execute_help,
               "on_getdeps_clicked": self.execute_get_dependencies,
               "on_clone_clicked": self.execute_clone
               }
        self.buildui.signal_autoconnect(dic)
        # Set git clone path
        self.buildui.get_widget("path_label").set_text(self.path)
        if not self.check_cloned():
            self.path = self.path + "/libo"
            
        self.buildui.get_widget("os_label").set_text(self.cconfig.get_env_string())
        self.buildui.get_widget("path_label").set_text(self.path)
        
    def main(self):
        gtk.main()


if __name__ == "__main__":
    mainwindow = BuildUI()
    mainwindow.main()
    
