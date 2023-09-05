#   ___ _____ ___ _     _____    ____             __ _
#  / _ \_   _|_ _| |   | ____|  / ___|___  _ __  / _(_) __ _
# | | | || |  | || |   |  _|   | |   / _ \| '_ \| |_| |/ _` |
# | |_| || |  | || |___| |___  | |__| (_) | | | |  _| | (_| |
#  \__\_\|_| |___|_____|_____|  \____\___/|_| |_|_| |_|\__, |
#                                                      |___/

# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
from libqtile import bar, extension, hook, layout, qtile, widget
from libqtile.config import Click, Drag, Group, Key, KeyChord, Match, Screen
from libqtile.lazy import lazy
# Make sure 'qtile-extras' is installed or this config will not work.
from qtile_extras import widget
from qtile_extras.widget.decorations import BorderDecoration
#from qtile_extras.widget import StatusNotifier
import colors
import arcobattery
from datetime import datetime as dt
import time


# Allows you to input a name when adding treetab section.
@lazy.layout.function
def add_treetab_section(layout):
    prompt = qtile.widgets_map["prompt"]
    prompt.start_input("Section name: ", layout.cmd_add_section)


# When application launched automatically focus it's group
@hook.subscribe.client_new
def modify_window(client):
    for group in groups:  # follow on auto-move
        match = next((m for m in group.matches if m.compare(client)), None)
        if match:
            targetgroup = client.qtile.groups_map[group.name]  # there can be multiple instances of a group
            targetgroup.cmd_toscreen(toggle=False)
            break

# Hook to fallback to the first group with windows when last window of group is killed
@hook.subscribe.client_killed
def fallback(window):
    if window.group.windows != [window]:
        return
    idx = qtile.groups.index(window.group)
    for group in qtile.groups[idx - 1::-1]:
        if group.windows:
            qtile.current_screen.toggle_group(group)
            return
    qtile.current_screen.toggle_group(qtile.groups[0])

# Work around for matching Spotify
@hook.subscribe.client_new
def slight_delay(window):
    time.sleep(0.04)


# Add th, nd or st to the date - use custom_date in text box
def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def custom_date():
    return custom_strftime('%A {S} %B %Y - %H:%M', dt.now())


#mod4 or mod = super key
mod = "mod4"
mod1 = "alt"
mod2 = "control"
home = os.path.expanduser('~')

myTerm = "alacritty"      # My terminal of choice


@lazy.function
def window_to_prev_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i - 1].name)

@lazy.function
def window_to_next_group(qtile):
    if qtile.currentWindow is not None:
        i = qtile.groups.index(qtile.currentGroup)
        qtile.currentWindow.togroup(qtile.groups[i + 1].name)

keys = [
    # The essentials
    Key([mod], "Return", lazy.spawn(myTerm), desc="Terminal"),
    Key([mod, "shift"], "l", lazy.spawn("dm-logout"), desc="Logout menu"),
    # Key([mod, "shift"], "p", lazy.spawn(home + "/.config/qtile/scripts/powermenu.sh"), desc="Open Powermenu (Slock)"),
    Key([mod, "shift"], "p", lazy.spawn(home + "/.config/rofi/powermenu.sh"), desc="Open Powermenu (Rofi)"),
    Key([mod, "shift"], "m", lazy.spawn("rofi -show combi"), desc="Open Run Menu"),
    Key([mod, "shift"], "w", lazy.spawn(home + "/.config/scripts/updatewal.sh"), desc="Update Theme and Wallpaper"),

# Most of our keybindings are in sxhkd file - except these

# SUPER + FUNCTION KEYS

    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "q", lazy.window.kill()),


# SUPER + SHIFT KEYS

    Key([mod, "shift"], "q", lazy.window.kill()),
    Key([mod, "shift"], "r", lazy.restart()),


# QTILE LAYOUT KEYS
    Key([mod], "n", lazy.layout.normalize()),
    Key([mod], "space", lazy.next_layout()),

# CHANGE FOCUS
    Key([mod], "Up", lazy.layout.up()),
    Key([mod], "Down", lazy.layout.down()),
    Key([mod], "Left", lazy.layout.left()),
    Key([mod], "Right", lazy.layout.right()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),


# RESIZE UP, DOWN, LEFT, RIGHT
    Key([mod, "control"], "l",
        lazy.layout.grow_right(),
        lazy.layout.grow(),
        lazy.layout.increase_ratio(),
        lazy.layout.delete(),
        ),
    Key([mod, "control"], "Right",
        lazy.layout.grow_right(),
        lazy.layout.grow(),
        lazy.layout.increase_ratio(),
        lazy.layout.delete(),
        ),
    Key([mod, "control"], "h",
        lazy.layout.grow_left(),
        lazy.layout.shrink(),
        lazy.layout.decrease_ratio(),
        lazy.layout.add(),
        ),
    Key([mod, "control"], "Left",
        lazy.layout.grow_left(),
        lazy.layout.shrink(),
        lazy.layout.decrease_ratio(),
        lazy.layout.add(),
        ),
    Key([mod, "control"], "k",
        lazy.layout.grow_up(),
        lazy.layout.grow(),
        lazy.layout.decrease_nmaster(),
        ),
    Key([mod, "control"], "Up",
        lazy.layout.grow_up(),
        lazy.layout.grow(),
        lazy.layout.decrease_nmaster(),
        ),
    Key([mod, "control"], "j",
        lazy.layout.grow_down(),
        lazy.layout.shrink(),
        lazy.layout.increase_nmaster(),
        ),
    Key([mod, "control"], "Down",
        lazy.layout.grow_down(),
        lazy.layout.shrink(),
        lazy.layout.increase_nmaster(),
        ),


# FLIP LAYOUT FOR MONADTALL/MONADWIDE
    Key([mod, "shift"], "f", lazy.layout.flip()),

# FLIP LAYOUT FOR BSP
    Key([mod, "mod1"], "k", lazy.layout.flip_up()),
    Key([mod, "mod1"], "j", lazy.layout.flip_down()),
    Key([mod, "mod1"], "l", lazy.layout.flip_right()),
    Key([mod, "mod1"], "h", lazy.layout.flip_left()),

# MOVE WINDOWS UP OR DOWN BSP LAYOUT
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "h", lazy.layout.shuffle_left()),
    Key([mod, "shift"], "l", lazy.layout.shuffle_right()),

# MOVE WINDOWS UP OR DOWN MONADTALL/MONADWIDE LAYOUT
    Key([mod, "shift"], "Up", lazy.layout.shuffle_up()),
    Key([mod, "shift"], "Down", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "Left", lazy.layout.swap_left()),
    Key([mod, "shift"], "Right", lazy.layout.swap_right()),

# TOGGLE FLOATING LAYOUT
    Key([mod, "shift"], "space", lazy.window.toggle_floating()),


        # ------------ Hardware Configs ------------
    # Volume
    Key([], "XF86AudioMute",
        lazy.spawn(home + "/.local/bin/statusbar/volumecontrol mute"),
        desc='Mute audio'
        ),
    Key([], "XF86AudioLowerVolume",
        lazy.spawn(home + "/.local/bin/statusbar/volumecontrol down"),
        desc='Volume down'
        ),
    Key([], "XF86AudioRaiseVolume",
        lazy.spawn(home + "/.local/bin/statusbar/volumecontrol up"),
        desc='Volume up'
        ),

    # Brightness
    Key([], "XF86MonBrightnessDown",
        lazy.spawn(home + "/.local/bin/statusbar/brightnesscontrol down"),
        desc='Brightness down'
        ),
    Key([], "XF86MonBrightnessUp",
        lazy.spawn(home + "/.local/bin/statusbar/brightnesscontrol up"),
        desc='Brightness up'
        ),

    # Screenshots
    # Save screen to clipboard
    Key([], "Print",
        lazy.spawn("/usr/bin/escrotum -C"),
        desc='Save screen to clipboard'
        ),
    # Save screen to screenshots folder
    Key([mod], "Print",
        lazy.spawn("/usr/bin/escrotum " + home + "/Pictures/Screenshots/screenshot_%d_%m_%Y_%H_%M_%S.png"),
        desc='Save screen to screenshots folder'
        ),
    # Capture region of screen to clipboard
    Key([mod, "shift"], "s",
        lazy.spawn("/usr/bin/escrotum -Cs"),
        desc='Capture region of screen to clipboard'
        ),


    ]

def window_to_previous_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i != 0:
        group = qtile.screens[i - 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.cmd_to_screen(i - 1)

def window_to_next_screen(qtile, switch_group=False, switch_screen=False):
    i = qtile.screens.index(qtile.current_screen)
    if i + 1 != len(qtile.screens):
        group = qtile.screens[i + 1].group.name
        qtile.current_window.togroup(group, switch_group=switch_group)
        if switch_screen == True:
            qtile.cmd_to_screen(i + 1)

keys.extend([
    # MOVE WINDOW TO NEXT SCREEN
    Key([mod,"shift"], "Right", lazy.function(window_to_next_screen, switch_screen=True)),
    Key([mod,"shift"], "Left", lazy.function(window_to_previous_screen, switch_screen=True)),
])

MYCOLORS = [
    '#073642',
    '#dc322f',
    '#00ff2a',
    '#b58900',
    '#268bd2',
    '#d33682',
    '#2aa198',
    '#eee8d5'
]

BLACK = MYCOLORS[0]
RED = MYCOLORS[1]
GREEN = MYCOLORS[2]
YELLOW = MYCOLORS[3]
BLUE = MYCOLORS[4]
MAGENTA = MYCOLORS[5]
CYAN = MYCOLORS[6]
WHITE = MYCOLORS[7]


workspaces = [
    {
        "name": " ₁",
        "key": "1",
        "matches": [Match(wm_class='firefox')],
        "layout": "monadtall"
            },
    {
        "name": " ₂",
        "key": "2",
        "matches": [
            Match(wm_class='kitty'),
            Match(wm_class='ranger')
         ],
        "layout": "monadtall"
            },
    {
        "name": " ₃",
        "key": "3",
        "matches": [
            Match(wm_class='vim')
            ],
        "layout": "monadtall"
            },
    {
        "name": " ₄",
        "key": "4",
        "matches": [
            Match(wm_class='telegram-desktop'),
            Match(wm_class='weechat')
            ],
        "layout": "monadtall"
            },
    {"name": " ₅", "key": "5", "matches": [Match(wm_class='gimp-2.10')], "layout": "monadtall"},
    {"name": "阮 ₆", "key": "6", "matches": [Match(wm_class='spotify')], "layout": "monadtall"},
    {"name": " ₇", "key": "7", "matches": [Match(wm_class='libreoffice')], "layout": "monadtall"},
    {"name": " ₈", "key": "8", "matches": [Match(wm_class='newsboat')], "layout": "monadtall"},
    {"name": " ₉", "key": "9", "matches": [Match(wm_class='neomutt')], "layout": "monadtall"},
]


groups = []

# FOR QWERTY KEYBOARDS
group_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",]

# FOR AZERTY KEYBOARDS
#group_names = ["ampersand", "eacute", "quotedbl", "apostrophe", "parenleft", "section", "egrave", "exclam", "ccedilla", "agrave",]

#group_labels = ["1 ", "2 ", "3 ", "4 ", "5 ", "6 ", "7 ", "8 ", "9 ", "0",]
group_labels = ["", "", "", "", "", "", "", "", "", "",]
#group_labels = ["Web", "Edit/chat", "Image", "Gimp", "Meld", "Video", "Vb", "Files", "Mail", "Music",]

group_layouts = ["monadtall", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall", "monadtall",]
#group_layouts = ["monadtall", "matrix", "monadtall", "bsp", "monadtall", "matrix", "monadtall", "bsp", "monadtall", "monadtall",]

for i in range(len(group_names)):
    groups.append(
        Group(
            name=group_names[i],
            layout=group_layouts[i].lower(),
            label=group_labels[i],
        ))

for i in groups:
    keys.extend([

#CHANGE WORKSPACES
        Key([mod], i.name, lazy.group[i.name].toscreen()),
        Key([mod], "Tab", lazy.screen.next_group()),
        Key([mod, "shift" ], "Tab", lazy.screen.prev_group()),
        Key(["mod1"], "Tab", lazy.screen.next_group()),
        Key(["mod1", "shift"], "Tab", lazy.screen.prev_group()),

# MOVE WINDOW TO SELECTED WORKSPACE 1-10 AND STAY ON WORKSPACE
        #Key([mod, "shift"], i.name, lazy.window.togroup(i.name)),
# MOVE WINDOW TO SELECTED WORKSPACE 1-10 AND FOLLOW MOVED WINDOW TO WORKSPACE
        Key([mod, "shift"], i.name, lazy.window.togroup(i.name) , lazy.group[i.name].toscreen()),
    ])


### COLORSCHEME ###
# Colors are defined in a separate 'colors.py' file.
# There 10 colorschemes available to choose from:
#
# colors = colors.DoomOne
# colors = colors.Dracula
# colors = colors.GruvboxDark
# colors = colors.MonokaiPro
# colors = colors.Nord
# colors = colors.OceanicNext
# colors = colors.Palenight
# colors = colors.SolarizedDark
# colors = colors.SolarizedLight
# colors = colors.TomorrowNight
#
# It is best not manually change the colorscheme; instead run 'dtos-colorscheme'
# which is set to 'MOD + p c'

colors = colors.DoomOne

### LAYOUTS ###
# Some settings that I use on almost every layout, which saves us
# from having to type these out for each individual layout.
layout_theme = {"border_width": 2,
                "margin": 8,
                "border_focus": colors[8],
                "border_normal": colors[0]
                }

layouts = [
    #layout.Bsp(**layout_theme),
    #layout.Floating(**layout_theme)
    #layout.RatioTile(**layout_theme),
    #layout.Tile(shift_windows=True, **layout_theme),
    #layout.VerticalTile(**layout_theme),
    #layout.Matrix(**layout_theme),
    layout.MonadTall(**layout_theme),
    #layout.MonadWide(**layout_theme),
    layout.Max(
         border_width = 0,
         margin = 0,
         ),
    layout.Stack(**layout_theme, num_stacks=2),
    layout.Columns(**layout_theme),
    layout.TreeTab(
         font = "Ubuntu Bold",
         fontsize = 11,
         border_width = 0,
         bg_color = colors[0],
         active_bg = colors[8],
         active_fg = colors[2],
         inactive_bg = colors[1],
         inactive_fg = colors[0],
         padding_left = 8,
         padding_x = 8,
         padding_y = 6,
         sections = ["ONE", "TWO", "THREE"],
         section_fontsize = 10,
         section_fg = colors[7],
         section_top = 15,
         section_bottom = 15,
         level_shift = 8,
         vspace = 3,
         panel_width = 240
         ),
    layout.Zoomy(**layout_theme),
]

# Some settings that I use on almost every widget, which saves us
# from having to type these out for each individual widget.
widget_defaults = dict(
    font="Ubuntu Bold",
    fontsize = 12,
    padding = 0,
    background=colors[0]
)

extension_defaults = widget_defaults.copy()


def init_widgets_list():
    widgets_list = [
        widget.Sep(padding=3, linewidth=0, background="#2f343f"),
        widget.Image(
            filename='~/.config/qtile/eos-c.png',
            margin=3,
            background="#2f343f",
            mouse_callbacks={'Button1': lambda: qtile.cmd_spawn("rofi -show combi")}
        ),
        # widget.Image(
        #     filename = "~/.config/qtile/icons/logo.png",
        #     scale = "False",
        #     mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(myTerm)},
        # ),
        widget.Prompt(
            font = "Ubuntu Mono",
            fontsize=14,
            foreground = colors[1]
        ),
        widget.GroupBox(
            fontsize = 11,
            margin_y = 3,
            margin_x = 4,
            padding_y = 2,
            padding_x = 3,
            borderwidth = 3,
            active = colors[8],
            inactive = colors[1],
            rounded = False,
            highlight_color = colors[2],
            highlight_method = "line",
            this_current_screen_border = colors[7],
            this_screen_border = colors [4],
            other_current_screen_border = colors[7],
            other_screen_border = colors[4],
        ),
        widget.TextBox(
            text = '|',
            font = "Ubuntu Mono",
            foreground = colors[1],
            padding = 2,
            fontsize = 14
        ),
        widget.CurrentLayoutIcon(
            # custom_icon_paths = [os.path.expanduser("~/.config/qtile/icons")],
            foreground = colors[1],
            padding = 0,
            scale = 0.7
        ),
        widget.CurrentLayout(
            foreground = colors[1],
            padding = 5
        ),
        widget.TextBox(
            text = '|',
            font = "Ubuntu Mono",
            foreground = colors[1],
            padding = 2,
            fontsize = 14
        ),
        widget.WindowName(
            foreground = colors[6],
            max_chars = 40
        ),
        widget.Spacer(),
        widget.GenPollText(
            func=custom_date, update_interval=1,
            **widget_defaults,
            mouse_callbacks={
                'Button1': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/calendar.sh show"), shell=True),
                'Button3': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/calendar.sh edit"), shell=True)
                }
        ),
        widget.Spacer(),
        widget.GenPollText(
            update_interval = 300,
            func = lambda: subprocess.check_output("printf $(uname -r)", shell=True, text=True),
            foreground = colors[3],
            fmt = '❤  {}',
            decorations=[
                BorderDecoration(
                    colour = colors[3],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.CPU(
            format = '▓  Cpu: {load_percent}%',
            foreground = colors[4],
            decorations=[
                BorderDecoration(
                    colour = colors[4],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.Memory(
            foreground = colors[8],
            mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(myTerm + ' -e htop')},
            format = '{MemUsed: .0f}{mm}',
            fmt = '🖥  Mem: {} used',
            decorations=[
                BorderDecoration(
                    colour = colors[8],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.DF(
            update_interval = 60,
            foreground = colors[5],
            mouse_callbacks = {'Button1': lambda: qtile.cmd_spawn(myTerm + ' -e df')},
            partition = '/',
            #format = '[{p}] {uf}{m} ({r:.0f}%)',
            format = '{uf}{m} free',
            fmt = '🖴  Disk: {}',
            visible_on_warn = False,
            decorations=[
                BorderDecoration(
                    colour = colors[5],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.Volume(
            foreground = colors[7],
            fmt = '🕫  Vol: {}',
            decorations=[
                BorderDecoration(
                    colour = colors[7],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.KeyboardLayout(
                 foreground = colors[4],
                 fmt = '⌨  Kbd: {}',
                 decorations=[
                     BorderDecoration(
                         colour = colors[4],
                         border_width = [0, 0, 2, 0],
                     )
                 ],
                 ),
        widget.Spacer(length = 8),
        widget.Clock(
            foreground = colors[8],
            format = "⏱  %a, %b %d - %H:%M",
            decorations=[
                BorderDecoration(
                    colour = colors[8],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        widget.ThermalSensor(
                foreground = colors[5],
                foreground_alert = colors[6],
                metric = True,
                padding = 3,
                threshold = 80,
                decorations=[
                BorderDecoration(
                    colour = colors[3],
                    border_width = [0, 0, 2, 0],
                )
            ],
        ),
        widget.Spacer(length = 8),
        arcobattery.BatteryIcon(
                padding=0,
                scale=0.7,
                y_poss=2,
                theme_path=home + "/.config/qtile/icons/battery_icons_horiz",
                update_interval = 5,
        ),
        widget.Spacer(length = 8),
        widget.Systray(padding = 3),
        widget.GenPollText(
            update_interval=1,
            **widget_defaults,
            func=lambda: subprocess.check_output(os.path.expanduser("~/.local/bin/statusbar/brightnesscontrol")).decode(),
            mouse_callbacks={
                'Button1': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/brightnesscontrol down"), shell=True),
                'Button3': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/brightnesscontrol up"), shell=True)
                }
        ),
        widget.Spacer(length=5),
        widget.GenPollText(update_interval=1, **widget_defaults, func=lambda: subprocess.check_output(os.path.expanduser("~/.local/bin/statusbar/volumecontrol")).decode(), mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/volumecontrol down"), shell=True), 'Button2': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/volumecontrol mute"), shell=True), 'Button3': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/volumecontrol up"), shell=True)}),
        widget.Spacer(length=5),
        widget.GenPollText(update_interval=1, **widget_defaults, func=lambda: subprocess.check_output(os.path.expanduser("~/.local/bin/statusbar/battery.py")).decode(), mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/battery.py --c left-click"), shell=True)}),
        widget.Spacer(length=5),
        widget.GenPollText(update_interval=1, **widget_defaults, func=lambda: subprocess.check_output(os.path.expanduser("~/.local/bin/statusbar/network.sh")).decode(), mouse_callbacks={'Button1': lambda: qtile.cmd_spawn(os.path.expanduser("~/.local/bin/statusbar/network.sh ShowInfo"), shell=True), 'Button3': lambda: qtile.cmd_spawn(terminal + ' -e nmtui', shell=True)}),
        widget.Spacer(length=10),

        widget.Spacer(length = 8),
        widget.TextBox(
            text='',
            mouse_callbacks= {
                'Button1':
                lambda: qtile.cmd_spawn(os.path.expanduser('~/.config/rofi/powermenu.sh'))
            },
            padding = 10,
            foreground='#e39378'
        ),

        ]
    return widgets_list

# Monitor 1 will display ALL widgets in widgets_list. It is important that this
# is the only monitor that displays all widgets because the systray widget will
# crash if you try to run multiple instances of it.
def init_widgets_screen1():
    widgets_screen1 = init_widgets_list()
    return widgets_screen1 

# All other monitors' bars will display everything but widgets 22 (systray) and 23 (spacer).
def init_widgets_screen2():
    widgets_screen2 = init_widgets_list()
    del widgets_screen2[22:24]
    return widgets_screen2

# For adding transparency to your bar, add (background="#00000000") to the "Screen" line(s)
# For ex: Screen(top=bar.Bar(widgets=init_widgets_screen2(), background="#00000000", size=24)),

def init_screens():
    return [Screen(top=bar.Bar(widgets=init_widgets_screen1(), size=26)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26)),
            Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26))]

if __name__ in ["config", "__main__"]:
    screens = init_screens()
    widgets_list = init_widgets_list()
    widgets_screen1 = init_widgets_screen1()
    widgets_screen2 = init_widgets_screen2()

# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    border_focus=colors[8],
    border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),   # gitk
        Match(wm_class="makebranch"),     # gitk
        Match(wm_class="maketag"),        # gitk
        Match(wm_class="ssh-askpass"),    # ssh-askpass
        Match(title="branchdialog"),      # gitk
        Match(title='Confirmation'),      # tastyworks exit box
        Match(title='Qalculate!'),        # qalculate-gtk
        Match(wm_class='kdenlive'),       # kdenlive
        Match(wm_class='Arandr'),
        Match(wm_class='Barrier'),
        Match(wm_class='pinentry-gtk-2'), # GPG key password entry
        Match(title="pinentry"),          # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser('~')
    subprocess.call([home + '/.config/qtile/scripts/autostart.sh'])

@hook.subscribe.startup
def start_always():
    # Set the cursor to something sane in X
    subprocess.Popen(['xsetroot', '-cursor_name', 'left_ptr'])

@hook.subscribe.client_new
def set_floating(window):
    if (window.window.get_wm_transient_for()
            or window.window.get_wm_type() in floating_types):
        window.floating = True


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
