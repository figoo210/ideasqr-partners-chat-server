from sqlalchemy.orm import joinedload


def fetch_data_with_relations(db, model, relations=None):
    query = db.query(model)

    if relations:
        # Use joinedload to eager load the specified relations
        query = query.options(*[joinedload(relation) for relation in relations])

    result = query.all()

    # Convert the SQLAlchemy objects to dictionaries
    data = [item.as_dict() for item in result]

    print("################################################: ", data)
    return data
