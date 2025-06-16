# Copyright (C) 2025 tfuxu, Alexander Vanhee
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Callable
from gi.repository import Gtk, Adw
from gradia.ui.drawing_tools_group import DrawingToolsGroup
from gradia.ui.background_selector import BackgroundSelector
from gradia.constants import rootdir  # pyright: ignore
from gradia.backend.settings import Settings

@Gtk.Template(resource_path=f"{rootdir}/ui/image_sidebar.ui")
class ImageSidebar(Adw.Bin):
    __gtype_name__ = "GradiaImageSidebar"

    # `annotation_tools_group` template children
    annotation_tools_group: DrawingToolsGroup = Gtk.Template.Child()

    # `background_selector_group` template children
    background_selector_group: Adw.PreferencesGroup = Gtk.Template.Child()

    # `image_options_group` template children
    image_options_group = Gtk.Template.Child()
    disable_button: Gtk.Switch = Gtk.Template.Child()  # Changed to Switch
    padding_row: Adw.SpinRow = Gtk.Template.Child()
    padding_adjustment: Gtk.Adjustment = Gtk.Template.Child()
    corner_radius_row: Adw.SpinRow = Gtk.Template.Child()
    corner_radius_adjustment: Gtk.Adjustment = Gtk.Template.Child()
    aspect_ratio_entry: Gtk.Entry = Gtk.Template.Child()
    shadow_strength_scale: Gtk.Scale = Gtk.Template.Child()

    # `file_info_group` template children
    filename_row: Adw.ActionRow = Gtk.Template.Child()
    location_row: Adw.ActionRow = Gtk.Template.Child()
    processed_size_row: Adw.ActionRow = Gtk.Template.Child()

    # Default values for reset functionality
    DEFAULT_PADDING = 0
    DEFAULT_CORNER_RADIUS = 0
    DEFAULT_ASPECT_RATIO = ""
    DEFAULT_SHADOW_STRENGTH = 0

    def __init__(
        self,
        background_selector_widget: BackgroundSelector,
        on_padding_changed: Callable[[int], None],
        on_corner_radius_changed: Callable[[int], None],
        on_aspect_ratio_changed: Callable[[str], None],
        on_shadow_strength_changed: Callable[[int], None],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self._on_padding_changed = on_padding_changed
        self._on_corner_radius_changed = on_corner_radius_changed
        self._on_aspect_ratio_changed = on_aspect_ratio_changed
        self._on_shadow_strength_changed = on_shadow_strength_changed

        self.image_options_group_content = self.image_options_group.get_first_child().get_first_child().get_next_sibling()

        self._actual_padding = 5
        self._actual_corner_radius = 2
        self._actual_aspect_ratio = ""
        self._actual_shadow_strength = 5

        self.background_selector_group.add(background_selector_widget)
        self._setup_image_options_group()

        self.disable_button.connect("toggled", self._on_disable_switch_clicked)
        Settings().bind_switch(self.disable_button, "image-options-lock")
        self._on_disable_switch_clicked(self.disable_button)

    """
    Setup Methods
    """
    def _setup_image_options_group(self) -> None:
        self.padding_adjustment.set_value(5)
        self.corner_radius_adjustment.set_value(2)
        self.shadow_strength_scale.set_value(5)

        self.padding_row.connect("output", self._on_padding_widget_changed)
        self.corner_radius_row.connect("output", self._on_corner_radius_widget_changed)
        self.aspect_ratio_entry.connect("changed", self._on_aspect_ratio_widget_changed)
        self.shadow_strength_scale.connect("value-changed", self._on_shadow_strength_widget_changed)

        self.padding_adjustment.connect("value-changed", self._on_actual_padding_changed)
        self.corner_radius_adjustment.connect("value-changed", self._on_actual_corner_radius_changed)
        self.aspect_ratio_entry.connect("changed", self._on_actual_aspect_ratio_changed)
        self.shadow_strength_scale.connect("value-changed", self._on_actual_shadow_strength_changed)

    """
    Callbacks for tracking actual values
    """
    def _on_actual_padding_changed(self, adjustment: Gtk.Adjustment) -> None:
        if not self.disable_button.get_active():
            self._actual_padding = int(adjustment.get_value())

    def _on_actual_corner_radius_changed(self, adjustment: Gtk.Adjustment) -> None:
        if not self.disable_button.get_active():
            self._actual_corner_radius = int(adjustment.get_value())

    def _on_actual_aspect_ratio_changed(self, entry: Gtk.Entry) -> None:
        if not self.disable_button.get_active():
            self._actual_aspect_ratio = entry.get_text()

    def _on_actual_shadow_strength_changed(self, scale: Gtk.Scale) -> None:
        if not self.disable_button.get_active():
            self._actual_shadow_strength = int(scale.get_value())

    def _on_padding_widget_changed(self, spin_row: Adw.SpinRow) -> None:
        if self.disable_button.get_active():
            self._on_padding_changed(self.DEFAULT_PADDING)
        else:
            self._on_padding_changed(int(spin_row.get_value()))

    def _on_corner_radius_widget_changed(self, spin_row: Adw.SpinRow) -> None:
        if self.disable_button.get_active():
            self._on_corner_radius_changed(self.DEFAULT_CORNER_RADIUS)
        else:
            self._on_corner_radius_changed(int(spin_row.get_value()))

    def _on_aspect_ratio_widget_changed(self, entry: Gtk.Entry) -> None:
        if self.disable_button.get_active():
            self._on_aspect_ratio_changed(self.DEFAULT_ASPECT_RATIO)
        else:
            self._on_aspect_ratio_changed(entry.get_text())

    def _on_shadow_strength_widget_changed(self, scale: Gtk.Scale) -> None:
        if self.disable_button.get_active():
            self._on_shadow_strength_changed(self.DEFAULT_SHADOW_STRENGTH)
        else:
            self._on_shadow_strength_changed(int(scale.get_value()))

    """
    Callbacks
    """
    def _on_disable_switch_clicked(self, switch: Gtk.Switch) -> None:
        state = switch.get_active()
        self.image_options_group_content.set_sensitive(not state)
        if state:
            # Default values
            self._on_padding_changed(self.DEFAULT_PADDING)
            self._on_corner_radius_changed(self.DEFAULT_CORNER_RADIUS)
            self._on_aspect_ratio_changed(self.DEFAULT_ASPECT_RATIO)
            self._on_shadow_strength_changed(self.DEFAULT_SHADOW_STRENGTH)
        else:
            # actual values
            self._on_padding_changed(self._actual_padding)
            self._on_corner_radius_changed(self._actual_corner_radius)
            self._on_aspect_ratio_changed(self._actual_aspect_ratio)
            self._on_shadow_strength_changed(self._actual_shadow_strength)

    """
    Internal Methods
    """
