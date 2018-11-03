from __future__ import print_function
import sys
import ssl
import time
import datetime
import logging, traceback
import paho.mqtt.client as mqtt

IoT_protocol_name = "x-amzn-mqtt-ca"
#aws_iot_endpoint = "AWS_IoT_ENDPOINT_HERE" # <random>.iot.<region>.amazonaws.com
#aws_iot_endpoint = '192.168.4.1'
aws_iot_endpoint = "demoPalexco_Core"

#ca = "root-ca-cert.pem" 
ca = "groupCA/root-ca.crt" 
#cert = "certs_GG_camara/fa469e9f96-certificate.pem.crt"
#private = "certs_GG_camara/fa469e9f96-private.pem.key"
cert    = "dispositivos/GG_visualizador_Luminosidad/a08b268e0e-certificate.pem.crt"
private = "dispositivos/GG_visualizador_Luminosidad/a08b268e0e-private.pem.key"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

def ssl_alpn():
    try:
        #debug print opnessl version
        logger.info("open ssl version:{}".format(ssl.OPENSSL_VERSION))
        ssl_context = ssl.create_default_context()
        #ssl_context.set_alpn_protocols([IoT_protocol_name])
        ssl_context.load_verify_locations(cafile=ca)
        ssl_context.load_cert_chain(certfile=cert, keyfile=private)

        return  ssl_context
    except Exception as e:
        print("exception ssl_alpn()")
        raise e




if __name__ == '__main__':

    topic = "$aws/things/GG_sensor_dB_lumens/shadow/update/documents"
    
    def on_msg(client, userdata, message):
        logger.info("recibimos msg")
        logger.info(message)
        print("%s", message.payload)
    
    def on_con(client, userdata, rc):
        logger.info("Conectado!!!")
        client.subscribe(topic,qos=0)

    try:
        mqttc = mqtt.Client(client_id="GG_visualizador_Luminosidad")
        mqttc.on_connect = on_con
        mqttc.on_message = on_msg

        ssl_context= ssl_alpn()
        mqttc.tls_set_context(context=ssl_context)
        logger.info("start connect")
        mqttc.connect(aws_iot_endpoint, port=8883)
        logger.info("connect success")

        mqttc.loop_forever()

        #mqttc.loop_start()

        #while True:
        #    now = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

        #    #logger.info("try to publish:{}".format(now))
        #    #mqttc.publish(topic, now)

        #    logger.info("in loop")
        #    time.sleep(1)

    except Exception as e:
        logger.error("exception main()")
        logger.error("e obj:{}".format(vars(e)))
        logger.error("message:{}".format(e.message))
        traceback.print_exc(file=sys.stdout)

