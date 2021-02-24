from celery import Celery

celery_app = Celery(
    "worker", broker="amqp://guest@queue//", backend="amqp://guest@queue//"
)

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
    "app.worker.linear_resolve_martyrology_datestrs": "main-queue",
}
