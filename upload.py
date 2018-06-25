import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import json
import os, shutil
import pickle


def upload():
    cred = credentials.Certificate("heartbeatanalysis-keys.json")
    app = firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://heartbeatanalysis.firebaseio.com/',
        'storageBucket': 'heartbeatanalysis.appspot.com'

    })

    dbref = db.reference("users")

    bucket = storage.bucket()

    if not os.path.exists("raw/alldata.json"):
        print("alldata.json not founded! please download data first!")
        input("press Enter to exit!")
        exit()
    datafile = open("raw/alldata.json", "rb")
    data = pickle.load(datafile)
    datafile.close()

    for userId in data.keys():
        userdata = data[userId]
        for recordId in userdata:
            record = userdata[recordId]
            if record is not None:
                name = record["name"]
                processed = record["processed"]
                time = record["time"]

                directory = "/" + userId + "/" + recordId
                processedfilename = "/processed_" + str(name).replace("/", "")
                cloudprocessfilepath = "users" + directory + processedfilename
                localprocessfilepath = "raw" + directory + processedfilename
                infofilepath = "raw" + directory + "/info.json"
                if os.path.exists(localprocessfilepath):
                    # upload processed file
                    blob = bucket.blob(cloudprocessfilepath)
                    blob.upload_from_filename(localprocessfilepath)

                    print(processedfilename + " uploaded!")
                    # update local info
                    infofile = open(infofilepath, "rb");
                    info = pickle.load(infofile)
                    infofile.close()
                    info["processed"] = True
                    infofile = open(infofilepath, "wb");
                    pickle.dump(info, infofile, pickle.HIGHEST_PROTOCOL)
                    infofile.close()
                    # update server info
                    print("update server info")
                    dbref.child(userId).child(str(recordId)).set(info)
                    # move files from raw to processed!
                    print("Moving process files to processed folder")
                    src = "raw" + directory
                    dest = "processed" + directory + "/"
                    if not os.path.exists(dest):
                        os.makedirs(dest)
                    files = os.listdir(src)

                    for file in files:
                        shutil.move(src + "/" + file, dest)

                    # delete empty folders
                    try:
                        os.rmdir(src)
                    except OSError as e:
                        print(e)



upload()
print("All done!")
input("press Enter to exit")
