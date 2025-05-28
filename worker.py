import pika
import json
import random
import os
import logging
from logging.handlers import RotatingFileHandler
import gun_type_finder
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
            
            no_name_gun = self.find_no_name_gun(message['data'])
            # Формируем ответ
            response = {
                'user_id': message['user_id'],
                'message_id': message['message_id'],
                'gun': self.find_simmilar(message['data'], no_name_gun),
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

    def find_simmilar(self, guns, new_gun):
        finder = gun_type_finder.GunTypeFinder()
        new_gun['type'] = finder.find_type(new_gun['sound_url'])
        simmilar_guns = []
        for gun in guns:
            gun['type'] = finder.find_type(gun['sound_url'])
            if gun['type'] == new_gun['sound_url'] : simmilar_guns.append(gun)

        if simmilar_guns.length == 1 : return simmilar_guns[0]

    def find_no_name_gun(self, guns):
        for index, gun in guns:
            if gun['name'] is None : return guns.pop(index)
"""
[
            {
                "id": 2,
                "name": "pistol2",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6MiwicHVyIjoiYmxvYl9pZCJ9fQ==--7aa3e4e419a9ceb65903c91271298d4127785fb0/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 3,
                "name": "pistol3",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6MywicHVyIjoiYmxvYl9pZCJ9fQ==--21364ef5dd4a5c49947b6b1f29010e700bc4fca3/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 4,
                "name": "4",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6NCwicHVyIjoiYmxvYl9pZCJ9fQ==--ad78aeda2021e7272753b4ec907ecd8540014ab4/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 6,
                "name": "5",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6NiwicHVyIjoiYmxvYl9pZCJ9fQ==--45d6e03bf2990aa6954af87a393361f3f6712bba/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 7,
                "name": "6",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6NywicHVyIjoiYmxvYl9pZCJ9fQ==--da34d07f7c7528bf4aa9f68c18894c487865e2f5/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 8,
                "name": "7",
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6OCwicHVyIjoiYmxvYl9pZCJ9fQ==--ded84794ae2b364af9bcb6d5c7c9178040bf527b/Pistol-cocking-4(chosic.com).mp3"
            },
            {
                "id": 33,
                "name": None,
                "sound_url": "http://localhost:3002/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6MzIsInB1ciI6ImJsb2JfaWQifX0=--c41177d72e65ceae5d380e33d2a8ea19260763c3/Pistol-cocking-4(chosic.com).mp3"
            }
        ]
"""
