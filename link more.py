import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import shutil
from yt_dlp import YoutubeDL
import threading


def is_ffmpeg_installed():
    return shutil.which("ffmpeg") is not None


def download_video():
    url = url_entry.get()
    platform = platform_var.get()
    file_format = format_var.get()
    resolution = res_var.get()
    folder = folder_path.get()

    if not url or not folder:
        messagebox.showwarning("Missing Info", "Please enter a URL and choose a save folder.")
        return

    use_ffmpeg = is_ffmpeg_installed()

    options = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4' if file_format == "MP4" else 'mp3',
        'postprocessors': []
    }

    # Format Selection with forced m4a to avoid Opus issues
    if use_ffmpeg:
        if file_format == "MP3":
            options['format'] = 'bestaudio[ext=m4a]/bestaudio/best'
            options['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            })
        else:
            options['format'] = f'bestvideo[height<={resolution}]+bestaudio[ext=m4a]/best[height<={resolution}]'
            options['postprocessors'].append({
                'key': 'FFmpegMerger',
            })
    else:
        # Fallback if no FFmpeg
        messagebox.showwarning("FFmpeg Missing",
                               "FFmpeg not found. Falling back to lower-quality stream with audio.")
        options['format'] = f'best[height<={resolution}]'

    def run_download():
        try:
            if platform == "Instagram":
                import instaloader
                L = instaloader.Instaloader(dirname_pattern=folder)
                L.download_profile(url, profile_pic_only=False)
            else:
                with YoutubeDL(options) as ydl:
                    ydl.download([url])
            messagebox.showinfo("Done", "Download completed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    threading.Thread(target=run_download).start()


def choose_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)


# GUI Setup
root = tk.Tk()
root.title("Media Downloader")
root.geometry("500x430")
root.resizable(False, False)

tk.Label(root, text="Enter Video URL:").pack(pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(pady=5)

tk.Label(root, text="Select Platform:").pack(pady=5)
platform_var = tk.StringVar(value="YouTube")
tk.OptionMenu(root, platform_var, "YouTube", "Instagram", "Douyin").pack(pady=5)

tk.Label(root, text="Choose Format:").pack(pady=5)
format_var = tk.StringVar(value="MP4")
tk.OptionMenu(root, format_var, "MP4", "MP3").pack(pady=5)

tk.Label(root, text="Choose Resolution:").pack(pady=5)
res_var = tk.StringVar(value="1080")
tk.OptionMenu(root, res_var, "1080", "1440", "2160", "4320").pack(pady=5)

folder_path = tk.StringVar()
tk.Button(root, text="Choose Download Folder", command=choose_folder).pack(pady=10)
tk.Label(root, textvariable=folder_path, fg="blue").pack()

tk.Button(root, text="Start Download", command=download_video, bg="green", fg="white", height=2, width=20).pack(pady=20)

root.mainloop()
