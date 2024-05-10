from celery import Celery

app = Celery(
    "myapp",  # Name of your application
    broker="amqp://localhost:5672",  # Broker URL (adjust for your broker)
    backend="redis://localhost:6379",
)  # Result backend (optional, adjust for your broker)


@app.task
def long_running_task(data):
    # Simulate a long-running task
    import time

    time.sleep(5)
    return f"Task completed with data: {data}"
