import queue
import tkinter as tk
from unified_canvas import UnifiedCanvas

root = tk.Tk()
root.withdraw()
uc = UnifiedCanvas(root)
q = queue.Queue()
q.put(("Hello", 10))
q.put(("Second line\n", None))

# mimic Time_Warp._flush_ui_queue behavior
try:
    while True:
        item = q.get_nowait()
        if isinstance(item, tuple) and len(item) >= 1:
            text = item[0]
            color = item[1] if len(item) > 1 else None
            txt = str(text)
            if not txt.endswith('\n'):
                txt = txt + '\n'
            uc.write_text(txt, color=color)
        else:
            uc.write_text(str(item))
except Exception:
    pass

uc.redraw()

print('LINES:', uc.lines)
with open('.diagnostics/local_flush_probe.log', 'w') as f:
    f.write('\n'.join(uc.lines))

root.destroy()
