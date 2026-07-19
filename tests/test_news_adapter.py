from pathlib import Path

from prosway_acquisition.adapters.news import NewsManualAdapter
from prosway_acquisition.domain import CompanyProfile


def test_news_manual_adapter_detects_growth_keywords(tmp_path: Path):
    path = tmp_path / "news.csv"
    path.write_text("siren,title,description,source_url\n123456789,Levée de fonds,ACME ouvre un bureau et annonce une forte croissance,https://news.example\n", encoding="utf-8")
    evidence = NewsManualAdapter(path).collect(CompanyProfile("ACME", "123456789"))
    assert {item.signal_type for item in evidence} == {"fundraising_recent", "new_office", "strong_growth_claim"}
