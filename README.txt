DIGITAL NOTICE BOARD SYSTEM
=========================
Files:
- app.py: complete Streamlit web application
- requirements.txt: required Python libraries

Run on Windows:
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Run: pip install -r requirements.txt
4. Run: streamlit run app.py
5. Open the local URL shown in the terminal (usually http://localhost:8501).

Administrator:
- Select Administrator in the sidebar.
- Demo password: admin123
- For deployment, set environment variable NOTICE_ADMIN_PASSWORD to a strong password.
- Notices are saved in notices.csv in the app's working folder.

Note: CSV storage is suitable for a small demonstration. For multi-user production use,
configure persistent database storage and proper authentication.
