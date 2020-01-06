# --------------------------------------------------- #
'''

MPK25 control script for ableton Live, written by Christopher Zaworski
Based of my script for the MPD26


special credits to Alzy (Seppe?), his original script can be found at
https://forum.ableton.com/viewtopic.php?f=4&t=157266
Also thank you to
http://livecontrol.q3f.org/ableton-liveapi/articles/introduction-to-the-framework-classes/
and especially http://remotescripts.blogspot.ca/

Also credits to Julien Bayle for providing much of Ableton's API in an awesome
resource available at:
http://julienbayle.net/AbletonLiveRemoteScripts_Docs/_Framework/


'''


#.....................................
#---------------------------------------------------- #
from __future__ import with_statement

import sys
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from ConfigurableButtonElement import ConfigurableButtonElement
from _Framework.SessionComponent import SessionComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.EncoderElement import EncoderElement
from _Framework.SessionZoomingComponent import SessionZoomingComponent

from _Framework.ChannelStripComponent import ChannelStripComponent
from _APC.DetailViewCntrlComponent import DetailViewCntrlComponent

from DeviceNavComponent import DeviceNavComponent


from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from consts import *
mixer = None


class WORSHIP_TRIGGERS(ControlSurface):
    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        self._device_selection_follows_track_selection = True
        with self.component_guard():
            self._suppress_send_midi = True
            self._suppress_session_highlight = True
            self._control_is_with_automap = False
            is_momentary = True
            self._suggested_input_port = 'nanoPAD2 (PAD)'
            self._suggested_output_port = 'nanoPAD2 (CTRL)'
            self.log("BEFORE mixer")
            self.scene_select_buttons = []
            # self._setup_mixer_control()
            # self._setup_device_control()
            self._setup_session_control()


            
    def _setup_session_control(self):
        """SESSION ViEW"""
        global session
        session = SessionComponent(GRIDSIZE[0],GRIDSIZE[1])
        session.name = 'Session_Control'
        # matrix = ButtonMatrixElement()
        # matrix.name = 'Button_Matrix'
        # up_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, UP_BUTTON)
        # down_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, DOWN_BUTTON)
        # left_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, LEFT_BUTTON)
        # right_button = ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, RIGHT_BUTTON)

        # session_zoom = SessionZoomingComponent(session)
        # session_zoom.set_nav_buttons(up_button,down_button,left_button,right_button)
        for idx in xrange(len(NAV_BUTTONS)):
            self.scene_select_buttons.append(ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, NAV_BUTTONS[idx]))
            self.scene_select_buttons[idx].add_value_listener(self._scene_select_event, identify_sender=True)

        session_stop_buttons = []
        self.log("SETTING UP GRID")
        for row in xrange(GRIDSIZE[1]):
            # button_row = []
            self.log("CZ ROW")
            self.log(str(row))
            scene = session.scene(row)
            scene.name = 'Scene_' + str(row)
            scene.set_launch_button(ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, SCENE_BUTTONS[row]))
            scene.set_triggered_value(2)

            # for column in xrange(GRIDSIZE[0]):
            #     self.log("CZ COLUMN")
            #     self.log(str(column))
            #     button = ConfigurableButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, LAUNCH_BUTTONS[row][column])
            #     button.name = str(column) + '_Clip_' + str(row) + '_Button'
            #     button_row.append(button)
            #     clip_slot = scene.clip_slot(column)
            #     clip_slot.name = str(column) + '_Clip_Slot_' + str(row)
            #     clip_slot.set_launch_button(button)

            # matrix.add_row(tuple(button_row))

        # for column in xrange(GRIDSIZE[0]):
        #     session_stop_buttons.append((ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, TRACK_STOPS[column])))

        self._suppress_session_highlight = False
        self._suppress_send_midi = False
        self.set_highlighting_session_component(session)
        # session.set_stop_track_clip_buttons(tuple(session_stop_buttons))
        session.set_mixer(mixer)

    def log(self, message):
        sys.stderr.write("LOG: " + message.encode("utf-8"))

    def _set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks):
        if not self._suppress_session_highlight:
            ControlSurface._set_session_highlight(self, track_offset, scene_offset, width, height, include_return_tracks)

    def _scene_select_event(self, value, sender):
        # assert (self._stop_button != None)
        assert isinstance(value, int)
        try:
            scene_offset = self.scene_select_buttons.index(sender) * GRIDSIZE[1]
            session.set_offsets(0, scene_offset)
        except Error:
            self.log("scene select error")
            return None
        

    def disconnect(self):
        """clean things up on disconnect"""
        for idx in xrange(len(NAV_BUTTONS)):
            if self.scene_select_buttons[idx] != None:
                self.scene_select_buttons[idx].remove_value_listener(self._scene_select_event)
                self.scene_select_buttons[idx] = None
            
        ControlSurface.disconnect(self)
        return None
