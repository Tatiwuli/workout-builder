## Table of Contents

1. [Project Overview](#project-overview)
   - [Purpose](#purpose)
2. [Pages](#pages)
   - [Home](#home)
   - [Questionnaire](#questionnaire)
   - [Workout Plan](#workout-plan)
3. [Tech Stack](#tech-stack)
   - [Backend](#backend)
   - [Frontend](#frontend)
   - [APIs](#apis)
4. [Next Steps](#next-steps)
   - Select All Option ✅
   - Add GIFs ✅
   - On-the-Spot Editing
5. [How to Run the Project](#how-to-run-the-project)
6. [Important Notes](#important-notes)

---

# Project Overview

#### Access the website through this link: https://workout-builder.streamlit.app/Home
This project generates a customized workout plan tailored to user needs and hypertrophy goals. It manages the entire workflow—from selecting exercises and designing workout volume to structuring easy-to-follow workout plans—through specialized agents.

### Purpose

I started my fitness journey five years ago, making a lot of mistakes, such as misunderstanding that weightlifting would make me bulkier, cardio would make me leaner, and spending time on trendy but ineffective exercises.

Things started to change when I discovered YouTubers like Jeff Nippard and Renaissance Periodization, where I learned how fat loss and muscle building actually work, and developed a healthier mindset toward weightlifting.

Today, fitness is a daily habit that fuels my energy and confidence. As a student, hiring a personal trainer isn’t affordable, so I learned how to create my own workout plans by watching these YouTube channels. Over time, I saw significant improvements in my strength and physique. However, the process wasn’t the most efficient—on average, I spent 1–2 hours each week watching videos, taking notes, and connecting insights to build my workout plans.

**To streamline this process, I decided to create a web app that references credible, science-based videos to build effective workout plans. This app learns about users’ needs and preferences to generate plans tailored to their goals, making the process of structuring a workout session less stressful and more efficient.**

---

## Pages

### Home
   Introduces the web app and prompts the user to provide their OpenAI API key for the agents.
   ![GIF demonstrating Home Page](https://github.com/Tatiwuli/workout-builder/blob/main/workoutBuilder_demo_home.gif)

### Questionnaire:
   Gathers information about the user’s workout preferences and needs. This data is passed to the agents to ensure they create an efficient workout plan tailored to the user’s goals.
  ![GIF demonstrating Questionnaire Page](https://github.com/Tatiwuli/workout-builder/blob/main/workoutBuilder_demo_questionnaire.mov)

### Workout Plan:
   Displays the final workout plan.
   The final plan includes:
      - Warm-up Section: Includes execution notes for movements, number of sets and reps, and duration.
      - Main Workout Section: Exercises are structured into sets. Based on the user's needs, the LLM may organize exercises into supersets or drop sets. Each exercise includes: Step-by-step execution instructions with a GIF; Guidelines for weights, sets, and reps; An alternative exercise for users without access to the required equipment, with its  execution instructions and GIF.
     ![GIF demonstrating the Workout Plan Page](workout-builder/workoutBuilder_demo_workoutPlan.gif)
     
*Check out the “Next Steps” section to learn about planned feature updates!*

---

## Tech Stack

### Backend
- Python

### Frontend
- Streamlit (with some HTML and CSS for styling)

Streamlit was chosen for its simplicity and ability to quickly build and iterate on a minimum viable product (MVP), while still providing a user-friendly UI.

### APIs
- **YouTube API:** Fetches videos from specific playlists.
- **OpenAI API:** Integrates the agents.

---

## Next Steps

- **Select All Option**  
  **Priority:** High  
  Add a “Select All” option in each muscle group section, allowing users to select all muscles at once.

- **On-the-Spot Editing**  
  **Priority:** Low  
  Currently, when users click “Edit” in the “Selected Muscles” section, the app resets all selected muscles. Instead, allow users to delete or add specific muscles without restarting the entire process.

- **Add Gifs**
  **Priority**: High
  Add gifs to demonstrate how to execute the movements. 
---

# How to Run the Project

1. **Clone the Repository**
   ```
   git clone <repository_url>
   ```
2. **Install Dependencies All dependencies are listed in requirements.txt. Use the following command to install them:**
```
pip install -r requirements.txt
```

3. **Run the App Navigate to the root directory and run the following commands:**
```
$env:PYTHONPATH = "."
streamlit run frontend/home.py
```
4. **Set API Key:**
On the Home page, enter your OpenAI API key and you’re good to go! :)

# Important Notes
- Disclaimer: These workout plans are not designed by a professional. Please review them carefully, and if you have any injuries, consult a professional before proceeding.
- Content Sources: The exercises and volume design principles are inspired by the following credible YouTube channels:
    - Renaissance Periodization
    - Jeff Nippard
