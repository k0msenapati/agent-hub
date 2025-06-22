from flask_login import UserMixin
from app import db
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = "users"

    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    projects = db.relationship("Project", backref="user", lazy=True)
    files = db.relationship("File", backref="user", lazy=True)
    knowledge_bases = db.relationship("KnowledgeBase", backref="user", lazy=True)
    agents = db.relationship("Agent", backref="user", lazy=True)
    chats = db.relationship("Chat", backref="user", lazy=True)
    analytics = db.relationship("Analytics", backref="user", lazy=True)

    def __repr__(self):
        return f"<User: {self.username}>"

    @property
    def id(self):
        return self.uid


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    knowledge_bases = db.relationship("KnowledgeBase", backref="project", lazy=True)
    agents = db.relationship("Agent", backref="project", lazy=True)

    def __repr__(self):
        return f"<Project: {self.name}>"


class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    original_filename = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<File: {self.filename}>"


class KnowledgeBase(db.Model):
    __tablename__ = "knowledge_bases"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    embedding_model_provider = db.Column(db.Text, nullable=False)
    embedding_model_name = db.Column(db.Text, nullable=False)
    embedding_model_base_url = db.Column(db.Text)
    metadata_columns = db.Column(db.Text)
    content_columns = db.Column(db.Text)
    id_column = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    agents = db.relationship("AgentKnowledgeBase", backref="knowledge_base", lazy=True)

    def __repr__(self):
        return f"<KnowledgeBase: {self.name}>"


class Agent(db.Model):
    __tablename__ = "agents"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    model_provider = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.Text, nullable=False)
    api_key = db.Column(db.Text)
    system_prompt = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    knowledge_bases = db.relationship("AgentKnowledgeBase", backref="agent", lazy=True)
    chats = db.relationship("Chat", backref="agent", lazy=True)

    def __repr__(self):
        return f"<Agent: {self.name}>"


class AgentKnowledgeBase(db.Model):
    __tablename__ = "agent_knowledge_bases"

    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey("agents.id"), nullable=False)
    knowledge_base_id = db.Column(
        db.Integer, db.ForeignKey("knowledge_bases.id"), nullable=False
    )

    def __repr__(self):
        return (
            f"<AgentKnowledgeBase: Agent {self.agent_id} - KB {self.knowledge_base_id}>"
        )


class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey("agents.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Chat: {self.id} at {self.timestamp}>"


class Analytics(db.Model):
    __tablename__ = "analytics"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    event_type = db.Column(
        db.Text, nullable=False
    )  # e.g., 'file_upload', 'kb_query', 'agent_query'
    event_count = db.Column(db.Integer, nullable=False, default=1)
    last_event = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<Analytics: {self.event_type} for user {self.user_id}>"
