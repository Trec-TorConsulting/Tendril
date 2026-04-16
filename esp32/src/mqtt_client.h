#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

void mqtt_setup();
void mqtt_loop();
void mqtt_publish(const char* subtopic, const char* payload);
void mqtt_heartbeat();

#endif
