# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 10:52:46 2023

@author: michael4167
"""

from bson import errors as bsonErrors
from bson.objectid import ObjectId
from bson import json_util 
from io import BytesIO
from pprint import pprint
import numpy as np
import pandas as pd
import datetime as dt
import json, re, os, html , random, time
import datetime as dt
from bs4 import BeautifulSoup

pd.set_option('display.max_colwidth', None)
#######################################################################################
# Help variables
#######################################################################################


file_extension_regex = r'\b\w+\.(?:txt|docx|jpg|zip|mp3|mp4|xlsx|pdf|png|doc|xls|ppt|jpeg|gif|bmp|avi|wav|csv|rtf|html|xml|json|css|js|php|cpp|py|java|sql|exe|dll|iso|rar|7z|tar|gz|apk|bin|bak|pptx|odt|ods|odp|odf|swf|md|log|ini|cfg|ts|svg|ico|woff|woff2|ttf|eot|psd|ai|indd|dwg|cdr|eps|raw|ico|flv|wmv|mov|3gp|aac|wma|flac|ogg|mid|midi|torrent)\b'
web_link_regex = r'(https?:\/\/[^\s]+\S+?\.[A-Za-z0-9]+|\bwww\.[^\s]+\S+?\.[A-Za-z0-9]+)'


#######################################################################################
# Help Functions
#######################################################################################
def key_tidy(obj):

    """
    Used to replace JSON specification unicode characters
    back to normal before updating entry
    """
    replacers=[
        ['\xa0', ' '],
        ['.', ','],
        [' ', '_'],
        ['\t', ''] 
    ]
    decoded_obj = {}
    for key, value in obj.items():
        # Replace non-breaking space character with a regular space
        if isinstance(key, str):
            for replacer in replacers:
                key = key.replace(replacer[0], replacer[1]).strip()
        decoded_obj[key] = value
    return decoded_obj


def value_tidy(obj):

    """
    Convert all values to strings to preserve sigfig etc.
    """
    decoded_obj = {}
    for key, value in obj.items():
        decoded_obj[key] = str(value)
    return decoded_obj


def tree_find(e, t):
 
    """
    https://stackoverflow.com/questions/75236722/flask-how-to-make-a-tree-in-jinja2-html
    Goes through the fiel structure 
    """
    if e in t:
        return t
    for v in t.values():
        r = tree_find(e, v)
        if r:
            return r
    return None

def collection_names_2_dict(list_of_lists):

    """
    Mongodb has collections of entries
    To simulate a dir structure we take our flat collections e.g.
    Mode_of_Transport
    Mode_of_Transport__Air
    Mode_of_Transport__Rail
    Mode_of_Transport__Road
    Mode_of_Transport__Road__Bus
    and represent them as dir structure:
    Mode_of_Transport
    ----Air
    ----Rail
    ----Road
    --------Bus
    """
    d = {}
    # For each line in the list of lists
    for line in sorted(list_of_lists):
        # Split the line by the double underscore (Convention)
        entries = line.split(".")
        # If there is no double underscore,
        # create the key with an empty list val
        if len(entries) == 1:
                k, v = entries[0], []
                d[k] = v
        else:
        # Otherwise, for all entries in the list
        # apart from the last, take the key and value
        # as the adjacent elements
            for i in range(len(entries)-1):
                k, v = entries[i], entries[i+1]
                # If the new key is not in the dict add it
                # with the value as an array
                if k not in d.keys():
                    d[k] = [v]
                else:
                # If they key is in the dict, check to see 
                # if the value is there also. If not, append
                # it to the value list
                    if v not in d[k]:
                        d[k].append(v)

    return d

def collection_paths(ls, sep="."):

    """
    Takes list of collections where <sep>
    denotes branch to new node.
    returns list with all combons of / included
    """
    d = []

    for item in ls:
        split = item.split(sep)
        # Put the first chunk in the list
        d.append(split[0])
        # loop over however many chunks are left
        for i in range(len(split)):
            # piece them back together seqentially
            new_item = sep.join(split[0:i])
            # Add to list 
            if len(new_item) > 0:
                d.append(new_item)

    # Clean up
    d = np.unique(list(np.unique(d)) + ls)

    return sorted(d)


def PopulateDBdirNav(db):
    
    """
    Passes the correct structure of the dir tree to the html
    template
    """
    coll_names = sorted(db.list_collection_names())
    coll_names_paths = collection_paths(coll_names)
    coll_names_d = collection_names_2_dict(coll_names)

    tree = {}
    for k,v in coll_names_d.items():
        n = tree_find(k, tree)
        (tree if not n else n)[k] = {e:{} for e in v}

    return tree, coll_names_paths



def str2htmlLinks(HTMLstring, regex_query, path_prepend=""):
    
    """
    Checks a string to see if it is a URL
    returns html of link.
    HTML string - string of html which needs <a> tags
    regex_query - regex to identify string to replace
    path - for the href, if needs prepending
    """
    # Find all strings that match regex
    strs = re.findall(regex_query, HTMLstring)  
    # rewrite as <a> tags
    new_strs = [
        '<a href="{0:}{1:}">{2:}</a>'.format(path_prepend, string, string) for string in strs]

    # Get rid of repeats and put in dictionary
    strs = np.unique(strs)
    new_strs = np.unique(new_strs)
    replacers = { k:v for k,v in list(zip(strs, new_strs))}
    
    # replace urls with new urls in html string
    for k,v in replacers.items():
        HTMLstring = HTMLstring.replace(k, v)
        
    return HTMLstring


def CorrectDFColsOrder(df):

    """
    returns a df with reordered columns
    for consistency.
    df. pandas dataframe
    returns df.
    Really need this function?
    """
    # Extract columns a list
    columns = list(df.columns)
    
    # These start and end columns MUST stay here. 
    # EditTableButtonClick of main js ensures the last 3 columns cannot be modified
    start_cols = ["Delete"]
    end_cols = ["Modified","Created","_id"]
    
    # First remove these columns if they exist
    for col in start_cols + end_cols:
        try:
            columns.remove(col)
        except ValueError:
            pass

    # Now take those columns and postend the stated end_cols
    new_col_order = columns + end_cols

    return df[new_col_order]


def idDict2StrVal(id):
    if '$oid' in id:
        id = json.loads(str(id).replace("'",'"'))['$oid']
    return id


def refineUpdates(old_entry, update):

    """
    looks at common keys between entry being altered 
    and the updated provided.
    old_entry = returned from MCRUD.Read() (single entry not list)
    updates = dict e.g. from json.loads(json)
    """
    preseved_keys = ["Modified","Created","_id"] # Cannot be deleted/edited
    matching_keys = list(set(update.keys()).intersection(set(old_entry.keys())))
    new_keys = list(set(update.keys()).difference(set(old_entry.keys())))
    # If new keys (i.e. fields) have been added, preseve them first
    update_refined = {key:update[key] for key in new_keys}
    update_refined = value_tidy(key_tidy(update_refined))

    for key in matching_keys:
        # Do nothing if key is preserved
        if key in preseved_keys:
            pass
        # If the new value is not the same as the old value
        # put it in the returning dict
        elif old_entry[key] != update[key]:
            update_refined[key] = update[key]
        else:
            pass

    #Finally get rid of the delete column
    del update_refined["Delete"]

    return update_refined


def dataDF2Json(df):

    def composite_object_hook(dct):
        dct = key_tidy(dct)
        dct = value_tidy(dct)
        return dct

    df_json = df.to_json(orient="records")
    json_dat = json.loads(df_json, object_hook=composite_object_hook)
    return json_dat


def CheckIdsValid(list_of_ids):

    """
    Takes a list of strings of ids
    attempts to convert to bson.Objectid()
    Returns where it works
    ids - list of strings
    Returns where it fails
    bad_ids = list of strings
    """
    good_ids = []
    bad_ids=[]

    for id in list_of_ids:
        try:
            objected = ObjectId(id)
            good_ids.append(id)
        except Exception as e:
            print("Invalid Id >>{}<< - {}".format(id, e))
            bad_ids.append(id)  
    
    return good_ids, bad_ids


def upload2disk(file, url):
    file.save(url)
    return 'file uploaded successfully to {}'.format(url)


def MakeCollNameNice(string):
    nice_string = string.replace(" ","_").replace("/",".")
    return nice_string


def HTMLtable2DF(data_string):
    soup = BeautifulSoup(data_string, 'html.parser')
    table = soup.find('table')

    # Extract column headers from the table
    headers = [th.text for th in table.find_all('th')]

    # Extract data rows from the table
    data = []
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        if cells:
            data.append([cell.text for cell in cells])

    # Create a pandas DataFrame
    data_df = pd.DataFrame(data, columns=headers)
    return data_df