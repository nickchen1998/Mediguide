# 🩺 智慧問診機器人（MediGuide）

> **_本專案僅供學術研究與展示用途，未經醫療專業認證，請勿用於實際醫療診斷。_**

這是一個以 Streamlit 打造的智慧問診機器人原型，整合 OpenAI GPT-4o 進行問答，以及 Whisper 模型辨識語音，讓使用者可以透過文字或語音與系統互動，模擬簡易問診流程。

---

## 🗂️ 專案結構


├── /MediGuide/main.py              # 主程式

├── /MediGuide/utils.py            # 工具函式：Whisper 語音辨識、對話紀錄處理

├── /MediGuide/chains.py           # LangChain LLM 處理：擷取使用者語音資料的關鍵資訊

├── Dockerfile    # Docker 映像檔設定檔 (可用於 fly.io 或 local 部署)

├── fly.toml    # 部署於 fly.io 的設定檔

├── pyproject.toml    # 套件需求

├── README.md           # 說明文件

└── requirements.txt    # 套件需求

---

## 🚀 Local 安裝與執行方式

### 1️⃣ 安裝依賴套件
建議使用虛擬環境，並安裝以下依賴：

```bash
poetry install
```

or 
```bash
pip install -r requirements.txt
```

### 2️⃣ 建立 `secrets.toml`

請建立以下檔案以儲存各項金鑰：

```
MediGuide/.streamlit/secrets.toml
```

內容範例如下或是可參考 `MediGuide/.streamlit/template_secrets.toml`：

```toml
OPENAI_API_KEY = "你的 OpenAI API 金鑰"
```

### 3️⃣ 執行應用程式

```bash
cd ./MediGuide
```

```bash
streamlit run ./main.py
```

打開瀏覽器後即可互動使用。

---

## 🎙️ 語音輸入教學

- 點選 Sidebar 的「🎤 使用聲音輔助輸入」按鈕。
- 說出類似：「我叫陳小明，身分證是 A123456789，生日是 2001 年 4 月 5 日，血型 O」

---

## 💡 延伸方向（可選擇實作）

- 設計緊急風險分類（例如偵測關鍵詞如「胸痛」、「喘不過氣」）
- 支援醫療單位串接或 HIS 整合

---
