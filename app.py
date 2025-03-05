# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # Python 2: Unicode by default
from flask import Flask, render_template, request, send_file
import os
import yt_dlp as youtube_dl  # Use yt-dlp instead of youtube-dl

app = Flask(__name__)

# Temporary folder for storing downloads
download_path = os.path.join(os.getcwd(), "downloads")

# Fix for Python 2.7 (No exist_ok=True support)
if not os.path.exists(download_path):
    os.makedirs(download_path)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                # Configure yt-dlp options (use cookies if needed)
                ydl_opts = {
                    'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                    'cookiefile': 'cookies.txt',  # Add this if video requires login
                }

                # Download video
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(video_url, download=True)
                    video_filename = ydl.prepare_filename(info_dict).decode("utf-8")  # Fix Unicode issues

                return render_template("index.html", message="Download Ready!", video_file=os.path.basename(video_filename))
            except Exception as e:
                return render_template("index.html", message=u"Error: " + unicode(e).encode("utf-8"))  # Unicode fix
    
    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(download_path, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
