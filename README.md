<a id="readme-top"></a>
<!-- TABLE OF CONTENTS -->
## Table of Contents
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li><a href="#deployment">Deployment</a></li>
    <li><a href='#hosting-locally'>Hosting Locally</a></li>
  </ol>

<br/>
<br/>

## About The Project

<p>
Effortless gardening with a purpose—H2Grow is a Telegram bot designed to keep your community garden thriving. Stay on top of watering schedules with timely reminders, weather-based insights, and an organized roster. By optimizing water usage and reducing waste, H2Grow takes a small yet meaningful step toward a greener, more sustainable future.
</p>

<p>
Join us in cultivating a thriving, eco-conscious community!
</p>

<br/>
<br/>

## Deployment

- View the Telegram bot <a href="https://t.me/h2growbot">`here`</a>
- View the Telegram channel <a href="https://t.me/h2_grow">`here`</a>

<br/>
<br/>

## Hosting Locally

### 1. Git Clone Repository
```bash
git clone https://github.com/tan-sd/h2grow.git
```

### 2. Create and activate Virtual Environment (if necessary)
       # For windows
       python -m venv myenv
   
       # For macOS/Linux
       source myenv/bin/activate
   
       # Activate Virtual Environment
       myenv\Scripts\activate

### 3. Install Dependency
```
pip install -r requirements.txt
```

### 4. Replicate constants.py.example (omit .example) and fill in API keys
    Request API Keys from the following links:
    - Telegram Bot API -> https://t.me/botfather
    - Telegram Channel ID (The channel which you want the bot to send daily reminders to)
    - Firestore Realtime Database -> https://console.firebase.google.com/u/0/

### 5. Ensure Database Structure
```
├── reminder: string  # Time for watering reminder (e.g., "08:00")
│
├── roster (Object)  # Watering duty roster for each day
│   ├── monday: string  # e.g., "name1"
│   ├── tuesday: string  # e.g., "name2"
│   ├── wednesday: string  # e.g., "name3"
│   ├── thursday: string  # e.g., "name4"
│   ├── friday: string  # e.g., "name5"
│   ├── saturday: string  # e.g., "name6"
│   ├── sunday: string  # e.g., "name7"
```

### 6. Run the Telegram bot
```
python main.py
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>
