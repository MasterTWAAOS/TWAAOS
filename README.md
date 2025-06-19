# Sistem de Planificare Examene FIESC

[![Build Status](https://img.shields.io/github/actions/workflow/status/fiesc/exam-scheduling/ci.yml?branch=main)](https://github.com/fiesc/exam-scheduling/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Requirements](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

Aplicație web pentru planificarea examenelor și colocviilor în cadrul **Facultății de Inginerie Electrică și Știința Calculatoarelor** (USV).

## Descriere

Sistemul informatic pentru planificarea examenelor și colocviilor are ca scop automatizarea și optimizarea procesului de planificare a examenelor și colocviilor pentru toate programele de studii din cadrul facultății. Aplicația facilitează comunicarea între studenți (prin șefii de grupă), cadre didactice și secretariat pentru stabilirea datelor de examinare.

## Obiective

- Reducerea erorilor umane în planificare
- Asigurarea transparenței și accesului la informații pentru toți utilizatorii
- Îmbunătățirea comunicării și colaborării între studenți și profesori
- Automatizarea procesului de planificare conform regulamentelor USV

## Tehnologii
- **Backend**: Python 3 (Flask, FastAPI)
- **Frontend**: Vue.js
- **Baza de date**: PostgreSQL
- **Autentificare**: Google OAuth 2.0 ("Sign In With Google")
- **Deployment**: Docker

## Funcționalități cheie
✔ **Planificare colaborativă** a examenelor și colocviilor între șefii de grupă și cadrele didactice  
✔ **Notificări email** prin servicii externe (ex. SendGrid)  
✔ **Export PDF/Excel** pentru planificările de examene  
✔ **Interfețe adaptate pe roluri** (Secretariat, Șef Grupă, Cadru Didactic, Administrator)  
✔ **Integrare cu API-ul Orar USV** pentru preluarea datelor despre discipline, săli și cadre didactice  
✔ **Validare și aprobare** a datelor de examen propuse de șefii de grupă  
✔ **Documentație API interactivă** cu Swagger UI pentru testare manuală și debugging  

## Roluri utilizatori

### Secretariat (SEC)
- Încărcarea datelor despre discipline, cadre didactice și șefi de grupă
- Configurarea perioadelor pentru colocvii și examene
- Verificarea și modificarea planificărilor
- Exportul planificărilor în formate Excel și PDF

### Șef Grupă (SG)
- Propunerea datelor pentru examene și colocvii
- Vizualizarea statusului propunerilor (acceptate/respinse)
- Primirea notificărilor despre deciziile cadrelor didactice

### Cadru Didactic (CD)
- Validarea datelor propuse de șefii de grupă
- Stabilirea sălilor, asistenților și intervalelor orare pentru examene
- Vizualizarea planificării examenelor pentru disciplinele proprii

### Administrator (ADM)
- Gestionarea conturilor și a informațiilor despre facultăți
- Configurarea aplicației
- Actualizarea credențialelor de acces

## Instalare și Configurare

### Cerințe Preliminare
- Docker instalat pe mașină
- Acces la internet pentru descărcarea dependențelor

### Pași de Instalare

1. **Clonare Repository**

```bash
git clone https://github.com/MasterTWAAOS/TWAAOS.git
cd exam-scheduling
```

2. **Construirea și Pornirea Containerelor Docker**

```bash
docker-compose up --build
```

3. **Configurarea Bazei de Date**

```bash
docker-compose exec db psql -U postgres -c "DROP DATABASE twaaos WITH (FORCE);"
docker-compose exec db psql -U postgres -c "CREATE DATABASE twaaos;"
```

4. **Gestionarea Migrațiilor**

```bash
# Ștergeți toate migrațiile existente
docker-compose exec api rm -rf migrations/versions/*

# Generați o migrație nouă bazată pe modelele curente
docker-compose exec api alembic revision --autogenerate -m "Create complete database schema"

# Rulați migrația pentru a crea toate tabelele
docker-compose exec api alembic upgrade head
```

5. **Sincronizarea Datelor**
   - Accesați interfața Swagger a aplicației: http://localhost:8000/docs
   - Executați endpoint-ul `/sync/data` pentru a sincroniza datele necesare

După finalizarea acestor pași, aplicația ar trebui să fie complet funcțională și accesibilă în browser la adresa: http://localhost:8080