from database.connection import get_database



def get_volunteer_collection():

    db = get_database()

    return db["volunteers"]



def create_volunteer(data):

    collection = get_volunteer_collection()

    collection.insert_one(data)

    return data["volunteer_id"]



def get_volunteer(volunteer_id):

    collection = get_volunteer_collection()

    return collection.find_one(
        {
            "volunteer_id": volunteer_id
        }
    )



def get_all_volunteers():

    collection = get_volunteer_collection()

    return list(
        collection.find()
    )



def update_volunteer(
    volunteer_id,
    data
):

    collection = get_volunteer_collection()

    result = collection.update_one(
        {
            "volunteer_id": volunteer_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_volunteer(volunteer_id):

    collection = get_volunteer_collection()

    result = collection.delete_one(
        {
            "volunteer_id": volunteer_id
        }
    )

    return result.deleted_count