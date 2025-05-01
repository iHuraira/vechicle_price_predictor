def insert_document(collection, document):
    """Insert a single document into a collection."""
    return collection.insert_one(document)

def insert_many_documents(collection, documents):
    """Insert multiple documents."""
    return collection.insert_many(documents)

def find_one_document(collection, query):
    """Find a single document matching query."""
    return collection.find_one(query)

def find_documents(collection, query={}):
    """Find all documents matching query (empty query = all)."""
    return list(collection.find(query))

def update_document(collection, query, update_data):
    """Update a single document."""
    return collection.update_one(query, {"$set": update_data})

def delete_document(collection, query):
    """Delete a single document."""
    return collection.delete_one(query)
