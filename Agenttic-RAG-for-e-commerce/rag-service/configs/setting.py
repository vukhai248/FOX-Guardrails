import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Thư mục gốc của RAG service (rag-service/) nơi chứa file .env
BASE_DIR = Path(__file__).resolve().parent.parent

# Nạp file .env với override=True để luôn ưu tiên cấu hình trong dự án
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

class Settings(BaseSettings):
    # 1. FastAPI Config
    PORT: int = 8080
    HOST: str = "0.0.0.0"
    DEBUG: bool = True

    # 2. Supabase Connection
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_ANON_KEY: str = ""  # Public key - dùng cho verify token (quyền hạn thấp)
    SUPABASE_JWT_SECRET: str = ""  # Sử dụng để giải mã JWT Token của Supabase offline

    # 3. LLM API Keys
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEY_2: str = ""
    GEMINI_API_KEY_3: str = ""
    GEMINI_API_KEY_4: str = ""
    GEMINI_API_KEY_5: str = ""
    GEMINI_API_KEY_6: str = ""
    GEMINI_API_KEY_7: str = ""
    GEMINI_API_KEY_8: str = ""

    GROQ_API_KEY: str = ""
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_3: str = ""
    GROQ_API_KEY_4: str = ""
    GROQ_API_KEY_5: str = ""
    GROQ_API_KEY_6: str = ""
    GROQ_API_KEY_7: str = ""
    GROQ_API_KEY_8: str = ""

    OPENROUTER_API_KEY: str = ""

    # TokenHarbor (OpenAI-compatible): LLM chính; trống → chỉ dùng Gemini
    TOKENHARBOR_API_KEY: str = ""
    TOKENHARBOR_BASE_URL: str = "https://tokenharbor.ai/v1"
    TOKENHARBOR_MODEL: str = "deepseek-v4.1-flash:free"
    TOKENHARBOR_TIMEOUT: float = 60
    TOKENHARBOR_COOLDOWN: float = 600

    # 4. Vector Database Config
    VECTOR_DB_DIR: str = "../database/chroma_db"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000

    @property
    def vector_db_absolute_path(self) -> str:
        """Tự động phân giải đường dẫn tương đối thành tuyệt đối dựa trên BASE_DIR (rag-service/)"""
        p = Path(self.VECTOR_DB_DIR)
        if p.is_absolute():
            return str(p)
        return str((BASE_DIR / p).resolve())

    # Đọc cấu hình từ file .env nằm ở thư mục gốc của rag-service/
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"  # Bỏ qua các biến môi trường thừa khác trên hệ thống
    )

# Khởi tạo instance settings toàn cục
settings = Settings()
