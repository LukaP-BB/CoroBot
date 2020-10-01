#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import requests as req
import pandas as pd
from scipy import stats
import scipy.signal
import geopandas as gpd
import matplotlib.pyplot as plt
from interface import depFromCode
from analyse import timeFrame, loadData
import datetime as dtt

from io import StringIO

# a dict to format the dataframes
types = {
    "dep" : str,
    "jour" : str,
    "week" : str,
    "P" : "int",
    "T" : "int",
    "cl_age90" : "int",
}

urlDepistQuot = "https://www.data.gouv.fr/fr/datasets/r/406c6a23-e283-4300-9484-54e78c8ae675"
urlDonneeHosp = "https://www.data.gouv.fr/fr/datasets/r/63352e38-d353-4b54-bfd1-f1b3ee1cabd7"

def loadFromUrl(url):
    data = req.get(url).text
    ioData = StringIO(data)
    return pd.read_csv(ioData, delimiter=";", dtype=types)

def loadDf():
    df = pd.read_csv("data/tauxQuotDep.csv", delimiter=";", dtype=types)
    return df


def donnesDepistage(days=40, floatingMean=15):
    """réduit les données de dépistage en une valeur par département"""
    # chargement des données de dépistage
    df = loadFromUrl(urlDepistQuot)
    df = df[df.cl_age90 == 0]
    
    today = dtt.date.today()
    firsDay = dtt.timedelta(days=days)
    firsDay = today - firsDay
    df = timeFrame(df, firsDay.isoformat(), today.isoformat())

    # régression linéaire sur le timeframe pour les taux de contamination
    depDict = {}
    deps = list(pd.unique(df.dep))
    for dep in deps :
        subData = df[df.dep == dep]
        nb_jours = range(subData.count().jour)
        taux = subData.P/pd.to_numeric(list(subData.T))
        taux = taux.rolling(window=floatingMean, min_periods=1).mean()
        slope, intercept, rvalue, pvalue, stderr = stats.linregress(nb_jours, taux)
        depDict[depFromCode(dep)] = slope

    # transformation du dictionnaire en DataFrame
    df = pd.DataFrame(depDict.items())

    return df

def donnesHosp(days=40, floatingMean=15, type="hosp"):
    df = loadData()
    today = dtt.date.today()
    firsDay = dtt.timedelta(days=days)
    firsDay = today - firsDay
    df = timeFrame(df, firsDay.isoformat(), today.isoformat())

    # régression linéaire sur le timeframe pour les données hospitalières
    depDict = {}
    deps = list(pd.unique(df.dep))
    for dep in deps :
        subData = df[df.dep == dep]
        nb_jours = range(subData.count().jour)
        donnees = subData.dc
        slope, intercept, rvalue, pvalue, stderr = stats.linregress(nb_jours, donnees)
        depDict[depFromCode(dep)] = slope

    # transformation du dictionnaire en DataFrame
    df = pd.DataFrame(depDict.items())

    return df

def mapDepInfection(df):
    """Crée une carte des départements de France dont la couleur dépend des données dans le dataframe (départements, données) """
    # une petite fonction pour décoder les quelques départements récalcitrants
    def checkIfEnc(str):
        if isinstance(str, bytes) :
            return str.decode("iso-8859-1")
        else :
            return str

    # chargement des données géographiques
    map_df = gpd.read_file("gis/dep/departements-20140306-100m.shp", encoding="utf-8")
    # correction des problèmes de décodage (foutus accents)
    map_df.nom = map_df.nom.apply(checkIfEnc)
    print(len(map_df.nom))

    # rapprochement des départements d'outre-mer
    guyane = map_df.nom == "Guyane"
    reunion = map_df.nom == "La Réunion"
    mayotte = map_df.nom == "Mayotte"
    martinique = map_df.nom == "Martinique"
    guadeloupe = map_df.nom == "Guadeloupe"
    map_df[guyane] = map_df[guyane].set_geometry(map_df[guyane].translate(48, 40))
    map_df[martinique] = map_df[martinique].set_geometry(map_df[martinique].translate(54, 33))
    map_df[guadeloupe] = map_df[guadeloupe].set_geometry(map_df[guadeloupe].translate(54, 33))
    map_df[reunion] = map_df[reunion].set_geometry(map_df[reunion].translate(-50, 62))
    map_df[mayotte] = map_df[mayotte].set_geometry(map_df[mayotte].translate(-43, 54))

    # la base pour la map
    fig, ax = plt.subplots(1, figsize=(25, 25))

    # création de points pour afficher les noms des départements
    map_df["repr"] = map_df.representative_point()
    for x, y, name in zip(map_df.repr.x, map_df.repr.y, map_df.nom) :
        ax.annotate(name, xy=(x, y))

    # on merge les données de dépistage aux données géographiques
    merged = map_df.set_index("nom").join(df.set_index(0))
    # print(merged)
    
    # création d'une échelle
    vmin = df[1].min()
    vmax = df[1].max()
    print(vmin, vmax)
    sm = plt.cm.ScalarMappable(cmap="Reds", norm=plt.Normalize(vmin=vmin, vmax=vmax))
    # ax.set_facecolor("#d5ffff")
    cbar = fig.colorbar(sm)
    ax.axis("off")
    # création de la map
    merged.plot(ax=ax, column=1, cmap="Reds", linewidth=0.8, edgecolor='0.8')
    plt.savefig("fig.jpg", bbox_inches='tight')

def setAgeClass(df, age):
    df = df[df.cl_age90 == int(age)]
    return df

def plotGivenDep(dep:str, days:int=40, floatingMean=15):
    today = dtt.date.today()
    firsDay = dtt.timedelta(days=days)
    firsDay = today - firsDay
    df = loadFromUrl()

    # df = loadDf2()

    df = setAgeClass(df, "0")
    df = timeFrame(df, firsDay.isoformat(), today.isoformat())
    df = df[df.dep == str(dep)]

    # print(df)

    nb_jours = range(df.count().jour)
    taux = df.P/pd.to_numeric(list(df.T))
    taux = taux.rolling(window=floatingMean, min_periods=1).mean()
    slope, intercept, rvalue, pvalue, stderr = stats.linregress(nb_jours, taux)

    fig, ax = plt.subplots()
    ax.plot(df.jour, taux, label="Taux de tests positifs")

    ax.plot(nb_jours,
        nb_jours*slope + intercept,
        label=f"Pente : {round(slope, 5)} /jour\n\
rvalue : {round(rvalue, 2)}")

    ax.legend()
    ax.xaxis.set_major_locator(plt.MaxNLocator(5))
    ax.yaxis.set_major_locator(plt.MaxNLocator(10))
    plt.title(f"Evolution des taux de dépistages positifs : {depFromCode(dep)}")
    plt.savefig("fig.jpg")

if __name__ == '__main__':
    df = donnesHosp(days=90, floatingMean= 7)
    # df = donnesDepistage(days=days, floatingMean=floatingMean)
    mapDepInfection(df)
    # plotGivenDep("75")