"""
intelligence/services/sentiment_analysis_service.py
----------------------------------------------------
SentimentAnalysisService — Aggregates sentiment metrics across documents.
"""

from __future__ import annotations

from schemas.domain.project_knowledge_bundle import ProjectKnowledgeBundle
from intelligence.schemas import SentimentAnalysis
from utils.logger import get_logger

_log = get_logger("intelligence.services.sentiment_analysis")


class SentimentAnalysisService:
    """
    Evaluates net sentiment score, category distribution, and overall sentiment trend.
    """

    def analyze(self, bundle: ProjectKnowledgeBundle) -> SentimentAnalysis:
        _log.debug("Analyzing sentiment for project_id=%s", bundle.project_id)

        docs = bundle.documents
        total = len(docs)

        if total == 0:
            return SentimentAnalysis(
                net_sentiment_score=0.0,
                urgent_count=0,
                negative_count=0,
                positive_count=0,
                neutral_count=0,
                sentiment_trend="stable",
            )

        urgent_cnt = 0
        neg_cnt = 0
        pos_cnt = 0
        neu_cnt = 0

        for d in docs:
            st = d.metadata.get("sentiment", "neutral")
            if st == "urgent":
                urgent_cnt += 1
            elif st == "negative":
                neg_cnt += 1
            elif st == "positive":
                pos_cnt += 1
            else:
                neu_cnt += 1

        # Net sentiment score formula: (positive - (negative + 1.5 * urgent)) / total
        raw_score = (pos_cnt - (neg_cnt + 1.5 * urgent_cnt)) / float(total)
        net_score = max(-1.0, min(1.0, raw_score))

        trend = "stable"
        if net_score < -0.3:
            trend = "declining"
        elif net_score > 0.3:
            trend = "improving"

        analysis = SentimentAnalysis(
            net_sentiment_score=round(net_score, 2),
            urgent_count=urgent_cnt,
            negative_count=neg_cnt,
            positive_count=pos_cnt,
            neutral_count=neu_cnt,
            sentiment_trend=trend,
        )
        _log.info(
            "SentimentAnalysis complete for project_id=%s — score=%.2f, trend=%s",
            bundle.project_id, net_score, trend,
        )
        return analysis
