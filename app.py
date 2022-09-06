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
app = Flask(__name__, template_folder='templates')
app.secret_key = "$d§u§n§n§o$"
DOSSIER_UPS = 'static/images/'
################################################################################
# Fonction permettant d'afficher la fiche de profil d'une image
@app.route('/<nom_img>/')
def picture_profil(nom_img):
    ''' 
        Fonction permettant de générer une vue des informations d'une image par
        la page profil_picture.html
        
        Args : nom_img : Chaîne de caractères contenant le nom de l'image
    '''
    conn = sqlite3.connect('data.db')
    # On recherche toutes les informations de l'image
    cursor = conn.execute("SELECT * FROM image WHERE name = ?",(nom_img,));
    # On spécifie que la requête ne renvoie qu'une image
    image=ml.showimg(cursor,'not_list')
    conn.commit()
    conn.close()
    return render_template('profil_picture.html', image=image)

# Fonction permettant d'afficher la home page
@app.route('/')
def homepage():
    ''' 
        Fonction permettant de générer une vue de la page home.html
    '''
    return render_template('home.html')

# Fonction permettant d'afficher la page des sources des images
@app.route('/sources/')
def sources():
    ''' 
        Fonction permettant de générer une vue de la page sources.html
    '''
    return render_template('sources.html')

@app.route('/search/result/<met>/<option_orand>/<option_wiwo>/<keys_search>/')
def result_search(keys_search,met,option_orand,option_wiwo):
    ''' 
        Fonction permettant de générer une vue des résultats de recherche
        (images ou annotations) dans la page result_search.html
        
        Args : 
            keys_search : Chaîne de caractères contenant le mots clés associés
                          à la recherche.
            met : Chaîne de caractères contenant la méthode de recherche
                  utilisée soit 'id', 'annotations' ou 'keywords'.
            option_orand : Chaîne de caractères contenant pour la méthode de 
                           recherche 'annotations' ou 'keywords', l'option 'or' 
                           ou l'option 'and'.
            option_orand : Chaîne de caractères contenant pour la méthode de 
                           recherche 'keywords', l'option 'wi' pour with 
                           annotation ou l'option 'wo' pour without annotation.
    '''
    conn = sqlite3.connect('data.db')
    liste_obj = []
    keys_s=keys_search.split(';')
    ############################################################################
    # Dans le cas de la recherche d'ID d'examen une seule méthode de recherche
    if met == 'id' :
        obj = 'img'
        # Pour chaque id examen on recherche toutes les informations de l'image
        for word in keys_s :
            if ml.interpret_string(word) != None :
                cursor = conn.execute('''SELECT * FROM image WHERE id_examen = ?
                ''',(word,));
                for row in cursor:
                    image=ml.showimg(row,'liste')
                    # S'il existe une image correspondant
                    if image != {} :
                        liste_obj.append(image)
                conn.commit()
            else :
                flash(u'Examination ID given is not integer !', 'error')
                break
    ############################################################################    
    #Dans le cas de la recherche d'images on a différentes méthodes de recherche
    elif met == 'keywords' :
        obj = 'img'
        no_doublon=[0]
        # On souhaite les images qui match avec le mot clé 1 ou le mot clé 2 ou 
        #le mot clé 3 [etc]
        if option_orand == 'or' :
            # Pour chaque mot clé entré en recherche, toutes les info de l'image
            for word in keys_s :
                # Si on veut sans annotations on prend les images qui n'ont 
                #aucune annotations
                if option_wiwo == 'wo' :
                    cursor = conn.execute('''SELECT * FROM image WHERE name NOT 
                    IN (SELECT name_img FROM annotation) AND keywords LIKE ?'''
                    ,("%"+word+"%",));
                # On veut les images qui ont des annotations et pas les autres
                elif option_wiwo == 'wi' :
                    cursor = conn.execute('''SELECT * FROM image WHERE name IN
                    (SELECT name_img FROM annotation) AND keywords LIKE ?'''
                    ,("%"+word+"%",));
                else :
                    cursor = conn.execute('''SELECT * FROM image WHERE keywords 
                    LIKE ?''',("%"+word+"%",));
                for row in cursor:
                    image=ml.showimg(row,'liste')
                    if image != {} :
                        # En vérifiant encore qu'on a pas de doublons
                        if image['id'] not in no_doublon :
                            no_doublon.append(image['id'])
                            liste_obj.append(image)
                conn.commit()
        # On souhaite les image qui match avec le mot clé 1 et le mot clé 2 et 
        #le mot clé 3 [etc]
        else :
            liste_id_ok=ml.andsearch(keys_s,obj)
            # Pour toutes ces images qui ont réussit le test on les affiche
            for id_img in liste_id_ok :
                # Si on veut sans annotations on prend les images qui n'ont 
                #aucune annotations
                if option_wiwo == 'wo' :
                    cursor = conn.execute('''SELECT * FROM image WHERE name NOT 
                    IN (SELECT name_img FROM annotation) AND id = ?'''
                    ,(id_img,));
                # On veut les images qui ont des annotations et pas les autres
                elif option_wiwo == 'wi' :
                    cursor = conn.execute('''SELECT * FROM image WHERE name IN
                    (SELECT name_img FROM annotation) AND id = ?''',(id_img,));
                else :
                    cursor = conn.execute('''SELECT * FROM image WHERE id = ?'''
                    ,(id_img,));
                for row in cursor:
                    image=ml.showimg(row,'liste')
                    # S'il existe une image correspondant
                    if image != {} :
                        liste_obj.append(image)
                conn.commit()
    ############################################################################
    # Sinon on recherche des annotations
    else :
        obj = 'ano'
        no_doublon=[0]
        # On souhaite les images qui match avec le mot clé 1 ou le mot clé 2 ou
        # le mot clé 3 [etc]
        if option_orand == 'or' :
            for word in keys_s :
                cursor = conn.execute('''SELECT name_img FROM annotation WHERE 
                annotation LIKE ?''',("%"+word+"%",));
                for row in cursor :
                    cursor_obj = conn.execute('''SELECT path_thumb FROM image 
                    WHERE name = ?''',(row[0],));
                    for roww in cursor_obj :
                        path_thumb=roww[0]
                    liste_annotations=ml.showano(row[0],path_thumb)
                    if liste_annotations !=[] :
                        for ano in liste_annotations:
                            if ano['id'] not in no_doublon :
                                no_doublon.append(ano['id'])
                                liste_obj.append(ano)
                    conn.commit()
        # On souhaite les image qui match avec le mot clé 1 et le mot clé 2 et
        # le mot clé 3 [etc]
        else :
            liste_id_ok=ml.andsearch(keys_s,obj)
            # Pour toutes ces annotations qui ont réussit le test on les affiche
            for id_ano in liste_id_ok :
                cursor = conn.execute('''SELECT name_img FROM annotation WHERE 
                id = ?''',(id_ano,));
                for row in cursor:
                    cursor_obj = conn.execute('''SELECT path_thumb FROM image 
                    WHERE name = ?''',(row[0],));
                    for roww in cursor_obj :
                        path_thumb=roww[0]
                    liste_annotations=ml.showano(row[0],roww[0])
                    # S'il existe une annotation correspondant
                    if liste_annotations != [] :
                        for ano in liste_annotations:
                            liste_obj.append(ano)
                conn.commit()
    conn.close()
    return render_template('result_search.html', liste_obj=liste_obj, 
    keys_search=keys_search, type_obj=obj)

# Fonction permettant d'afficher la recherche des mots clés
@app.route('/search/', methods=['GET', 'POST'])
def search():
    ''' 
        Fonction permettant de générer une vue du formulaire de recherche dans 
        la page search.html
        
        Return : Redirige vers la fonction result_search et la vue associée
    '''
    if request.method == 'POST':
        # Recuperation des informations du formulaire
        words_search = request.form['words']
        w_search = ml.clean_kw(words_search)
        # La méthode va indiquer si on cherche des mots clés, des annotations 
        # ou des  id
        met=request.form['met']
        if met == 'menu' :
            flash(u'You must choose a research method !', 'error')
        else :
            if w_search == [] :
                    flash(u'You must enter at least one word !', 'error')
            else :
                if met == 'id' :
                    option_orand=0
                    option_wiwo=0
                else :
                    option_orand=request.form['orand']
                    if met == 'keywords' :
                        option_wiwo=request.form['withorwithout']
                    else : 
                        option_wiwo=0
                return redirect(url_for('result_search', 
                keys_search=";".join(w_search),met=met, 
                option_orand=option_orand, option_wiwo=option_wiwo))
    return render_template('search.html')

# Fonction permettant d'afficher la page de supprimer d'une image
@app.route('/<string:nom_img>/add_annotation/<string:path>', 
methods=['GET', 'POST'])
def add_annotation(nom_img,path):
    ''' 
        Fonction permettant de réaliser des annotations sur des à partir d'
        informations receuillis dans le formulaire de la vue 
        annotate_picture.html
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
            path : Chaîne de caractères contenant le chemin de l'image annotée
                   ou si celle-ci n'a encore jamais été annotée, le chemin de 
                   l'image.
                   
        Returns : Redirige vers elle-même (fonction add_annotation) pour mettre
                  à jour le visuel et la légende avec la nouvelle annotation 
                  saisie
    '''
    conn = sqlite3.connect('data.db')
    cursor_obj = conn.execute('''SELECT PATH_THUMB from IMAGE WHERE NAME= ?'''
    ,(nom_img,));
    for roww in cursor_obj :
        path_thumb=roww[0]
    liste_annotations=ml.showano(nom_img,path_thumb)
    if request.method == 'POST':
        # Récupérer les informations de l'annotation
        x1=ml.interpret_string(request.form['x1'])
        y1=ml.interpret_string(request.form['y1'])
        h=ml.interpret_string(request.form['h'])
        w=ml.interpret_string(request.form['w'])
        auteur = request.form['Auteur']
        kw_ano = request.form['a_keywords']
        # Nettoyage des mots cles
        keys = ';'.join(ml.clean_kw(kw_ano))
        auteur = request.form['Auteur']
        if x1 == None :
        # Vérification des champs :
            flash(u'You must select an annotation area !', 'error')
        else :
            if auteur == "" :
                flash(u'You must enter an author name !', 'error')
            else :
                if auteur == 'Autre': # Si c'est un nouvel auteur :
                    auteur = "".join(ml.clean_kw(request.form['champ1']))
                if keys == "" : # On souhaite au minimum un mot cle :
                    flash(u'You must enter at lest one annotation keyword !'
                    , 'error')
                else :
                    # Ouverture de la db
                    conn = sqlite3.connect('data.db')
                    # On créé le nouvel élément d'annotation :
                    conn.execute('''INSERT INTO annotation (x1,y1,h,w,
                    creation_date,modification_date,annotation,name_img,auteur,
                    color_r, color_g, color_b) VALUES (? , ?, ?, ?, 
                    current_timestamp, current_timestamp, ?, ? , ?,'temp','temp'
                    ,'temp')''',(x1,y1,h,w,keys,nom_img,auteur));
                    conn.commit()
                    # Dessine un rectangle avec les coordonnées sur l'image 
                    #et enregistre l'image annotée dans /ano
                    path_and_color = ml.draw_ano(nom_img,path.replace(';','/')
                    ,x1,y1,h,w)
                    # On met à jour le chemin de l'image annotée dans la DB
                    conn.execute('''UPDATE image SET path_ano = ? WHERE name= ?
                    ''',(path_and_color[0],nom_img));
                    conn.commit()
                    # On récupère l'ID de l'annotation
                    cursor = conn.execute('''SELECT id FROM annotation WHERE id 
                    == (SELECT MAX(id) FROM annotation)''')
                    for row in cursor:
                        id_ano= row[0]
                    conn.commit()
                    conn.execute('''UPDATE annotation SET color_r = ?, 
                    color_g = ?, color_b = ? WHERE id= ?''',
                    (path_and_color[1][0],path_and_color[1][1],
                    path_and_color[1][2],id_ano));
                    conn.commit()
                    conn.close()
                    # On va retourner rechArgser la page en affichant les 
                    #annotations qui existent sur elle
                    return redirect(url_for('add_annotation', 
                    path=path_and_color[0].replace('/',';'), nom_img=nom_img, 
                    liste_annotations=liste_annotations))
    return render_template('annotate_picture.html', path=path.replace(';','/'),
    nom_img=nom_img,liste_annotations=liste_annotations)

# Fonction permettant d'afficher la page de supprimer d'une image
@app.route('/delete/<nom_img>/<option>/<id_ano>/<path>/'
, methods=['GET', 'POST'])
def delete(nom_img,path,option,id_ano):
    ''' 
        Fonction permettant de supprimer une annotation ou une image par la vue
        delete.html
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
            path : Chaîne de caractères contenant le chemin de l'image que l'on 
                   souhaite supprimer ou de l'image à laquelle est associée l'
                   annotation que l'on souhaite supprimer; au format minature
            option : Chaîne de caractères indiquant s'il sagit d'une image 
                    ('img') ou d'une annotation ('ano') que l'ont souhaite
                    supprimer.
            id_ano : Integer correspondant à l'id de l'annotation à supprimer et
                     sinon vaut 0 si on veut supprimer une image.

        Returns : Redirige vers la fonction picture_profil et la vue 
                  profil_picture.html si la suppression s'est effectué avec 
                  succès dans le cas de l'annotation. Dans le cas de l'image,
                  si la suppression s'est bien effectuée, redirige vers la 
                  fonction homepage et la vue home.html
    '''
    conn = sqlite3.connect('data.db')
    kw_annotation='Empty'
    # Si on veut supprimer une annotation pour l'identifier on affiche ses
    # mots clés.
    if id_ano !=0 :
        cursor = conn.execute('''SELECT annotation FROM annotation WHERE id = ?
        ''',(id_ano,));
        for row in cursor:
            kw_annotation=keys_s=row[0].split(';')
 
    if request.method == 'POST':
        if option == 'img' :
            cursor = conn.execute('''SELECT path_ano, path_thumb, path_image 
            FROM image WHERE name = ?''',(nom_img,));
            for row in cursor:
                path_ano = row[0]
                path_thumb = row[1]
                path_image = row[2]
            # Pour toutes les annotions on les supprime avec l'image
            conn.execute('''DELETE FROM annotation WHERE name_img = ?'''
            ,(nom_img,));
            conn.commit()
            conn.execute("DELETE FROM image WHERE name = ?",(nom_img,));
            conn.commit()
            conn.close()
            os.remove(path_image)
            os.remove(path_thumb)
            if path_ano != 'EMPTY' :
                os.remove(path_ano)
            flash(u'The picture has been removed with succes.', 'succes')
            return redirect(url_for('homepage'))
        else :
            conn.execute('''DELETE FROM annotation WHERE name_img = ? AND id = 
            ?''',(nom_img,id_ano));
            conn.commit()
            # Mettre à jour l'image d'annotation de l'image
            new_path=ml.update_ano(nom_img)
            conn.execute('''UPDATE image SET path_ano = ? WHERE name= ?'''
            ,(new_path,nom_img));
            conn.commit()
            conn.close()
            flash(u'The annotation has been removed with succes.', 'succes')
            return redirect(url_for('picture_profil', nom_img=nom_img))
    return render_template('delete.html', path=path.replace(';','/'), 
    nom_img=nom_img, option=option, annotation=kw_annotation)

# Fonction permettant d'afficher la page de modification d'une image
@app.route('/modification/<nom_img>/<option>/<id_ano>/<path>/<kw_modif>/'
, methods=['GET', 'POST'])
def modification(nom_img,path,kw_modif,option,id_ano):
    ''' 
        Fonction permettant de modifier une annotation ou une image par la vue
        delete.html
        
        Args : 
            nom_img : Chaîne de caractères contenant le nom de l'image
            path : Chaîne de caractères contenant le chemin de l'image que l'on 
                   souhaite modifier ou de l'image à laquelle est associée l'
                   annotation que l'on souhaite modifier; au format minature
            option : Chaîne de caractères indiquant s'il sagit d'une image 
                    ('img') ou d'une annotation ('ano') que l'ont souhaite
                    modifier.
            id_ano : Integer correspondant à l'id de l'annotation à modifier et
                     sinon vaut 0 si on veut modifier une image.
            kw_modif : Chaîne de caractères contenant les mots clés associés à
                       l'image ou l'annotation que l'on souhaite modifier, ils
                       sont séparés par des ';'
                     
        Returns : Redirige vers la fonction picture_profil et la vue 
                  profil_picture.html si la modification s'est effectué avec 
                  succès.
    '''
    if request.method == 'POST':
        conn = sqlite3.connect('data.db')
        kw_modif = request.form['keywords']
        keys = ';'.join(ml.clean_kw(kw_modif))
        if keys == "" :
            conn.close()
            flash(u'You must enter at least one keyword !', 'error')
        else :
            if option == 'img' :
                conn.execute('''UPDATE image SET keywords = ? WHERE name= ?'''
                ,(keys,nom_img));
                conn.execute('''UPDATE image SET modification_date = 
                current_timestamp WHERE name= ?''',(nom_img,));
                conn.commit()
                conn.close()
                flash(u'Keywords has been edit with succes.', 'succes')
                return redirect(url_for('picture_profil', nom_img=nom_img))
            else :
                conn.execute('''UPDATE annotation SET annotation = ? WHERE id= ?
                ''',(keys,id_ano));
                conn.execute('''UPDATE ANNOTATION set modification_date = 
                current_timestamp WHERE id= ?''',(id_ano,));
                conn.commit()
                conn.close()
                flash(u'Annotation keywords has been edit with succes.',
                 'succes')
                return redirect(url_for('picture_profil', nom_img=nom_img))
    return render_template('modificate.html', nom_img=nom_img,
    path=path.replace(';','/'), keys=kw_modif,option=option,id_ano=id_ano)

# Fonction permettant d'afficher la page d'upload d'une image et de la mettre 
#dans la DB
@app.route('/upload_image/', methods=['GET', 'POST'])
def upload():
    ''' 
        Fonction permettant d'enregistrer sur le serveur une image par la vue
        upload_image.html
        
        Returns : Redirige vers la fonction picture_profil et la vue 
                  profil_picture.html si le téléchargement s'est effectué avec 
                  succès.
    '''
    if request.method == 'POST':
        # Recuperation des informations du formulaire
        f = request.files['fic']
        kw_image = request.form['keywords']
        # Nettoyage des mots cles
        keys = ';'.join(ml.clean_kw(kw_image))
        auteur = request.form['Auteur']
        id_examen = ml.interpret_string(request.form['id_examen'])
        if id_examen != None :
            # Ouverture de la db
            conn = sqlite3.connect('data.db')
            # On verifie que l'examen existe :
            cursor = conn.execute('''SELECT id FROM examen WHERE id == 
            (SELECT MAX(id) FROM examen)''')
            for row in cursor:
                id_max_examen= row[0]
            if id_examen > id_max_examen :
                flash(u'Examination ID not found, try again !', 'error')
            else :
                if auteur == "" :
                    flash(u'You must enter an author name !', 'error')
                else:
                    if auteur == 'Autre': # Si c'est un nouvel auteur :
                        auteur = "".join(ml.clean_kw(request.form['champ1']))
                    if keys == "" : # On souhaite au minimum un mot cle :
                        flash(u'You must enter at least one keyword !',
                         'error')
                    else :
                        if f: # on vérifie qu'un fichier a bien été envoyé
                            # on vérifie que son extension est valide
                            if ml.extension_ok_image(f.filename): 
                                # Création d'un objet dans la DB
                                conn.execute('''INSERT INTO image (name,
                                path_image,path_thumb,path_ano,creation_date,
                                modification_date,keywords, auteur, id_examen) 
                                VALUES ('temp','temp', 'temp', 'EMPTY', 
                                current_timestamp, current_timestamp, ?, ?, ?)
                                ''',(keys,auteur,id_examen));
                                conn.commit()
                                # On va modifier les champs temporaires
                                cursor = conn.execute('''SELECT id FROM image 
                                WHERE id == (SELECT MAX(id) FROM image)''')
                                for row in cursor:
                                    id_img= row[0]
                                conn.commit()
                                old = f.filename
                                nom_img = 'img'+ str(id_img) +'.' + old.rsplit(
                                '.', 1)[1]
                                # Chemin ou l'image est sauvegarde
                                path_img = DOSSIER_UPS + nom_img
                                f.save(path_img)
                                path_thumb = DOSSIER_UPS + 'thumb/' + nom_img
                                # Création de la miniature : 
                                # https://opensource.com/life/15/2/resize-images-python
                                ml.resize(path_img, path_thumb)
                                # Modification de l'objet la DB pour mettre 
                                #les chemins
                                conn.execute('''UPDATE image SET path_image = ? 
                                WHERE id= ?''',(path_img,id_img));
                                conn.execute('''UPDATE image SET path_thumb = ? 
                                WHERE id= ?''',(path_thumb,id_img));
                                conn.execute('''UPDATE image SET name = ? WHERE 
                                ID= ?''',(nom_img,id_img));
                                conn.commit()
                                conn.close()
                                return redirect(url_for('picture_profil', 
                                nom_img=nom_img))
                            else:
                                flash(u'This file contains an extension not'
                                + 'allowed !', 'error')
                        else:
                            flash(u'You must select a file !', 'error')
        else :
            flash(u'Examination ID not found, ID are integer numbers !','error')
    return render_template('upload_image.html')

if __name__ == '__main__':
    app.run(debug=True)
