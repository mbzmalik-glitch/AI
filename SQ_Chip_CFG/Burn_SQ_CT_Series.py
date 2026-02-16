import os
import re
import sys
import json
import threading
import time
import traceback
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import ctypes
except ImportError:
    ctypes = None

try:
    from pywinauto import Application, Desktop
except ImportError:
    Application = None
    Desktop = None


DEFAULT_BURN_EXE_PATH = Path(r"C:\Program Files (x86)\Cisco Systems\BurnSccSetup\BurnScc.exe")
DEFAULT_CT_SEARCH_ROOT = Path(r"D:\SQUAD\_SQUAD_Output_File_")
CHIP_TYPE_PATTERN = re.compile(r"Chip_Type\s*=\s*(.+?)\s*$", re.IGNORECASE)


def get_desktop_path() -> Path:
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        desktop = Path(user_profile) / "Desktop"
        if desktop.exists():
            return desktop

    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop

    return Path.home()


ERROR_LOG_PATH = get_desktop_path() / "Burn_SQ_CT_Series_error.log"


@dataclass
class BurnJob:
    ip_address: str
    starting_index: int
    list_file_path: Path | None
    chip_types: list[str]
    burn_exe_path: Path
    ct_search_root: Path


def _resolve_path(path_text: str, base_dir: Path) -> Path:
    raw_path = Path(str(path_text).strip())
    if raw_path.is_absolute():
        return raw_path
    return (base_dir / raw_path).resolve()


def load_job_from_json(config_path: Path) -> BurnJob:
    try:
        config_data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as error:
        raise RuntimeError(f"Failed to read JSON config: {error}") from error

    if not isinstance(config_data, dict):
        raise RuntimeError("JSON config root must be an object.")

    def require_text(key: str) -> str:
        value = config_data.get(key)
        if value is None:
            raise RuntimeError(f"Missing required key in JSON config: {key}")
        value_text = str(value).strip()
        if not value_text:
            raise RuntimeError(f"JSON key '{key}' cannot be empty.")
        return value_text

    config_dir = config_path.parent
    ip_address = require_text("ip_address")

    try:
        starting_index = int(config_data.get("starting_index"))
    except Exception as error:
        raise RuntimeError("JSON key 'starting_index' must be an integer.") from error

    if starting_index < 0:
        raise RuntimeError("JSON key 'starting_index' must be >= 0.")

    burn_exe_text = str(config_data.get("burn_exe_path", str(DEFAULT_BURN_EXE_PATH))).strip()
    ct_root_text = str(config_data.get("ct_search_root", str(DEFAULT_CT_SEARCH_ROOT))).strip()

    burn_exe_path = _resolve_path(burn_exe_text, config_dir)
    ct_search_root = _resolve_path(ct_root_text, config_dir)

    chip_types: list[str] = []
    list_file_path: Path | None = None

    chip_type_list_value = config_data.get("chip_type_list")
    if chip_type_list_value is not None:
        if not isinstance(chip_type_list_value, list):
            raise RuntimeError("JSON key 'chip_type_list' must be an array of chip type strings.")

        for item in chip_type_list_value:
            item_text = str(item).strip().strip('"').strip("'")
            if item_text:
                chip_types.append(item_text)

        if not chip_types:
            raise RuntimeError("JSON key 'chip_type_list' is present but empty.")
    else:
        list_file_path = _resolve_path(require_text("chip_list_file"), config_dir)
        if not list_file_path.exists() or not list_file_path.is_file():
            raise RuntimeError(f"chip_list_file not found: {list_file_path}")
        chip_types = parse_chip_types(list_file_path)

    if not burn_exe_path.exists() or not burn_exe_path.is_file():
        raise RuntimeError(f"burn_exe_path not found: {burn_exe_path}")
    if not ct_search_root.exists() or not ct_search_root.is_dir():
        raise RuntimeError(f"ct_search_root not found: {ct_search_root}")

    return BurnJob(
        ip_address=ip_address,
        starting_index=starting_index,
        list_file_path=list_file_path,
        chip_types=chip_types,
        burn_exe_path=burn_exe_path,
        ct_search_root=ct_search_root,
    )


def is_admin() -> bool:
    if ctypes is None:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> None:
    if ctypes is None:
        raise RuntimeError("ctypes is unavailable; cannot elevate privileges.")

    script = str(Path(__file__).resolve())
    params = f'"{script}"'
    result = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    if result <= 32:
        raise RuntimeError("Administrator elevation was denied or failed.")
    sys.exit(0)


def parse_chip_types(list_file_path: Path) -> list[str]:
    chip_types: list[str] = []
    with list_file_path.open("r", encoding="utf-8") as file:
        for line in file:
            match = CHIP_TYPE_PATTERN.search(line)
            if not match:
                continue
            value = match.group(1).strip().strip('"').strip("'")
            if value:
                chip_types.append(value)

    if not chip_types:
        raise ValueError("No lines with 'Chip_Type =' were found in the selected file.")
    return chip_types


def find_ct_file(chip_type: str, root_path: Path) -> Path:
    if not root_path.exists():
        raise FileNotFoundError(f"CT search root not found: {root_path}")

    def normalize_token(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "", value.lower())

    chip_raw = chip_type.strip().strip('"').strip("'")
    chip_lower = chip_raw.lower()
    chip_norm = normalize_token(chip_raw)

    all_ct_files = [
        path
        for path in root_path.rglob("*")
        if path.is_file() and path.suffix.lower() == ".ct"
    ]

    if not all_ct_files:
        raise FileNotFoundError(f"No .ct files found under {root_path}")

    exact_stem = [
        path
        for path in all_ct_files
        if path.stem.lower() == chip_lower or normalize_token(path.stem) == chip_norm
    ]
    if len(exact_stem) == 1:
        return exact_stem[0]
    if len(exact_stem) > 1:
        exact_stem_sorted = sorted(exact_stem, key=lambda item: (len(item.name), str(item).lower()))
        return exact_stem_sorted[0]

    contains_match = [
        path
        for path in all_ct_files
        if chip_lower in path.stem.lower() or chip_norm in normalize_token(path.stem)
    ]

    if not contains_match:
        raise FileNotFoundError(f"No .ct file found for chip type '{chip_raw}' in {root_path}")

    if len(contains_match) == 1:
        return contains_match[0]

    preview = "\n".join(str(path) for path in sorted(contains_match)[:10])
    raise RuntimeError(
        "Ambiguous CT file match for chip type "
        f"'{chip_raw}'. Multiple candidates found:\n{preview}\n"
        "Please rename files for exact match (stem == chip type) or make chip type more specific."
    )


def _find_edit_for_label(window, label_pattern: str):
    labels = window.descendants(control_type="Text")
    for label in labels:
        label_text = label.window_text().strip()
        if not re.search(label_pattern, label_text, flags=re.IGNORECASE):
            continue

        rect = label.rectangle()
        edits = window.descendants(control_type="Edit")
        nearest_edit = None
        nearest_distance = None
        for edit in edits:
            edit_rect = edit.rectangle()
            if edit_rect.left < rect.left - 30:
                continue
            if abs(edit_rect.top - rect.top) > 80:
                continue
            distance = abs(edit_rect.left - rect.right) + abs(edit_rect.top - rect.top)
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_edit = edit

        if nearest_edit is not None:
            return nearest_edit
    return None


def _find_edit_for_file_name_field(window):
    labels = window.descendants(control_type="Text")
    preferred = []
    fallback = []

    for label in labels:
        label_text = label.window_text().strip()
        normalized = re.sub(r"\s+", " ", label_text.lower())

        if "file name" not in normalized:
            continue
        if "log" in normalized:
            continue

        rect = label.rectangle()
        edits = window.descendants(control_type="Edit")
        nearest_edit = None
        nearest_distance = None
        for edit in edits:
            edit_rect = edit.rectangle()
            if edit_rect.left < rect.left - 30:
                continue
            if abs(edit_rect.top - rect.top) > 80:
                continue
            distance = abs(edit_rect.left - rect.right) + abs(edit_rect.top - rect.top)
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_edit = edit

        if nearest_edit is None:
            continue

        if "full path for the file name" in normalized:
            preferred.append((nearest_distance or 0, nearest_edit))
        else:
            fallback.append((nearest_distance or 0, nearest_edit))

    if preferred:
        preferred.sort(key=lambda item: item[0])
        return preferred[0][1]
    if fallback:
        fallback.sort(key=lambda item: item[0])
        return fallback[0][1]
    return None


def _normalize_label(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().rstrip(":" )).lower()


def _control_rect_key(control) -> tuple[int, int, int, int]:
    rect = control.rectangle()
    return (rect.left, rect.top, rect.right, rect.bottom)


def _find_edit_candidates_for_exact_label(window, exact_label: str) -> list[object]:
    expected = _normalize_label(exact_label)
    labels = window.descendants(control_type="Text")
    collected: list[object] = []

    for label in labels:
        if _normalize_label(label.window_text()) != expected:
            continue

        rect = label.rectangle()
        input_candidates = window.descendants(control_type="Edit") + window.descendants(control_type="ComboBox")
        ranked: list[tuple[int, int, object]] = []

        for candidate in input_candidates:
            candidate_rect = candidate.rectangle()
            if candidate_rect.left < rect.left - 20:
                continue

            row_distance = abs(candidate_rect.mid_point().y - rect.mid_point().y)
            horizontal_gap = max(0, candidate_rect.left - rect.right)
            ranked.append((row_distance, horizontal_gap, candidate))

        if not ranked:
            continue

        strict_row = [item for item in ranked if item[0] <= 28]
        target_pool = strict_row if strict_row else ranked
        target_pool.sort(key=lambda item: (item[0], item[1]))

        for _, _, chosen in target_pool:
            if chosen.element_info.control_type == "ComboBox":
                combo_edits = chosen.descendants(control_type="Edit")
                if combo_edits:
                    collected.append(combo_edits[0])
            else:
                collected.append(chosen)

    deduped: list[object] = []
    seen: set[tuple[int, int, int, int]] = set()
    for candidate in collected:
        key = _control_rect_key(candidate)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(candidate)

    return deduped


def _find_edit_for_exact_label(window, exact_label: str):
    candidates = _find_edit_candidates_for_exact_label(window, exact_label)
    return candidates[0] if candidates else None


def _set_edit_value(window, label_pattern: str, value: str, exact_label: str | None = None) -> None:
    if exact_label:
        edit = _find_edit_for_exact_label(window, exact_label)
    else:
        edit = _find_edit_for_label(window, label_pattern)
    if edit is None:
        if exact_label:
            raise RuntimeError(f"Could not find input field for exact label: {exact_label}")
        raise RuntimeError(f"Could not find input field for label pattern: {label_pattern}")

    edit.click_input()
    try:
        edit.set_edit_text(value)
    except Exception:
        edit.type_keys("^a{BACKSPACE}", set_foreground=True)
        edit.type_keys(value, with_spaces=True, set_foreground=True)


def _get_edit_value(window, exact_label: str) -> str:
    edit = _find_edit_for_exact_label(window, exact_label)
    if edit is None:
        raise RuntimeError(f"Could not find input field for exact label: {exact_label}")

    try:
        value_pattern = edit.iface_value.CurrentValue
        if isinstance(value_pattern, str):
            return value_pattern
    except Exception:
        pass

    try:
        return str(edit.window_text())
    except Exception:
        return ""


def _set_exact_with_verify(window, exact_label: str, value: str, retries: int = 3):
    expected = str(Path(value)).rstrip("\\/").lower() if value else ""
    for _ in range(retries):
        _set_edit_value(window, r"", value, exact_label=exact_label)

        time.sleep(0.2)
        actual_raw = _get_edit_value(window, exact_label)
        actual = str(Path(actual_raw)).rstrip("\\/").lower() if actual_raw else ""
        if actual == expected:
            return
    raise RuntimeError(f"Failed to set '{exact_label}' to '{value}'.")


def run_burn_sequence(job: BurnJob, log_callback) -> None:
    if Application is None or Desktop is None:
        raise RuntimeError("pywinauto is required. Install with: pip install pywinauto")

    chip_types = job.chip_types
    log_callback(f"Loaded {len(chip_types)} chip type(s) from list.")

    range_index = job.starting_index
    for chip_type in chip_types:
        log_callback(f"Processing chip type: {chip_type}")
        ct_file = find_ct_file(chip_type, job.ct_search_root)
        log_callback(f"Found CT file: {ct_file}")

        app = Application(backend="uia").start(f'"{job.burn_exe_path}"')
        window = app.window(title_re=r".*Burn.*")
        window.wait("visible", timeout=30)
        window.set_focus()

        _set_edit_value(window, r"IP\s*Address", job.ip_address)
        try:
            _set_exact_with_verify(window, "Full path for the File Name", str(ct_file))
            log_callback(f"Set 'Full path for the File Name' to: {ct_file}")
        except RuntimeError:
            fallback_edit = _find_edit_for_file_name_field(window)
            if fallback_edit is None:
                raise RuntimeError("Could not find File Name input field (non-log fallback).")
            fallback_edit.click_input()
            try:
                fallback_edit.set_edit_text(str(ct_file))
            except Exception:
                fallback_edit.type_keys("^a{BACKSPACE}", set_foreground=True)
                fallback_edit.type_keys(str(ct_file), with_spaces=True, set_foreground=True)
            log_callback(f"Set File Name field (non-log fallback) to: {ct_file}")
        _set_edit_value(window, r"Ranges?\s*of\s*chips", str(range_index))

        burn_button = window.child_window(title_re=r"^Burn$", control_type="Button")
        if not burn_button.exists(timeout=5):
            raise RuntimeError("Could not find Burn button.")

        burn_button.click_input()
        log_callback(f"Burn clicked for {chip_type}, range index {range_index}.")

        time.sleep(5)
        for popup in Desktop(backend="uia").windows(control_type="Window"):
            popup_title = popup.window_text().strip().lower()
            if "burn" in popup_title or "success" in popup_title or "complete" in popup_title:
                for button in popup.descendants(control_type="Button"):
                    button_text = button.window_text().strip().lower()
                    if button_text == "ok":
                        button.click_input()
                        break

        try:
            window.close()
        except Exception:
            pass

        range_index += 1

    log_callback("All chip types processed.")


class BurnSeriesGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Burn_SQ_CT_Series")
        self.root.geometry("760x500")

        self.config_file_var = tk.StringVar(value=str(Path(__file__).resolve().with_name("Burn_SQ_CT_Series_config.json")))

        self._build_ui()

    def _build_ui(self) -> None:
        frm = tk.Frame(self.root)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(frm, text="JSON config file").grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Entry(frm, textvariable=self.config_file_var, width=40).grid(row=0, column=1, sticky="we", pady=(0, 6))
        tk.Button(frm, text="Browse...", command=self._browse_config_file).grid(row=0, column=2, padx=(8, 0), pady=(0, 6))

        tk.Label(
            frm,
            text=(
                "Config keys: ip_address, starting_index, chip_type_list (preferred) or "
                "chip_list_file, burn_exe_path (optional), ct_search_root (optional)"
            ),
            anchor="w",
            justify="left",
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Button(frm, text="Start Burn Series", command=self._start).grid(row=2, column=0, columnspan=3, sticky="we")

        self.log_text = tk.Text(frm, height=18, state="disabled")
        self.log_text.grid(row=3, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

        frm.columnconfigure(1, weight=1)
        frm.rowconfigure(3, weight=1)

    def _browse_config_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select Burn_SQ_CT_Series JSON config",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
        )
        if file_path:
            self.config_file_var.set(file_path)

    def _log(self, message: str) -> None:
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def _start(self) -> None:
        config_path = Path(self.config_file_var.get().strip())
        if not config_path.exists() or not config_path.is_file():
            messagebox.showerror("Validation error", "Please select a valid JSON config file.")
            return

        try:
            job = load_job_from_json(config_path)
        except Exception as error:
            messagebox.showerror("Config error", str(error))
            return

        self._log(f"Config loaded: {config_path}")
        self._log(f"IP address: {job.ip_address}")
        self._log(f"Starting index: {job.starting_index}")
        if job.list_file_path is not None:
            self._log(f"Chip source file: {job.list_file_path}")
        else:
            self._log("Chip source: chip_type_list from JSON")
        self._log(f"Total chip types: {len(job.chip_types)}")
        self._log(f"Burn executable: {job.burn_exe_path}")
        self._log(f"CT search root: {job.ct_search_root}")

        worker = threading.Thread(target=self._run_job, args=(job,), daemon=True)
        worker.start()

    def _run_job(self, job: BurnJob) -> None:
        try:
            self._log("Starting burn sequence...")
            run_burn_sequence(job, self._log)
            self._log("Burn sequence completed.")
        except Exception as error:
            trace = traceback.format_exc()
            self._log(f"ERROR: {error}")
            self._log(trace)

            try:
                with ERROR_LOG_PATH.open("a", encoding="utf-8") as file:
                    file.write("\n--- ERROR ---\n")
                    file.write(trace)
            except Exception:
                pass

            messagebox.showerror("Burn failed", f"{error}\n\nDetails saved to:\n{ERROR_LOG_PATH}")


def main() -> None:
    if not is_admin():
        relaunch_as_admin()

    root = tk.Tk()
    BurnSeriesGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
