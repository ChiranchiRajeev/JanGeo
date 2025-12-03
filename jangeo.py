import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import mysql.connector
from mysql.connector import Error
import datetime
import hashlib
import streamlit.components.v1 as components
from PIL import Image
import io
import pyarrow as pa
import pyarrow.parquet as pq
import os

# =============================================
#           MYSQL CONNECTION (PRODUCTION READY)
# =============================================

try:
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", "Rajeevsonu@2005"),  # Change this!
        database=os.getenv("MYSQL_DATABASE", "jangeo"),
        autocommit=False,
        ssl_disabled=True
    )
    c = conn.cursor(buffered=True)

except Error as err:
    st.error(f"Database connection failed: {err}")
    st.stop()

# Create tables — EXACT same structure as your SQLite
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    consent TINYINT(1) DEFAULT 0
)''')

c.execute('''CREATE TABLE IF NOT EXISTS reports (
    id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    issue_type VARCHAR(255),
    description TEXT,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    photo LONGBLOB,
    department VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Pending'
)''')

c.execute('''CREATE TABLE IF NOT EXISTS feedbacks (
    id VARCHAR(50) PRIMARY KEY,
    report_id VARCHAR(50),
    feedback TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS id_counter (
    entity_type VARCHAR(50) PRIMARY KEY,
    last_number INT DEFAULT 0
)''')

# Initialize counters
for entity in ['User', 'Report', 'Feedback']:
    c.execute("INSERT IGNORE INTO id_counter (entity_type, last_number) VALUES (%s, 0)", (entity,))
conn.commit()

# =============================================
#       FULL MULTI-LANGUAGE SUPPORT (100% YOUR ORIGINAL)
# =============================================

# Multi-language support — Telugu, Tamil, Kannada, Malayalam
languages = {
    'en': 'English',
    'te': 'తెలుగు',      # Telugu
    'ta': 'தமிழ்',        # Tamil
    'kn': 'ಕನ್ನಡ',       # Kannada
    'ml': 'മലയാളം',       # Malayalam
    'hi': 'हिन्दी'
}

translations = {
    'en': {  # Keep English as base
        'Account': 'Account', 'Login': 'Login', 'Register': 'Register', 'Username': 'Username',
        'Password': 'Password', 'Logged in!': 'Logged in!', 'Registered! Please login.': 'Registered! Please login.',
        'Welcome!': 'Welcome!', 'Logout': 'Logout', 'Data Consent': 'Data Consent',
        'Please provide consent for data usage.': 'Please provide consent for data usage.',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.',
        'I Consent': 'I Consent', 'Report Issue': 'Report Issue', 'View Reports': 'View Reports',
        'Dashboard': 'Dashboard', 'Feedback': 'Feedback', 'Report Infrastructure Issue': 'Report Infrastructure Issue',
        'Latitude': 'Latitude', 'Longitude': 'Longitude', 'Issue Type': 'Issue Type', 'Pothole': 'Pothole',
        'Water Leak': 'Water Leak', 'Power Outage': 'Power Outage', 'Garbage': 'Garbage', 'Other': 'Other',
        'Description': 'Description', 'Upload Photo': 'Upload Photo', 'Assign to Department': 'Assign to Department',
        'Submit Report': 'Submit Report', 'Report Submitted!': 'Report Submitted!', 'View My Reports': 'View My Reports',
        'Department Dashboard': 'Department Dashboard', 'Select Department': 'Select Department',
        'Select Report to Update': 'Select Report to Update', 'Update Status': 'Update Status',
        'Update': 'Update', 'Updated!': 'Updated!', 'Export Format (for Power BI)': 'Export Format (for Power BI)',
        'Download Data': 'Download Data', 'Provide Feedback': 'Provide Feedback', 'Select Report': 'Select Report',
        'Submit Feedback': 'Submit Feedback', 'Feedback Submitted!': 'Feedback Submitted!',
        'High Contrast Mode': 'High Contrast Mode', 'Partners: State Gov, Tech Co': 'Partners: State Gov, Tech Co'
    },
    'te': {  # తెలుగు - Telugu
        'Account': 'ఖాతా', 'Login': 'లాగిన్', 'Register': 'నమోదు', 'Username': 'వినియోగదారు పేరు',
        'Password': 'పాస్‌వర్డ్', 'Logged in!': 'లాగిన్ అయింది!', 'Registered! Please login.': 'నమోదయింది! దయచేసి లాగిన్ చేయండి.',
        'Welcome!': 'స్వాగతం!', 'Logout': 'లాగౌట్', 'Data Consent': 'డేటా అనుమతి',
        'Please provide consent for data usage.': 'డేటా ఉపయోగం కోసం అనుమతి ఇవ్వండి.',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'రిపోర్టింగ్ కోసం మీ లొకేషన్ డేటా సేకరించడానికి మీ అనుమతి అవసరం. డేటా సురక్షితం మరియు ఈ-పాలన కోసం మాత్రమే ఉపయోగించబడుతుంది.',
        'I Consent': 'నేను అంగీకరిస్తున్నాను', 'Report Issue': 'సమస్య నివేదించండి', 'View Reports': 'నివేదికలు చూడండి',
        'Dashboard': 'డాష్‌బోర్డ్', 'Feedback': 'అభిప్రాయం', 'Report Infrastructure Issue': 'మౌలిక సదుపాయాల సమస్య నివేదించండి',
        'Latitude': 'అక్షాంశం', 'Longitude': 'రేఖాంశం', 'Issue Type': 'సమస్య రకం', 'Pothole': 'గుంత',
        'Water Leak': 'నీటి లీకేజీ', 'Power Outage': 'విద్యుత్ అంతరాయం', 'Garbage': 'చెత్త', 'Other': 'ఇతరం',
        'Description': 'వివరణ', 'Upload Photo': 'ఫోటో అప్‌లోడ్ చేయండి', 'Assign to Department': 'విభాగానికి కేటాయించండి',
        'Submit Report': 'నివేదిక సమర్పించండి', 'Report Submitted!': 'నివేదిక సమర్పించబడింది!', 'View My Reports': 'నా నివేదికలు చూడండి',
        'Department Dashboard': 'విభాగ డాష్‌బోర్డ్', 'Select Department': 'విభాగం ఎంచుకోండి',
        'Select Report to Update': 'అప్‌డేట్ చేయడానికి నివేదిక ఎంచుకోండి', 'Update Status': 'స్థితి అప్‌డేట్ చేయండి',
        'Update': 'అప్‌డేట్', 'Updated!': 'అప్‌డేట్ అయింది!', 'Export Format (for Power BI)': 'ఎగుమతి ఫార్మాట్ (పవర్ BI కోసం)',
        'Download Data': 'డేటా డౌన్‌లోడ్ చేయండి', 'Provide Feedback': 'అభిప్రాయం ఇవ్వండి', 'Select Report': 'నివేదిక ఎంచుకోండి',
        'Submit Feedback': 'అభిప్రాయం సమర్పించండి', 'Feedback Submitted!': 'అభిప్రాయం సమర్పించబడింది!',
        'High Contrast Mode': 'అధిక కాంట్రాస్ట్ మోడ్', 'Partners: State Gov, Tech Co': 'భాగస్వాములు: రాష్ట్ర ప్రభుత్వం, టెక్ కంపెనీ'
    },
    'ta': {  # தமிழ் - Tamil
        'Account': 'கணக்கு', 'Login': 'உள்நுழை', 'Register': 'பதிவு', 'Username': 'பயனர் பெயர்',
        'Password': 'கடவுச்சொல்', 'Logged in!': 'உள்நுழைந்துவிட்டீர்கள்!', 'Registered! Please login.': 'பதிவு செய்யப்பட்டது! தயவுசெய்து உள்நுழையவும்.',
        'Welcome!': 'வரவேற்கிறோம்!', 'Logout': 'வெளியேறு', 'Data Consent': 'தரவு அனுமதி',
        'Please provide consent for data usage.': 'தரவு பயன்பாட்டிற்கு அனுமதி வழங்கவும்.',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'அறிக்கையிடலுக்காக உங்கள் இருப்பிட தரவை சேகரிக்க உங்கள் அனுமதி தேவை. தரவு பாதுகாப்பாக உள்ளது மற்றும் மின்னணு ஆட்சிக்கு மட்டுமே பயன்படுத்தப்படுகிறது.',
        'I Consent': 'நான் ஒப்புக்கொள்கிறேன்', 'Report Issue': 'பிரச்சனை புகாரளி', 'View Reports': 'அறிக்கைகளைப் பார்',
        'Dashboard': 'டாஷ்போர்டு', 'Feedback': 'கருத்து', 'Report Infrastructure Issue': 'உள்கட்டமைப்பு பிரச்சனை புகாரளி',
        'Latitude': 'அட்சரேகை', 'Longitude': 'தீர்க்கரேகை', 'Issue Type': 'பிரச்சனை வகை', 'Pothole': 'குழி',
        'Water Leak': 'நீர் கசிவு', 'Power Outage': 'மின்தடை', 'Garbage': 'குப்பை', 'Other': 'மற்றவை',
        'Description': 'விளக்கம்', 'Upload Photo': 'புகைப்படம் பதிவேற்றவும்', 'Assign to Department': 'துறைக்கு ஒதுக்கு',
        'Submit Report': 'அறிக்கை சமர்ப்பி', 'Report Submitted!': 'அறிக்கை சமர்ப்பிக்கப்பட்டது!', 'View My Reports': 'என் அறிக்கைகளைப் பார்',
        'Department Dashboard': 'துறை டாஷ்போர்டு', 'Select Department': 'துறையைத் தேர்ந்தெடு',
        'Select Report to Update': 'புதுப்பிக்க அறிக்கையைத் தேர்ந்தெடு', 'Update Status': 'நிலையைப் புதுப்பி',
        'Update': 'புதுப்பி', 'Updated!': 'புதுப்பிக்கப்பட்டது!', 'Export Format (for Power BI)': 'ஏற்றுமதி வடிவம் (Power BIக்கு)',
        'Download Data': 'தரவைப் பதிவிறக்கு', 'Provide Feedback': 'கருத்து தெரிவி', 'Select Report': 'அறிக்கையைத் தேர்ந்தெடு',
        'Submit Feedback': 'கருத்தை சமர்ப்பி', 'Feedback Submitted!': 'கருத்து சமர்ப்பிக்கப்பட்டது!',
        'High Contrast Mode': 'உயர் மாறுபாடு பயன்முறை', 'Partners: State Gov, Tech Co': 'கூட்டாளிகள்: மாநில அரசு, தொழில்நுட்ப நிறுவனம்'
    },
    'kn': {  # ಕನ್ನಡ - Kannada
        'Account': 'ಖಾತೆ', 'Login': 'ಲಾಗಿನ್', 'Register': 'ನೋಂದಣಿ', 'Username': 'ಬಳಕೆದಾರ ಹೆಸರು',
        'Password': 'ಪಾಸ್ವರ್ಡ್', 'Logged in!': 'ಲಾಗಿನ್ ಆಯಿತು!', 'Registered! Please login.': 'ನೋಂದಾಯಿತು! ದерахವಾಗಿ ಲಾಗಿನ್ ಮಾಡಿ.',
        'Welcome!': 'ಸ್ವಾಗತ!', 'Logout': 'ಲಾಗ್ಔಟ್', 'Data Consent': 'ಡೇಟಾ ಅನುಮತಿ',
        'Please provide consent for data usage.': 'ಡೇಟಾ ಬಳಕೆಗೆ ಅನುಮತಿ ನೀಡಿ.',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'ವರದಿ ಮಾಡಲು ನಿಮ್ಮ ಸ್ಥಳದ ಮಾಹಿತಿಯನ್ನು ಸಂಗ್ರಹಿಸಲು ನಿಮ್ಮ ಅನುಮತಿ ಬೇಕು. ಡೇಟಾ ಸುರಕ್ಷಿತವಾಗಿದೆ ಮತ್ತು ಇ-ಆಡಳಿತಕ್ಕೆ ಮಾತ್ರ ಬಳಸಲಾಗುತ್ತದೆ.',
        'I Consent': 'ನಾನು ಒಪ್ಪುತ್ತೇನೆ', 'Report Issue': 'ತೊಂದರೆ ವರದಿ ಮಾಡಿ', 'View Reports': 'ವರದಿಗಳನ್ನು ನೋಡಿ',
        'Dashboard': 'ಡ್ಯಾಶ್‌ಬೋರ್ಡ್', 'Feedback': 'ಪ್ರತಿಕ್ರಿಯೆ', 'Report Infrastructure Issue': 'ಮೂಲಸೌಕರ್ಯ ಸಮಸ್ಯೆ ವರದಿ ಮಾಡಿ',
        'Latitude': 'ಅಕ್ಷಾಂಶ', 'Longitude': 'ರೇಖಾಂಶ', 'Issue Type': 'ತೊಂದರೆ ಪ್ರಕಾರ', 'Pothole': 'ಗುಂಡಿ',
        'Water Leak': 'ನೀರು ಸೋರಿಕೆ', 'Power Outage': 'ವಿದ್ಯುತ್ ತೊಂದರೆ', 'Garbage': 'ಕಸ', 'Other': 'ಇತರೆ',
        'Description': 'ವಿವರಣೆ', 'Upload Photo': 'ಫೋಟೋ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ', 'Assign to Department': 'ಇಲಾಖೆಗೆ ನಿಗದಿಪಡಿಸಿ',
        'Submit Report': 'ವರದಿ ಸಲ್ಲಿಸಿ', 'Report Submitted!': 'ವರದಿ ಸಲ್ಲಿಸಲಾಗಿದೆ!', 'View My Reports': 'ನನ್ನ ವರದಿಗಳನ್ನು ನೋಡಿ',
        'Department Dashboard': 'ಇಲಾಖೆ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್', 'Select Department': 'ಇಲಾಖೆ ಆಯ್ಕೆಮಾಡಿ',
        'Select Report to Update': 'ಅಪ್‌ಡೇಟ್ ಮಾಡಲು ವರದಿ ಆಯ್ಕೆಮಾಡಿ', 'Update Status': 'ಸ್ಥಿತಿ ಅಪ್‌ಡೇಟ್ ಮಾಡಿ',
        'Update': 'ಅಪ್‌ಡೇಟ್', 'Updated!': 'ಅಪ್‌ಡೇಟ್ ಆಯಿತು!', 'Export Format (for Power BI)': 'ಏಷಿಯಾ ಫಾರ್ಮ್ಯಾಟ್ (Power BIಗೆ)',
        'Download Data': 'ಡೇಟಾ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ', 'Provide Feedback': 'ಪ್ರತಿಕ್ರಿಯೆ ನೀಡಿ', 'Select Report': 'ವರದಿ ಆಯ್ಕೆಮಾಡಿ',
        'Submit Feedback': 'ಪ್ರತಿಕ್ರಿಯೆ ಸಲ್ಲಿಸಿ', 'Feedback Submitted!': 'ಪ್ರತಿಕ್ರಿಯೆ ಸಲ್ಲಿಸಲಾಗಿದೆ!',
        'High Contrast Mode': 'ಹೆಚ್ಚಿನ ಕಾಂಟ್ರಾಸ್ಟ್ ಮೋಡ್', 'Partners: State Gov, Tech Co': 'ಪಾಲುದಾರರು: ರಾಜ್ಯ ಸರ್ಕಾರ, ತಂತ್ರಜ್ಞಾನ ಕಂಪನಿ'
    },
    'ml': {  # മലയാളം - Malayalam
        'Account': 'അക്കൗണ്ട്', 'Login': 'ലോഗിൻ', 'Register': 'രജിസ്റ്റർ', 'Username': 'ഉപയോക്തൃനാമം',
        'Password': 'പാസ്‌വേഡ്', 'Logged in!': 'ലോഗിൻ ചെയ്തു!', 'Registered! Please login.': 'രജിസ്റ്റർ ചെയ്തു! ദയവായി ലോഗിൻ ചെയ്യൂ.',
        'Welcome!': 'സ്വാഗതം!', 'Logout': 'ലോഗൗട്ട്', 'Data Consent': 'ഡാറ്റ അനുമതി',
        'Please provide consent for data usage.': 'ഡാറ്റ ഉപയോഗത്തിന് അനുമതി നൽകുക.',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'റിപ്പോർട്ടിംഗിനായി നിങ്ങളുടെ ലൊക്കേഷൻ ഡാറ്റ ശേഖരിക്കാൻ നിങ്ങളുടെ അനുമതി ആവശ്യമാണ്. ഡാറ്റ സുരക്ഷിതമാണ്, ഇ-ഗവേണൻസിന് മാത്രം ഉപയോഗിക്കുന്നു.',
        'I Consent': 'ഞാൻ അനുമതി നൽകുന്നു', 'Report Issue': 'പ്രശ്നം റിപ്പോർട്ട് ചെയ്യൂ', 'View Reports': 'റിപ്പോർട്ടുകൾ കാണൂ',
        'Dashboard': 'ഡാഷ്ബോർഡ്', 'Feedback': 'ഫീഡ്ബാക്ക്', 'Report Infrastructure Issue': 'അടിസ്ഥാന സൗകര്യ പ്രശ്നം റിപ്പോർട്ട് ചെയ്യൂ',
        'Latitude': 'അക്ഷാംശം', 'Longitude': 'രേഖാംശം', 'Issue Type': 'പ്രശ്ന തരം', 'Pothole': 'കുഴി',
        'Water Leak': 'വെള്ളം ചോർച്ച', 'Power Outage': 'വൈദ്യുതി മുടക്കം', 'Garbage': 'മാലിന്യം', 'Other': 'മറ്റുള്ളവ',
        'Description': 'വിവരണം', 'Upload Photo': 'ഫോട്ടോ അപ്‌ലോഡ് ചെയ്യൂ', 'Assign to Department': 'വകുപ്പിന് നൽകൂ',
        'Submit Report': 'റിപ്പോർട്ട് സമർപ്പിക്കൂ', 'Report Submitted!': 'റിപ്പോർട്ട് സമർപ്പിച്ചു!', 'View My Reports': 'എന്റെ റിപ്പോർട്ടുകൾ കാണൂ',
        'Department Dashboard': 'വകുപ്പ് ഡാഷ്ബോർഡ്', 'Select Department': 'വകുപ്പ് തിരഞ്ഞെടുക്കൂ',
        'Select Report to Update': 'അപ്ഡേറ്റ് ചെയ്യാൻ റിപ്പോർട്ട് തിരഞ്ഞെടുക്കൂ', 'Update Status': 'സ്റ്റാറ്റസ് അപ്ഡേറ്റ് ചെയ്യൂ',
        'Update': 'അപ്ഡേറ്റ്', 'Updated!': 'അപ്ഡേറ്റ് ചെയ്തു!', 'Export Format (for Power BI)': 'എക്‌സ്‌പോർട്ട് ഫോർമാറ്റ് (Power BI)',
        'Download Data': 'ഡാറ്റ ഡൗൺലോഡ് ചെയ്യൂ', 'Provide Feedback': 'ഫീഡ്ബാക്ക് നൽകൂ', 'Select Report': 'റിപ്പോർട്ട് തിരഞ്ഞെടുക്കൂ',
        'Submit Feedback': 'ഫീഡ്ബാക്ക് സമർപ്പിക്കൂ', 'Feedback Submitted!': 'ഫീഡ്ബാക്ക് സമർപ്പിച്ചു!',
        'High Contrast Mode': 'ഉയർന്ന കോൺട്രാസ്റ്റ് മോഡ്', 'Partners: State Gov, Tech Co': 'പങ്കാളികൾ: സംസ്ഥാന സർക്കാർ, ടെക് കമ്പനി'
    },
    'hi': {  # ← Your full Hindi dict
        'Account': 'खाता', 'Login': 'लॉगिन', 'Register': 'पंजीकरण', 'Username': 'उपयोगकर्ता नाम',
        'Password': 'पासवर्ड', 'Logged in!': 'लॉग इन हो गया!', 'Registered! Please login.': 'पंजीकृत! कृपया लॉगिन करें।',
        'Welcome!': 'स्वागत है!', 'Logout': 'लॉगआउट', 'Data Consent': 'डेटा सहमति',
        'Please provide consent for data usage.': 'कृपया डेटा उपयोग के लिए सहमति प्रदान करें।',
        'We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance.': 'हमें रिपोर्टिंग उद्देश्यों के लिए जियोलोकेशन डेटा एकत्र करने और संसाधित करने के लिए आपकी सहमति की आवश्यकता है। डेटा सुरक्षित है और केवल ई-गवर्नेंस के लिए उपयोग किया जाता है।',
        'I Consent': 'मैं सहमति देता हूँ', 'Report Issue': 'समस्या की सूचना दें', 'View Reports': 'रिपोर्ट देखें',
        'Dashboard': 'डैशबोर्ड', 'Feedback': 'प्रतिक्रिया', 'Report Infrastructure Issue': 'बुनियादी ढांचे की समस्या की सूचना दें',
        'Latitude': 'अक्षांश', 'Longitude': 'देशांतर', 'Issue Type': 'समस्या का प्रकार', 'Pothole': 'गड्ढा',
        'Water Leak': 'पानी का रिसाव', 'Power Outage': 'बिजली कटौती', 'Garbage': 'कचरा', 'Other': 'अन्य',
        'Description': 'विवरण', 'Upload Photo': 'फोटो अपलोड करें', 'Assign to Department': 'विभाग को सौंपें',
        'Submit Report': 'रिपोर्ट सबमिट करें', 'Report Submitted!': 'रिपोर्ट सबमिट की गई!', 'View My Reports': 'मेरी रिपोर्ट देखें',
        'Department Dashboard': 'विभाग डैशबोर्ड', 'Select Department': 'विभाग चुनें',
        'Select Report to Update': 'अपडेट करने के लिए रिपोर्ट चुनें', 'Update Status': 'स्थिति अपडेट करें',
        'Update': 'अपडेट', 'Updated!': 'अपडेट किया गया!', 'Export Format (for Power BI)': 'निर्यात प्रारूप (पावर बीआई के लिए)',
        'Download Data': 'डेटा डाउनलोड करें', 'Provide Feedback': 'प्रतिक्रिया प्रदान करें', 'Select Report': 'रिपोर्ट चुनें',
        'Submit Feedback': 'प्रतिक्रिया सबमिट करें', 'Feedback Submitted!': 'प्रतिक्रिया सबमिट की गई!',
        'High Contrast Mode': 'उच्च कंट्रास्ट मोड', 'Partners: State Gov, Tech Co': 'भागीदार: राज्य सरकार, तकनीकी कंपनी'
    }
}
# Session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'lang' not in st.session_state:
    st.session_state.lang = 'en'
if 'consent' not in st.session_state:
    st.session_state.consent = False

# Translation function
def _(text):
    return translations.get(st.session_state.lang, translations['en']).get(text, text)

# Generate custom ID
def generate_id(entity_type):
    c.execute("SELECT last_number FROM id_counter WHERE entity_type=%s FOR UPDATE", (entity_type,))
    row = c.fetchone()
    if not row:
        last_number = 0
        c.execute("INSERT INTO id_counter (entity_type, last_number) VALUES (%s, 0)", (entity_type,))
    else:
        last_number = row[0]
    new_number = last_number + 1
    c.execute("UPDATE id_counter SET last_number=%s WHERE entity_type=%s", (new_number, entity_type))
    conn.commit()
    return f"Jan{entity_type}{new_number}"

# Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def register_user(username, password):
    hashed = hash_password(password)
    user_id = generate_id("User")
    try:
        c.execute("INSERT INTO users (id, username, password, consent) VALUES (%s, %s, %s, 0)", (user_id, username, hashed))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    hashed = hash_password(password)
    c.execute("SELECT id, consent FROM users WHERE username=%s AND password=%s", (username, hashed))
    user = c.fetchone()
    if user:
        st.session_state.user = user[0]
        st.session_state.consent = bool(user[1])
        return True
    return False

def update_consent(user_id):
    c.execute("UPDATE users SET consent=1 WHERE id=%s", (user_id,))
    conn.commit()
    st.session_state.consent = True

# Geolocation JS component (exact same as original)
def get_location():
    components.html("""
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition);
        } else {
            parent.document.getElementById("location").innerHTML = "Geolocation is not supported.";
        }
    }
    function showPosition(position) {
        window.parent.postMessage({
            type: "location",
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
        }, "*");
    }
    getLocation();
    </script>
    """, height=0)

    if 'location' not in st.session_state:
        st.session_state.location = None

# Report submission
def submit_report(issue_type, description, lat, lon, photo, department):
    report_id = generate_id("Report")
    photo_data = photo.read() if photo else None
    c.execute("""INSERT INTO reports 
        (id, user_id, issue_type, description, latitude, longitude, photo, department)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (report_id, st.session_state.user, issue_type, description, lat, lon, photo_data, department))
    conn.commit()

# Fetch reports
def get_reports(department=None):
    if department:
        c.execute("SELECT * FROM reports WHERE department=%s", (department,))
    else:
        c.execute("SELECT * FROM reports")
    rows = c.fetchall()
    if not rows:
        return pd.DataFrame(columns=['id', 'user_id', 'issue_type', 'description', 'latitude', 'longitude', 'timestamp', 'photo', 'department', 'status'])
    return pd.DataFrame(rows, columns=['id', 'user_id', 'issue_type', 'description', 'latitude', 'longitude', 'timestamp', 'photo', 'department', 'status'])

# Update status
def update_status(report_id, status):
    try:
        c.execute("UPDATE reports SET status=%s WHERE id=%s", (status, report_id))
        conn.commit()
        return True
    except:
        return False

# Feedback
def submit_feedback(report_id, feedback):
    feedback_id = generate_id("Feedback")
    c.execute("INSERT INTO feedbacks (id, report_id, feedback) VALUES (%s, %s, %s)",
              (feedback_id, report_id, feedback))
    conn.commit()

# Map display
def display_map(df):
    if not df.empty:
        m = folium.Map(location=[df['latitude'].mean(), df['longitude'].mean()], zoom_start=10)
        for idx, row in df.iterrows():
            folium.Marker([row['latitude'], row['longitude']], popup=f"{row['issue_type']}: {row['description']}").add_to(m)
        folium_static(m)

# Export data
def export_data(df, format='csv'):
    export_df = df.drop(columns=['photo'], errors='ignore')
    if format == 'csv':
        return export_df.to_csv(index=False).encode('utf-8')
    elif format == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            export_df.to_excel(writer, index=False)
        return output.getvalue()
    elif format == 'parquet':
        table = pa.Table.from_pandas(export_df)
        output = io.BytesIO()
        pq.write_table(table, output)
        return output.getvalue()

# Departments
departments = ['Roads', 'Water', 'Electricity', 'Sanitation', 'Other']

# =============================================
#                  MAIN APP (100% YOUR ORIGINAL)
# =============================================

st.set_page_config(page_title="JanGeo", layout="wide", initial_sidebar_state="expanded")

# Language selector
lang = st.sidebar.selectbox(_("Language / Idioma / Langue / भाषा"), list(languages.values()))
st.session_state.lang = list(languages.keys())[list(languages.values()).index(lang)]

# Sidebar for auth
if not st.session_state.user:
    tab = st.sidebar.radio(_("Account"), [_("Login"), _("Register")])
    if tab == _("Login"):
        username = st.sidebar.text_input(_("Username"))
        password = st.sidebar.text_input(_("Password"), type="password")
        if st.sidebar.button(_("Login")):
            if login_user(username, password):
                st.sidebar.success(_("Logged in!"))
                if not st.session_state.consent:
                    st.warning(_("Please provide consent for data usage."))
    else:
        username = st.sidebar.text_input(_("Username"))
        password = st.sidebar.text_input(_("Password"), type="password")
        if st.sidebar.button(_("Register")):
            if register_user(username, password):
                st.sidebar.success(_("Registered! Please login."))
else:
    st.sidebar.success(_("Welcome!") + st.session_state.user)
    if st.sidebar.button(_("Logout")):
        st.session_state.user = None
        st.session_state.consent = False
        st.rerun()

if st.session_state.user and not st.session_state.consent:
    st.title(_("Data Consent"))
    st.write(_("We require your consent to collect and process geolocation data for reporting purposes. Data is secured and used only for e-governance."))
    if st.button(_("I Consent")):
        update_consent(st.session_state.user)
        st.rerun()

if st.session_state.user and st.session_state.consent:
    tab1, tab2, tab3, tab4 = st.tabs([_("Report Issue"), _("View Reports"), _("Dashboard"), _("Feedback")])

    with tab1:
        st.header(_("Report Infrastructure Issue"))
        get_location()
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input(_("Latitude"), value=0.0)
            lon = st.number_input(_("Longitude"), value=0.0)
        issue_type = st.selectbox(_("Issue Type"), [_("Pothole"), _("Water Leak"), _("Power Outage"), _("Garbage"), _("Other")])
        description = st.text_area(_("Description"))
        photo = st.file_uploader(_("Upload Photo"), type=['jpg', 'png'])
        department = st.selectbox(_("Assign to Department"), departments)
        if st.button(_("Submit Report")):
            submit_report(issue_type, description, lat, lon, photo, department)
            st.success(_("Report Submitted!"))
            st.balloons()  # Added back

    with tab2:
        st.header(_("View My Reports"))
        all_reports = get_reports()
        df = all_reports[all_reports['user_id'] == st.session_state.user]  # Fixed: no .query()
        display_map(df)
        st.dataframe(df[['issue_type', 'description', 'timestamp', 'status']])
        for idx, row in df.iterrows():
            if row['photo']:
                img = Image.open(io.BytesIO(row['photo']))
                st.image(img, caption=row['id'])

    with tab3:
        st.header(_("Department Dashboard"))
        dept = st.selectbox(_("Select Department"), departments)
        df = get_reports(dept)
        display_map(df)
        st.dataframe(df[['id', 'user_id', 'issue_type', 'description', 'latitude', 'longitude', 'timestamp', 'department', 'status']])
        report_id = st.selectbox(_("Select Report to Update"), df['id'].tolist(), key="update_report_select")
        status = st.selectbox(_("Update Status"), ['Pending', 'In Progress', 'Resolved'], key="update_status_select")
        if st.button(_("Update"), key="update_button"):
            if update_status(report_id, status):
                st.success(_("Updated!"))
                st.rerun()
            else:
                st.error("Failed to update status. Please try again.")

        format = st.selectbox(_("Export Format (for Power BI)"), ['csv', 'excel', 'parquet'], key="export_format_select")
        data = export_data(df, format)
        st.download_button(_("Download Data"), data, file_name=f"reports.{format}", mime=f"application/{format}", key="download_button")

    with tab4:
        st.header(_("Provide Feedback"))
        all_reports = get_reports()
        my_reports = all_reports[all_reports['user_id'] == st.session_state.user]  # Fixed: no .query()
        report_id = st.selectbox(_("Select Report"), my_reports['id'].tolist(), key="feedback_report_select")
        feedback = st.text_area(_("Feedback"), key="feedback_text")
        if st.button(_("Submit Feedback"), key="submit_feedback_button"):
            submit_feedback(report_id, feedback)
            st.success(_("Feedback Submitted!"))

# High contrast & footer
if st.sidebar.checkbox(_("High Contrast Mode")):
    st.markdown("""<style> body { background-color: black; color: white; } </style>""", unsafe_allow_html=True)

st.sidebar.markdown(_("Partners: State Gov, Tech Co"))