
from ctypes.wintypes import tagRECT
from tkinter import image_names
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, flash, get_flashed_messages
from flask.helpers import flash
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
import json
from datetime import date, timedelta

app=Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'contacts'
mysql = MySQL(app)


app.secret_key="applogin"

app.config["IMAGE"] = "app\static\docs"
app.config["FACTURAS"] = "app\static\Facturas"
app.config["FECHA_ENVIO"] = date.today()



@app.route('/') ######################################################################
def index():
    session.clear()
    return render_template("inicio.html")

@app.route('/mejoravit') ######################################################################
def mejoravit():
    return render_template("mejoravit.html")

@app.route('/hipoteca-verde') ######################################################################
def hipoteca_verde():
    return render_template("hipoteca-verde.html")

@app.route('/bancos') ######################################################################
def bancos():
    return render_template("bancos.html")



@app.route('/login-asesores',methods = ["GET","POST"]) ######################################################################
def login_asesores():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 1:           ##  Indica que existe la cuenta y tiene permisos para entrar a asesores
                session['nombre'] = name
                session['estado'] = valor[1]

                return redirect(url_for('asesores', estados = session['estado']))

            else:
                return redirect(url_for('login-asesores'))        ##  La cuenta no es valida y no entrará a asesores

        return render_template('login-asesores.html')

    else:
        return redirect(url_for('asesores', estados = session['estado']))


    
@app.route('/login-admin',methods = ["GET","POST"]) ######################################################################
def login_admin():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 2:       ## indica que la cuenta es administrador o superior y puede entrar a admin
                session['nombre'] = name
                session['estado'] = valor[1]

                print(valor)
                return redirect(url_for('admin'))

            else:                         ##  indica que la cuenta no existe o es de rango inferior y no entrará a admin
                  return redirect(url_for('login_admin'))

        return render_template('login-administrador.html')

    elif session['estado'] == "administrador":
        return redirect(url_for('admin'))

    else:
        return redirect(url_for('asesores', estados = session['estado']))

@app.route('/login-graficas',methods = ["GET","POST"]) ######################################################################
def login_graficas():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 2:
                session['nombre'] = name
                session['estado'] = valor[1]

                print(valor)
                return redirect(url_for('graficas'))

            else:
                return redirect(url_for('login_graficas'))

        return render_template('login-graficas.html')

    elif session['estado'] == "administrador":
        return redirect(url_for('graficas'))

    else:
        return redirect(url_for('asesores', estados = session['estado']))

@app.route('/login-facturas',methods = ["GET","POST"]) ######################################################################
def login_facturas():

    if not session:
        if request.method == 'POST':
            name = request.form['nmUserNamea']
            passw = request.form['nmPassa']

            valor = login(name,passw)

            if valor[0] >= 1:           ##  Indica que existe la cuenta y tiene permisos para entrar a asesores
                session['nombre'] = name
                session['estado'] = valor[1]

                return redirect(url_for('facturas'))

            else:
                return redirect(url_for('login-facturas'))        ##  La cuenta no es valida y no entrará a asesores

        return render_template('login-facturas.html')

    else:
        return redirect(url_for('facturas'))



####################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/delete/<string:id>/<fechainicial>/<fechafinal>') ######################################################################
def delete_contact(id,fechainicial,fechafinal):
    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])       
        if priv[0] <= 1:                         ### se revisan los privilegios antes de dar la orden de eliminar
            return redirect(url_for('asesores', estados = priv[1]))
        
        else:

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(id))
            data = cur.fetchall()

            FECHA = date.today()
            correo(data,FECHA,0)

            number = data[0][4]
            try: 
                path1 = os.path.join(app.config["IMAGE"], "{}_ine.pdf".format(number))
                os.remove(path1)
            except:
                print("archivo no encontrado")
            
            try:
                path2 = os.path.join(app.config["IMAGE"], "{}_solicitud.pdf".format(number))
                os.remove(path2)
            except:
                print("archivo no encontrado")

            try:
                path3 = os.path.join(app.config["IMAGE"], "{}_estado_cuenta.pdf".format(number))
                os.remove(path3)
            except:
                print("archivo no encontrado")
            
            for i in range(1,10):
                try:
                    path_factura = os.path.join(app.config["FACTURAS"], "{}_factura{}.pdf".format(number,i))
                    os.remove(path_factura)
                except:
                    print("No hay que borrar")



            cur = mysql.connection.cursor()
            cur.execute('DELETE FROM prueba_3 WHERE id = {0}'.format(id))
            mysql.connection.commit()
            return redirect(url_for('tabla', fechainiciall = fechainicial, fechafinall = fechafinal))


@app.route('/edit/<string:id>/<fechainicial>/<fechafinal>') ######################################################################
def get_contact(id,fechainicial,fechafinal):

    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])
        if priv[0] <= 1:                ### se revisan los privilegios antes de dar la orden de editar
            return redirect(url_for('asesores', estados = priv[1]))

        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(id))
            data = cur.fetchall()

            dicc = {
                    'usuario' : session['nombre'],
                    'fechainicial' : fechainicial,
                    'fechafinal' : fechafinal
                    }  
            return render_template('edit-contact.html',data = dicc ,contact = data[0])
        ##pendiente

@app.route('/update/<id>/<fechainicial>/<fechafinal>', methods = ['POST']) ######################################################################
def update_contact(id,fechainicial,fechafinal):

    if not session:
        return redirect(url_for('login_admin'))

    else:
        priv = privilegios(session['nombre'])
        if priv[0] <= 1:                ### se revisan los privilegios antes de dar la orden de editar
            return redirect(url_for('asesores', estados = priv[1]))

        else:
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(id))
            data = cur.fetchall()

            #Obtención de datos
            if request.method == 'POST':
                ascesor = request.form['ascesor']
                nombre_cliente= request.form['nombre_cliente']
                numero_tarjeta=request.form['numero_tarjeta']
                monto = request.form['monto']
                retorno_cliente = request.form['retorno_cliente']
                retorno_ascesor = request.form['retorno_ascesor']
                banco = request.form['banco']
                clabe = request.form['clabe']
                ine = request.files['ine']
                solicitud = request.files['solicitud']
                estado = request.files['estado_cuenta']

                if (extension(ine.filename) == False) or (extension(solicitud.filename) == False) or (extension(estado.filename) == False):
                    flash("error")
                    return redirect(url_for('get_contact', id = id, fechainicial = fechainicial, fechafinal = fechafinal))

                Nine = numero_tarjeta + "_" + "ine.pdf"
                Nsolicitud = numero_tarjeta + "_" + "solicitud.pdf"
                Nestado_cuenta = numero_tarjeta + "_" + "estado_cuenta.pdf"

                ine.save(os.path.join(app.config["IMAGE"], Nine))
                solicitud.save(os.path.join(app.config["IMAGE"], Nsolicitud))
                estado.save(os.path.join(app.config["IMAGE"], Nestado_cuenta))

        #consulta SQL
                cur = mysql.connection.cursor()
                cur.execute("""
                UPDATE prueba_3 
                SET ascesor = %s,
                    nombre_cliente = %s,
                    numero_tarjeta= %s,
                    monto = %s,
                    retorno_cliente = %s,
                    retorno_ascesor = %s,
                    banco = %s,
                    clabe = %s
                    WHERE id = %s
                """, (ascesor,nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor,banco,clabe,id))
                mysql.connection.commit()

                
                FECHA = date.today()
                correo(data,FECHA,1)

                return redirect(url_for('tabla', fechainiciall = fechainicial, fechafinall = fechafinal))

####################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################


@app.route('/administracion', methods = ['GET',"POST"]) ######################################################################
def admin():   

    if not session:
        return redirect(url_for('login_admin'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('asesores', estados = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            fi = request.form['fi']
            ff= request.form['ff']

            if (fi!= None and ff != None):

                fii = fi.replace("-","")
                fff = ff.replace("-","")

                return redirect(url_for('tabla', fechainiciall = fii, fechafinall = fff))


        return render_template('administrador.html', data = dicc)


def extension(filename):
    if not "." in filename:
        return 5
    
    ext = filename.rsplit(".",1)[1]

    if ext.upper() in ["PDF"]:
        return True
    else:
        return False

@app.route('/asesores/<estados>', methods = ['GET',"POST"]) ######################################################################
def asesores(estados):

    if estados != session['estado']:
        return redirect(url_for('asesores', estados = session['estado']))

    if not session:
        return redirect(url_for('login_asesores'))

    else:
        dicc = {
                'estados': session['estado'],
                'usuario': session['nombre']
            }
        

        if request.method == 'POST':
            ascesor = request.form['ascesor']
            nombre_cliente= request.form['nombre_cliente']
            numero_tarjeta=request.form['numero_tarjeta']
            monto = request.form['monto']
            retorno_cliente = request.form['retorno_cliente']
            retorno_ascesor = request.form['retorno_ascesor']
            banco = request.form['banco']
            clabe = request.form['clabe']
            ine = request.files['ine']
            solicitud = request.files['solicitud']
            estado = request.files['estado_cuenta']

            if (extension(ine.filename) == False) or (extension(solicitud.filename) == False) or (extension(estado.filename) == False):
                flash("extension incorrecta")
                return redirect(url_for('asesores', estados = session['estado']))

            Nine = numero_tarjeta + "_" + "ine.pdf"
            Nsolicitud = numero_tarjeta + "_" + "solicitud.pdf"
            Nestado_cuenta = numero_tarjeta + "_" + "estado_cuenta.pdf"

            ine.save(os.path.join(app.config["IMAGE"], Nine))
            solicitud.save(os.path.join(app.config["IMAGE"], Nsolicitud))
            estado.save(os.path.join(app.config["IMAGE"], Nestado_cuenta))

            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO prueba_3(ascesor, nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor, banco,clabe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (ascesor,nombre_cliente,numero_tarjeta,monto,retorno_cliente,retorno_ascesor,banco,clabe))
            mysql.connection.commit()

            #cur = mysql.connection.cursor()
            #cur.execute('INSERT INTO prueba_3(ascesor, nombre_cliente, numero_tarjeta, monto, retorno_cliente, retorno_ascesor, banco,#clabe,ine,solicitud,estado_de_cuenta) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            #(ascesor,nombre_cliente,numero_tarjeta,monto,retorno_cliente,retorno_ascesor,banco,clabe,Nine,Nsolicitud,Nestado_cuenta))
            #mysql.connection.commit()

        return render_template('asesores.html', data = dicc)
                
@app.route('/doc/<numero>')   ######################################################################
def imagenes(numero):

    if not session:
        return redirect(url_for('login_admin'))

    elif session['estado'] != 'administrador':
        return redirect(url_for('asesores', estados = session['estado']))

    else:
        dicc = {
            "url" : numero
        }

        return render_template('doc.html', data = dicc)

@app.route('/graficas')   ######################################################################
def graficas():

    if not session:
        return redirect(url_for('login_graficas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('asesores', estados = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        return render_template('graficas.html', data = dicc)

        
@app.route('/tabla/<fechainiciall>/<fechafinall>') ######################################################################
def tabla(fechainiciall,fechafinall): 

    if not session:
        return redirect(url_for('login_graficas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('asesores', estados = session['estado']))

    else:
        dicc = {
            'usuario' : session['nombre'],
            'fechainicial' : fechainiciall,
            'fechafinal' : fechafinall
            }  

        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM prueba_3 WHERE fecha BETWEEN {} AND {}'.format(fechainiciall,fechafinall))
        data = cur.fetchall() 

        fechas = {
            'fecha_inicial' : fecha(fechainiciall),
            'fecha_final' : fecha(fechafinall)
        }

        return render_template('tabla.html', data = dicc, contacts = data, FECHAS = fechas)

@app.route('/facturas', methods = ['GET',"POST"]) ######################################################################
def facturas():

    if not session:
        return redirect(url_for('login_asesores'))

    else:
        dicc = {
                'usuario': session['nombre']
            }
        

        return render_template('facturas.html', data = dicc)

@app.route('/graph')
def graph():

    dicc = { 'numero' : 10}

    return render_template('graph.html', num = dicc)

##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/factura-asesores', methods = ['GET',"POST"])
def factura_asesores():
    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre']
        }

        return render_template('factura-asesores.html', data = dicc)

@app.route('/factura-administrativa', methods = ['GET',"POST"])
def factura_admin():
    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre']
        }

        return render_template('factura-administrativa.html', data = dicc)


@app.route('/subir-factura-b', methods = ['GET',"POST"])
def subir_factura_b():
    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            number_target = request.form['number_target']

            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM prueba_3 WHERE numero_tarjeta="{}"'.format(number_target))
            data = cur.fetchall() 
            
            if len(data) == 0:
                flash('Numero de tarjeta no encontrado', 'warning')
                return redirect(url_for('subir_factura_b', target = number_target))

            return redirect(url_for('subir_factura', target = number_target))


        return render_template('subir-factura-b.html', data = dicc)

@app.route('/subir-factura/<target>', methods = ['GET',"POST"])  #######################################################################
def subir_factura(target):

    if not session:
        return redirect(url_for('login_facturas'))
    
    elif session['estado'] != 'administrador':
        return redirect(url_for('facturas'))  ## descargar facturas

    else:
        dicc = {
            'usuario' : session['nombre'],
            'target' : target
        }
        if request.method == 'POST':

            for i in range(1,10):
                facturas = request.files['factura{}'.format(str(i))]
                
                if ((extension(facturas.filename) == False)):
                    flash("extension incorrecta")
                    return redirect(url_for('subir_factura', target = target))

                if ((extension(facturas.filename) == True)):
                    Nfactura = target + "_" + "factura{}.pdf".format(str(i))

                    facturas.save(os.path.join(app.config["FACTURAS"], Nfactura))
                    
                if i == 9:
                    flash("¡Factura enviada exitosamente!", "success")
                    return redirect(url_for('subir_factura_b'))
                
            folio = request.form['folio']
        

        return render_template('subir-factura.html', data = dicc)


@app.route('/descargar-factura-b', methods = ['GET',"POST"])
def descargar_factura_b():

    if not session:
        return redirect(url_for('login_facturas'))

    else:
        dicc = {
            'usuario' : session['nombre']
        }
        if request.method == 'POST':
            number_target = request.form['number_target']

            return redirect(url_for('descargar_factura', target = number_target))


        return render_template('descargar-facturas-b.html', data = dicc)


@app.route('/desargar-factura/<target>')  #######################################################################
def descargar_factura(target):

    if not session:
        return redirect(url_for('login_facturas'))

    else:
        dicc = {
            'usuario' : session['nombre'],
            'target' : target
        }
        

        return render_template('descargar-facturas.html', data = dicc)

##########################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################################

@app.route('/salir') ######################################################################
def salir():
    return redirect(url_for('index'))

def error_404(error): ######################################################################
    session.clear()
    return render_template('error.html'), 404


def login(nombre,passw):        ## función para revisar que la cuenta exxista y sea valida

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE name="{}"'.format(nombre))
    data = cur.fetchall() 


    if data[0][3] == passw:
        if data[0][4] == "44":
            estado = data[0][5]
            return([1,estado])

        else:
            return([2,'administrador'])

    else:
        return([0,'No hay'])

def privilegios(nombre):        ## función sólo para revisar privilegios sin recibir contraseña
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE name="{}"'.format(nombre))
    data = cur.fetchall() 


    if data[0][4] == "44":
        estado = data[0][5]
        return([1,estado])

    else:
        return([2,'administrador'])


def fecha(num):         ## función para poder desplegar la fecha bonita y no con los digitos pegados

    new_num = list(num)

    año = (''.join(new_num[0:4]))
    mes = (''.join(new_num[4:6]))
    dia = (''.join(new_num[6:9]))

    fecha = [año, mes, dia]
    fecha = ('-'.join(fecha))

    return(fecha)

def correo(data,fecha,operacion):


    if fecha == app.config["FECHA_ENVIO"]:

        print("SE ENVIA CORREO")

        td = timedelta(1)
        app.config["FECHA_ENVIO"] = fecha + td
        file = open("Info.txt","w")
        file.write("CAMBIOS EN LA BASE DE DATOS DEL " + fecha.strftime('%d-%m-%Y') + " al " + app.config["FECHA_ENVIO"].strftime('%d-%m-%Y') + "\n\n")
        file.close()

    file = open("Info.txt","a")
    
    if operacion == 1:
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM prueba_3 WHERE id = {}'.format(data[0][0]))
        data2 = cur.fetchall()

        file.write("Los datos: \n")
        file.write("Id: % s"%data[0][0] + ", Fecha de registro: " + data[0][1].strftime('%d-%m-%Y') + ", Ascesor: " + data[0][2] + ", Nombre de cliente: " + data[0][3] + ", Numero de tarjeta: % s"%data[0][4] + ", Monto del vale: % s"%data[0][5] + ", Retorno del cliente: % s"%data[0][6] + ", Retorno del ascesor: % s"%data[0][7] + ", Banco: " + data[0][8] + ", CLABE interbancaria: % s"%data[0][9] + "\n \n")

        file.write("Fueron editados POR: \n")

        file.write("Id: % s"%data2[0][0] + ", Fecha de registro: " + data2[0][1].strftime('%d-%m-%Y') + ", Ascesor: " + data2[0][2] + ", Nombre de cliente: " + data2[0][3] + ", Numero de tarjeta: % s"%data2[0][4] + ", Monto del vale: % s"%data2[0][5] + ", Retorno del cliente: % s"%data2[0][6] + ", Retorno del ascesor: % s"%data2[0][7] + ", Banco: " + data2[0][8] + ", CLABE interbancaria: % s"%data2[0][9] + "\n \n")

        file.write("El dia " + fecha.strftime('%d-%m-%Y') + " por el usuario " + session["nombre"] + "\n\n")

        file.close()

    if operacion == 0:
        file.write("Datos que fueron eliminador el dia " + fecha.strftime('%d-%m-%Y') + " por el usuario " + session["nombre"] + ":\n")
        file.write("Id: % s"%data[0][0] + ", Fecha de registro: " + data[0][1].strftime('%d-%m-%Y') + ", Ascesor: " + data[0][2] + ", Nombre de cliente: " + data[0][3] + ", Numero de tarjeta: % s"%data[0][4] + ", Monto del vale: % s"%data[0][5] + ", Retorno del cliente: % s"%data[0][6] + ", Retorno del ascesor: % s"%data[0][7] + ", Banco: " + data[0][8] + ", CLABE interbancaria: % s"%data[0][9] + "\n \n")
        file.close()

    return 1



if __name__ == '__main__': ######################################################################
    app.register_error_handler(404, error_404)
    app.run(debug=True, port=5000)

