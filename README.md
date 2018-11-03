# py-api-visualizadores

Ejemplo de api json basada en [bottle.py](https://bottlepy.org) para monitorizar dispositivos de AWS IoT Platform


# clase Visualizador
La clase _Visualizador_ permite conectarse como un dispositivo visualizador, a la plataform IoT de AWS, o bien a un Greengrass Core,
y subscribirse a un topic mqtt de otro dispositivo (siempre que esté habilitada esta posibilidad en el grupo greengrass)

## init

Para instanciar el objeto es necesario pasar los siguientes parámetros:

- "host": endpoint AWS IoT
- "certificatePath": path al certificado del dispositivo visualizador
- "privateKeyPath": path a la parte privada del certificado del visualizador
- "rootCAPath": [ca de servidor](https://docs.aws.amazon.com/es_es/iot/latest/developerguide/managing-device-certs.html)
- "thingName": nombre del dispositivo visualizador en la plataforma IoT (clientId)
- "topic": Topic mqtt al que queremos subscribir el visualizador


## loop vs loopPlatform

Una vez instanciado el cliente, podemos conectarnos bien a la plataforma con **loopPlatform**
o bien tratar de hacer el discover del greengrass core local (**loop**)

Ejemplo:

```
    v = Visualizador(
            privateKeyPath="certs/key.pem", 
            certificatePath="certs/cert.pem",
            host="asfsaojo.aws.iot.eu-west-1.amazonaws.com",
            rootCAPath="./rootCA.pem",
            topic="$aws/things/my_thing_to_visualice/shadow/update/documents",
            thingName="my_thing_name"
        )

    v.loop()


```
