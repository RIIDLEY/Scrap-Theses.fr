import time
import csv
import sys
from urllib import response
import requests
from bs4 import BeautifulSoup

url = 'http://www.theses.fr/fr/?q='
url_racine = "http://www.theses.fr"

url_navig_debut = url + "&fq=dateSoutenance:[1965-01-01T23:59:59Z%2BTO%2B2022-12-31T23:59:59Z]&checkedfacets=&start="
url_navig_end = "&sort=none&status=&access=&prevision=&filtrepersonne=&zone1=titreRAs&val1=&op1=AND&zone2=auteurs&val2=&op2=AND&zone3=etabSoutenances&val3=&op3=AND&zone4=dateSoutenance&val4a=&val4b=&type="


def init():#Création d'un lien dynamique en fonction de la recherche courante
    sys.argv.pop(0)
    if(len(sys.argv)==0):
        print("Il manque les mots clés pour effectuer la recherche.")
    else:    
        scrap_links(url+"+".join(sys.argv))

def scrap_links(url):#Collecte le lien de toutes les theses

    links = []
    reponse = requests.get(url)#Recupere la première page
    soup = BeautifulSoup(reponse.text, "html.parser")

    try:#Verifie s'il y a un résultat à la recherche demandée
        nbthese = int(soup.find("span", {"id": "sNbRes"}).text)
    except:
        print("Aucun document ne correspond à la recherche")
        return

    print("Il y'a " + str(nbthese) + " thèses.\nCollecte en cours.")

    for i in range(0, nbthese, 10):  #Navige entre les pages

        url_page = url_navig_debut + str(i) + url_navig_end #Création du lien de la page a traiter
        reponse = requests.get(url_page)#Recupere l'html de la page

        if reponse.ok:#Si la collecte a fonctionné

            soup = BeautifulSoup(reponse.text, "html.parser")

            div = soup.find_all("div", {"class": "encart arrondi-10"})#Selectionne la div où il y'a les informations

            for info in div:
                a = info.find("a")
                link = a['href']#recupere le lien de la these
                links.append(url_racine+link)#L'ajoute dans le tableau

            print("Les liens de la page " + str(int(i/10)+1) + " ont été collecté.")
            time.sleep(1)#Attend 1 second avant de passer à la page suivante pour pas se faire bloquer par le site

    get_meta_in_link(links)#Passe a la collecte de metadonnées


def get_meta_in_link(links):#Collecte les métadonnées de toute les thèses courantes

    print("===========================================")
    print("Création du CSV")
    i = 1

    with open('scrap.csv', 'w', encoding='utf8') as fileCSV:#Création du CSV

        fieldnames = ['Titre', 'Lien', 'Auteur', 'Mots clés','Description','Information complémentaire']#Colonne du CSV
        writer = csv.DictWriter(fileCSV, fieldnames=fieldnames)
        writer.writeheader()#Ecrit les colonnes dans le fichier CSV

        for link in links:
            reponse = requests.get(link.strip())#Recupere le html de la page
            if reponse.ok:
                soup = BeautifulSoup(reponse.text, "html.parser")
                keyword_to_CSV = ""

                titre = soup.find("h1", {"property": "dc:title"}).text.replace(","," ")#Recupere le titre
                auteur = soup.find("span", {"property": "foaf:name"}).text#Recupere le nom et prénom de l'auteur
                description = soup.find("span", {"property": "dc:description"}).text.replace(","," ")#Recupere la description
                info = soup.find("div", {"id": "ficheTitre"}).findAll("div", {"class":"donnees-ombre"})#Recupere les informations complémentaires
                

                if(len(info)==0):#S'il y'a pas d'information complémentaire
                    infoCSV = 'None'
                else:
                    infoCSV = ''.join(info[1].text.splitlines()).replace(","," ")#Prepare une chaine de caractere pour le CSV

                try:#Essaie de collecter les mots clés
                    keyword_list = soup.find("ul", {"class": "mots"}).findAll("span", {"about": link+"/id", "property": "dc:subject"})
                except AttributeError:#s'il n'y en a pas
                    keyword_to_CSV = "None"

                if (len(keyword_list)>0):#S'il y'a des mots clés
                    for keyword in keyword_list:
                        keyword_to_CSV = keyword_to_CSV + "| " + keyword.text.strip().replace(","," ")#Prepare une chaine de caractere pour le CSV

                writer.writerow({'Titre': titre, 'Lien': link, 'Auteur': auteur, 'Mots clés': keyword_to_CSV, 'Description': description, 'Information complémentaire': infoCSV})
                print("These numéro : " + str(i) + " | " + link + " Done")
                i+=1

init()