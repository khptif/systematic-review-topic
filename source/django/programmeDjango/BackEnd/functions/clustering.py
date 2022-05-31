from tabnanny import verbose

from BackEnd.models import Number_trial
import pacmap
import matplotlib.pyplot as plt
import hdbscan
from sklearn import cluster, metrics

set_seed = 5

import optuna
import yake
import joblib
import pandas as pd
from scipy import sparse

from DataBase.models import *
from programmeDjango.settings import X_INTERVAL_LITTLE,X_INTERVAL_BIG,Y_INTERVAL_LITTLE,Y_INTERVAL_BIG

import numpy as np

def pacmap_default(tf_idf, plot=True):

    
    np.random.seed(set_seed)
    try:
        embedding_2d = pacmap.PaCMAP(random_state=set_seed, apply_pca=True,verbose=True).fit(
        tf_idf, init="pca"
    )
    except:
        pass
    
    if plot:
        
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.scatter(*embedding_2d.embedding_.T, s=0.6)

    return embedding_2d


class pacmap_hdbscan:
    def __init__(
        self,
        tf_idf,
        pacmap_n_dims=2,
        pacmap_n_neighbors=None,
        pacmap_MN_ratio=0.5,
        pacmap_FP_ratio=2,
        pacmap_init="pca",
        hdbscan_min_cluster_size=5,
        hdbscan_min_samples=None,
        hdbscan_cluster_selection_method="eom",
        hdbscan_metric="euclidean",
    ):

        self.matrix = tf_idf

        self.pacmap_n_dims = pacmap_n_dims
        self.pacmap_n_neighbors = pacmap_n_neighbors
        self.pacmap_MN_ratio = pacmap_MN_ratio
        self.pacmap_FP_ratio = pacmap_FP_ratio
        self.pacmap_init = pacmap_init

        self.hdbscan_min_cluster_size = hdbscan_min_cluster_size
        self.hdbscan_min_samples = hdbscan_min_samples
        self.hdbscan_cluster_selection_method = hdbscan_cluster_selection_method
        self.hdbscan_metric = hdbscan_metric

    def evaluate(self):

        self._project_with_pacmap_and_cluster()
        self._compute_coherence_value()
        self._print_results()
        return self.score  # , self.coherence

    def _project_with_pacmap_and_cluster(self):

        np.random.seed(set_seed)

        self.embedding = pacmap.PaCMAP(
            random_state=set_seed,
            n_components=self.pacmap_n_dims,
            n_neighbors=self.pacmap_n_neighbors,
            MN_ratio=self.pacmap_MN_ratio,
            FP_ratio=self.pacmap_FP_ratio,
            apply_pca=True,
        ).fit(self.matrix, init=self.pacmap_init)

        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.hdbscan_min_cluster_size,
            min_samples=self.hdbscan_min_samples,
            metric=self.hdbscan_metric,
            gen_min_span_tree=True,
            algorithm="generic",
            core_dist_n_jobs=-1,
            # memory=Memory(cachedir=f'{data_folder}/hdbscan/clustering'),
            cluster_selection_method=self.hdbscan_cluster_selection_method,
            approx_min_span_tree=False,
            # allow_single_cluster=False,
            prediction_data=False,
        ).fit(sparse.csr_matrix(self.embedding.embedding_, dtype=np.float64))

        self.col_len = len(set(self.clusterer.labels_)) - (
            1 if -1 in self.clusterer.labels_ else 0
        )
        self.n_noise = list(self.clusterer.labels_).count(-1)
        self.perc_noise = (self.n_noise / self.matrix.shape[0]) * 100

    def _compute_coherence_value(self):

        try:
            self.coherence = metrics.silhouette_score(
                self.embedding.embedding_, self.clusterer.labels_, metric="cosine"
            )
        except ValueError:
            self.coherence = -1

        self.score = self.clusterer.relative_validity_

    def _print_results(self):
        print("Number of clusters: %d" % self.col_len)
        print("Number of noise points: %d" % self.n_noise)
        print("Percentage of noise points: %0.1f" % self.perc_noise)
        print("Silhouette Coefficient: %0.3f" % self.coherence)
        print("DBCV Score: %0.3f" % self.score)


class Objective(object):
    def __init__(self, tf_idf,research):

        self.tf_idf = tf_idf
        self.research = research

    def __call__(self, trial):

        tf_idf = self.tf_idf
        
        pacmap_n_dims = trial.suggest_int("pacmap_n_dims", 2, 400)
        pacmap_n_neighbors = trial.suggest_int("pacmap_n_neighbors", 4, 400)
       

        hdbscan_min_cluster_size = trial.suggest_int("hdbscan_min_cluster_size", 2, 400)
        hdbscan_min_samples = trial.suggest_int("hdbscan_min_samples", 2, 400)
        hdbscan_cluster_selection_method = trial.suggest_categorical(
            "hdbscan_cluster_selection_method", ["eom", "leaf"]
        )
        hdbscan_metric = trial.suggest_categorical(
            "hdbscan_metric", ["euclidean", "cosine"]
        )

        study = pacmap_hdbscan(
            tf_idf,
            pacmap_n_dims=pacmap_n_dims,
            pacmap_n_neighbors=pacmap_n_neighbors,
            hdbscan_min_cluster_size=hdbscan_min_cluster_size,
            hdbscan_min_samples=hdbscan_min_samples,
            hdbscan_cluster_selection_method=hdbscan_cluster_selection_method,
            hdbscan_metric=hdbscan_metric,
        )
        
        return_data =study.evaluate()
        

        # we increment the number of finish trial
        Number_trial.objects.create(research=self.research)
        # we write the score if it is greater
        current_score = self.research.best_dbcv
        new_score = study.score
        if new_score > current_score:
            self.research.best_dbcv = new_score
            self.research.save()
        
        return return_data 


def optimization(research,tf_idf, name, n_trials=100, n_threads = 1):

    from programmeDjango.settings import DATABASES as db

    db = db['default']
    storage = 'postgresql://' + db['USER'] + ":" + db["PASSWORD"] + "@" + db['HOST'] + ":" + db["PORT"] + "/" + db["NAME"]   
    objective = Objective(tf_idf,research)

    
    study = optuna.create_study(
        study_name=name,
        storage=storage,
        direction="maximize",
        load_if_exists=True,
    )
   
    study.optimize(
            objective,
            n_trials=n_trials,
            gc_after_trial=True,
            n_jobs=n_threads,
            catch=(AttributeError, ValueError),
        )
   

    return study


def retrieve_best_study(research, tf_idf, study):

   
    best_study = pacmap_hdbscan(
        tf_idf,
        pacmap_n_dims=study.best_trials[0].params["pacmap_n_dims"],
        pacmap_n_neighbors=study.best_trials[0].params["pacmap_n_neighbors"],
        hdbscan_min_cluster_size=study.best_trials[0].params[
            "hdbscan_min_cluster_size"
        ],
        hdbscan_min_samples=study.best_trials[0].params["hdbscan_min_samples"],
        hdbscan_cluster_selection_method=study.best_trials[0].params[
            "hdbscan_cluster_selection_method"
        ],
        hdbscan_metric=study.best_trials[0].params["hdbscan_metric"],
    )

    __ = best_study.evaluate()
    # we conserve best score in database with the research
    research.best_dbcv = best_study.score
    research.save()
    best_study_embedding = best_study.embedding.embedding_
    best_study_clusterer = best_study.clusterer

    return best_study_clusterer


def hover_with_keywords(research,list_id, list_final, embedding_2d, best_study_clusterer):

    Texts = [doc.split() for doc in list_final]
    num_clusters = len(set(best_study_clusterer.labels_)) - (
        1 if -1 in best_study_clusterer.labels_ else 0
    )

    keywords_extractor = yake.KeywordExtractor(
        lan="en", n=1, dedupLim=7, dedupFunc="sqm", windowsSize=1, top=10, features=None
    )

    for cluster_num in range(num_clusters):
        
        # we get the position in list_final of the article from the same cluster
        position_article = []
        for i in range(len(best_study_clusterer.labels_)):
            if best_study_clusterer.labels_[i] == cluster_num:
                position_article.append(i)
        
        # we build a string with all words from all article from the current cluster
        text_cluster = ""
        for i in position_article:
            text_cluster += "".join(list_final[i]) + " "
        
        if len(text_cluster)>20:
            print("text"+text_cluster[0:20])
        else:
            print("text"+text_cluster)

        # we extract the keyword of this cluster
        try:
            keywords = keywords_extractor.extract_keywords(text_cluster)
        except UnboundLocalError:
            keywords = []
            print("keyword_error")

        
        # we build a string with all the keywords
        labels = ""
        if len(keywords) > 0:
            kws = []
            for kw in keywords:
                kws.append(str(kw[1]))
            labels = ", ".join(kws)
        
        
        # we get the min and max for x and y so we can translate to
        # [0,100]x[0,200] dimension i number of article < 10000, 1000x2000 if more 
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0
        for i in position_article:
            pos_x = pd.DataFrame(embedding_2d.embedding_)[0][i]
            pos_y = pd.DataFrame(embedding_2d.embedding_)[1][i]

            if x_min > pos_x:
                x_min = pos_x
            if x_max < pos_x:
                x_max = pos_x
            if y_min > pos_y:
                y_min = pos_y
            if y_max < pos_y:
                y_max = pos_y
        if len(position_article) < 10000:
            size_x = X_INTERVAL_LITTLE
            size_y = Y_INTERVAL_LITTLE
        else:
            size_x = X_INTERVAL_BIG
            size_y = Y_INTERVAL_BIG
        # we write to database all cluster data
        for i in position_article:
            pos_x = pd.DataFrame(embedding_2d.embedding_)[0][i]
            pos_x = ((size_x)/(x_max -x_min))*(pos_x - x_min)

            pos_y = pd.DataFrame(embedding_2d.embedding_)[1][i]
            pos_y = ((size_y)/(y_max -y_min))*(pos_y - y_min)

            article = Article.objects.filter(id=list_id[i])[0]
            # we check if the article exist for the same research
            c = Cluster.objects.filter(research = research,article=article)
            if c.exists():
                c = c[0]
                c.topic = labels
                c.pos_x = pos_x
                c.pos_y = pos_y
                c.save()
            else:
                Cluster.objects.create(research = research,article=article,topic=labels,pos_x=pos_x, pos_y=pos_y)
        
