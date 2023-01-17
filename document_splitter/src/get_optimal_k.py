"""
This script contains the functions to get keyword representations and elbow point
"""
from typing import List, Dict
import logging
import math
import pandas as pd
from PIL import Image
from sklearn.cluster import KMeans
from keybert import KeyBERT
from document_splitter.enumerators import DataType, ColumnNames, EncoderModel
from sentence_transformers import SentenceTransformer

KEYWORD_EXTRACTION_MODEL = KeyBERT()
log = logging.getLogger("Log ")


def get_keywords(text: str) -> str:
    """
    Function to get keyword representation from full text
    Args:
        text (str): the text from which keywords need to be extracted
    Returns:
        keyword_representation (str): keywords extracted
    """
    keywords_extracted = KEYWORD_EXTRACTION_MODEL.extract_keywords(text, top_n=50)
    keywords_list = list(set([(word[0]).lower() for word in keywords_extracted]))
    keyword_representation = " ".join(keywords_list)
    log.info(f"Keyword representation is - {keyword_representation} \n")

    return keyword_representation


def get_slope(x_list: List, y_list: List) -> Dict:
    """
    Function to get slope fo respective points in two lists
    Args:
        x_list (List): list of k values
        y_list (List): list of qcss scores
    Returns:
        slope_dict (Dict): Slope values to get elbow point
    """
    slope_dict = {}

    for i in range(0, len(x_list) - 1):
        x1 = x_list[i]
        x2 = x_list[i + 1]
        y1 = y_list[i]
        y2 = y_list[i + 1]
        slope = (y2 - y1) / (x2 - x1)
        slope_dict[x1] = slope

    log.info(f"Slopes are - {slope_dict} \n")

    return slope_dict


def get_elbow_point(data_df: pd.DataFrame, data_distinction_type: DataType):
    """
    Function to get elbow point of sample space by calculating
    second derivative of within cluster sum of squared distance
    (wcss) of all the points.
    Args:
        data_df (pd.DataFrame): list of k values
        data_distinction_type (str): type of feature (text or image)
        based on which the images can be distinguished
    Returns:
        optimal_k_value (int): optimal K value
        best_cluster_model: cluster model trained with optimal K value
        embedder_model: the embedder model based on image distinctive feature
    """
    # within cluster sum of squared distances
    wcss = {}

    # type of encoding depends on data_distinction_type
    if data_distinction_type == DataType.TEXT.value:  # encode textual features
        data = data_df[ColumnNames.FULL_TEXT.value].tolist()
        embedder_model = SentenceTransformer(EncoderModel.TEXT.value)

    elif data_distinction_type == DataType.IMAGE.value:  # encode visual features
        data = data_df[ColumnNames.IMAGE_NAME.value].tolist()
        data = [Image.open(item) for item in data]
        embedder_model = SentenceTransformer(EncoderModel.IMAGE.value)
    else:
        raise NotImplementedError(f"Type: {data_distinction_type} is not supported")

    embedded_data = embedder_model.encode(data)

    # upper limit of k is decided as 50 or square root of
    # number of documents, whichever is smallest
    k_limit = int(math.sqrt(len(data))) + 1
    k_limit = min(k_limit, 50)
    log.info(f"k-limit is {k_limit} \n")

    # calculate wcss scores for different k values
    for k in range(2, k_limit):
        cluster_model = KMeans(n_clusters=k)
        cluster_model.fit(embedded_data)
        wcss[k] = cluster_model.inertia_

    # get second derivative to find elbow point
    first_derivative = get_slope(list(wcss.keys()), list(wcss.values()))
    second_derivative = get_slope(list(first_derivative.keys()), list(first_derivative.values()))

    # elbow point is largest negative slope
    sorted_scores = dict(sorted(second_derivative.items(), key=lambda item: item[1]))
    optimal_k_value = next(iter(sorted_scores))
    log.info(f"Optimal k value is {optimal_k_value} \n")

    best_cluster_model = KMeans(n_clusters=optimal_k_value)
    best_cluster_model.fit(embedded_data)

    return optimal_k_value, best_cluster_model, embedder_model
