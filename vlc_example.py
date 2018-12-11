#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 19:40:32 2018

@author: pedrohames
"""

import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('GdkX11', '3.0')
from gi.repository import GdkX11
import contiudo
import sip_register

import vlc

class ApplicationWindow(Gtk.Window):

    def __init__(self):
        self.my_IP = '192.168.1.231'
        self.my_number = 6032
        self.video_port = 4000
        self.audio_port = 4001
        self.cam_IP = '192.168.1.211'
        self.cam_number = '6002'
        self.port_reg = 5060
        self.ip_server = '192.168.1.1'
        self.port_reg_dest = 5060

        self.obj_sip_reg = sip_register.sip_register(self.my_IP, self.port_reg, self.ip_server, self.port_reg_dest, self.my_number)
        self.reg_str = self.obj_sip_reg.register()
        self.obj_sip_reg.send(self.reg_str)
        Gtk.Window.__init__(self, title="Python-Vlc Media Player")
        self.player_paused=False
        self.is_player_active = False
        self.connect("destroy", Gtk.main_quit)

    def show(self):
        self.show_all()

    def setup_objects_and_events(self):
        self.playback_button = Gtk.Button()
        self.stop_button = Gtk.Button()

        self.play_image = Gtk.Image.new_from_icon_name(
                "gtk-media-play",
                Gtk.IconSize.MENU
            )
        self.pause_image = Gtk.Image.new_from_icon_name(
                "gtk-media-pause",
                Gtk.IconSize.MENU
            )
        self.stop_image = Gtk.Image.new_from_icon_name(
                "gtk-media-stop",
                Gtk.IconSize.MENU
            )

        self.playback_button.set_image(self.play_image)
        self.stop_button.set_image(self.stop_image)

        self.playback_button.connect("clicked", self.toggle_player_playback)
        self.stop_button.connect("clicked", self.stop_player)

        self.draw_area = Gtk.DrawingArea()
        self.draw_area.set_size_request(300,300)

        self.draw_area.connect("realize",self._realized)

        self.hbox = Gtk.Box(spacing=6)
        self.hbox.pack_start(self.playback_button, True, True, 0)
        self.hbox.pack_start(self.stop_button, True, True, 0)

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.vbox)
        self.vbox.pack_start(self.draw_area, True, True, 0)
        self.vbox.pack_start(self.hbox, False, False, 0)

    def do_delete_event(self, event):
        self.reg_str = self.obj_sip_reg.deregister()
        self.obj_sip_reg.send(self.reg_str)

    def stop_player(self, widget, data=None):
        self.player.stop()
        self.is_player_active = False
        self.playback_button.set_image(self.play_image)

    def toggle_player_playback(self, widget, data=None):

        """
        Handler for Player's Playback Button (Play/Pause).
        """

        if self.is_player_active == False and self.player_paused == False:
            self.player.play()
            self.playback_button.set_image(self.pause_image)
            self.is_player_active = True

        elif self.is_player_active == True and self.player_paused == True:
            self.player.play()
            self.playback_button.set_image(self.pause_image)
            self.player_paused = False

        elif self.is_player_active == True and self.player_paused == False:
            self.player.pause()
            self.playback_button.set_image(self.play_image)
            self.player_paused = True
        else:
            pass

    def _realized(self, widget, data=None):
        self.vlcInstance = vlc.Instance("--no-xlib")
        self.player = self.vlcInstance.media_player_new()
        win_id = widget.get_window().get_xid()
        self.player.set_xwindow(win_id)
#        self.player.set_mrl(MRL)
        media = self.vlcInstance.media_new(MRL)
        self.player.set_media(media)
        self.player.play()
        self.playback_button.set_image(self.pause_image)
        self.is_player_active = True

if __name__ == '__main__':
    window = ApplicationWindow()

    my_IP = '192.168.1.231'
    my_number = 6032
    video_port = 4000
    audio_port = 4001
    cam_IP = '192.168.1.211'
    cam_number = '6002'
    port_reg = 5060
    ip_server = '192.168.1.1'
    port_reg_dest = 5060
    cont = contiudo.contiudo(my_IP, str(my_number), video_port, audio_port, cam_IP, cam_number, ip_server)
    open('stream.sdp','w').write(cont.getSDP())
    MRL = 'stream.sdp'
#    MRL = 'rtsp://184.72.239.149/vod/mp4:BigBuckBunny_175k.mov'
    window.setup_objects_and_events()
    window.show()
    Gtk.main()
    window.player.stop()
    window.vlcInstance.release()
