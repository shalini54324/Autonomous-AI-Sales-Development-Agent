import os, tempfile, pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.models import Base
from app.database.repositories import Repository

@pytest.fixture
def repo():
    engine=create_engine("sqlite:///:memory:",connect_args={"check_same_thread":False}); Base.metadata.create_all(engine)
    S=sessionmaker(bind=engine,expire_on_commit=False); s=S(); yield Repository(s); s.close()
