from fastapi import FastAPI
app: FastAPI = FastAPI(title="hello World Api")


@app.get('/')
def read_root():
    return {'Hello': 'World'}
