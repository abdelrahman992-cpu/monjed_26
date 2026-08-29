from database.connection import get_database


def get_reports_collection():

    db = get_database()

    return db["community_reports"]



def create_report(data):

    collection = get_reports_collection()

    collection.insert_one(data)

    return data["report_id"]



def get_report(report_id):

    collection = get_reports_collection()

    return collection.find_one(
        {
            "report_id": report_id
        }
    )



def get_all_reports():

    collection = get_reports_collection()

    return list(
        collection.find()
    )



def update_report(
    report_id,
    data
):

    collection = get_reports_collection()

    result = collection.update_one(
        {
            "report_id": report_id
        },
        {
            "$set": data
        }
    )

    return result.modified_count



def delete_report(report_id):

    collection = get_reports_collection()

    result = collection.delete_one(
        {
            "report_id": report_id
        }
    )

    return result.deleted_count