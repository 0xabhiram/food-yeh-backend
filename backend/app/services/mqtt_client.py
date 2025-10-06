import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Warning: paho-mqtt not available. MQTT functionality will be simulated.")

from app.config import settings

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = None
        self.is_connected = False
        
        if MQTT_AVAILABLE:
            self._setup_client()
        else:
            logger.warning("MQTT client not available - running in simulation mode")
    
    def _setup_client(self):
        """Setup MQTT client with proper configuration"""
        try:
            # Get client ID first
            mqtt_client_id = getattr(settings, 'mqtt_client_id', 'foodyeh_backend')
            self.client = mqtt.Client(client_id=mqtt_client_id)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            # Set connection stability options
            self.client.reconnect_delay_set(min_delay=1, max_delay=120)
            self.client.max_inflight_messages_set(20)
            self.client.max_queued_messages_set(100)
            
            # Set clean session to false for persistent connection
            self.client._clean_session = False
            
            # Set connection parameters - use the correct config fields
            mqtt_host = getattr(settings, 'mqtt_broker_url', 'localhost')
            mqtt_port = getattr(settings, 'mqtt_broker_port', 1883)
            mqtt_keepalive = getattr(settings, 'mqtt_keepalive', 300)  # Increase to 5 minutes
            mqtt_username = getattr(settings, 'mqtt_username', None)
            mqtt_password = getattr(settings, 'mqtt_password', None)
            
            # Store connection parameters for later use
            self.mqtt_host = mqtt_host
            self.mqtt_port = mqtt_port
            self.mqtt_keepalive = mqtt_keepalive
            
            # Set authentication if provided
            if mqtt_username and mqtt_password:
                self.client.username_pw_set(mqtt_username, mqtt_password)
                logger.info(f"Using MQTT authentication: {mqtt_username}")
            else:
                logger.info("No MQTT authentication configured")
            
            logger.info(f"Connecting to MQTT broker at {mqtt_host}:{mqtt_port}")
            # Don't connect here - let the start() method handle it
            # self.client.connect(mqtt_host, mqtt_port, mqtt_keepalive)
            
        except Exception as e:
            logger.error(f"Failed to setup MQTT client: {e}")
            self.client = None
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info("✅ Successfully connected to MQTT broker")
            self.is_connected = True
            
            # Subscribe to status updates from ESP32
            client.subscribe("vending/status/+/+")  # deviceId/orderId
            logger.info("📡 Subscribed to vending/status/+/+")
            
        else:
            error_messages = {
                1: "Incorrect protocol version",
                2: "Invalid client identifier",
                3: "Server unavailable",
                4: "Bad username or password",
                5: "Not authorized"
            }
            error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
            logger.error(f"❌ Failed to connect to MQTT broker: {error_msg} (code: {rc})")
            self.is_connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        logger.info(f"🔌 Disconnected from MQTT broker with code: {rc}")
        self.is_connected = False
        
        # Let the built-in reconnection handle it
        if rc != 0:  # Auto-reconnect for all disconnects except manual (code 0)
            logger.info(f"🔄 Built-in reconnection will handle code: {rc}")
        else:
            logger.info("🛑 Manual disconnect - not reconnecting")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received from ESP32"""
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) == 4 and topic_parts[0] == 'vending' and topic_parts[1] == 'status':
                device_id = topic_parts[2]
                order_id = int(topic_parts[3])
                
                payload = json.loads(msg.payload.decode())
                logger.info(f"📨 Status update from ESP32: {payload}")
                
                # Handle status update
                self._handle_status_update(order_id, device_id, payload)
                
        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON in MQTT message: {msg.payload}")
        except Exception as e:
            logger.error(f"❌ Error processing MQTT message: {e}")
    
    def _handle_status_update(self, order_id: int, device_id: str, payload: Dict[str, Any]):
        """Handle status update from ESP32"""
        try:
            status = payload.get('state', 'unknown')
            message = payload.get('message', '')
            timestamp = payload.get('ts', datetime.utcnow().isoformat())
            
            logger.info(f"🔄 Order {order_id} status: {status} - {message}")
            
            # Here you would update the database
            # This will be implemented in the order router
            
            # Publish to frontend for real-time updates
            self.publish_frontend_update(order_id, status, message, timestamp)
            
        except Exception as e:
            logger.error(f"❌ Error handling status update: {e}")
    
    def publish_frontend_update(self, order_id: int, status: str, message: str, timestamp: str):
        """Publish status update to frontend"""
        payload = {
            "order_id": order_id,
            "status": status,
            "message": message,
            "timestamp": timestamp,
            "type": "status_update"
        }
        
        # Publish to frontend topic
        self.publish("foodyeh/frontend/order_status", payload)
    
    def publish_order_command(self, device_id: str, order_id: int, items: list):
        """Publish order command to ESP32"""
        payload = {
            "orderId": order_id,
            "items": items,
            "ts": datetime.utcnow().isoformat()
        }
        
        topic = f"vending/commands/{device_id}"
        self.publish(topic, payload)
        logger.info(f"📤 Sent order {order_id} to device {device_id}")
    
    def send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        if self.is_connected:
            try:
                self.publish("foodyeh/heartbeat", {"timestamp": datetime.utcnow().isoformat()})
                # Only log heartbeat at DEBUG level to reduce log spam
                logger.debug("💓 Heartbeat sent successfully")
            except Exception as e:
                logger.error(f"❌ Failed to send heartbeat: {e}")
        else:
            logger.debug("⚠️ Cannot send heartbeat - client not connected")
    
    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        """Publish message to MQTT topic"""
        if not MQTT_AVAILABLE:
            logger.info(f"📤 MQTT simulation - would publish to {topic}: {payload}")
            return
        
        if not self.client:
            logger.error("❌ MQTT client not initialized")
            return
            
        if not self.is_connected:
            logger.warning("⚠️ MQTT client not connected - attempting to reconnect")
            try:
                # Use stored connection parameters for reconnection
                self.client.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive)
                # Wait a bit for connection
                import time
                time.sleep(3)
                
                # Check if reconnection was successful
                if not self.is_connected:
                    logger.error("❌ Reconnection failed - client still not connected")
                    return
                else:
                    logger.info("✅ Reconnection successful")
                    
            except Exception as e:
                logger.error(f"❌ Failed to reconnect to MQTT: {e}")
                return
        
        try:
            message = json.dumps(payload)
            
            # Only log heartbeat publishes at DEBUG level
            if topic == "foodyeh/heartbeat":
                logger.debug(f"📤 Attempting to publish to {topic}")
                logger.debug(f"📤 Message: {message}")
            else:
                logger.info(f"📤 Attempting to publish to {topic}")
                logger.info(f"📤 Message: {message}")
            
            result = self.client.publish(topic, message, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                if topic == "foodyeh/heartbeat":
                    logger.debug(f"✅ Successfully published to {topic}")
                    logger.debug(f"📤 Payload: {payload}")
                else:
                    logger.info(f"✅ Successfully published to {topic}")
                    logger.info(f"📤 Payload: {payload}")
            else:
                error_messages = {
                    mqtt.MQTT_ERR_NO_CONN: "No connection",
                    mqtt.MQTT_ERR_CONN_LOST: "Connection lost",
                    mqtt.MQTT_ERR_PROTOCOL: "Protocol error",
                    mqtt.MQTT_ERR_PAYLOAD_SIZE: "Payload too large",
                    mqtt.MQTT_ERR_NOT_SUPPORTED: "Not supported",
                    mqtt.MQTT_ERR_ERRNO: "System error"
                }
                error_msg = error_messages.get(result.rc, f"Unknown error: {result.rc}")
                logger.error(f"❌ Failed to publish to {topic}: {error_msg}")
                
        except Exception as e:
            logger.error(f"❌ Error publishing MQTT message: {e}")
            logger.error(f"❌ Topic: {topic}")
            logger.error(f"❌ Payload: {payload}")
    
    def start(self):
        """Start the MQTT client"""
        if not MQTT_AVAILABLE:
            logger.info("📡 MQTT not available - starting in simulation mode")
            return
        
        if not self.client:
            logger.error("❌ MQTT client not initialized")
            return
        
        try:
            # Connect to broker using stored parameters
            logger.info(f"🔄 Connecting to MQTT broker at {self.mqtt_host}:{self.mqtt_port}")
            logger.info(f"🔄 Using keepalive: {self.mqtt_keepalive}")
            self.client.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive)
            
            # Start the client loop
            self.client.loop_start()
            logger.info("🚀 MQTT client started successfully")
            
            # Wait longer for connection to establish
            import time
            time.sleep(5)
            
            # Check connection status
            if self.is_connected:
                logger.info("✅ MQTT client is connected")
                self.send_heartbeat()
                logger.info("💓 Initial heartbeat sent")
            else:
                logger.warning("⚠️ MQTT client not connected yet - reconnection will handle it")
            
        except Exception as e:
            logger.error(f"❌ Error starting MQTT client: {e}")
            logger.error(f"❌ Host: {self.mqtt_host}, Port: {self.mqtt_port}, Keepalive: {self.mqtt_keepalive}")
    
    def stop(self):
        """Stop the MQTT client"""
        if not MQTT_AVAILABLE or not self.client:
            return
        
        try:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("🛑 MQTT client stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping MQTT client: {e}")

# Global MQTT client instance
mqtt_client = MQTTClient()
