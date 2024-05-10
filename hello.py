from celery_ import long_running_task

result = long_running_task.delay("some data")

# Access the task result (optional)
if result.ready():
    print(result.get())  # Get the task result
else:
    print("Task is still running")
