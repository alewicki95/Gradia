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

@Gtk.Template(resource_path=f"{rootdir}/ui/image_sidebar.ui")
class ImageSidebar(Adw.Bin):
    __gtype_name__ = "GradiaImageSidebar"

    # `annotation_tools_group` template children
    annotation_tools_group: DrawingToolsGroup = Gtk.Template.Child()

    # `background_selector_group` template children
    background_selector_group: Adw.PreferencesGroup = Gtk.Template.Child()

    # `image_options_group` template children
    disable_button: Gtk.Button = Gtk.Template.Child()
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
        on_padding_changed: Callable[[Adw.SpinRow], None],
        on_corner_radius_changed: Callable[[Adw.SpinRow], None],
        on_aspect_ratio_changed: Callable[[Gtk.Entry], None],
        on_shadow_strength_changed: Callable[[Gtk.Scale], None],
        **kwargs
    ) -> None:
        super().__init__(**kwargs)

        # Store callbacks for reset functionality
        self._on_padding_changed = on_padding_changed
        self._on_corner_radius_changed = on_corner_radius_changed
        self._on_aspect_ratio_changed = on_aspect_ratio_changed
        self._on_shadow_strength_changed = on_shadow_strength_changed

        self.background_selector_group.add(background_selector_widget)
        self._setup_image_options_group(
            on_padding_changed,
            on_corner_radius_changed,
            on_aspect_ratio_changed,
            on_shadow_strength_changed
        )

        self.disable_button.connect("clicked", self._on_disable_button_clicked)

    """
    Setup Methods
    """
    def _setup_image_options_group(
        self,
        on_padding_changed: Callable[[Adw.SpinRow], None],
        on_corner_radius_changed: Callable[[Adw.SpinRow], None],
        on_aspect_ratio_changed: Callable[[Gtk.Entry], None],
        on_shadow_strength_changed: Callable[[Gtk.Scale], None],
    ) -> None:
        self.padding_adjustment.set_value(5)
        self.corner_radius_adjustment.set_value(2)

        self.padding_row.connect("output", on_padding_changed)
        self.corner_radius_row.connect("output", on_corner_radius_changed)
        self.aspect_ratio_entry.connect("changed", on_aspect_ratio_changed)
        self.shadow_strength_scale.connect("value-changed", on_shadow_strength_changed)

    """
    Callbacks
    """
    def _on_disable_button_clicked(self, button: Gtk.Button) -> None:
        self.padding_row.handler_block_by_func(self._on_padding_changed)
        self.corner_radius_row.handler_block_by_func(self._on_corner_radius_changed)
        self.aspect_ratio_entry.handler_block_by_func(self._on_aspect_ratio_changed)
        self.shadow_strength_scale.handler_block_by_func(self._on_shadow_strength_changed)

        try:
            self.padding_adjustment.set_value(self.DEFAULT_PADDING)
            self.corner_radius_adjustment.set_value(self.DEFAULT_CORNER_RADIUS)
            self.aspect_ratio_entry.set_text(self.DEFAULT_ASPECT_RATIO)
            self.shadow_strength_scale.set_value(self.DEFAULT_SHADOW_STRENGTH)
        finally:
            self.padding_row.handler_unblock_by_func(self._on_padding_changed)
            self.corner_radius_row.handler_unblock_by_func(self._on_corner_radius_changed)
            self.aspect_ratio_entry.handler_unblock_by_func(self._on_aspect_ratio_changed)
            self.shadow_strength_scale.handler_unblock_by_func(self._on_shadow_strength_changed)

        self._on_padding_changed(self.padding_row)
        self._on_corner_radius_changed(self.corner_radius_row)
        self._on_aspect_ratio_changed(self.aspect_ratio_entry)
        self._on_shadow_strength_changed(self.shadow_strength_scale)

    def reset_to_defaults(self) -> None:
        self._on_disable_button_clicked(self.disable_button)

    """
    Internal Methods
    """
