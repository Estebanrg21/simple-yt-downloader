import os
import time
import zipfile
from io import BytesIO

from flask import Flask, send_file, send_from_directory, Response, jsonify
from flask import request
from yt_dlp import YoutubeDL
from urllib.parse import urlparse

app = Flask(__name__)


@app.route("/yt-ready/<path:respath>")
def yt_ready(respath):
    folder = 'dump/videos/'
    path = folder + respath
    if os.path.isdir(path):
        file_name = "{}_{}.zip".format("playlist", respath)
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(path):
                for file in files:
                    zipf.write(os.path.join(root, file),
                               arcname=os.path.join(root, file)[len(folder) + 1:])
        memory_file.seek(0)
        return send_file(memory_file,
                         download_name=file_name,
                         as_attachment=True)
    else:
        return send_file(path)


@app.route('/download-video/')
def download_video():
    main_folder = "dump/videos"
    url = request.args.get('url')
    url_parsed = urlparse(url, allow_fragments=False)

    v_type = request.args.get("type")
    name = request.args.get("name")
    v_type = v_type if v_type else "mp4"
    name = name if name else time.strftime("%Y%m%d-%H%M%S")
    is_playlist = True if os.path.split(url_parsed.path)[-1] == "playlist" else False
    folder = main_folder + ("" if not is_playlist else "/" + name)
    path = f"{folder}/{name}.%(ext)s" \
        if not is_playlist else f"{folder}/%(id)s-%(title)s.%(ext)s"
    ydl = YoutubeDL({
        "format": v_type,
        "restrictfilenames": True,
        'outtmpl': path
    })
    info = ydl.extract_info(url, download=True)
    new_url = request.url_root + "yt-ready/" + \
              (ydl.prepare_filename(info) if not is_playlist else name) \
                  .replace("\\", "/") \
                  .replace(main_folder + "/", "")
    return jsonify({"url": new_url})


@app.route('/video/')
def video():
    return send_from_directory("templates", "form-yt-url.html")
