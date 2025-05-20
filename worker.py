import pika
import json
import random
import os
import logging
from logging.handlers import RotatingFileHandler
# from config import RABBITMQ_CONFIG

class RabbitMQWorker:
    def __init__(self):
        self.logger = logging.getLogger('rabbitmq_worker')
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.credentials = pika.PlainCredentials(**{'username': 'guest', 'password': 'guest'})
        self.connection_params = pika.ConnectionParameters(host=os.environ.get('RABBITMQ_HOST', 'localhost'), port='5672', credentials=self.credentials)
        # self.connection = pika.BlockingConnection(self.parameters)
        # self.channel = self.connection.channel()
        self._connect()

    def _connect(self):
        """Устанавливаем соединение через AMQP"""
        try:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            
            # Настройка RabbitMQdocke
            self._setup_rabbitmq()
            print("Connected to RabbitMQ via AMQP")
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Failed to connect: {e}")
            raise

    def _setup_rabbitmq(self):
        """Объявляем exchange и очереди"""
        
        # Очереди (durable для сохранения сообщений)
        self.channel.queue_declare(
            queue='ruby_to_py',
            durable=True
        )
        self.channel.queue_declare(
            queue='py_to_ruby',
            durable=True
        )

    def process_message(self, ch, method, properties, body):
        """Обработка входящего сообщения"""
        try:
            message = json.loads(body)
            self.logger.info(f"Received from Ruby: {message}")
            
            # Формируем ответ
            response = {
                'user_id': message['user_id'],
                'message_id': message['message_id'],
                'gun': random.choice(message['data']),
                "processed_by": "python_worker",
                "status": "success" 
            }
            
            # Отправляем ответ в выходную очередь
            self.channel.basic_publish(
                exchange='',
                routing_key='py_to_ruby',
                body=json.dumps(response),
                properties=properties
            )
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError:
            print("Invalid JSON received")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            print(f"Error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """Запускаем потребитель"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='ruby_to_py',
            on_message_callback=self.process_message,
            auto_ack=False
        )
        
        print(f" [*] Waiting for messages from input_queue. To exit press CTRL+C")
        self.channel.start_consuming()
