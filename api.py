from bottle import hook, route, run, response
from threading import Thread
from visualizador import Visualizador

# apanho para poder mutar a variable global
lumens =  [0]
dB =  [0]
T = [0]
H =  [0]

def threadLumens():
    global lumens

    v = Visualizador(
            certificatePath="GG_visualizador_Luminosidad/a08b268e0e-certificate.pem.crt", 
            privateKeyPath="GG_visualizador_Luminosidad/a08b268e0e-private.pem.key",
            host="a3rg80zsalgmg0-ats.iot.eu-west-1.amazonaws.com",
            rootCAPath="GG_visualizador_Luminosidad/rootCA.pem",
            topic="$aws/things/GG_sensor_dB_lumens/shadow/update/documents",
            thingName="GG_visualizador_Luminosidad"
    )

    v.loopPlatform(lumens)


# create threads
t1 = Thread( target=threadLumens, args=())
t1.start()



@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
    response.headers['Content-Type'] = 'application/json'

@route('/lumens')
def get_lumens():
    return lumens[0]

@route('/dB')
def get_dB():
    return dB[0]
    #return {"a": 1}

@route('/temp')
def get_temp():
    return T[0]

@route('/humidity')
def get_humidity():
    return H[0]


run(host='localhost', port=8080, debug=True)

# stop threads
t1._Thread__stop()
