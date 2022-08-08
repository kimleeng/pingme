# AUTOGENERATED! DO NOT EDIT! File to edit: ../01_api.ipynb.

# %% auto 0
__all__ = ['app', 'read_main', 'read_test', 'get_fest', 'get_test', 'web_service']

# %% ../01_api.ipynb 5
# Imports required for package
from .core import PingMe

# %% ../01_api.ipynb 8
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

# client = TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     print(response)
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}

# %% ../01_api.ipynb 10
@app.get("/test")
async def read_test():
    return {"msg": "Test World"}

# %% ../01_api.ipynb 12
@app.get("/fest")
async def get_fest(name:str):
    return {"Fest": f"{name}fest"}

# %% ../01_api.ipynb 14
@app.get("/teams")
async def get_test():
    notification = PingMe(title="Test", text="Test")
    test= notification.send_to_webhook("https://dksund.webhook.office.com/webhookb2/00b7d9bf-4d44-4eaa-8922-a96700f72c82@d0155445-8a4c-4780-9c13-33c78f22890e/IncomingWebhook/20b9007420b2416d9ca54e66da2b30dc/ac8e8393-1bd6-4d64-a2e5-f869e41d4ab8")
    return test

# %% ../01_api.ipynb 17
def web_service():
    uvicorn.run(app)
