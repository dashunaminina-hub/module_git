from datetime import date
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(
    title="МТР Purchase Service API",
    description="Микросервис управления заявками на закупку "
    "материально-технических ресурсов (МТР)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# DTO (Модели данных на базе Pydantic)
class PurchaseRequestCreate(BaseModel):
    item_name: str = Field(
        ...,
        description="Наименование ресурса",
        example="Труба стальная 150мм",
    )
    quantity: int = Field(..., gt=0, description="Количество", example=50)
    desired_date: date = Field(..., description="Желаемый срок поставки")
    justification: str = Field(
        ...,
        description="Обоснование необходимости",
        example="Для ремонта цеха №2",
    )
    department: str = Field(
        ..., description="Подразделение-заявитель", example="Цех №2"
    )


class PurchaseRequestResponse(PurchaseRequestCreate):
    id: int = Field(
        ..., description="Уникальный идентификатор заявки", example=1
    )
    status: str = Field(
        default="Зарегистрирована",
        description="Статус заявки",
        example="Зарегистрирована",
    )

    model_config = ConfigDict(from_attributes=True)


# In-Memory хранилище данных (заглушка)
fake_db = [
    {
        "id": 1,
        "item_name": "Кабель силовий ВВГнг 3х2.5",
        "quantity": 100,
        "desired_date": date(2026, 6, 1),
        "justification": "Электромонтажные работы",
        "department": "Электроцех",
        "status": "Зарегистрирована",
    },
    {
        "id": 2,
        "item_name": "Цемент М500 (мешки 50кг)",
        "quantity": 200,
        "desired_date": date(2026, 6, 15),
        "justification": "Строительные работы",
        "department": "Строительный отдел",
        "status": "Проверена",
    },
]


# Эндпоинты REST API
@app.get(
    "/api/v1/purchase-requests/",
    response_model=List[PurchaseRequestResponse],
    status_code=status.HTTP_200_OK,
    summary="Получение списка всех заявок",
)
def get_purchase_requests():
    """Возвращает список всех зарегистрированных заявок на закупку МТР."""
    return fake_db


@app.get(
    "/api/v1/purchase-requests/{id}",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_200_OK,
    summary="Получение детальной информации о заявке",
)
def get_purchase_request(id: int):
    """Ищет заявку по ее уникальному идентификатору (id)."""
    for req in fake_db:
        if req["id"] == id:
            return req
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Заявка с ID {id} не найдена",
    )


@app.post(
    "/api/v1/purchase-requests/",
    response_model=PurchaseRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой заявки",
)
def create_purchase_request(payload: PurchaseRequestCreate):
    """Создает новую заявку на закупку МТР и сохраняет ее в память."""
    new_id = max([r["id"] for r in fake_db], default=0) + 1
    new_request = {
        "id": new_id,
        "item_name": payload.item_name,
        "quantity": payload.quantity,
        "desired_date": payload.desired_date,
        "justification": payload.justification,
        "department": payload.department,
        "status": "Зарегистрирована",
    }
    fake_db.append(new_request)
    return new_request


@app.delete(
    "/api/v1/purchase-requests/{id}",
    status_code=status.HTTP_200_OK,
    summary="Удаление заявки",
)
def delete_purchase_request(id: int):
    """Удаляет заявку из системы по ее ID."""
    for index, req in enumerate(fake_db):
        if req["id"] == id:
            del fake_db[index]
            return {"detail": f"Заявка с ID {id} успешно удалена"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Заявка с ID {id} не найдена",
    )