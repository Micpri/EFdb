# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 09:22:15 2023

@author: michael4167
"""
from flask import Flask, render_template, send_from_directory, request, send_file, url_for, redirect
from mongoCRUDservice import MongoCRUD
from helpFunctions import *



#######################################################################################
# init
#######################################################################################

app_host = "0.0.0.0"
app_port = 5000
mongo_host = "127.0.0.1"
mongo_port = 27017

# Initialise mongoCRUDservice and read in database
MCRUD = MongoCRUD(host=mongo_host, port=mongo_port)

db = MCRUD.ReadDatabase("EFdb")

# Initialise Flask app
# Html templates and static files
app = Flask(
    __name__,
    template_folder=os.path.abspath('./build/html/'),
    static_folder=os.path.abspath('./build/static/'), # sets the folder on the filesystem
    static_url_path=os.path.abspath('static/'), #sets the path used within the URL
) 

app.config['Server_Name'] = "{}:{}".format(mongo_host, app_port)
app.config['host'] = app_host
app.config['SECRET_KEY'] = "<key>"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT']= False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = app.static_folder
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024


#######################################################################################
# Database CRUD Service
#######################################################################################

#CREATE COLLECTION
@app.route('/CreateCollection/<collection_name>', methods = ['POST','GET'])
def CreateCollection(collection_name):

    print("Created", collection_name)
    collection = MCRUD.CreateCollection(db, collection_name)
    return "{} collection created.".format(collection_name)

#READ COLLECTION
@app.route('/ReadCollection/', methods = ['POST','GET'])
def ReadCollection():
    
    # Get name of collection where data is stored in db
    coll_name_path = request.json.get('coll_name_path')

    # Decide if this is the end of the tree or still on the branch
    #######################
    
    # Read database
    db_data = MCRUD.Read(db, coll_name_path, query={})
    if len(db_data) > 0:
        # Convert to JSON
        db_data_j = json_util.dumps(db_data)
        # Convert to pd.df (dtype false to keep all as strings)
        db_data_df = pd.read_json(db_data_j, dtype=False)
        # Here it is writing the columns which dont exist in one entry into the other entry.
        # This means that when the comparison is done, the update now contains this new entry
        # Which the old version didn't before.

         # _id firstcomes out of MCRUD.Read() as "{'$oid':'x'}". Convert to 'x'
        db_data_df["_id"]=db_data_df["_id"].apply(idDict2StrVal)
        # Sort order of columns 
        # important to ensure _id is last in html table
        db_data_df = CorrectDFColsOrder(db_data_df) 
        # Convert to HTML
        db_data_html = db_data_df.to_html(index=False)
        # Edit html before sending back:
        # Insert delete column and button in
        deletebuttonHTML = '<td><button type="button" class="RemoveRowButton" title="Remove this row">X</button></td>'
        db_data_html = db_data_html.replace(
         '<tr style="text-align: right;">',
         '<tr style="text-align: right;"><th>Delete</th>'
         )
        db_data_html = db_data_html.replace("<tr>", "<tr>"+deletebuttonHTML)
         # Insert col_name_path and id into html so js can know it
        db_data_html = db_data_html.replace(
            '<table border="1" class="dataframe">', 
            '<table border="1" class="dataframe" id="main_table" coll_name_path={}>'.format(
                coll_name_path
            )
        )
        # Put <a> tags round id'd weblinks. Matches https://
        db_data_html = str2htmlLinks(db_data_html, web_link_regex)
        # Put <a> tags around documents to link to file server 
        db_data_html = str2htmlLinks(db_data_html, file_extension_regex, path_prepend="/resources/files/")
    else:
        # Still need to pass a table with coll_name_path and class="dataframe" for js functions to work
        db_data_html = '<table class="dataframe" coll_name_path={}><tr><th>No data in {}</th></tr></table>'.format(
            coll_name_path,
            coll_name_path
        )

    return db_data_html


#DELETE COLLECTION
@app.route('/DeleteCollection/<collection_name>', methods = ['POST','GET'])
def DeleteCollection(collection_name):

    print("DELETE COLLECTION:", collection_name)
    ans = db.drop_collection(collection_name)
    return "{} Collection Deleted".format(collection_name)


#CREATE ENTRIES
@app.route('/CreateEntry/<collection_name>', methods = ['POST','GET'])
def CreateEntry(collection_name):

    print("/CreateEntry/<{}>".format(collection_name))
    collection = MCRUD.CreateCollection(db, collection_name)
    if request.method == "POST":
        # Take byte string from AJAX post andd ecode to UTF-8
        # Decode html but want to keep äöå encoding
        # Convert to df from html
        data_string = request.data.decode('utf-8')  
        data_df = pd.read_html(data_string)[0][1:]
        # A mixture of HF.CorrectDFColsOrder() and 
        # main.js.EditTableButtonClick() ensure _id cannot be edited by the user.
        # Therefore all _ids coming from the front end should be good_ids.
        # However if new rows are added, this column is empty. 
        # entries with good ids are removed leaving only the new entries
        good_ids, bad_ids = CheckIdsValid(data_df["_id"])
        #print("CreateEntry good_ids:", good_ids)
        #print("CreateEntry bad_ids:", bad_ids)
        if len(bad_ids) > 0:
            data_df = data_df[data_df['_id'].isin(bad_ids)]
            # Get rid of _id column so writing it sets a new one
            data_df.drop("_id", axis=1, inplace=True)
            new_entries = dataDF2Json(data_df)
            # Chose CRUD route
            if len(new_entries) == 1:
                MCRUD.CreateEntry(collection, new_entries[0])
                return_statement = "Created entry"
            else:
                MCRUD.CreateEntries(collection, new_entries)
                return_statement = "Created entries"
        else:
            return_statement = "No entries to create"  

    return return_statement


#UPDATE ENTRIES
@app.route('/UpdateEntry/<collection_name>', methods = ['POST','GET'])
def UpdateEntry(collection_name):

    print("/UpdateEntry/<{}>".format(collection_name))

    if request.method == "POST":
        # Take byte string from AJAX post andd ecode to UTF-8
        # Decode html but want to keep äöå encoding
        # Convert to df from html
        data_string = request.data.decode('utf-8')  
        data_df = HTMLtable2DF(data_string)

        # A mixture of HF.CorrectDFColsOrder() and 
        # main.js.EditTableButtonClick() ensure _id cannot be edited by the user.
        # Therefore all _ids coming from the front end should be good_ids.
        # However if new rows are added, this column is empty. 
        # Remove these bad ids from the data and update. If there are new columns
        # without IDs these are handled by the CreateEntry route.
        good_ids, bad_ids = CheckIdsValid(data_df["_id"])
        #print("UpdateEntry good_ids", good_ids)
        #print("UpdateEntry bad_ids", bad_ids)
        # First check to see if any need updating. If not then pass.
        if len(good_ids) > 0:

            # Load the data in
            data_df = data_df[data_df['_id'].isin(good_ids)]
            updates = dataDF2Json(data_df)
        
            # For each object in the updates, for each kv pair of the object
            # Look for a change in value and throw away all other kv pairs
            # Loop over all dictionaries
            # updates_refined = []
            for update in updates:
                update["_id"] = ObjectId(update["_id"])
                old_entry = MCRUD.Read(db, collection_name, query={"_id":update["_id"]})[0]
                update_refined = refineUpdates(old_entry, update)
                # updates_refined.append(update_refined)
                #print("old_entry", old_entry)
                #print("update_refined", update_refined)
                # Only using Update entry for now
                if not len(update_refined) == 0:
                    MCRUD.UpdateEntry(
                        collection=db[collection_name],
                        query={"_id":update["_id"]},
                        updates=update_refined
                    )
                return_statement = "Updated entries"
        else:
            return_statement = "No entries to update"  
    return return_statement


#DELETE ENTRIES
@app.route('/DeleteEntry/<collection_name>', methods = ['POST','GET'])
def DeleteEntry(collection_name):
    print("/DeleteEntry/<{}>".format(collection_name))

    if request.method == "POST":
        # Take byte string from AJAX post andd ecode to UTF-8
        # Decode html but want to keep äöå encoding
        # Convert to list from html
        id_list = json.loads(request.data.decode('utf-8')  )
        id_list = [ObjectId(id) for id in id_list]
        if len(id_list) == 1:
            MCRUD.DeleteEntry(db[collection_name], id_list[0])
            return_statement = "Entry deleted"
        else:          
            MCRUD.DeleteEntries(db[collection_name], {"_id": {"$in": id_list}})
            return_statement = "Entries deleted"

    return return_statement

# These do not yet exist.
#CREATE ENTRIES - Wrapped in CREATE ENTRY
#DELETE ENTRIES - Wrapped in DELETE ENTRY
# #UPDATE ENTRIES - Needed for Add field button?


#######################################################################################
# VIEWS
#######################################################################################

@app.route("/home/")
@app.route("/")
def home():
    """Homepage with db dir nav"""
    tree, coll_names_paths = PopulateDBdirNav(db)
    return render_template('index.html', tree=tree, coll_names_paths=coll_names_paths)


@app.route('/files/')
def files():
    """List all files (attachments to db entries) in the resources/files static/folder/"""
    filenames = os.listdir("{}/resources/files/".format(app.static_folder))
    return render_template('files.html', files=filenames)


@app.route('/templates/')
def templates():
    """List all files (attachments to db entries) in the resources/templates static/folder/"""
    filenames = os.listdir("{}/resources/templates/".format(app.static_folder))
    return render_template('templates.html', files=filenames)

@app.route("/about/")
def about():
    return render_template('about.html')

@app.route("/contact/")
def contact():
    return render_template('contact.html')


#######################################################################################
# FILE SERVER
#######################################################################################


# CREATE 
@app.route('/FilesUploader/', methods = ['GET', 'POST'])
def ResourceUploader():

    if request.method == 'POST':
        # List all files 
        files = request.files.getlist('ResourceUploadInput')
        for f in files:
            url = "{}/resources/files/{}".format(app.static_folder, f.filename)
            upload2disk(f, url)

    return redirect(url_for('files'))


@app.route('/TemplateUploader/', methods = ['GET', 'POST'])
def TemplateUploader():

    if request.method == 'POST':

        # List all files 
        files = request.files.getlist('TemplateUploadInput')
        # foreach file upload to dist
        for f in files:
            url = "{}/resources/templates/{}".format(app.static_folder, f.filename)
            upload2disk(f, url)

    return redirect(url_for('templates', _external=True, _scheme='http', _host='127.0.0.1'))


@app.route('/CollectionUploader/', methods = ['GET', 'POST'])
def CollectionUploader():
   
    def entriesInCollection(db, collection_name, url):
        # Read the uploaded file now on the server
        data_df = pd.read_csv(url)
        # Convert to JSON
        updates = dataDF2Json(data_df)

        collection = MCRUD.CreateCollection(db, collection_name)
        MCRUD.CreateEntries(collection, updates)

        return "Collection uploaded"
        
    url = "{}/resources/files/upload_file.csv".format(app.static_folder)
    file = request.files['CollectionUploadInput']

    new_collection_name = request.form.get("NewCollectionName")
    new_collection_name = MakeCollNameNice(new_collection_name)
    if len(new_collection_name) <1:
        new_collection_name = "X_No_Name"
      
    print("new_collection_name: ", new_collection_name)

    if request.method == 'POST':
        upload2disk(file, url)
        #CreateCollection(new_collection_name)
        entriesInCollection(db, new_collection_name, url)

    # Return the main view
    return redirect(url_for('home', _external=True, _scheme='http', _host='127.0.0.1'))


# READ
@app.route('/resources/<path:filename>')
def getDocument(filename):
    """Return a resource, file or template"""
    return send_from_directory(
        directory="{}/resources/".format(app.static_folder),
        path=filename,
        max_age=0
    )

# UPDATE 


# DELETE
@app.route('/DeleteResource/', methods = ['POST','GET'])
def DeleteResource():
    """Delete a Resource"""
    if request.method == 'POST':
        file_name = request.form.get('file')
        extension = request.form.get('extension').replace("/", "")
        file_path = os.path.join("{}/resources/{}/".format(app.static_folder, extension), file_name)
        os.remove(file_path)
        
    return redirect(url_for(extension, _external=True, _scheme='http', _host='127.0.0.1'))



@app.route('/ExportTable/', methods = ['POST','GET'])
def ExportTable():

    # Take byte string from AJAX post and encode to UTF-8
    data_string = request.data.decode('utf-8')    
    # Decode html but want to keep äöå encoding
    # Convert to df from html
    data_df = pd.read_html(data_string)[0][1:]
    
    # Write CSV to static folder
    filename='exported_table.csv'
    file_path='/resources/files/{}'.format(filename)
    save_path="{}{}".format(app.static_folder, file_path)

    data_df.drop("Delete", axis=1, inplace=True)
    data_df.to_csv(save_path, index=False, encoding="utf-8-sig")
    html_link = '<a id="CSVExportTable" href={}>{}</a>'.format(file_path, filename)
    # Returns html which is injected into the DOM providing a download link
    return html_link


#######################################################################################
# JS & CSS SERVER
#######################################################################################

## JS must be served
@app.route('/app.min.js')
def main_js():
    return send_from_directory(app.static_folder, "app.min.js")


@app.route('/app.min.js.map')
def main_js_map():
    return send_from_directory(app.static_folder, "app.min.js.map")


@app.route('/main.css')
def main_css():
    return send_from_directory(app.static_folder, "main.css")


@app.route("/test2/")
def template_test():
    return render_template('template_test.html', my_string="Wheeeee! here !", my_list=[0,1,2,3,4,5])


#######################################################################################
# RUN
#######################################################################################
if __name__ == '__main__':
    app.run(host=app_host, port=app_port, debug=True)
