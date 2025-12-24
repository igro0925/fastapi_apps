from fastapi import FastAPI, Form, Request, status
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import os

from database import engine, SessionLocal
from models import Base
import models
# 연결한 DB엔진에 테이블을 생성
# models에 정의한 모든 클래스를 테이블로 생성
Base.metadata.create_all(bind=engine)

# FastAPI() 객체 생성
app = FastAPI()

abs_path = os.path.dirname(os.path.realpath(__file__))
# print(abs_path)
# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
# templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# DB 세션 객체 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()


@app.get("/")
def home(request: Request,
         db: Session = Depends(get_db)):
    # todo 데이터 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.desc()).all()
    # print(todos)
    # for todo in todos:
        # print(todo.id, todo.task, todo.completed)
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos})

@app.post("/add")
def add(request: Request, 
        task: str = Form(...),
        db: Session = Depends(get_db)):
    
    # todo 객체 생성
    todo = models.Todo(task=task)
    print(todo)

    # todo를 DB에 추가
    db.add(todo)

    # DB반영
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), 
                            status_code=status.HTTP_303_SEE_OTHER)