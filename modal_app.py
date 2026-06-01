import modal

app = modal.App("data-decision-inference-api")
image = (
    modal.Image.debian_slim()
    .pip_install("fastapi", "torch", "numpy", "uvicorn", "httpx")
    .add_local_dir(".", remote_path="/root/app", copy=True)
    .run_commands("cd /root/app && pip install -e .")
)

@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    from src.app.main import app
    return app