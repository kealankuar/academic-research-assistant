# src/data_access.py

from db import get_session
from models import Topic, Document

def get_topic_by_name(session, topic_name):
    """
    Retrieve a Topic by its name.
    Returns the Topic instance if found, otherwise None.
    """
    return session.query(Topic).filter(Topic.name == topic_name).first()

def add_topic(session, topic_name):
    """
    Add a new topic to the database if it doesn't already exist.
    Returns the Topic instance.
    """
    topic = get_topic_by_name(session, topic_name)
    if topic is None:
        topic = Topic(name=topic_name, document_count=0)
        session.add(topic)
        session.commit()  # Commit to assign an ID
        session.refresh(topic)  # Refresh to load the new data
    return topic

def add_document(session, topic_name, title, text, pdf_link, authors):
    """
    Add a new document under the given topic.
    If the topic doesn't exist, it is created.
    If a document with the same title exists, it is not inserted again.
    The topic's document_count is updated accordingly.
    
    Returns the Document instance.
    """
    # Ensure the topic exists
    topic = add_topic(session, topic_name)
    
    # Check for duplicate documents by title
    existing_doc = session.query(Document).filter(Document.title == title).first()
    if existing_doc:
        return existing_doc  # Return the existing document if found
    
    # Create the new document
    new_doc = Document(
        topic_id=topic.id,
        title=title,
        text=text,
        pdf_link=pdf_link,
        authors=authors
    )
    session.add(new_doc)
    
    # Update the document count for the topic
    topic.document_count += 1
    
    session.commit()  # Save both the topic update and the new document
    session.refresh(new_doc)  # Refresh the new_doc instance to get its ID etc.
    return new_doc

def get_documents_by_topic(session, topic_name):
    """
    Retrieve all documents associated with the given topic name.
    Returns a list of Document instances.
    """
    topic = get_topic_by_name(session, topic_name)
    if topic:
        return session.query(Document).filter(Document.topic_id == topic.id).all()
    return []

# Testing the data access functions:
if __name__ == "__main__":
    session = get_session()
    
    # Example: Adding a document to "machine learning" topic
    test_doc = add_document(
        session,
        topic_name="machine learning",
        title="A New Perspective on Machine Learning",
        text="This paper presents innovative methodologies in machine learning, including ...",
        pdf_link="http://arxiv.org/pdf/example.pdf",
        authors="John Doe, Jane Doe"
    )
    print("Inserted Document:", test_doc)
    
    # Retrieve and print all documents under "machine learning"
    docs = get_documents_by_topic(session, "machine learning")
    print(f"\nDocuments under 'machine learning':")
    for doc in docs:
        print(doc)
    
    session.close()
