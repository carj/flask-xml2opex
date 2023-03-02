import os
import xml.etree.ElementTree
import xml.etree.ElementTree as ET
import zipfile
import uuid
from os.path import isfile
import shutil

from flask import request, Flask, render_template, flash, session, send_file, redirect
from flask_bootstrap import Bootstrap
from flask_dropzone import Dropzone
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from wtforms import SubmitField

app = Flask(__name__)

app.config['DROPZONE_ALLOWED_FILE_CUSTOM'] = True
app.config['DROPZONE_ALLOWED_FILE_TYPE'] = 'application/xml, text/xml, .xml, .metadata'


app.config['DROPZONE_DEFAULT_MESSAGE'] = "Drop your descriptive metadata XML files here to upload"
app.config['DROPZONE_MAX_FILE_SIZE'] = 10

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
bootstrap = Bootstrap(app)
dropzone = Dropzone(app)

FILES_DIR = "/home/opextest/mysite/upload"
MY_SITE = "/home/opextest/mysite/"

opex_ns = {"opex": "http://www.openpreservationexchange.org/opex/v1.2"}

xml.etree.ElementTree.register_namespace("oai_dc", "http://www.openarchives.org/OAI/2.0/oai_dc/")
xml.etree.ElementTree.register_namespace("ead", "urn:isbn:1-931666-22-9")
xml.etree.ElementTree.register_namespace("opex", opex_ns['opex'])
xml.etree.ElementTree.register_namespace("xip", "http://preservica.com/XIP/v6.6")


class DownloadForm(FlaskForm):
    xml_button = SubmitField('Download OPEX Documents')


@app.route('/', methods=['POST', 'GET'])
def upload():
    form = DownloadForm()
    if form.validate_on_submit():
        try:
            client = session['active_session']
            folder = os.path.join(FILES_DIR, client)
            files = [f for f in os.listdir(folder) if isfile(os.path.join(folder, f))]
            print(len(files))
            if len(files) > 1:
                zip_return = os.path.join(MY_SITE, f"{client}.zip")
                with zipfile.ZipFile(zip_return, 'w') as myzip:
                    for file in files:
                        print(os.path.join(folder, file))
                        myzip.write(os.path.join(folder, file), arcname=file)
                for file in files:
                    os.remove(os.path.join(folder, file))
                print(f"ZIP file is {zip_return}")
                return send_file(zip_return, mimetype="application/zip", as_attachment=True)
            if len(files) == 1:
                file = files[0]
                return send_file(os.path.join(folder, file), mimetype="application/xml", as_attachment=True)
        except FileNotFoundError:
            return redirect("/")
        return redirect("/")
    if request.method == 'POST':
        file = request.files.get('file')
        fn = secure_filename(file.filename)
        path = os.path.join(FILES_DIR, fn)
        file.save(path)
        try:
            tree = ET.parse(path)
            client = session['active_session']
            folder = os.path.join(FILES_DIR, client)
            if not os.path.exists(folder):
                os.mkdir(folder)

            ## convert to OPEX here
            opex_doc = xml.etree.ElementTree.Element(ET.QName(opex_ns["opex"], 'OPEXMetadata'))
            dm = xml.etree.ElementTree.SubElement(opex_doc, ET.QName(opex_ns["opex"], "DescriptiveMetadata"))
            head, _sep, tail = os.path.basename(path).rpartition(".")
            file_name = head + ".opex"
            xml_file = os.path.join(folder, file_name)
            print(xml_file)
            with open(path, 'r', encoding="utf-8") as md:
                tree = xml.etree.ElementTree.parse(md)
                dm.append(tree.getroot())
                fd = open(xml_file, "w", encoding="utf-8")
                fd.write(ET.tostring(element=opex_doc, encoding="UTF-8", xml_declaration=True).decode("utf-8"))
                fd.close()
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            return render_template('index.html', form=form)
        except xml.etree.ElementTree.ParseError:
            flash('Invalid XML Document')
            os.remove(path)
            return "Invalid XML document, deleted from server"
    if request.method == 'GET':
        session['active_session'] = str(uuid.uuid4())
        return render_template('index.html', form=form)
