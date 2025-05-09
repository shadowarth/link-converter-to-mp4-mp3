import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import requests
import pyperclip
from yt_dlp import YoutubeDL


def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None


def choose_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)


def resolve_shortlink(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, allow_redirects=True, headers=headers, timeout=5)
        return response.url
    except Exception as e:
        print(f"Error resolving shortlink: {e}")
        return url


def hook_progress(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            progress_bar["value"] = percent
            status_label.config(text=f"Downloading: {percent:.1f}%")
    elif d['status'] == 'finished':
        status_label.config(text="Processing...")


def test_url():
    url = url_entry.get()
    if not url.startswith("http"):
        messagebox.showerror("Invalid", "Please enter a valid URL.")
        return

    test_status.config(text="Checking...")
    try:
        final_url = resolve_shortlink(url) if "v.douyin.com" in url else url
        response = requests.head(final_url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True, timeout=5)
        if response.status_code == 200:
            test_status.config(text="✅ URL is reachable", fg="green")
        else:
            test_status.config(text=f"⚠️ URL error: {response.status_code}", fg="orange")
    except Exception as e:
        test_status.config(text=f"❌ Error: {str(e)}", fg="red")


def download_video():
    url = url_entry.get()
    file_format = format_var.get()
    resolution = res_var.get()
    folder = folder_path.get()

    if not url or not folder:
        messagebox.showwarning("Missing Info", "Please enter a URL and choose a save folder.")
        return

    # Resolve short Douyin links
    if "v.douyin.com" in url:
        status_label.config(text="Resolving short link...")
        url = resolve_shortlink(url)
        status_label.config(text="Resolved full URL.")

    use_ffmpeg = is_ffmpeg_installed()
    progress_bar["value"] = 0
    status_label.config(text="Starting download...")

    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'progress_hooks': [hook_progress],
        'merge_output_format': 'mp4' if file_format == "MP4" else 'mp3',
        'postprocessors': [],
        'quiet': True,
        'noplaylist': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        }
    }

    if use_ffmpeg:
        if file_format == "MP3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            })
        else:
            ydl_opts['format'] = f'bestvideo[height<={resolution}]+bestaudio/best/best'
            ydl_opts['postprocessors'].append({'key': 'FFmpegMerger'})
    else:
        messagebox.showwarning("FFmpeg Missing",
                               "FFmpeg not found. Falling back to lower-quality stream with audio.")
        ydl_opts['format'] = f'best[height<={resolution}]'

    def run_download():
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status_label.config(text="✅ Download complete.")
            progress_bar["value"] = 100
        except Exception as e:
            messagebox.showerror("Error", str(e))
            status_label.config(text="Download failed.")

    threading.Thread(target=run_download).start()


# --- GUI Setup ---
root = tk.Tk()
root.title("Universal Video Downloader")
root.geometry("540x500")
root.resizable(False, False)

tk.Label(root, text="Enter Video URL:").pack(pady=5)
url_entry = tk.Entry(root, width=65)
url_entry.pack(pady=5)

# Clipboard auto-paste
clipboard_text = pyperclip.paste()
if clipboard_text.startswith("http"):
    url_entry.insert(0, clipboard_text)

tk.Button(root, text="Test URL", command=test_url, bg="gray", fg="white").pack(pady=3)
test_status = tk.Label(root, text="", fg="blue")
test_status.pack()

tk.Label(root, text="Choose Format:").pack(pady=5)
format_var = tk.StringVar(value="MP4")
tk.OptionMenu(root, format_var, "MP4", "MP3").pack(pady=5)

tk.Label(root, text="Choose Resolution:").pack(pady=5)
res_var = tk.StringVar(value="1080")
tk.OptionMenu(root, res_var, "1080", "1440", "2160", "4320").pack(pady=5)

folder_path = tk.StringVar()
tk.Button(root, text="Choose Download Folder", command=choose_folder).pack(pady=10)
tk.Label(root, textvariable=folder_path, fg="blue").pack()

tk.Button(root, text="Start Download", command=download_video, bg="green", fg="white", height=2, width=20).pack(pady=15)

progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=10)

status_label = tk.Label(root, text="", fg="blue")
status_label.pack(pady=5)

root.mainloop()
