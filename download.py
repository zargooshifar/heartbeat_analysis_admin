import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import json
import os
import pickle


def download():
    print("please wait!\n")
    cred = credentials.Certificate("heartbeatanalysis-keys.json")
    app = firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://heartbeatanalysis.firebaseio.com/',
        'storageBucket': 'heartbeatanalysis.appspot.com'

    })
    bucket = storage.bucket()


    ref = db.reference("users")
    data = ref.get()
    if (data == None):
        print("there is no data!")
        exit()
    if not os.path.exists("raw"):
        os.makedirs("raw")
    datafile = open("raw/alldata.json", "wb")
    pickle.dump(data, datafile, pickle.HIGHEST_PROTOCOL)
    datafile.close()

    print(str(len(data)) + " users founded")

    for userId in data.keys():
        userdata = data[userId]
        print("\nUser Id: " + userId)
        print(str(len(userdata)) + " record found for this user! wait till download records, i only download not processed records!")
        for recordId in userdata:
            record = userdata[recordId]
            if record is not None:
                name = record["name"]
                processed = record["processed"]
                time = record["time"]

                if (not processed):
                    directory = "raw/" + userId + "/" + recordId
                    recordfilepath = directory + name
                    recordinfopath = directory + "/info.json"
                    cloudfilepath = "users/" + userId + "/" + recordId + name
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    if not os.path.exists(recordfilepath):
                        print(cloudfilepath)
                        blob = bucket.blob(cloudfilepath)
                        file = open(recordfilepath, "wb")
                        blob.download_to_file(file)
                        file.close()

                    if not os.path.exists(recordinfopath):
                        infofile = open(recordinfopath, "wb")
                        pickle.dump(record, infofile, pickle.HIGHEST_PROTOCOL)
                        infofile.close()

    print("\n\nAll Done!")
    input("press Enter to exit")


download()
