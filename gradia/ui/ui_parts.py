# Copyright (C) 2025 Alexander Vanhee, tfuxu
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
import tempfile
from typing import Optional
from gi.repository import Gtk, Gdk, Adw

class AboutDialog:
    def __init__(
        self,
        version: str,
        primary_color: str | None = None,
        secondary_color: str | None = None,
        icon_path: str = "/usr/share/icons/hicolor/scalable/apps/be.alexandervanhee.gradia.svg"
    ):
        self.version = version
        self.primary_color = primary_color or "#57e389"
        self.secondary_color = secondary_color or "#3584e4"
        self.icon_path = icon_path
        self.custom_icon_name = "gradia-custom-icon"
        self._temp_icon_dir = None
        self.dialog = None
        self.icon_theme =  Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        self._register_custom_icon()



    def _load_and_modify_svg(self) -> str:
        icon_info = self.icon_theme.lookup_icon("be.alexandervanhee.gradia", None, 128, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.NONE)
        if not icon_info:
            return ""

        with open(icon_info.get_file().get_path(), 'r') as f:
            svg_content = f.read()

        def adjust_color_brightness(hex_color: str, factor: float) -> str:
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
            clamp = lambda x: max(0, min(255, x))
            if factor >= 0:
                r, g, b = (clamp(int(c + (255 - c) * factor)) for c in (r, g, b))
            else:
                r, g, b = (clamp(int(c * (1 + factor))) for c in (r, g, b))
            return f"#{r:02x}{g:02x}{b:02x}"

        def hex_to_luminance(hex_color: str) -> float:
            hex_color = hex_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        if hex_to_luminance(self.secondary_color) < hex_to_luminance(self.primary_color):
            self.primary_color, self.secondary_color = self.secondary_color, self.primary_color

        light_primary = adjust_color_brightness(self.primary_color, 0.3)
        dark_primary = adjust_color_brightness(self.primary_color, -0.1)
        gradient_a_colors = [self.primary_color, light_primary, dark_primary, dark_primary, light_primary, self.primary_color]
        gradient_b_colors = [self.secondary_color, self.primary_color]

        svg_content = re.sub(r'(<linearGradient id="a"[^>]*>)(.*?)(</linearGradient>)',
                             lambda m: m.group(1) + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip(['0','0.05','0.1','0.9','0.95','1'], gradient_a_colors)) + m.group(3),
                             svg_content, flags=re.DOTALL)

        svg_content = re.sub(r'(<linearGradient id="b"[^>]*>)(.*?)(</linearGradient>)',
                             lambda m: m.group(1) + ''.join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in zip(['0','1'], gradient_b_colors)) + m.group(3),
                             svg_content, flags=re.DOTALL)

        return svg_content


    def _register_custom_icon(self):
        modified_svg = self._load_and_modify_svg()

        temp_dir = tempfile.mkdtemp()
        hicolor_dir = os.path.join(temp_dir, "hicolor")
        scalable_dir = os.path.join(hicolor_dir, "scalable", "apps")
        os.makedirs(scalable_dir, exist_ok=True)

        index_theme = os.path.join(hicolor_dir, "index.theme")
        with open(index_theme, 'w') as f:
            f.write("""[Icon Theme]
                    Name=hicolor
                    Comment=Hicolor icon theme
                    Hidden=true
                    Directories=scalable/apps

                    [scalable/apps]
                    Size=48
                    Context=Applications
                    Type=Scalable
                    """)

        icon_file = os.path.join(scalable_dir, f"{self.custom_icon_name}.svg")
        with open(icon_file, 'w') as f:
            f.write(modified_svg)

        self.icon_theme.add_search_path(temp_dir)
        self._temp_icon_dir = temp_dir

    def create(self) -> Adw.AboutDialog:
        self.dialog = Adw.AboutDialog(
            application_icon=self.custom_icon_name,
            application_name="Gradia",
            version=self.version,
            comments=_("Make your images ready for all"),
            website="https://github.com/AlexanderVanhee/Gradia",
            issue_url="https://github.com/AlexanderVanhee/Gradia/issues",
            developer_name="Alexander Vanhee",
            developers=[
                "Alexander Vanhee https://github.com/AlexanderVanhee",
                "tfuxu https://github.com/tfuxu",
            ],
            designers=[
                "drpetrikov https://github.com/drpetrikov"
            ],
            # Translators: This is a place to put your credits (formats: "Name https://example.com" or "Name <email@example.com>", no quotes) and is not meant to be translated literally.
            translator_credits=_("translator-credits"),
            copyright="Copyright © 2025 Alexander Vanhee",
            license_type=Gtk.License.GPL_3_0
        )

        self.dialog.add_acknowledgement_section(
            _("Code and Design Borrowed from"),
            [
                "Switcheroo https://apps.gnome.org/en-GB/Converter/",
                "Halftone https://github.com/tfuxu/Halftone",
                "Gradience https://github.com/GradienceTeam/Gradience",
                "Emblem https://apps.gnome.org/en-GB/Emblem/",
                "Builder https://apps.gnome.org/en-GB/Builder/",
                None
            ]
        )

        self.dialog.add_acknowledgement_section(
            _("Image Sources"),
            [
                "GNOME backgrounds https://gitlab.gnome.org/GNOME/gnome-backgrounds",
                "Fruit Basket https://unsplash.com/photos/background-pattern-oWr5S1bO2ak",
                None
            ]
        )

        return self.dialog

    def show(self, parent: Optional[Gtk.Window] = None):
        if not self.dialog:
            self.create()
        self.dialog.present(parent)

class ShortcutsDialog:
    def __init__(self, parent: Optional[Gtk.Window] = None):
        self.parent = parent
        self.dialog = None
        self.shortcut_groups = [
            {
                "title": _("File Actions"),
                "shortcuts": [
                    (_("Open File"), "<Ctrl>O"),
                    (_("Save to File"), "<Ctrl>S"),
                    (_("Copy Image to Clipboard"), "<Ctrl>C"),
                    (_("Paste From Clipboard"), "<Ctrl>V"),
                    (_("Share Image"), "<Ctrl>M"),
                ]
            },
            {
                "title": _("Annotations"),
                "shortcuts": [
                    (_("Undo"), "<Ctrl>Z"),
                    (_("Redo"), "<Ctrl><Shift>Z"),
                    (_("Erase Selected"), "Delete")
                ]
            },
            {
                "title": _("Cropping"),
                "shortcuts": [
                    (_("Toggle Crop Mode"), "<Ctrl>R"),
                    (_("Reset Crop"), "<Ctrl><Shift>R")
                ]
            },
            {
                "title": _("General"),
                "shortcuts": [
                    (_("Keyboard Shortcuts"), "<Ctrl>question"),
                    (_("Preferences"), "<Ctrl>comma"),
                    (_("Open Source Snippets"), "<Ctrl>P"),
                ]
            }
        ]

    def create(self) -> Gtk.ShortcutsWindow:
        self.dialog = Gtk.ShortcutsWindow(transient_for=self.parent, modal=True)
        section = Gtk.ShortcutsSection()

        for group_data in self.shortcut_groups:
            group = Gtk.ShortcutsGroup(title=group_data["title"], visible=True)
            for title, accel in group_data["shortcuts"]:
                group.add_shortcut(Gtk.ShortcutsShortcut(
                    title=title,
                    accelerator=accel
                ))
            section.add_group(group)

        self.dialog.add_section(section)
        self.dialog.connect("close-request", lambda dialog: dialog.destroy())
        return self.dialog

    def show(self):
        if not self.dialog:
            self.create()
        self.dialog.present()

    def set_parent(self, parent: Gtk.Window):
        self.parent = parent
        if self.dialog:
            self.dialog.set_transient_for(parent)

