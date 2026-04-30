"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import pyray as rl
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.text_measure import measure_text_cached
from openpilot.system.ui.widgets import Widget


def _get_usage_color(percent: int) -> rl.Color:
  if percent >= 90:
    return rl.RED
  if percent >= 80:
    return rl.Color(255, 188, 0, 255)
  return rl.WHITE


class SystemUsageOverlay(Widget):
  RIGHT_PANEL_WIDTH = 60
  BOTTOM_STRIP_HEIGHT = 60
  FONT_SIZE_SMALL = 32
  FONT_SIZE_LARGE = 38

  def __init__(self):
    super().__init__()
    self._font = gui_app.font(FontWeight.BOLD)
    self._mode = -1

  def _update_state(self) -> None:
    self._mode = int(ui_state.developer_ui)

  def _render(self, rect: rl.Rectangle) -> None:
    if self._mode <= 0:
      return

    mem_pct = int(ui_state.sm['deviceState'].memoryUsagePercent)
    cpu_usage = ui_state.sm['deviceState'].cpuUsagePercent
    cpu_pct = int(round(sum(cpu_usage) / len(cpu_usage))) if len(cpu_usage) else 0

    show_bottom = self._mode in (1, 3)
    show_right = self._mode in (2, 3)

    if show_right:
      self._draw_right_panel(rect, mem_pct, cpu_pct)
    if show_bottom:
      self._draw_bottom_strip(rect, mem_pct, cpu_pct)

  def _draw_right_panel(self, rect: rl.Rectangle, mem_pct: int, cpu_pct: int) -> None:
    x = int(rect.x + rect.width - self.RIGHT_PANEL_WIDTH)
    y = int(rect.y + rect.height - 200)

    rl.draw_rectangle(x, y, self.RIGHT_PANEL_WIDTH, 112, rl.Color(0, 0, 0, 120))

    mem_text = f"{mem_pct}%"
    mem_color = _get_usage_color(mem_pct)
    mem_w = measure_text_cached(self._font, mem_text, self.FONT_SIZE_SMALL, 0).x
    rl.draw_text_ex(self._font, "MEM", rl.Vector2(x + (self.RIGHT_PANEL_WIDTH - measure_text_cached(self._font, "MEM", self.FONT_SIZE_SMALL, 0).x) / 2, y + 4), self.FONT_SIZE_SMALL, 0, rl.WHITE)
    rl.draw_text_ex(self._font, mem_text, rl.Vector2(x + (self.RIGHT_PANEL_WIDTH - mem_w) / 2, y + 28), self.FONT_SIZE_SMALL, 0, mem_color)

    cpu_text = f"{cpu_pct}%"
    cpu_color = _get_usage_color(cpu_pct)
    cpu_w = measure_text_cached(self._font, cpu_text, self.FONT_SIZE_SMALL, 0).x
    rl.draw_text_ex(self._font, "CPU", rl.Vector2(x + (self.RIGHT_PANEL_WIDTH - measure_text_cached(self._font, "CPU", self.FONT_SIZE_SMALL, 0).x) / 2, y + 56), self.FONT_SIZE_SMALL, 0, rl.WHITE)
    rl.draw_text_ex(self._font, cpu_text, rl.Vector2(x + (self.RIGHT_PANEL_WIDTH - cpu_w) / 2, y + 78), self.FONT_SIZE_SMALL, 0, cpu_color)

  def _draw_bottom_strip(self, rect: rl.Rectangle, mem_pct: int, cpu_pct: int) -> None:
    bar_h = self.BOTTOM_STRIP_HEIGHT
    y = int(rect.y + rect.height - bar_h)

    rl.draw_rectangle(int(rect.x), y, int(rect.width), bar_h, rl.Color(0, 0, 0, 100))

    mem_label = "MEM "
    mem_val = f"{mem_pct}%"
    cpu_label = "CPU "
    cpu_val = f"{cpu_pct}%"

    mem_label_w = measure_text_cached(self._font, mem_label, self.FONT_SIZE_LARGE, 0).x
    mem_val_w = measure_text_cached(self._font, mem_val, self.FONT_SIZE_LARGE, 0).x
    cpu_label_w = measure_text_cached(self._font, cpu_label, self.FONT_SIZE_LARGE, 0).x
    cpu_val_w = measure_text_cached(self._font, cpu_val, self.FONT_SIZE_LARGE, 0).x

    total_w = mem_label_w + mem_val_w + cpu_label_w + cpu_val_w
    gap = 16
    total_w += gap
    start_x = int(rect.x + (rect.width - total_w) / 2)
    center_y = y + bar_h // 2

    rl.draw_text_ex(self._font, mem_label, rl.Vector2(start_x, center_y - self.FONT_SIZE_LARGE // 2), self.FONT_SIZE_LARGE, 0, rl.WHITE)
    rl.draw_text_ex(self._font, mem_val, rl.Vector2(start_x + mem_label_w, center_y - self.FONT_SIZE_LARGE // 2), self.FONT_SIZE_LARGE, 0, _get_usage_color(mem_pct))
    rl.draw_text_ex(self._font, cpu_label, rl.Vector2(start_x + mem_label_w + mem_val_w + gap, center_y - self.FONT_SIZE_LARGE // 2), self.FONT_SIZE_LARGE, 0, rl.WHITE)
    rl.draw_text_ex(self._font, cpu_val, rl.Vector2(start_x + mem_label_w + mem_val_w + gap + cpu_label_w, center_y - self.FONT_SIZE_LARGE // 2), self.FONT_SIZE_LARGE, 0, _get_usage_color(cpu_pct))
