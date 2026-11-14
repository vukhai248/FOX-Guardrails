from .base_retriever import BaseRetriever

class ProductRetriever(BaseRetriever):
    def __init__(self, config, settings):   
        super().__init__(
            config=config,
            settings=settings,
            collection_name="products_collection",
            k_query=config.retrieval.product.k_query,  
            k_rerank=config.retrieval.product.k_rerank 
        )
