<div align="center" width="100%">
    <img src="./stamp-logo.svg" width="100" alt="" />
</div>

# Stamp-API

**Stamp-API** is a REST API server for embedding **invisible watermarks** into images.  
Developed using Python and the **FastAPI** framework, it supports two types of invisible watermarks: **text** and **image**.

---

## 📋 Features

- **Text Watermark**: Embed custom text as an invisible watermark into an image.
- **Image Watermark**: Embed another image as an invisible watermark into a target image.

---

## 🚀 Installation and Usage

### Prerequisites

- Python 3.9 or higher
- `pip` package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/Stamp-API.git
   cd Stamp-API
   ```
2. **Set up a virtual environment**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```
3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```
4. **Run the server**
    ```bash
    uvicorn app.main:app --reload
    ```

## 📂 Project Structure
```bash
Stamp-API/
├── auth/             # Auth (ex: google token validation)
├── config/           # Configuration files
├── controllers/      # Controller of api
├── db/               # Mongo db modules
├── postoffice/       # Modules for watermark creating and validating
├── routes/           # API rountes files
├── Dockerfile        # Dockerfile
├── main.py           # main:app
├── requirements.txt  # Dependency list
└── README.md         # Project documentation
```

## 📜 License

This project is licensed under the MIT License. For more information, see the [LICENSE](./LICENSE) file.