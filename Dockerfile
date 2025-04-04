FROM python:3.11 AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# 安裝 Poetry 並建立虛擬環境
RUN pip install poetry
RUN poetry config virtualenvs.in-project true

# 複製 pyproject 檔案並安裝依賴
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root

# 第二階段建立精簡映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製虛擬環境與所有程式碼
COPY --from=builder /app/.venv .venv/
COPY . .

# 設定環境變數讓 Streamlit 使用虛擬環境
ENV PATH="/app/.venv/bin:$PATH"

# 啟動 Streamlit
CMD ["streamlit", "run", "MediGuide/main.py"]
