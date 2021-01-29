import os
import random
from flask import Flask, flash, session, request, redirect, render_template, send_file
from werkzeug.utils import secure_filename
from ftssim import gpx, wander
from threading import Thread

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = ['gpx']


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
    return render_template('index.html')


@app.route('/gpx')
def gpx_form():
    return render_template('gpx.html')


@app.route('/wander')
def wander_form():
    return render_template('wander.html')


@app.route('/gpx', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        gap = request.form.get("gap")
        speed = request.form.get("kph")
        server = request.form.get("server")
        callsign = request.form.get("callsign")
        cot_type = request.form.get("cot_type")
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            session['seshid'] = str(random.randint(100, 99999))

            upload_folder = 'C:\\temp'
            session_folder = os.path.join(upload_folder, session['seshid'])
            gpx_file = os.path.join(session_folder, filename)

            if not os.path.exists(upload_folder):
                os.mkdir(upload_folder)

            if not os.path.exists(session_folder):
                os.mkdir(session_folder)
            file.save(gpx_file)
            player = gpx.GpxPlayer(server, gpx_file, str(callsign), speed_kph=int(speed), max_time_step_secs=int(gap),
                                   cot_type=str(cot_type))
            t1 = Thread(target=player.play_gpx)
            t1.start()
            return redirect('/')


@app.route('/wander', methods=['POST'])
def submit_wander():
    if request.method == 'POST':
        gap = request.form.get("gap")
        speed = request.form.get("kph")
        total_distance = request.form.get("total_distance")
        distance_between_change = request.form.get("distance_between_change")
        start_lat = request.form.get("start_lat")
        start_lon = request.form.get("start_lon")
        server = request.form.get("server")
        callsign = request.form.get("callsign")
        cot_type = request.form.get("cot_type")
        wanderer = wander.Wander(server, total_distance_km=int(total_distance),
                                 distance_between_change=int(distance_between_change), callsign=callsign,
                                 speed_kph=int(speed), max_time_step_secs=int(gap), start_lat=float(start_lat),
                                 start_lon=float(start_lon), cot_type=cot_type)
        t1 = Thread(target=wanderer.start_wandering)
        t1.start()
        return redirect('/')


@app.route('/failed')
def failed():
    return render_template('failed.html')


if __name__ == "__main__":
    app.run()
