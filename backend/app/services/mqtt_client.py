import json
import logging
from datetime import datetime
from typing import Dict, Any
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Order, OrderStatus
from app.schemas import MQTTCommand, MQTTStatus

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(client_id=settings.mqtt_client_id)
        self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.db_session: Session = None
        
    def set_db_session(self, db_session: Session):
        """Set database session for MQTT client"""
        self.db_session = db_session
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subscribe to status updates
            client.subscribe("vending/status/+/+")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        logger.info(f"Disconnected from MQTT broker with code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) == 4 and topic_parts[0] == 'vending' and topic_parts[1] == 'status':
                device_id = topic_parts[2]
                order_id = int(topic_parts[3])
                
                payload = json.loads(msg.payload.decode())
                status_data = MQTTStatus(
                    state=payload.get('state', 'unknown'),
                    timestamp=datetime.fromisoformat(payload.get('ts', datetime.utcnow().isoformat())),
                    message=payload.get('message')
                )
                
                self.handle_status_update(order_id, status_data)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def handle_status_update(self, order_id: int, status_data: MQTTStatus):
        """Update order status based on MQTT status update"""
        if not self.db_session:
            logger.error("No database session available")
            return
        
        try:
            order = self.db_session.query(Order).filter(Order.id == order_id).first()
            if not order:
                logger.warning(f"Order {order_id} not found")
                return
            
            # Map MQTT states to order statuses
            state_mapping = {
                'queued': OrderStatus.CONFIRMED,
                'cooking': OrderStatus.PREPARING,
                'dispensing': OrderStatus.READY,
                'done': OrderStatus.COMPLETED,
                'error': OrderStatus.CANCELLED
            }
            
            new_status = state_mapping.get(status_data.state, OrderStatus.PENDING)
            order.status = new_status
            order.updated_at = datetime.utcnow()
            
            self.db_session.commit()
            logger.info(f"Updated order {order_id} status to {new_status}")
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            self.db_session.rollback()
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(settings.mqtt_broker_url, settings.mqtt_broker_port, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def publish_command(self, device_id: str, command: MQTTCommand):
        """Publish command to device"""
        try:
            topic = f"vending/commands/{device_id}"
            payload = {
                "orderId": command.order_id,
                "items": [{"dishId": item.dish_id, "qty": item.quantity} for item in command.items],
                "ts": command.timestamp.isoformat()
            }
            
            result = self.client.publish(topic, json.dumps(payload))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published command to {topic}")
            else:
                logger.error(f"Failed to publish command to {topic}")
                
        except Exception as e:
            logger.error(f"Error publishing MQTT command: {e}")


# Global MQTT client instance
mqtt_client = MQTTClient()
