"""
MQTT client service for communication with ESP32 firmware.
Handles secure connection to mqtt.foodyeh.io:8883
"""

import json
import ssl
import time
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from paho.mqtt import client as mqtt_client
import structlog
from config import settings

logger = structlog.get_logger(__name__)


class MQTTService:
    """MQTT service for secure communication with ESP32 firmware."""
    
    def __init__(self):
        """Initialize MQTT service."""
        self.client = None
        self.is_connected = False
        self.connection_attempts = 0
        self.max_connection_attempts = 5
        self.reconnect_delay = 5  # seconds
        
        # Message callbacks
        self.message_handlers: Dict[str, Callable] = {}
        
        # Connection status
        self.last_connection_time: Optional[datetime] = None
        self.last_message_time: Optional[datetime] = None
        
        # Initialize connection
        self._setup_client()
    
    def _setup_client(self):
        """Setup MQTT client with secure configuration."""
        try:
            # Generate unique client ID
            client_id = f"{settings.mqtt_client_id}_{int(time.time())}"
            
            # Create client
            self.client = mqtt_client.Client(
                client_id=client_id,
                clean_session=True,
                protocol=mqtt_client.MQTTv311
            )
            
            # Set up SSL/TLS
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Set SSL configuration
            self.client.tls_set_context(ssl_context)
            
            # Set authentication if provided
            if settings.mqtt_username and settings.mqtt_password:
                self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            self.client.on_publish = self._on_publish
            self.client.on_log = self._on_log
            
            logger.info("MQTT client setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Handle MQTT connection events."""
        if rc == 0:
            self.is_connected = True
            self.connection_attempts = 0
            self.last_connection_time = datetime.utcnow()
            logger.info("MQTT client connected successfully")
            
            # Subscribe to relevant topics
            self._subscribe_to_topics()
            
        else:
            self.is_connected = False
            error_messages = {
                1: "Incorrect protocol version",
                2: "Invalid client identifier",
                3: "Server unavailable",
                4: "Bad username or password",
                5: "Not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"MQTT connection failed: {error_msg}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection events."""
        self.is_connected = False
        logger.warning(f"MQTT client disconnected (rc={rc})")
        
        # Attempt reconnection if not intentional disconnect
        if rc != 0 and self.connection_attempts < self.max_connection_attempts:
            self.connection_attempts += 1
            logger.info(f"Attempting MQTT reconnection ({self.connection_attempts}/{self.max_connection_attempts})")
            time.sleep(self.reconnect_delay)
            self.connect()
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            self.last_message_time = datetime.utcnow()
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.debug("Received MQTT message", topic=topic, payload_length=len(payload))
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning("Invalid JSON payload received", topic=topic, payload=payload[:100])
                return
            
            # Call registered handlers
            if topic in self.message_handlers:
                try:
                    self.message_handlers[topic](data)
                except Exception as e:
                    logger.error(f"Error in message handler for topic {topic}: {e}")
            else:
                logger.debug("No handler registered for topic", topic=topic)
                
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_publish(self, client, userdata, mid):
        """Handle successful message publishing."""
        logger.debug("Message published successfully", message_id=mid)
    
    def _on_log(self, client, userdata, level, buf):
        """Handle MQTT client logs."""
        if level == mqtt_client.MQTT_LOG_ERR:
            logger.error(f"MQTT error: {buf}")
        elif level == mqtt_client.MQTT_LOG_WARNING:
            logger.warning(f"MQTT warning: {buf}")
        else:
            logger.debug(f"MQTT log: {buf}")
    
    def _subscribe_to_topics(self):
        """Subscribe to relevant MQTT topics."""
        topics = [
            ("foodyeh/status", 1),
            ("foodyeh/order/+/response", 1),
            ("foodyeh/error", 1),
            ("foodyeh/heartbeat", 0)
        ]
        
        for topic, qos in topics:
            try:
                result = self.client.subscribe(topic, qos)
                if result[0] == mqtt_client.MQTT_ERR_SUCCESS:
                    logger.info(f"Subscribed to topic: {topic}")
                else:
                    logger.error(f"Failed to subscribe to topic: {topic}")
            except Exception as e:
                logger.error(f"Error subscribing to topic {topic}: {e}")
    
    def connect(self) -> bool:
        """
        Connect to MQTT broker.
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.client:
            logger.error("MQTT client not initialized")
            return False
        
        try:
            logger.info(f"Connecting to MQTT broker: {settings.mqtt_broker}:{settings.mqtt_port}")
            
            # Connect to broker
            result = self.client.connect(
                settings.mqtt_broker,
                settings.mqtt_port,
                keepalive=settings.mqtt_keepalive
            )
            
            if result == mqtt_client.MQTT_ERR_SUCCESS:
                # Start the loop in a separate thread
                self.client.loop_start()
                return True
            else:
                logger.error(f"Failed to connect to MQTT broker: {result}")
                return False
                
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        if self.client and self.is_connected:
            try:
                self.client.loop_stop()
                self.client.disconnect()
                self.is_connected = False
                logger.info("MQTT client disconnected")
            except Exception as e:
                logger.error(f"Error disconnecting MQTT client: {e}")
    
    def publish_order(self, order_id: str, item_id: str, slot_id: int, quantity: int = 1) -> bool:
        """
        Publish order to MQTT broker.
        
        Args:
            order_id: Unique order identifier
            item_id: Item identifier
            slot_id: Slot number
            quantity: Quantity to vend
        
        Returns:
            True if message published successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Cannot publish order: MQTT not connected")
            return False
        
        try:
            topic = f"foodyeh/order/{order_id}"
            payload = {
                "order_id": order_id,
                "item_id": item_id,
                "slot_id": slot_id,
                "quantity": quantity,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
            
            message = json.dumps(payload, separators=(',', ':'))
            result = self.client.publish(topic, message, qos=1)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logger.info("Order published successfully", 
                           order_id=order_id, item_id=item_id, slot_id=slot_id)
                return True
            else:
                logger.error(f"Failed to publish order: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing order: {e}")
            return False
    
    def publish_admin_command(self, command: str, parameters: Dict[str, Any] = None) -> bool:
        """
        Publish admin command to MQTT broker.
        
        Args:
            command: Admin command (e.g., "reboot", "override")
            parameters: Command parameters
        
        Returns:
            True if message published successfully, False otherwise
        """
        if not self.is_connected:
            logger.error("Cannot publish admin command: MQTT not connected")
            return False
        
        try:
            topic = f"foodyeh/admin/{command}"
            payload = {
                "command": command,
                "parameters": parameters or {},
                "timestamp": datetime.utcnow().isoformat(),
                "source": "api"
            }
            
            message = json.dumps(payload, separators=(',', ':'))
            result = self.client.publish(topic, message, qos=2)  # QoS 2 for admin commands
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logger.info("Admin command published successfully", command=command)
                return True
            else:
                logger.error(f"Failed to publish admin command: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing admin command: {e}")
            return False
    
    def register_message_handler(self, topic: str, handler: Callable):
        """
        Register a message handler for a specific topic.
        
        Args:
            topic: MQTT topic to handle
            handler: Callback function to handle messages
        """
        self.message_handlers[topic] = handler
        logger.info(f"Registered message handler for topic: {topic}")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current MQTT connection status.
        
        Returns:
            Dictionary with connection status information
        """
        return {
            "connected": self.is_connected,
            "broker": f"{settings.mqtt_broker}:{settings.mqtt_port}",
            "client_id": self.client._client_id.decode() if self.client else None,
            "last_connection": self.last_connection_time.isoformat() if self.last_connection_time else None,
            "last_message": self.last_message_time.isoformat() if self.last_message_time else None,
            "connection_attempts": self.connection_attempts
        }
    
    def is_healthy(self) -> bool:
        """
        Check if MQTT service is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        if not self.is_connected:
            return False
        
        # Check if we've received a message recently (within last 5 minutes)
        if self.last_message_time:
            time_since_last_message = (datetime.utcnow() - self.last_message_time).total_seconds()
            if time_since_last_message > 300:  # 5 minutes
                logger.warning("No MQTT messages received recently", 
                              seconds_since_last=time_since_last_message)
                return False
        
        return True


# Global MQTT service instance
mqtt_service = MQTTService()


def get_mqtt_service() -> MQTTService:
    """Get the global MQTT service instance."""
    return mqtt_service 