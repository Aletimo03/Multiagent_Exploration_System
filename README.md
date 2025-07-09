# Multiagent UAV Exploration System

Bachelor degree project — UniFi 2024/25  
Progetto di tesi triennale UniFi 2024/25

This project develops an exploration algorithm for a multi-agent UAV network, tasked with searching for users who require signal coverage.  
The system also implements:
- simulation of user movement and behaviour (active/inactive);
- a channel model incorporating both Line-of-Sight (LoS) and Non-Line-of-Sight (NLoS) conditions.

---

## 📋 Prerequisites

- Python 3.8+
- Recommended: virtual environment (`venv`)

---

## 🚀 Installation

### 1️⃣ Clone the repository
```bash
git clone <https://github.com/Aletimo03/Multiagent_Exploration_System>
cd Multiagent_Exploration_System   
```

### 2️⃣ Create and activate a virtual environment

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:  
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 🧪 Running the project
Run the main script:

```bash
python main.py
```

Or specify any other entry point as needed.

### 📝 Notes
To deactivate the virtual environment:
```bash
deactivate
```

To update requirements.txt if dependencies change:
```bash
pip freeze > requirements.txt
```

### 🤝 Contributing

If you wish to contribute, feel free to fork the repo and open a pull request.


