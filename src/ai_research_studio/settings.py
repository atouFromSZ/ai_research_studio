from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "AI Research Studio"
    report_subdir: str = "daily"
    request_timeout: int = 10

    binance_base_url: str = "https://api.binance.com"
    market_symbols: str = "BTCUSDT,ETHUSDT,SOLUSDT"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def data_dir(self) -> Path:
        return self.project_root / "data"

    @property
    def reports_dir(self) -> Path:
        return self.project_root / "reports"

    @property
    def daily_reports_dir(self) -> Path:
        return self.reports_dir / self.report_subdir

    @property
    def symbol_list(self) -> list[str]:
        return [symbol.strip().upper() for symbol in self.market_symbols.split(",") if symbol.strip()]


settings = Settings()