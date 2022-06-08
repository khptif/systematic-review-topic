from django.test import TestCase
from BackEnd.functions.Get_PM import *


class test_get_max_article(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        number_article_result = get_max_article(input)
        number_article_expected = 42
        self.assertGreaterEqual(number_article_result,number_article_expected)

class test_get_ID(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        list_id = get_ID(input)
        number_id_expected = 42
        self.assertGreaterEqual(len(list_id),number_id_expected)

class test_extract_data(TestCase):

    def test_method(self):
        input = 33623601
        output_expected ={'title': 'Profil clinique, biologique et radiologique des patients Algériens hospitalisés pour COVID-19: données préliminaires.', 'doi': '', 'date': datetime.date(2020, 6, 15), 'author': [('Ketfi', 'Abdelbassat'), ('Chabati', 'Omar'), ('Chemali', 'Samia'), ('Mahjoub', 'Mohamed'), ('Gharnaout', 'Merzak'), ('Touahri', 'Rama'), ('Djenouhat', 'Kamel'), ('Selatni', 'Fayçal'), ('Saad', 'Helmi Ben')], 'abstract': "Aucune etude anterieure n'a elabore le profil des patients Algeriens hospitalises pour COVID-19. L'objectif de cette etude etait de determiner le profil clinique, biologique et tomodensitometrique des patients Algeriens hospitalises pour COVID-19. Une etude prospective etait menee aupres des patients hospitalises pour COVID-19 (periode: 19 mars-30 avril 2020). Les donnees cliniques, biologiques et radiologiques, le type de traitement recu et la duree de l'hospitalisation etaient notes. Le profil clinique des 86 patients atteints de COVID-19 etait un homme non-fumeur, age de 53 ans, qui etait dans 42% des cas en contact avec un cas suspect/confirme de COVID-19 et ayant une comorbidite dans 70% des cas (hypertension arterielle, diabete sucre, pathologie respiratoire chronique et allergie, cardiopathie). Les plaintes cliniques etaient dominees par la triade <<asthenie-fievre-toux>> dans plus de 70% des cas. Les anomalies biologiques les plus frequentes etaient: syndrome inflammatoire biologique (90,1%), basocytemie (70,8%), lymphopenie (53,3%), augmentation de la lactico-deshydrogenase (52,2%), anemie (38,7%), augmentation de la phosphokinase (28,8%) et cytolyse hepatique (27,6%). Les signes tomodensitometriques les plus frequents etaient: verre depoli (91,8%), condensations alveolaires (61,2%), verre depoli en plage (60,0%), et verre depoli nodulaire (55,3%). Un traitement a base de <<chloroquine, azithromycine, zinc, vitamine C, enoxaparine, double antibiotherapie et +- corticoides>> etait prescrit chez 34,9% des patients. La moyenne de la duree d'hospitalisation etait de 7+-3 jours. La connaissance des profils des formes moderees et severes du COVID-19 contribuerait a faire progresser les strategies de controle de l'infection en Algerie. ", 'url': ''}
        output_result = extract_metadata(input)
        print(output_result)
        
        self.assertEqual(output_expected,output_result)

class test_get_article_parallel(TestCase):

    def test_method(self):
        input = '"vitamine c"'
        research = Research.objects.create()
        max_article_expected = get_max_article(input)
        list_id = get_ID(input)
        get_article_parallel(research,list_id)

        #we check if we have atmost half of article expected

        self.assertGreater(Research_Article.objects.filter(research=research).count(),max_article_expected/2)