from .base_retriever import BaseRetriever

class PolicyRetriever(BaseRetriever):
    def __init__(self, config, settings):
        super().__init__(
            config=config,
            settings=settings,
            collection_name="policies_collection",
            k_query=config.retrieval.policy.k_query,  
            k_rerank=config.retrieval.policy.k_rerank 
        )

    def retrieve(self, query_text: str, limit: int = None, **kwargs) -> list:
        """
        Truy vấn chính sách cửa hàng. Tự động chuyển hướng sang đối sánh từ khóa trực tiếp
        nếu dịch vụ vector embedding bên ngoài (OpenRouter) gặp sự cố mạng hoặc 401.
        """
        try:
            return super().retrieve(query_text=query_text, limit=limit, **kwargs)
        except Exception as e:
            # Fallback đối sánh từ khóa trực tiếp trên các tài liệu chính sách đã lưu
            col = self.db.get_or_create_collection(self.collection_name)
            all_records = col.get()
            docs = all_records.get("documents") or []
            metas = all_records.get("metadatas") or []

            scored = []
            q_lower = (query_text or "").lower()
            keywords = [w for w in q_lower.split() if len(w) > 1]
            for doc, meta in zip(docs, metas):
                doc_lower = doc.lower()
                title_lower = (meta.get("title") or "").lower()
                cat_lower = (meta.get("category") or "").lower()

                score = 0.0
                for kw in keywords:
                    if kw in title_lower:
                        score += 3.0
                    if kw in cat_lower:
                        score += 2.0
                    if kw in doc_lower:
                        score += 0.5
                if score > 0:
                    scored.append({"document": doc, "metadata": meta, "score": score})

            scored.sort(key=lambda x: x["score"], reverse=True)
            k = limit or self.k_rerank
            if scored:
                return scored[:k]
            # Fallback nếu không có từ khóa khớp cụ thể, trả về tài liệu đầu tiên
            return [{"document": docs[0], "metadata": metas[0], "score": 1.0}] if docs else []
