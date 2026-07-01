import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES, DND_ALL, COPY, REFUSE_DROP
from PIL import Image
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import threading
from urllib.parse import unquote, urlparse

from .theme import setup_theme, BG_BASE, TEXT_PRIMARY, TEXT_MUTED, BORDER
from .views.sidebar import Sidebar
from .views.canvas import CanvasArea
from .views.inspector import Inspector
from .components.toast import show_toast
from core.image_processing import process_formation_image
from core.excel_export import build_participant_dataframe, export_to_excel

class AppWindow(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)
        
        setup_theme()
        self.title("ODM Undip 2026")
        self.geometry("1440x900")
        self.minsize(1280, 800)
        self.configure(fg_color=BG_BASE)
        
        # State
        self.uploaded_paths = {}
        self.formations_data = {}
        self.excel_bytes = None
        self.show_grid = True
        self.bg_color = "putih"
        
        self.active_tab = None
        self._canvas_ref = None
        self._photo_refs = {}
        self._drop_in_progress = False
        self._manual_upload_dialog_open = False

        self._build_layout()
        self._setup_dnd()
        
        # Initial state
        self.canvas_area.show_placeholder()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=240) # Sidebar
        self.grid_columnconfigure(1, weight=1)              # Canvas Area
        self.grid_columnconfigure(2, weight=0, minsize=320) # Inspector
        self.grid_rowconfigure(0, weight=1)
        
        self.sidebar = Sidebar(self, self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.canvas_area = CanvasArea(self, self)
        self.canvas_area.grid(row=0, column=1, sticky="nsew")
        
        self.inspector = Inspector(self, self)
        self.inspector.grid(row=0, column=2, sticky="nsew")

    def _setup_dnd(self):
        # Only register the main window for drops to prevent TkinterDnD conflicts
        self.register_drop_targets(self)
        self.register_drop_targets(*self.canvas_area.drop_target_widgets())

    def register_drop_targets(self, *widgets):
        for widget in widgets:
            if not widget:
                continue
            try:
                widget.drop_target_register(DND_FILES, DND_ALL)
                widget.dnd_bind('<<DropEnter>>', self._allow_drop)
                widget.dnd_bind('<<DropPosition>>', self._allow_drop)
                widget.dnd_bind('<<Drop:DND_Files>>', self.on_drop)
                widget.dnd_bind('<<Drop>>', self.on_drop)
            except Exception:
                pass

    def _allow_drop(self, event):
        if not self.active_tab:
            return REFUSE_DROP
        return COPY

    def _split_drop_data(self, data):
        try:
            candidates = list(self.tk.splitlist(data))
        except Exception:
            candidates = [data]

        paths = []
        for item in candidates:
            text = str(item).replace("\r", "\n")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if len(lines) > 1:
                paths.extend(lines)
            else:
                paths.append(str(item).strip())
        return paths

    def _normalize_drop_paths(self, data):
        paths = []
        for path in self._split_drop_data(data):
            if not path or path.startswith("#"):
                continue
            parsed = urlparse(path)
            if parsed.scheme == "file":
                path = unquote(parsed.path)
            elif parsed.scheme:
                continue
            paths.append(path)
        return paths

    def on_drop(self, event):
        if self._drop_in_progress:
            return COPY
        self._drop_in_progress = True

        files = self._normalize_drop_paths(event.data)
        if not files:
            self._drop_in_progress = False
            return REFUSE_DROP
        
        if self.active_tab:
            file = files[0]
            ext = os.path.splitext(file)[1].lower()
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                self.after(100, lambda t=self.active_tab, f=file: self._finish_drop(t, f))
            else:
                self.after(100, self._finish_drop_error)
            return COPY

        self._drop_in_progress = False
        return REFUSE_DROP

    def _finish_drop(self, index, path):
        self._drop_in_progress = False
        self.handle_upload(index, path)

    def _finish_drop_error(self):
        self._drop_in_progress = False
        show_toast(self, "Format file tidak didukung", type="error")

    def open_manual_upload_dialog(self):
        if self._manual_upload_dialog_open or not self.active_tab:
            return

        index = self.active_tab
        self._manual_upload_dialog_open = True
        self.after(50, lambda i=index: self._run_manual_upload_dialog(i))

    def _run_manual_upload_dialog(self, index):
        try:
            from .utils import modern_file_picker
            path = modern_file_picker(title=f"Pilih Formasi {index:02d}")
            if path:
                self.handle_upload(index, path)
        except Exception as e:
            show_toast(self, f"Gagal membuka file: {e}", type="error")
        finally:
            self._manual_upload_dialog_open = False

    def handle_upload(self, index, path):
        self.uploaded_paths[index] = path
        if index in self.formations_data:
            del self.formations_data[index]
            
        self.sidebar.slots[index].set_state("uploaded")
        self.check_export_state()
        
        if self.active_tab == index:
            self.switch_tab(index)

    def handle_remove(self, index):
        if index in self.uploaded_paths:
            del self.uploaded_paths[index]
        if index in self.formations_data:
            del self.formations_data[index]
            
        self.sidebar.slots[index].set_state("empty")
        self.inspector.update_metrics(len(self.formations_data))
        self.check_export_state()
        
        if self.active_tab == index:
            self.switch_tab(index)

    def process_all(self):
        if not self.uploaded_paths:
            show_toast(self, "Upload minimal 1 gambar", type="warning")
            return
            
        self.canvas_area.btn_process.configure(state="disabled", text="Memproses...")
        
        def _task():
            success = 0
            for idx, path in list(self.uploaded_paths.items()):
                try:
                    res = process_formation_image(path)
                    self.formations_data[idx] = res
                    self.after(0, lambda i=idx: self.sidebar.slots[i].set_state("processed"))
                    success += 1
                except Exception as e:
                    print(f"Error F{idx}: {e}")
                    
            self.after(0, lambda: self._post_process(success))
            
        threading.Thread(target=_task, daemon=True).start()

    def _post_process(self, success_count):
        self.canvas_area.btn_process.configure(state="normal", text="Generate")
        self.inspector.update_metrics(len(self.formations_data))
        self.check_export_state()
        
        if success_count > 0:
            show_toast(self, f"Berhasil memproses {success_count} formasi", type="success")
            last_idx = max(self.formations_data.keys())
            self.switch_tab(last_idx)

    def switch_tab(self, index):
        self.active_tab = index
        
        for idx, slot in self.sidebar.slots.items():
            slot.set_active(idx == index)
            
        if index not in self.uploaded_paths:
            self.canvas_area.show_empty_state(index)
            self.inspector.render_distribution(None)
        else:
            self.canvas_area.show_full_state(index)
            if index in self.formations_data:
                self.render_preview(index)
            else:
                self.render_unprocessed(index)

    def render_unprocessed(self, index):
        path = self.uploaded_paths[index]
        if self._canvas_ref:
            self._canvas_ref.get_tk_widget().destroy()
            self._canvas_ref = None
            
        try:
            pil_img = Image.open(path)
            # Adjust thumbnail logic so it looks good in the split view container
            pil_img.thumbnail((600, 600), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=pil_img.size)
            self._photo_refs[index] = ctk_img
            self.canvas_area.set_image(ctk_img)
        except:
            self.canvas_area.lbl_image.configure(image="", text="Failed to load image")
            
        self.canvas_area.clear_plot()
        ctk.CTkLabel(self.canvas_area.plot_frame, text="Not generated yet.\nClick 'Generate' to process.", 
                     font=("Helvetica", 14), text_color=TEXT_MUTED).place(relx=0.5, rely=0.5, anchor="center")
                     
        self.inspector.render_distribution(None)

    def render_preview(self, index):
        data = self.formations_data[index]
        path = self.uploaded_paths[index]
        
        try:
            pil_img = Image.open(path)
            pil_img.thumbnail((600, 600), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=pil_img, size=pil_img.size)
            self._photo_refs[index] = ctk_img
            self.canvas_area.set_image(ctk_img)
        except: pass
            
        self.canvas_area.clear_plot()
            
        fig = self._create_figure(data, f"F{index}")
        self._canvas_ref = FigureCanvasTkAgg(fig, master=self.canvas_area.plot_frame)
        self._canvas_ref.draw()
        self.canvas_area.attach_canvas(self._canvas_ref.get_tk_widget())
        
        self.inspector.render_distribution(data)

    def _create_figure(self, data, label):
        preview = data["preview_rgb"]
        fig, ax = plt.subplots(1, 1, figsize=(6, 6), facecolor=BG_BASE)
        ax.set_facecolor(BG_BASE)
        ax.imshow(preview, interpolation="nearest", aspect="equal")
        
        ax.set_title(f"Grid Preview", color=TEXT_PRIMARY, fontsize=14, fontweight="bold", pad=12)
        ax.tick_params(colors=TEXT_MUTED, labelsize=9)
        
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)

        if self.show_grid:
            for i in range(0, 60 + 1, 1):
                ax.axhline(i - 0.5, color=BORDER, linewidth=0.5)
                ax.axvline(i - 0.5, color=BORDER, linewidth=0.5)

        ticks = list(range(0, 60, 5))
        ax.set_xticks(ticks)
        ax.set_xticklabels([t + 1 for t in ticks])
        ax.set_yticks(ticks)
        ax.set_yticklabels([t + 1 for t in ticks])
        plt.tight_layout(pad=1)
        return fig

    # Canvas floating toolbar hooks
    def zoom_grid(self, factor):
        if self._canvas_ref:
            ax = self._canvas_ref.figure.axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            cx = (xlim[0] + xlim[1]) / 2
            cy = (ylim[0] + ylim[1]) / 2
            wx = (xlim[1] - xlim[0]) * factor
            wy = (ylim[1] - ylim[0]) * factor
            ax.set_xlim(cx - wx/2, cx + wx/2)
            ax.set_ylim(cy - wy/2, cy + wy/2)
            self._canvas_ref.draw()
            
    def fit_grid(self):
        if self._canvas_ref:
            ax = self._canvas_ref.figure.axes[0]
            ax.set_xlim(-0.5, 60 - 0.5)
            ax.set_ylim(60 - 0.5, -0.5)
            self._canvas_ref.draw()
            
    def toggle_grid_lines(self):
        self.show_grid = not self.show_grid
        if self.active_tab and self.active_tab in self.formations_data:
            self.render_preview(self.active_tab)

    def check_export_state(self):
        if not self.formations_data:
            self.inspector.btn_gen_excel.configure(state="disabled", text="Generate Data")
            self.inspector.btn_dl_excel.configure(state="disabled")
            self.excel_bytes = None
        else:
            self.inspector.btn_gen_excel.configure(state="normal", text="Generate Data")
            
    def generate_excel(self):
        if not self.formations_data: return
        self.inspector.btn_gen_excel.configure(state="disabled", text="Generating...")
        
        def _task():
            try:
                sorted_keys = sorted(self.formations_data.keys())
                flist = [self.formations_data[k] for k in sorted_keys]
                
                df = build_participant_dataframe(flist, bg_color=self.bg_color)
                self.excel_bytes = export_to_excel(df, flist)
                
                self.after(0, lambda: self._on_gen_success())
            except Exception as e:
                err = str(e)
                self.after(0, lambda e_msg=err: self._on_gen_error(e_msg))
                
        threading.Thread(target=_task, daemon=True).start()

    def _on_gen_success(self):
        self.inspector.btn_gen_excel.configure(state="normal", text="Generate Data")
        self.inspector.btn_dl_excel.configure(state="normal")
        show_toast(self, "Data Excel siap diunduh!", type="success")

    def _on_gen_error(self, err):
        self.inspector.btn_gen_excel.configure(state="normal", text="Generate Data")
        show_toast(self, f"Gagal: {err}", type="error")

    def download_excel(self):
        if not self.excel_bytes: return
        
        from .utils import modern_save_picker
        path = modern_save_picker(title="Simpan File Excel")
        if path:
            try:
                with open(path, "wb") as f:
                    f.write(self.excel_bytes)
                show_toast(self, "Excel disimpan!", type="success")
            except Exception as e:
                show_toast(self, f"Gagal: {e}", type="error")
