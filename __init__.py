from flask import Flask, redirect, render_template, request
from werkzeug.utils import secure_filename
import os
import sys
from flasgger import Swagger
from server import app
from server.routes.prometheus import track_requests
from userapp import osclient
import mimetypes
import os.path
from os import path

app=Flask(__name__,template_folder='templates')
UPLOAD_FOLDER = '.'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024


# The python-flask stack includes the flask extension flasgger, which will build
# and publish your swagger ui and specification at the /apidocs url. Here we set up
# the basic swagger attributes, which you should modify to match you application.
# See: https://github.com/rochacbruno-archive/flasgger
swagger_template = {
  "swagger": "2.0",
  "info": {
    "title": "Example API for python-flask stack",
    "description": "API for helloworld, plus health/monitoring",
    "contact": {
      "responsibleOrganization": "IBM",
      "responsibleDeveloper": "Henry Nash",
      "email": "henry.nash@uk.ibm.com",
      "url": "https://appsody.dev",
    },
    "version": "0.2"
  },
  "schemes": [
    "http"
  ],
}
swagger = Swagger(app, template=swagger_template)

# The python-flask stack includes the prometheus metrics engine. You can ensure your endpoints
# are included in these metrics by enclosing them in the @track_requests wrapper.
@app.route('/hello')
@track_requests
def HelloWorld():
    # To include an endpoint in the swagger ui and specification, we include a docstring that
    # defines the attributes of this endpoint.
    """A hello message
    Example endpoint returning a hello message
    ---
    responses:
      200:
        description: A successful reply
        examples:
          text/plain: Hello from Appsody!
    """
    return 'Hello from Appsody!'

# It is considered bad form to return an error for '/', so let's redirect to the apidocs
@app.route('/')
def index():
    return redirect('/apidocs')

# If you have additional modules that contain your API endpoints, for instance
# using Blueprints, then ensure that you use relative imports, e.g.:
# from .mymodule import myblueprint

@app.route("/home")
def home():
  bukets = osclient.get_buckets()
  print(bukets)
  return render_template("index.html", buckets=bukets, msg="Hello, the response from the server will be displayed here!")

@app.route('/upload', methods = ['GET', 'POST'])
@track_requests
def upload_file():
   """Upload file
    Upload a file to Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns home page html.
    """
   if request.method == 'POST':
      f = request.files['file']
      print(request.form)
      bucket = request.form["buket"]
      # save to object storage
      resp = osclient.put_file(bucket, f.filename, f.read());
      bukets = osclient.get_buckets()
      return render_template("index.html", buckets=bukets, msg=resp)

@app.route('/getobject', methods = ['GET'])
@track_requests
def get_object():
   """Get file
    Get a file from Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns html with file contents for text and image files.
    """
   # clear the cache
   if path.exists("./userapp/image"):
       os.remove("./userapp/image");

   if request.method == 'GET':
      print(request.args)
      bucket = request.args["buket"]
      name =  request.args["filename"]
      contents = osclient.get_file(bucket, name)
      mime = mimetypes.guess_type(name)[0]
      txtcontent = "";
   if "text" in mime:
      txtcontent=contents.read().decode('utf-8')
      return render_template("display.html", filename=name, textcontent=txtcontent)

   if "image" in mime:
     f = open("./userapp/image", "wb+");
     f.write(contents.read());
     f.close()
     return render_template("display.html", filename=name, textcontent=txtcontent)



@app.route('/delobject', methods = ['GET'])
@track_requests
def delete_object():
   """Delete file
    Delete a file from Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns home page html.
    """
   if request.method == 'GET':
      print(request.args)
      bucket = request.args["buket"]
      name =  request.args["filename"]
      resp = osclient.delete_item(bucket, name)
      bukets = osclient.get_buckets()
      return render_template("index.html", buckets=bukets, msg=resp)

@app.route('/listcontents', methods = ['GET'])
@track_requests
def list_contents():
   """List bucket contents
    List bucket contents in Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns home page html with bucket contents.
   """
   bucketname = request.args.get("bucketname");
   bukets = osclient.get_buckets()
   files = osclient.get_files(bucketname);
   resp = "Contents of bucket " +bucketname+":"
   for file in files:
     resp = resp +" " + file.key + ", "
   return render_template("index.html", buckets=bukets, msg=resp)


@app.route('/createbucket', methods = ['GET'])
@track_requests
def create_bucket():
   """Create bucket
    Create a bucket in Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns home page html.
   """
   bucketname = request.args.get("bucketname");
   print("creating bucket: " + bucketname);
   resp = osclient.create_bucket(bucketname);
   bukets = osclient.get_buckets()
   return render_template("index.html", buckets=bukets, msg=resp)

@app.route('/deletebucket', methods = ['GET'])
@track_requests
def delete_bucket():
   """Delete bucket
    Delete a bucket to Cloud Object Storage
    ---
    responses:
      200:
        description: A successful reply. Returns home page html.
    """
   bucketname = request.args.get("bucketname");
   print("deleting bucket: " + bucketname);
   resp = osclient.delete_bucket(bucketname);
   bukets = osclient.get_buckets()
   return render_template("index.html", buckets=bukets, msg=resp)


# Utility API. The below APIs are used to send back the image file retrieved from object storage
# for display on the browser
@app.route('/getimage', methods = ['GET'])
@track_requests
def getimage():
  if path.exists("./userapp/image"):
      f = open("./userapp/image", "rb");
      print(f)
      print("image found!")
      contents = f.read()
      return contents;
  else:
      print("no image found!")
      return "";
