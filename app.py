from flask import Flask, render_template, request
import jsonify
import requests
import pickle
import numpy as np
import pandas as pd
import sklearn  #here sklearn=0.22 version is installed. v0.31 gives error
app = Flask(__name__)

#make sure you have installed gunicorn in this env

#loading pickle files
model = pickle.load(open('rf_final.pkl', 'rb'))
transformer = pickle.load(open('kms_present_transformer.pkl','rb'))
encoder = pickle.load(open('leave_one_out_encoder.pkl','rb'))


@app.route('/',methods=['GET'])
def Home():
    return render_template('index.html')



@app.route("/predict", methods=['POST'])
def predict():
    
    if request.method == 'POST':
        
        Merk_Mobil = request.form['vehicle_name']
        d = pd.DataFrame({'Merk_Mobil':[Merk_Mobil]})
        
        #Encoding car name
        encode = encoder.transform(d['Merk_Mobil'])
        Merk_Mobil = encode['Merk_Mobil']
        
        #year
        Tahun = int(request.form['Tahun'])
        Usia=2022-Tahun
        
        
        Harga_Saat_Ini=float(request.form['Harga_Saat_Ini'])
        Kilometer=int(request.form['Kilometer'])
        
        #tranforming the kms and present value
        transform = transformer.transform([[Kilometer,Harga_Saat_Ini]])
        Kilometer = transform[0][0]
        Harga_Saat_Ini = transform[0][1]
        
        
        Kepemilikan=int(request.form['Kepemilikan'])
        Jenis_Bahan_Bakar_Solar=0
        Jenis_Bahan_Bakar=request.form['Jenis_Bahan_Bakar']
        if(Jenis_Bahan_Bakar=='Bensin'):
                Jenis_Bahan_Bakar_Solar=1
        else:
            Jenis_Bahan_Bakar_Solar=0

        Tipe_Penjual=request.form['Tipe_Penjual']
        if(Tipe_Penjual=='Individual'):
            Tipe_Penjual_Individual=1
        else:
            Tipe_Penjual_Individual=0

        Transmisi =request.form['Transmisi']
        if(Transmisi =='Manual'):
            Transmisi_Manual=1
        else:
            Transmisi_Manual=0

        prediction=model.predict([[Merk_Mobil,Jenis_Bahan_Bakar_Solar,Tipe_Penjual_Individual,Transmisi_Manual,Kilometer,Harga_Saat_Ini,Kepemilikan,Usia]])
        output=round(prediction[0],2)
        if output<0:
            return render_template('index.html',prediction_texts="Maaf! Anda tidak dapat menjual kendaraan ini.")
        else:
            return render_template('index.html',prediction_text="Anda dapat menjual mobil ini seharga {} juta rupiah".format(output))
    else:
        return render_template('index.html')

if __name__=="__main__":
    app.run(debug=True)