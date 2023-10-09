# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 15:24:32 2022

@author: michael4167
"""
from pymongo import MongoClient
from helpFunctions import *


class MongoCRUD(object):

    """
    Interact with mongo database.
    """

    def __init__(self, host='localhost', port=27017):
        self.client = MongoClient(host, port)

        return None

    def __str__(self):
        return str(self.client)

    def __repr__(self):
        return str(self.client)


    #################### CREATE ####################
    def CreateDatabase(self, database_name):
        return self.client[database_name]


    def ReadDatabase(self, database_name):
        return self.client[database_name]


    def CreateCollection(self, db, collection_name):

        """
        """

        collection_name = MakeCollNameNice(collection_name)
        if collection_name not in db.list_collection_names():
             collection = db.create_collection(name=collection_name)
        else:
            print("collection {} already exists".format(collection_name))
            collection = db[collection_name]

        return collection


    def CreateEntry(self, collection, dictionary):

        """Create an entry."""
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # Modify dict sent through
        dictionary["Created"] = now
        dictionary["Modified"] = ""
        dictionary["Delete"] = "write over or create key"
        del dictionary["Delete"]
        # Convert vals to strings
        insert_dictionary = value_tidy(key_tidy(dictionary))
        collection.insert_one(key_tidy(insert_dictionary))
        print("______________________________________________")
        print("              CreateEntry                     ")
        print("           Added new entries to DB            ")
        print("______________________________________________")
        return "Entry Created {}.".format(now)


    def CreateEntries(self, collection, ls):

        """CreateEntries."""

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        in_ls = []
        for dictionary in ls:
            dictionary["Created"] = now
            dictionary["Modified"] = ""
            dictionary["Delete"] = "write over or create key"
            del dictionary["Delete"]
            insert_dictionary = value_tidy(key_tidy(dictionary))
            print("obj: ", dictionary)
            in_ls.append(insert_dictionary)
        collection.insert_many(in_ls)
        print("______________________________________________")
        print("              CreateEntries                   ")
        print("           Added {} new entries to DB         ".format(len(in_ls)))
        print("______________________________________________")
        return "Entries Created {}.".format(now)


    #################### READ ####################
    def Read(self, db, collection_name, query={}):

        """Reads collections and entries. one and many"""

        collection_name = MakeCollNameNice(collection_name)
        collection=db[collection_name]
        cursor = collection.find(query)
        documents = []
        #try:
        for document in cursor:
            documents.append(document)#, object_hook=custom_decoder))
            #documents.append(json.loads(document, object_hook=custom_decoder))
       # except TypeError:
            #print("No items found.")

        return documents


    #################### UPDATE ####################
    def UpdateEntry(self, collection, query, updates):

        """Update an entry."""

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        updates["Modified"] = now
        updates["Delete"] = "write over or create key"
        del updates["Delete"]
        print("______________________________________________")
        print("              UpdateEntry                     ")
        print(query)
        updates = value_tidy(key_tidy(updates))
        print(updates)
        collection.update_one(query, {'$set': updates})
        print("______________________________________________")
        return "Entry updated {}.".format(now)


    def UpdateEntries(self, collection, query={}, updates={}):

        """Update entries."""

        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        updates["Modified"] = now
        updates["Delete"] = "write over or create key"
        del updates["Delete"]
        print("______________________________________________")
        print("              UpdateEntries                   ")
        print(query)
        updates = value_tidy(key_tidy(updates))
        print(updates)
        collection.update_many(query, {'$set': updates})
        print("______________________________________________")
        return "Entries updated {}.".format(now)


    #################### Delete ####################
    def DeleteEntry(self, collection, id):
        """DeleteEntry."""
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        collection.delete_one({ "_id" : id})
        return "Entry deleted {}.".format(now)


    def DeleteEntries(self, collection, query={}):
        """DeleteEntries."""
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        collection.delete_many(query)
        return "Entries deleted {}.".format(now)
    

    def DeleteCollection(self, db, collection_name):
        return db.drop_collection(collection_name)


    def DeleteDatabase(self, database_name):
        return self.client.drop_database(database_name)