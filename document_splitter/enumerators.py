"""Lists enumerators used in the scope of document splitting"""

from enum import Enum


class EncoderModel(Enum):
    """Enumerates huggingface encoder models"""

    TEXT = "sentence-transformers/distilroberta-base-msmarco-v2"
    IMAGE = "sentence-transformers/clip-ViT-B-32"


class DataType(Enum):
    """Enumerates scope"""

    TEXT = "text"
    IMAGE = "image"


class DefaultParams(Enum):
    """Enumerates default parameter values"""

    DEFAULT_N_SAMPLES = 8
    DEFAULT_CUSTOM_K_VALUE = 0


class ColumnNames(Enum):
    """Enumerates column names in the dataset"""

    FULL_TEXT = "full_text"
    IMAGE_NAME = "image_name"
    PAGE_NUM = "page_num"
    KEYWORD_REPRESENTATION = "keyword_rep"
    CLUSTER_REPRESENTATION = "cluster_representation"
    CLUSTER = "cluster"
    SCORE = "score"
    WITHIN_CLUSTER_INDEX = "within_cluster_index"
