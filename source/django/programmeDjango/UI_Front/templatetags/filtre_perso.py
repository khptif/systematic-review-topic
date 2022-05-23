
from django import template
from django.conf import settings

import html
import random


from DataBase.models import *
from BackEnd.models import *

register = template.Library()

@register.filter
def number_trials(research):
    number = Number_trial.objects.filter(research=research).count()
    return str(number)

@register.filter
def total_article(research):
    number = Research_Article.objects.filter(research=research).count()
    return str(number)

@register.filter
def number_article_prepoc(research):
    number = Number_preprocess.objects.filter(research=research).count()
    return str(number)

@register.filter
def number_article(research):

    number = Research_Article.objects.filter(research=research).count()
    return str(number)

@register.filter
def get_first_param(elem):
    return elem[0]

@register.filter
def historical(research):
    """ 
    A research is in the format : (id_research, [list of key_words who match the search]).for each research, we give the line 
    string chain, keywords(the one who match in bold), number of articles
    """
    return_string = ""
    research_object = Research.objects.get(id=research[0])
    all_keywords = Keyword.objects.filter(research=research_object).order_by('word')

    # string search
    return_string += "[ " + html.escape(research_object.search) + "] | "
    # keywords
    for key in all_keywords:
        if key.word in research[1]:
            return_string += "<b>" + html.escape(key.word) + "</b>, "
        else:
            return_string += html.escape(key.word) + ", "
    return_string += " | "
    # number of articles
    number_article = len(Research_Article.objects.filter(research=research_object))
    return_string += str(number_article) + " articles | "

    return return_string

@register.filter
def cluster_display(cluster_list):
    """ display all the cluster in the graphic"""
    #the template html code we will return
    return_html = """"""
    template = """<button class="topic_{topic}" 
                style='width:10px;
                        height:15px;
                        border-width: 3px;
                        background-color:rgb({red},{green},{blue});
                        position:absolute; 
                        left:{pos_x}px;top:{pos_y}px; 
                        border-radius: 25px;'

                onclick="article_show('{article_id}')" 
                ondblclick="test('{article_id}')" 
                onmouseover="light(this)" 
                onmouseout="dark(this)">
            </button>"""
    #which color for which topic.
    topic_color = dict()
    #we define colors
    colors = []
    for x in reversed(range(9)):
        for y in reversed(range(9)):
            colors.append((x*25,y*25,0))
            colors.append((x*25,0,y*25))
            colors.append((0,x*25,y*25))
    
    number_colors = len(colors)
    color_iter = 0
    for cluster in cluster_list:
        topic = cluster.topic
        #we check if this a new topic or not.
        if not topic in topic_color:
            topic_color[topic] = colors[color_iter]
            color_iter += 1
            # if there are more topics than colors
            color_iter = color_iter%number_colors
        
        red = topic_color[topic][0]
        green = topic_color[topic][1]
        blue = topic_color[topic][2]
        # if we have the same position for two article, we add random number
        pos_x = int((cluster.pos_x + random.randint(0,10))*1.5)
        pos_y = int((cluster.pos_y + random.randint(0,20))*2.5)
        article_id = "article_" + str(cluster.article.id)
        #we build the html code
        #we replace space in topic for undescore
        
        #we escape the topic
        topic = html.escape(topic)
        html_code = template.format(topic=topic,red=red,green=green,blue=blue,pos_x=pos_x,pos_y=pos_y,article_id=article_id)
        return_html += html_code
    
    return return_html

@register.filter
def topic_display(cluster_list):
    """ display all the topics in the list"""
    #the template html code we will return
    return_html = """"""
    template = """ <button  onmouseover="light_cluster('topic_{topic}')" 
                            onmouseout="dark_cluster('{topic}')"
                            ondblclick="add_data_post('topic','{topic}')"
                        style=
                            "
                            background-color:rgba({red},{green},{blue},0.3);
                            word-wrap: break-word;
                            "
                        > 
                    {topic} </button>"""
    #which color for which topic.
    topic_color = dict()
    #we define colors
    colors = []
    for x in reversed(range(9)):
        for y in reversed(range(9)):
            colors.append((x*25,y*25,0))
            colors.append((x*25,0,y*25))
            colors.append((0,x*25,y*25))
    
    number_colors = len(colors)
    color_iter = 0
    for cluster in cluster_list:
        topic = cluster.topic
        # if we already displayed the topic, we continue on the next
        if topic in topic_color:
            continue
        #we check if this a new topic or not.
        if not topic in topic_color:
            topic_color[topic] = colors[color_iter]
            color_iter += 1
            # if there are more topics than colors
            color_iter = color_iter%number_colors
        
        red = topic_color[topic][0]
        green = topic_color[topic][1]
        blue = topic_color[topic][2]
        
        #we escape the topic
        topic = html.escape(topic)
        html_code = template.format(topic=topic,red=red,green=green,blue=blue)
        return_html += html_code
    
    return return_html    

@register.filter
def article_display(article_list):
    """ We display information about article"""
    return_html = """"""
    template = """
                <div 
                    id='{article_id}' 
                    style=
                        "position:absolute; 
                        left:0px;
                        top:0px; 
                        visibility:hidden;
                        margin:10px;
                        "
                > 
                    <b>Title</b><br> {title} <br>
                    <b>Authors</b><br> {authors}<br>
                    <b>Abstract</b><br> {abstract}
                </div>
                    """
    for article in article_list:
        title = html.escape(article.title)
        article_id = "article_" + str(article.id)
        authors_list = Author.objects.filter(article_author__article = article)
        authors =""
        for author in authors_list:
            authors += html.escape(author.last_name) + " " + html.escape(author.first_name) + ";<br> "
        abstract = html.escape(article.abstract)
        html_code = template.format(article_id=article_id,title=title,authors=authors, abstract=abstract)
        return_html += html_code
    return return_html

@register.filter
def authors_display(row):
    """display author in page_table_choice.html"""
    article = row.article
    authors = Author.objects.filter(article_author__article =article)
    html_code = ""
    for author in authors:
        html_code += html.escape(author.last_name) + " " + html.escape(author.first_name) + " <br>"
    return html_code
    