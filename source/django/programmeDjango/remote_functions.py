import requests
import json
from django.shortcuts import redirect
 
def http_request(adresse,port,path,is_ssl):
    
    response_http = ""
    if is_ssl:
        response_http = requests.get(f"https://{adresse}:{port}/{path}")
    else:
        response_http = requests.get(f"http://{adresse}:{port}/{path}")
    return response_http

def get_max_article_remote(search,date_begin,date_end):
    from programmeDjango.settings import BackEnd_host_adresse as adresse
    from programmeDjango.settings import BackEnd_host_port as port
    
    response_http = ''
    date_begin = date_begin.strftime("%Y/%m/%d")
    date_end = date_end.strftime("%Y/%m/%d")
    path = f"get_max?search_term={search}&date_begin={date_begin}&date_end={date_end}"

    try:
        from programmeDjango.settings import BackEnd_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return -1
    
    if not response_http.status_code < 400:
        return 0
    else:
        return int(response_http.text)


def begin_research_remote(research):
    from programmeDjango.settings import BackEnd_host_adresse as adresse
    from programmeDjango.settings import BackEnd_host_port as port

    response_http = ''
    id = str(research.id)
    path = f"research_create?research_id={id}"

    try:
        from programmeDjango.settings import BackEnd_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        research.delete()
        return False
    
    if response_http.status_code < 400:
        return True
    else:
        research.delete()
        return False

def check_research_remote(research):
    from programmeDjango.settings import BackEnd_host_adresse as adresse
    from programmeDjango.settings import BackEnd_host_port as port

    response_http = ''
    id = str(research.id)
    path = f"check_research?research_id={id}"

    try:
        from programmeDjango.settings import BackEnd_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    
    if response_http.status_code < 400:
        is_alive = bool(response_http.content)
        return is_alive
    else:
        return False

def relaunch_if_fault_remote():
    from programmeDjango.settings import BackEnd_host_adresse as adresse
    from programmeDjango.settings import BackEnd_host_port as port

    response_http = ''
    path = f"restart_research"

    try:
        from programmeDjango.settings import BackEnd_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    
    if response_http.status_code < 400:
        return False
    else:
        return True


def download_article_remote(article):
    from programmeDjango.settings import DataBase_host_adresse as adresse
    from programmeDjango.settings import DataBase_host_port as port
    
    article_id = str(article.id)
    path = f"download_article?article_id={article_id}"

    try:
        from programmeDjango.settings import DataBase_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    return True

def create_plot_remote(research):
    from programmeDjango.settings import DataBase_host_adresse as adresse
    from programmeDjango.settings import DataBase_host_port as port
    
    research_id = str(research.id)
    path = f"create_plot?research_id={research_id}"

    try:
        from programmeDjango.settings import DataBase_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    return True

def get_plot_remote(research):
    from programmeDjango.settings import DataBase_host_adresse as adresse
    from programmeDjango.settings import DataBase_host_port as port
    
    research_id = str(research.id)
    path = f"get_plot?research_id={research_id}"

    try:
        from programmeDjango.settings import DataBase_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    return response_http

def get_plot_remote_string(research):
    from programmeDjango.settings import DataBase_host_adresse as adresse
    from programmeDjango.settings import DataBase_host_port as port
    
    research_id = str(research.id)
    path = f"get_plot_string?research_id={research_id}"

    try:
        from programmeDjango.settings import DataBase_SSL as is_ssl
        response_http =http_request(adresse,port,path,is_ssl)
    except:
        return False
    html_string = json.loads(response_http.content)
    return html_string

def get_final_zip_remote(research,user):
    from programmeDjango.settings import DataBase_host_adresse as adresse
    from programmeDjango.settings import DataBase_host_port as port
    
    user_id = str(user.id)
    research_id = str(research.id)
    path = f"get_final?research_id={research_id}&user_id={user_id}"

    try:
        from programmeDjango.settings import DataBase_SSL as is_ssl
        if is_ssl:
            return redirect("https://" + adresse + ":" + port + "/" + path)
        else:
            return redirect("http://" + adresse + ":" + port + "/" + path)
    except:
        return False
