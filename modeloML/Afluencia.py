import os
directorio = '/home/alfie-gonzalez/Documentos/Maestría/Segundo Semestre/Métodos de Gran Escala'
os.chdir(directorio)

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

X = pd.read_csv('afluencia-diaria-del-metro-cdmx.csv') #IFE

def rmse(y, pred):
    return(np.sqrt(np.mean((y-pred)**2)))

def categorias(x, y): #Al empezar modelado #EN EL MODELADO
    n = len(x) #EN EL MODELADO
    z = np.array(x, dtype = str) #EN EL MODELADO
    q25 = np.quantile(y, 0.25) #EN EL MODELADO
    q75 = np.quantile(y, 0.75) #EN EL MODELADO
    z[x <= q25] = 'Bajo' #EN EL MODELADO
    z[(x >= q25) & (x <= q75)] = 'Normal' #EN EL MODELADO
    z[x >= q75] = 'Alto' #EN EL MODELADO
    return(z) #EN EL MODELADO

X['Fecha'] = pd.to_datetime(X['Fecha'])     #IFE
X['Dia'] = pd.DatetimeIndex(X['Fecha']).day.astype('object')
X['Mes'] = pd.DatetimeIndex(X['Fecha']).month.astype('object')
X['Dia_Semana'] = (pd.DatetimeIndex(X['Fecha']).weekday + 1).astype('object') #FFE

variables_categoricas = X.dtypes.pipe(lambda x: x[x == 'object']).index     #Sí va en FE

num_cols = X.dtypes.pipe(lambda x: x[x != 'object']).index
for x in num_cols:
    imp = SimpleImputer(missing_values = np.nan, strategy = 'median')
    imp.fit(np.array(X[x]).reshape(-1, 1))
    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))

nominal_cols = X.dtypes.pipe(lambda x: x[x == 'object']).index
for x in nominal_cols:
    imp = SimpleImputer(missing_values = np.nan, strategy = 'most_frequent')
    imp.fit(np.array(X[x]).reshape(-1, 1))
    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))

x_mat = pd.get_dummies(X, columns = variables_categoricas, drop_first = True)   #FFE

#Inicio de modelado

indice_ent = X['Fecha'] <= '2019-11-30'        #Va en modelado

variables_a_eliminar = ['Fecha', 'Año', 'Afluencia']    #Va en modelado

x_ent = x_mat[indice_ent].drop(variables_a_eliminar, axis = 1)
x_pr = x_mat[~indice_ent].drop(variables_a_eliminar, axis = 1)
y_ent = categorias(x_mat['Afluencia'][indice_ent], 
                   x_mat['Afluencia'][indice_ent])
y_pr = categorias(x_mat['Afluencia'][~indice_ent], 
                  x_mat['Afluencia'][indice_ent])

def modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc):

    y_ent1 = np.where(y_ent == cat, 1, 0)
    y_pr1 = np.where(y_pr == cat, 1, 0)

    modelo = LogisticRegression()
    modelo.fit(x_ent, y_ent1)

    pred = modelo.predict_proba(x_pr)[:,1]
    prob = pred.copy()
    pred = np.where(pred >= sc, 1, 0)
    TP = np.sum((pred == 1) & (y_pr1 == 1))
    TN = np.sum((pred == 0) & (y_pr1 == 0))
    FP = np.sum((pred == 1) & (y_pr1 == 0))
    FN = np.sum((pred == 0) & (y_pr1 == 1))

    accuracy = (TP+TN)/(TP+TN+FP+FN)

    precision = TP/(TP+FP)

    recall = TP/(TP+FN)

    a = {'modelo':modelo, 'pred':pred, 'prob':prob, 
         'accuracy':accuracy, 'precision':precision, 'recall':recall}
    return(a)

cat = 'Bajo'
sc = 0.56
modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)

modelo['accuracy']
modelo['precision']
modelo['recall']
pred_bajo = modelo['pred']
prob_bajo = modelo['prob']

cat = 'Normal'
sc = 0.50
modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)

modelo['accuracy']
modelo['precision']
modelo['recall']
pred_normal = modelo['pred']
prob_normal = modelo['prob']

cat = 'Alto'
sc = 0.50
modelo = modelo_cat(cat, x_ent, y_ent, x_pr, y_pr, sc)

modelo['accuracy']
modelo['precision']
modelo['recall']
pred_alto = modelo['pred']
prob_alto = modelo['prob']

def pred_final(pred_bajo, prob_bajo, 
               pred_normal, prob_normal, 
               pred_alto, prob_alto):

    n = len(pred_normal)
    pred_final = np.array(pred_normal, dtype = str)
    pred = pd.DataFrame({'Bajo':pred_bajo, 
                         'Normal':pred_normal, 
                         'Alto':pred_alto})
    prob = pd.DataFrame({'Bajo':prob_bajo, 
                         'Normal':prob_normal, 
                         'Alto':prob_alto})
    
    for i in np.arange(1, n+1):
        if pred.iloc[i-1, :].sum() == 1:
            pred_final[i-1] = pred.iloc[i-1, :].idxmax()
        else:
            pred_final[i-1] = prob.iloc[i-1, :].idxmax()
    
    return(pred_final)

pred_f = pred_final(pred_bajo, prob_bajo, 
               pred_normal, prob_normal, 
               pred_alto, prob_alto)

conf = pd.DataFrame(confusion_matrix(y_pr, pred_f), 
                    index = ['real Bajo', 'real Normal', 'real Alto'], 
                    columns = ['pred Bajo', 'pred Normal', 'pred Alto'])
conf

accuracy = np.sum(np.diag(conf))/np.sum(conf).sum()
accuracy

X['Fecha'] = pd.to_datetime(X['Fecha'])     #IFE
X['Dia'] = pd.DatetimeIndex(X['Fecha']).day.astype('object')
X['Mes'] = pd.DatetimeIndex(X['Fecha']).month.astype('object')
X['Dia_Semana'] = (pd.DatetimeIndex(X['Fecha']).weekday + 1).astype('object') #FFE

variables_categoricas = X.dtypes.pipe(lambda x: x[x == 'object']).index     #Sí va en FE

num_cols = X.dtypes.pipe(lambda x: x[x != 'object']).index
for x in num_cols:
    imp = SimpleImputer(missing_values = np.nan, strategy = 'median')
    imp.fit(np.array(X[x]).reshape(-1, 1))
    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))

nominal_cols = X.dtypes.pipe(lambda x: x[x == 'object']).index
for x in nominal_cols:
    imp = SimpleImputer(missing_values = np.nan, strategy = 'most_frequent')
    imp.fit(np.array(X[x]).reshape(-1, 1))
    X[x] = imp.transform(np.array(X[x]).reshape(-1, 1))

x_mat = pd.get_dummies(X, columns = variables_categoricas, drop_first = True)   #FFE