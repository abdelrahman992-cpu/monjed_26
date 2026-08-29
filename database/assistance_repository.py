from database.connection import get_database


def get_assistance_requests_collection():

    db = get_database()

    return db["assistance_requests"]



def create_assistance_request(data):

    collection = get_assistance_requests_collection()

    collection.insert_one(data)

    return data["request_id"]



def get_assistance_request(request_id):

    collection = get_assistance_requests_collection()

    return collection.find_one(
        {
            "request_id": request_id
        }
    )



def get_all_assistance_requests():

    collection = get_assistance_requests_collection()

    return list(
        collection.find()
    )



def update_assistance_request(
    request_id,
    data
):

    collection = get_assistance_requests_collection()

    result = collection.update_one(
        {
            "request_id": request_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_assistance_request(request_id):

    collection = get_assistance_requests_collection()

    result = collection.delete_one(
        {
            "request_id": request_id
        }
    )

    return result.deleted_count