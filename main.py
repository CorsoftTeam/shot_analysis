import worker
import time

if __name__ == '__main__':
    time.sleep(10)
    listener = worker.RabbitMQWorker()
    listener.start_consuming()
