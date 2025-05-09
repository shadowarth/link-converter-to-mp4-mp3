import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from yt_dlp import YoutubeDL
import subprocess

# Create main application window
root = tk.Tk()
root.title("YouTube/Instagram Downloader")

# Variables to store user selections
platform_var = tk.StringVar(value="YouTube")
url_var = tk.StringVar()
quality_var = tk.StringVar(value="1080p")
format_var = tk.StringVar(value="MP4")

def download_video():
    """Handle the download when the user clicks 'Download'."""
    url = url_var.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a valid URL.")
        return
    selected_platform = platform_var.get()
    selected_format = format_var.get()
    selected_quality = quality_var.get()

    # Determine output directory (Downloads folder)
    downloads_path = Path.home() / "Downloads"
    output_template = str(downloads_path / "%(title)s.%(ext)s")

    # Common yt-dlp options
    ydl_opts = {
        'outtmpl': output_template,
        'nocheckcertificate': True,
        'quiet': True
    }

    # Format and quality settings
    if selected_format == "MP3":
        # Extract audio only
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        # Download video (MP4) with chosen resolution limit
        # Map user choice to max height
        quality_map = {"1080p": 1080, "1440p": 1440, "2160p/4K": 2160}
        max_height = quality_map.get(selected_quality, 1080)
        # Format string to get best video+audio up to the specified height
        ydl_opts['format'] = f'bestvideo[height<={max_height}]+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        # Use yt-dlp to download the content
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", f"Download completed:\nSaved to {downloads_path}")
    except Exception as e:
        messagebox.showerror("Download Error", f"An error occurred:\n{str(e)}")

# Layout: Platform selection (YouTube or Instagram)
platform_frame = ttk.LabelFrame(root, text="Select Platform")
platform_frame.pack(fill="x", padx=10, pady=5)
ttk.Radiobutton(platform_frame, text="YouTube", variable=platform_var, value="YouTube").pack(side="left", padx=5, pady=5)
ttk.Radiobutton(platform_frame, text="Instagram", variable=platform_var, value="Instagram").pack(side="left", padx=5, pady=5)

# URL input field
url_frame = ttk.Frame(root)
url_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(url_frame, text="Video URL:").pack(side="left")
ttk.Entry(url_frame, textvariable=url_var, width=50).pack(side="left", padx=5)

# Quality selection dropdown
quality_frame = ttk.Frame(root)
quality_frame.pack(fill="x", padx=10, pady=5)
ttk.Label(quality_frame, text="Quality:").pack(side="left")
qualities = ["1080p", "1440p", "2160p/4K"]
ttk.OptionMenu(quality_frame, quality_var, quality_var.get(), *qualities).pack(side="left", padx=5)

# Format selection (MP4 or MP3)
format_frame = ttk.LabelFrame(root, text="Output Format")
format_frame.pack(fill="x", padx=10, pady=5)
ttk.Radiobutton(format_frame, text="MP4 (video)", variable=format_var, value="MP4").pack(side="left", padx=5, pady=5)
ttk.Radiobutton(format_frame, text="MP3 (audio)", variable=format_var, value="MP3").pack(side="left", padx=5, pady=5)

# Download button
download_button = ttk.Button(root, text="Download", command=download_video)
download_button.pack(pady=10)

root.mainloop()
