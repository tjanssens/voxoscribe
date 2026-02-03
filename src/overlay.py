"""Visual feedback overlay for VoxoScribe."""

import threading
import tkinter as tk
from typing import Optional


class Overlay:
    """Shows visual feedback during recording and processing."""

    def __init__(self):
        self._root: Optional[tk.Tk] = None
        self._label: Optional[tk.Label] = None
        self._canvas: Optional[tk.Canvas] = None
        self._dot: Optional[int] = None
        self._visible = False
        self._thread: Optional[threading.Thread] = None
        self._pulse_after_id: Optional[str] = None
        self._status = "idle"
        self._lock = threading.Lock()
        self._ready = threading.Event()

    def start(self) -> None:
        """Start the overlay window in a separate thread."""
        if self._thread is not None and self._thread.is_alive():
            return

        self._ready.clear()
        self._thread = threading.Thread(target=self._run_overlay, daemon=True)
        self._thread.start()
        self._ready.wait(timeout=2.0)

    def _run_overlay(self) -> None:
        """Run the overlay window (must run in its own thread)."""
        self._root = tk.Tk()
        self._root.withdraw()
        self._root.overrideredirect(True)
        self._root.attributes('-topmost', True)
        self._root.attributes('-alpha', 0.9)

        if hasattr(self._root, 'attributes'):
            try:
                self._root.attributes('-transparentcolor', '')
            except tk.TclError:
                pass

        self._root.configure(bg='#2d2d2d')

        frame = tk.Frame(self._root, bg='#2d2d2d', padx=15, pady=10)
        frame.pack()

        self._canvas = tk.Canvas(frame, width=16, height=16, bg='#2d2d2d',
                                  highlightthickness=0)
        self._canvas.pack(side=tk.LEFT, padx=(0, 8))
        self._dot = self._canvas.create_oval(2, 2, 14, 14, fill='#666666', outline='')

        self._label = tk.Label(frame, text="Ready", fg='white', bg='#2d2d2d',
                                font=('Segoe UI', 10))
        self._label.pack(side=tk.LEFT)

        self._root.update_idletasks()
        width = self._root.winfo_width()
        height = self._root.winfo_height()

        screen_width = self._root.winfo_screenwidth()
        x = screen_width - width - 20
        y = 20

        self._root.geometry(f'+{x}+{y}')

        self._ready.set()
        self._root.mainloop()

    def show_recording(self) -> None:
        """Show recording status."""
        with self._lock:
            self._status = "recording"

        if self._root:
            self._root.after(0, self._update_recording)

    def _update_recording(self) -> None:
        """Update UI for recording state."""
        if self._label:
            self._label.config(text="Listening...")
        if self._canvas and self._dot:
            self._canvas.itemconfig(self._dot, fill='#ff4444')
        self._show()
        self._start_pulse()

    def show_processing(self) -> None:
        """Show processing status."""
        with self._lock:
            self._status = "processing"

        if self._root:
            self._root.after(0, self._update_processing)

    def _update_processing(self) -> None:
        """Update UI for processing state."""
        self._stop_pulse()
        if self._label:
            self._label.config(text="Processing...")
        if self._canvas and self._dot:
            self._canvas.itemconfig(self._dot, fill='#ffaa00')
        self._show()

    def hide(self) -> None:
        """Hide the overlay."""
        with self._lock:
            self._status = "idle"

        if self._root:
            self._root.after(0, self._do_hide)

    def _do_hide(self) -> None:
        """Actually hide the overlay."""
        self._stop_pulse()
        if self._root:
            self._root.withdraw()
            self._visible = False

    def _show(self) -> None:
        """Show the overlay."""
        if self._root and not self._visible:
            self._root.deiconify()
            self._visible = True

    def _start_pulse(self) -> None:
        """Start pulsing animation."""
        self._pulse(True)

    def _stop_pulse(self) -> None:
        """Stop pulsing animation."""
        if self._pulse_after_id and self._root:
            self._root.after_cancel(self._pulse_after_id)
            self._pulse_after_id = None

    def _pulse(self, bright: bool) -> None:
        """Pulse the recording dot."""
        with self._lock:
            if self._status != "recording":
                return

        if self._canvas and self._dot:
            color = '#ff4444' if bright else '#cc2222'
            self._canvas.itemconfig(self._dot, fill=color)

        if self._root:
            self._pulse_after_id = self._root.after(500, lambda: self._pulse(not bright))

    def stop(self) -> None:
        """Stop the overlay and cleanup."""
        if self._root:
            self._root.after(0, self._root.quit)


overlay = Overlay()
