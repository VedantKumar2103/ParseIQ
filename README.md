# ParseIQ ( A Resume Analyser App )

## Source
- Extracting user's information from the Resume, I used [PyResparser](https://omkarpathak.in/pyresparser/)
- Extracting Resume PDF into Text, I used [PDFMiner](https://pypi.org/project/pdfminer/).

## Features
- User's & Admin Section
- Resume Score
- Career Recommendations
- Resume writing Tips suggestions
- Courses Recommendations
- Skills Recommendations
- Youtube video recommendations

## Usage
- Clone my repository.
- Open CMD in working directory.
- Run following command.
  ```
  pip install -r requirements.txt
  ```
- `App.py` is the main Python file of Streamlit Web-Application. 
- `Courses.py` is the Python file that contains courses and youtube video links.
- Download XAMP or any other control panel, and turn on the Apache & SQL service.
- To run app, write following command in CMD. or use any IDE.
  ```
  streamlit run App.py
  ```
- `Uploaded_Resumes` folder is contaning the user's uploaded resumes.
- `Classifier.py` is the main file which is containing a KNN Algorithm.
- For more explanation of this project see the tutorial on Machine Learning Hub YouTube channel.
- Admin side credentials is `admin` and password is `admin123`. 

## Screenshots

## User side
<img src="[![screencapture-localhost-8501-2025-05-20-15_09_29](https://github.com/user-attachments/assets/d29b767b-17f5-4495-b3b1-1709cdb5973d)](https://github.com/VedantKumar2103/ParseIQ/blob/189d321930cf6a59c3a9b818532fbd1f570e9886/User.png)">


## Admin Side
<img src="https://github.com/VedantKumar2103/ParseIQ/blob/b35ebb510bdf8caa0ae869ced64af3f415b38695/Admin.png">


