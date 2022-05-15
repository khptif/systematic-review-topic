import numpy as np
import pacmap
import matplotlib.pyplot as plt
import hdbscan
from sklearn import metrics

set_seed = 5
import os
import optuna
import functions.scatter_with_hover as scatter_with_hover
import yake
import joblib
from multiprocessing import Process
import pandas as pd
from scipy import sparse

#num_cores = multiprocessing.cpu_count()


def pacmap_default(tf_idf, save, path_data_folder, plot=True):

    np.random.seed(set_seed)

    embedding_2d = pacmap.PaCMAP(random_state=set_seed, apply_pca=True).fit(
        tf_idf, init="pca"
    )

    if plot:
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        ax.scatter(*embedding_2d.embedding_.T, s=0.6)

    if save:
        joblib.dump(embedding_2d, f"{path_data_folder}/embedding_2d.pkl")

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
    def __init__(self, tf_idf):

        self.tf_idf = tf_idf

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

        return study.evaluate()


def optimization(tf_idf, name, save, path_data_folder, n_trials=100, n_core = 1):

    
    objective = Objective(tf_idf)
    
    study = optuna.create_study(
        study_name=name,
        storage='postgresql://db_user:1234@localhost/db_cluster',
        #storage=f"sqlite:///{db_path}",
        direction="maximize",
        load_if_exists=True,
    )
   
    study.optimize(
            objective,
            n_trials=n_trials,
            gc_after_trial=True,
            n_jobs=n_core,
            catch=(AttributeError, ValueError),
        )
   
    print(study.best_trial)

    if save:
        joblib.dump(study, f"{path_data_folder}/study.pkl")

    return study


def retrieve_best_study(tf_idf, study, save, path_data_folder):

    print("Retrieving best study")

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

    best_study_embedding = best_study.embedding.embedding_
    best_study_clusterer = best_study.clusterer

    if save:
        joblib.dump(
            best_study_embedding, f"{path_data_folder}/best_study_embedding.pkl"
        )
        pd.DataFrame(best_study_embedding).to_csv(
            f"{path_data_folder}/best_study_embedding.csv", index=False
        )
        joblib.dump(
            best_study_clusterer, f"{path_data_folder}/best_study_clusterer.pkl"
        )

    print("Best study retrieved")

    return best_study_clusterer


def hover_with_keywords(
    df, list_final, embedding_2d, best_study_clusterer, save, path_data_folder
):

    df_hover = df.copy()
    df_hover = df_hover.fillna(np.nan)
    df_hover["labels"] = ""
    df_hover["text"] = [doc.split() for doc in list_final]
    num_clusters = len(set(best_study_clusterer.labels_)) - (
        1 if -1 in best_study_clusterer.labels_ else 0
    )

    keywords_extractor = yake.KeywordExtractor(
        lan="en", n=1, dedupLim=7, dedupFunc="sqm", windowsSize=1, top=10, features=None
    )

    for cluster_num in range(num_clusters):

        w = np.where(best_study_clusterer.labels_ == cluster_num)[0]
        text = " ".join([" ".join(doc) for doc in df_hover["text"][w]])

        try:
            keywords = keywords_extractor.extract_keywords(text)
        except UnboundLocalError:
            keywords = []

        if len(keywords) > 0:
            kws = []
            for kw in keywords:
                kws.append(str(kw[1]))
            df_hover["labels"][w] = ", ".join(kws)

    labels, uniques = pd.factorize(df_hover["labels"])
    df_hover["cluster"] = labels
    df_hover["cluster"][np.where(df_hover["labels"] == "")[0]] = -1
    df_hover["x"] = pd.DataFrame(embedding_2d.embedding_)[0]
    df_hover["y"] = pd.DataFrame(embedding_2d.embedding_)[1]

    if save:
        joblib.dump(df_hover, f"{path_data_folder}/df_hover.pkl")

    return df_hover
