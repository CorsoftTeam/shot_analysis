import worker
import time

if __name__ == '__main__':
    time.sleep(10)
    worker = worker.RabbitMQWorker()
    worker.start_consuming()
