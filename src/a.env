# src/models.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    document_count = Column(Integer, default=0)
    
    # Relationship: One topic can have many documents
    documents = relationship("Document", back_populates="topic")
    
    def __repr__(self):
        return f"<Topic(name='{self.name}', document_count={self.document_count})>"

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    title = Column(Text, nullable=False)
    text = Column(Text, nullable=False)
    pdf_link = Column(Text)
    authors = Column(Text)
    # Optional: To track when a document was inserted
    fetch_date = Column(DateTime, server_default=func.now())
    
    # Relationship: Each document belongs to one topic
    topic = relationship("Topic", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(title='{self.title[:30]}...', topic_id={self.topic_id})>"
