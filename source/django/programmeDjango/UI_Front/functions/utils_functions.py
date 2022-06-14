from DataBase.models import *


def neighbour_article(article,research,number_neighbor=5):
    """ The function take an article, a research and process with cluster object, the nearest neighbor. By default, we take the 5 nearest.
    by iteration, we search around the article +-100 and if we doesnt have enough, the same but with +-200 around. We make max +-1000.
    The function return a list of article but there isn't the center article in the list"""

    neighbour_articles = []
    distant = 100
    cluster_center_article = Cluster.objects.filter(article=article,research=research)
    #if the article doesn't exist in the cluster
    if not cluster_center_article.exists():
        return neighbour_articles

    cluster_center_article = cluster_center_article[0]
    center = (cluster_center_article.pos_x,cluster_center_article.pos_y)
    def distant_from_center(pos_x,pos_y):
        return (center[0] - pos_x)**2 + (center[1] - pos_y)**2

    nearest_cluster = []
    
    while True:
        if len(nearest_cluster)>=number_neighbor or distant > 1000:
            break
        
        cluster_list = Cluster.objects.filter(research=research, 
                                                pos_x__gte=center[0] - distant, 
                                                pos_x__lte=center[0] + distant,
                                                pos_y__gte=center[1] - distant,
                                                pos_y__lte=center[1] + distant)
        
        for cluster in cluster_list:
            
            # if this is the cluster of the center article we pass to next iteration
            if cluster.article == article:
                continue

            # if there are some place, we add the cluster
            if len(nearest_cluster)<number_neighbor:
                nearest_cluster.append(cluster)
            else:
                # else, we check distant from center with all cluster in list
                # if there is one who is better, the new replace the ancient
                for i in range(len(nearest_cluster)):
                    ancient_distant = distant_from_center(nearest_cluster[i].pos_x,nearest_cluster[i].pos_y)
                    new_distant = distant_from_center(cluster.pos_x,cluster.pos_y)
                    if new_distant < ancient_distant:
                        nearest_cluster[i] = cluster
                        break

        distant += 100
   
    # we recuperate all article from cluster list
    for cluster in nearest_cluster:
        neighbour_articles.append(cluster.article)

    return neighbour_articles     

