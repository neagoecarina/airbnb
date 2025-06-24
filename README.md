#  Airbnb Manager

**Airbnb Manager** este o aplicație web dedicată proprietarilor de locuințe închiriate prin Airbnb. Scopul aplicației este de a simplifica gestionarea rezervărilor, a veniturilor, cheltuielilor și a rapoartelor financiare lunare.

---

## Tehnologii folosite

- **Python 3.12**
- **Django 4.2**
- **HTML, CSS, JavaScript**
- **Chart.js** – grafice pentru analize financiare
- **WeasyPrint** – generare facturi PDF
- **OpenPyXL** – export Excel
- **Bootstrap 5** – stilizare interfață

---

##  Funcționalități principale

### Dashboard
- Rezumat venituri & profit lunar
- Rezervări viitoare
- Calendar cu rezervările pe proprietăți

### Gestiune Proprietăți
- Adăugare / Editare locuințe
- Vizualizare rezervări pe casă

### Analiză Financiară
- Grafic profit lunar
- Rapoarte per casă / per lună / an
- Export Excel

### Cheltuieli & Utilități
- Adăugare cheltuieli lunare (curățenie, electricitate, apă)
- Rapoarte și statistici de consum

### Facturi & Discounturi
- Generare factură PDF pentru rezervări
- Setare discounturi pe perioade și locuințe


##  Instalare locală

1. **Clonează repo-ul:**
```bash
git clone https://github.com/neagoecarina/airbnb.git
cd airbnb_manager
python -m venv venv
source venv/bin/activate     # Linux / Mac
venv\Scripts\activate.bat    # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
