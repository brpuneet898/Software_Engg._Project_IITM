# **Software Engineering Project for the Term May 2024**  
**IIT Madras B.S Program**

Welcome to the Software Engineering Project for the May 2024 term,In this project our team designed a SEEK Portal with GenaAI Features for the B.S Program at IIT Madras. This README file will guide you through the process of setting up and running the application on your local machine.

## **Table of Contents**
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Application](#running-the-application)
5. [Usage](#usage)
6. [Troubleshooting](#troubleshooting)

## **Prerequisites**
Before you begin, ensure you have the following installed:
- **Python**: Version 3.10 or higher
- **Git**: For cloning the repository

## **Installation**

### 1. **Clone the Repository**
Open your terminal (CMD, Powershell, or Bash) and run the following command to clone the repository:

```bash
git clone https://github.com/AryanCodesDS/soft-engg-project-may-2024-se-may-20.git
```

Alternatively, you can use GitHub Desktop to clone the repository.

### 2. **Set Up a Virtual Environment**
Navigate to the project directory:

```bash
cd soft-engg-project-may-2024-se-may-20
```

Create and activate a virtual environment:

- On **Windows**:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. **Install Dependencies**
Install all required libraries using the following command:

```bash
pip install -r requirements.txt
```

**Note**: The installation size is roughly 3 GB, so ensure you have sufficient disk space available.

## **Configuration**

Before running the application, you need to configure the API keys:

1. Open `chatbot.py` and `llm_setup.py`.
2. Add your **Google Cloud Generative AI** API keys and **Pinecone Vector DB** API keys in the respective files.

## **Running the Application**

To start the application, use one of the following commands:

- On **Windows**:
  ```bash
  python app.py
  ```

- On **macOS/Linux**:
  ```bash
  python3 app.py
  ```

## **Usage**

1. Once the application is running, open your web browser and visit:
   ```
   http://127.0.0.1:5000/
   ```
   
2. Click on the "Sign in with Google" button and sign in using your **IITM BS student email ID**.

   **Note**: We only collect your email and profile picture, ensuring that your personal data remains 100% safe.

3. Explore the portal and enjoy the new and exciting features!

## **Troubleshooting**

If you encounter any issues:
- Ensure your Python version is 3.10 or higher.
- Check if all dependencies are correctly installed.
- Verify that your API keys are correctly configured in `chatbot.py` and `llm_setup.py`.
- If the app doesn’t start, make sure your virtual environment is activated.

For further assistance, refer to the project documentation or contact the project maintainer (21f1001076@ds.study.iitm.ac.in) .
