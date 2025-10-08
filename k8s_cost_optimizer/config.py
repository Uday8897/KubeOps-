# from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import Field

# class PrometheusSettings(BaseSettings):
#     url: str = "http://localhost:9090"
#     timeout: int = 30

# class AgentSettings(BaseSettings):
#     dry_run: bool = True

# class Settings(BaseSettings):
#     model_config = SettingsConfigDict(
#         env_file=".env", env_nested_delimiter="__", extra="ignore"
#     )

#     api_key: str = Field(..., alias="API_KEY")
#     groq_api_key: str = Field(..., alias="GROQ_API_KEY")
#     groq_model_name: str = Field("", alias="GROQ_MODEL_NAME")
    
#     log_level: str = "INFO"

#     prometheus: PrometheusSettings = PrometheusSettings()
#     agent: AgentSettings = AgentSettings()

# settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class PrometheusSettings(BaseSettings):
    url: str = Field("http://localhost:9090", alias="PROMETHEUS_URL")
    timeout: int = 30

class KubecostSettings(BaseSettings):
    url: str = Field("http://localhost:9000", alias="KUBECOST_URL")

class AgentSettings(BaseSettings):
    dry_run: bool = True

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", extra="ignore"
    )

    api_key: str = Field("", alias="API_KEY") # Optional for local dev
    groq_api_key: str = Field(..., alias="GROQ_API_KEY")
    groq_model_name: str = Field("openai/gpt-oss-20b", alias="GROQ_MODEL_NAME")
    
    log_level: str = "INFO"

    prometheus: PrometheusSettings = PrometheusSettings()
    kubecost: KubecostSettings = KubecostSettings()
    agent: AgentSettings = AgentSettings()

settings = Settings()

