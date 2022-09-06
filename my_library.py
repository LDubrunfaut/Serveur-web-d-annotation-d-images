#!/usr/bin/env python
# -*- coding:utf-8 -*-
################################################################################
import PIL
import sqlite3
import os
import random
import re
import pygame
import my_library as ml
from flask import Flask, request, flash, redirect, url_for, render_template
from flask import send_file
from PIL import Image, ImageDraw
################################################################################
COLORS =[]
DOSSIER_UPS = 'static/images/'
################################################################################
# Génère des couleurs aléatoires :
def generate_new_color(COLORS):
    ''' 
        Fonction permettant de générer aléatoirement des couleurs en code rgb.
        
        Args : COLORS : Liste des couleurs déjà existantes 
        
        Returns : new_color : Tuple de la couleur générée en code rgb 
                        exemple : (0,255,0)
    '''
    r=random.randint(1,255)
    g=random.randint(1,255)
    b=random.randint(1,255)
    new_color=(r,g,b)
    if new_color not in COLORS :
        COLORS.append(new_color)
        return new_color
    else :
        return generate_new_color(COLORS)


# Fonction import from :
# https://openclassrooms.com/courses/creez-vos-applications-web-avec-flask/tp-service-web-d-upload-d-images
# Verification de l'extension du fichier image envoyé
def extension_ok_image(nom_imgfic):
    ''' 
        Fonction permettant de vérifier que l'extension de l'image est autorisée
        Extensions autorisées : png, jpg, jpeg, gif, bmp
        
        Args : nom_imgfic : Chaîne de caractères contenant le nom de l'image
            
        Returns : Booléen avec TRUE si l'extension et correct et FALSE sinon
    '''
    extension=('png', 'jpg', 'jpeg', 'gif', 'bmp')
    return '.' in nom_imgfic and nom_imgfic.rsplit('.', 1)[1] in extension


# Verification de l'extension du fichier protocole ou analyse envoyé
def extension_ok_fic(nom_imgfic):
    ''' 
        Fonction permettant de vérifier que l'extension du fichier est autorisée
        Extensions autorisée : pdf
        
        Args : nom_imgfic : Chaîne de caractères contenant le nom du fichier
            
        Returns : Booléen avec TRUE si l'extension et correct et FALSE sinon
    '''
    return '.' in nom_imgfic and nom_imgfic.rsplit('.', 1)[1] in ('pdf')


# Fonction import from :
# http://stackoverflow.com/questions/12020821/python-int-function
# Fonction permettant de convertir un string en int ou float
def interpret_string(s):
    ''' 
        Fonction permettant de convertir un string en int et si ce n'est pas. 
        possible renvoie None 
        
        Args : s : Chaîne de caractères à convertir en int
        
        Returns : Int si c'est possible et sinon None
    '''
    if s.isdigit():
        return int(s)
    else :
        return None


# Fonction import from :
# https://opensource.com/life/15/2/resize-images-python
# Redimensionne l'image
def resize(path_img, path_thumb):
    ''' 
        Fonction permettant de redimensionner une image passée en argument en
        une miniature que l'on sauvegarde.
        
        Args :
            path_img : Chaîne de caractères contenant le chemin de l'image
            path_thumb : Chaîne de caractères contenant le chemin où on souhaite
                         enregistrer la miniature
        
        Returns : 
            path_thumb : Chaîne de caractères contenant le chemin où on souhaite
                         enregistrer la miniature
    '''
    basewidth = 150
    img = Image.open(path_img)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save(path_thumb)


# Fonction permettant de nettoyer les mots clés.
def clean_kw(kw):
    ''' 
        Fonction permettant à partir d'une chaîne de caractère d'isoler les mots
        en considérant les ";" et espaces comme séparateurs de mots clés. 
        Ensuite ne conserve que les mots comportant descaractères 
        alphanumériques et des "-".
        
        Args : kw : Chaîne de caractères contenant un ou plusieurs mots
        
        Returns : keywords : Liste des mots ayant été conservés.
            
    '''
    keywords = []
    # On interprète le ; comme un séparateur de mots clés
    kw=kw.replace(";"," ")
    liste_key=kw.split()
    alphanum = re.compile('^[a-zA-Z0-9][ A-Za-z0-9_-]*$')
    for word in liste_key :
        # Ne veut conserver que des termes alphanumériques
        res = alphanum.search(word)
        if res != None :
            keywords.append(word.lower())
    return keywords


# Fonction permettant d'afficher les annotations dans la DB
def showano(nom_img,path_thumb):
    ''' 
        Fonction permettant de récupérer dans une liste de dictionnaires, les 
        informations des annoations associées à l'image passée en argument. 
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
            path_thumb : Chaîne de caractères contenant le chemin où on souhaite
                         enregistrer la miniature
        
        Returns : liste_annotations : Liste des dictionnaires correspondants à
                                      l'ensemble des informations de chaque 
                                      annoation.
            
    '''
    liste_annotations = []
    conn = sqlite3.connect('data.db')
    # On cherche dans la table des annotations s'il en existe pour cette image
    cursor = conn.execute('''SELECT CREATION_DATE,MODIFICATION_DATE,ANNOTATION, 
    AUTEUR, ID, NAME_IMG, COLOR_R, COLOR_G, COLOR_B from ANNOTATION WHERE 
    NAME_IMG = ?''',(nom_img,));
    # Pour chaque annotation on récupère les informations voulues
    for row in cursor:
        annotation = {}
        annotation['creation_date'] = row[0]
        annotation['modification_date'] = row[1]
        annotation['keywords'] = row[2].rsplit(';')
        annotation['auteur'] = row[3]
        annotation['id'] = row[4]
        annotation['nom_img'] = row[5]
        annotation['path_thumb'] = path_thumb
        annotation['color_r'] = row[6]
        annotation['color_g'] = row[7]
        annotation['color_b'] = row[8]
        liste_annotations.append(annotation)
    conn.commit()
    conn.close()
    return liste_annotations


# Fonction permettant d'afficher les informations associées à une image de la DB
def showimg(cursor_object,liste):
    ''' 
        Fonction permettant de récupérer dans une liste de dictionnaires, les 
        informations de l'image ou des images contenues dans la liste passée en
        argument. Permet également d'optenir les informations sur les
        annotations de chaque image si elles en ont. 
        
        Args : 
            cursor_object : objet de type cursor object contenant le ou les 
                            résultat(s) d'une requête sql.
            liste : Chaîne de caractère qui vaut 'liste' dans le cas où l'objet 
                    cursor contient plusieurs lignes de résultat.
        
        Returns : image : Liste des dictionnaires correspondants à l'ensemble 
                          des informations de chaque image ainsi que des 
                          annoations associées à chacune d'elles.
            
    '''
    if liste=='liste':
        cursor_object=[cursor_object]
    image = {}
    for row in cursor_object:
        image['id'] = row[0]
        image['nom_img'] = row[1]
        image['path_image'] = row[2]
        image['path_thumb'] = row[3]
        image['path_ano'] = row[4]
        image['creation_date'] = row[5]
        image['modification_date'] = row[6]
        image['keywords'] = row[7].rsplit(';')
        image['auteur'] = row[8]
        image['id_examen'] = row[9]
        image['annotations']=showano(image['nom_img'],image['path_thumb'])
    return image


# Fonction permettant de dessiner les rectangles d'annotation sur l'image
def draw_ano(nom_img,path,x1,y1,h,w):
    ''' 
        Fonction permettant de dessiner sur une image passée en argument, un 
        rectangle dont les coordonnées sont également fournies en argument.
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
            path : Chaîne de caractères contenant le chemin de l'image sur
                   laquelle on souhaite dessiner.
            x1, y1 : Coordonnées de l'angle supérieur gauche du rectangle à
                     dessiner.
            h : Hauteur du rectangle à dessiner
            w : Largeur du rectangle à dessiner
        
        Returns : 
            path_ano : Chaîne de caractères contenant le chemin de l'image sur
                       laquelle a été dessiné le rectangle.
            col : Tuple de la couleur générée en code rgb exemple : (0,255,0)
            
    '''
    im = pygame.image.load(path)
    col=generate_new_color(COLORS)
    pygame.draw.rect(im, col, (x1,y1,w,h), 4)
    path_ano = DOSSIER_UPS+'ano/'+nom_img
    pygame.image.save(im, path_ano)
    return (path_ano,col)


# Fonction qui met à jour l'image des annotations
def update_ano(nom_img):
    ''' 
        Fonction de mettre à jour l'image d'annotation lorsqu'une annotation
        vient d'être supprimée.
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
        
        Returns : 
            path_ano : Chaîne de caractères contenant le chemin de l'image sur
                       laquelle a été dessiné le rectangle.
            
    '''
    conn = sqlite3.connect('data.db')
    cursor = conn.execute('''SELECT PATH_IMAGE from IMAGE WHERE NAME = ?''',
    (nom_img,));
    for row in cursor :
        path = row[0]
    cursor = conn.execute('''SELECT X1,Y1,H,W,ID from ANNOTATION WHERE 
    NAME_IMG = ?''',(nom_img,));
    for row in cursor :
        x1 = row[0]
        y1 = row[1]
        h = row[2]
        w = row[3]
        id_ano = row[4]
        path_and_color = draw_ano(nom_img,path,x1,y1,h,w)
        path_ano=path_and_color[0]
        conn.execute('''UPDATE ANNOTATION set COLOR_R = ?, COLOR_G = ?, 
        COLOR_B = ? WHERE ID = ?''',(path_and_color[1][0],
        path_and_color[1][1],path_and_color[1][2],id_ano));
        conn.commit()
    return path_ano

# Fonction permettant de faire une recherche de type and
def andsearch(keys_s,type_obj):
    ''' 
        Fonction de réaliser une recherche des mots clés avec l'option and, soit
        rechercher pour l'ensemble des mots clés saisis les images qui ont
        exactement tous les mots clés entrés.
        
        Args : 
            keys_s : Chaîne de caractères contenant un ou plusieurs mots
            type_obj : Chaîne de caractères indiquant s'il s'agit d'une 
                       recherche d'objets de type image ou d'objets de type 
                       annotation
        
        Returns : 
            liste_id_ok : Liste contenant l'ensemble des id image ou annotation
                          qui ont exactement tous les mots clés de keys_s
            
    '''
    # Le nombre de mots qui doivent matcher
    score=len(keys_s)
    liste_match=[]
    id_connu=[0]
    conn = sqlite3.connect('data.db')
    # Pour chaque mot clé les images ou annotations avec lesquelles il match
    for word in keys_s :
        # Dans ce cas on ne veut pas de doublon mais seulement au sein d'une 
        # meme requete mot
        no_doublon=[0]
        if type_obj == 'img' :
            cursor = conn.execute('''SELECT ID from IMAGE WHERE KEYWORDS LIKE ?
            ''',("%"+word+"%",));
        else :
            cursor = conn.execute('''SELECT ID from ANNOTATION WHERE ANNOTATION 
            LIKE ?''',("%"+word+"%",));
        for row in cursor:
            # On supprime les possibles doublons dans la recherche
            if row[0] not in no_doublon :
                no_doublon.append(row[0])
                # Si c'est la première fois qu'on rencontre cette ID image ou 
                # annotation
                if row[0] not in id_connu :
                    match_id={}
                    match_id['id']=row[0]
                    match_id['score']=1
                    liste_match.append(match_id)
                    id_connu.append(row[0])
                # Si on connait déjà cet ID image
                else : 
                    for dico in liste_match:
                        if dico['id'] == row[0] :
                            dico['score'] = dico['score'] +1
                            break
        conn.commit()            
    # On a regardé pour tous les mots clés, on regarde maintenant combien
    #d'image ont eu le score attendu pour avoir matché avec toutes les images
    liste_id_ok = []
    for dico in liste_match:
        if dico['score'] == score :
            liste_id_ok.append(dico['id'])
    conn.close()
    return liste_id_ok  

