This project is a command-line Python quiz app. The goal of this app is to quiz users on their Python knowledge. 

Features include: 
- Local login system that saves scores and learning objectives. Login system will be based on the username and password. 
- Will read questions from a JSON file. There will be three types of problems (multiple choice, true false, short answer)
- Will quiz users, tracks scores and performance statistics securely (in a non-human-readable format) 
- Allows users to provide feedback on questions to influence future quiz selections (This will be a beginning survey that asks about prior Python knowledge and what category they want to focus on). 
- Points system that rewards consecutive correct answers and penalizes wrong answers
- Saves results
- Use OpenAI 4.0 mini API from openrouterto provide an explanation on why the answer choice is correct and if the user chose the wrong answer it will explain why that answer it wrong

User workflow
1) The app runs
2) creates axolotle art in the console and brings up the title "Welcome to the Amazing Python Quiz"
3) Asks user to input their username and password (this will be saved and user can return to their progress)
4) There will be a short survey to get a guage of the user's Python experience and what they want to focus on with the quiz (This will only show up the first time the user logs in, then there will be a button in the main menu that allows the user to retake this survey if they want to focus on a different topic down the line)
5) The survey will include the questions: What category do you want to focus on, How many questions do you want to test, How confident do you feel about your current Python knowledge
5) Brings them to a menu screen that shows some options for them to click into (start quiz, performance statistics, retake survey, exit quiz, account (allows them to view username with hidden password and can also change login information))
6) When user enters start quiz it will take the number of questions the user inputted in the survey and take questions from the file questions.json from the category the user indicated
7) When the user answers the OpenAI 4.0 mini API from openrouter will provide feedback on their answer (if they clicked the correct one they will get a congratulatory message and a short description why they are correct. If they clicked the wrong one they will get a message about why their answer is wrong and what the correct option is and why)
8) When the user finishes with the quiz it displays the user's score. Then this will update the performance statistics page. This page will be lifetime performance statistics
9) When the user exits the quiz it will display a "Goodbye {username}" message and display art of axolotle saying goodbye

Notes:
- File structure: Account file (handles account logic and saving logic), Quix file (handles quiz, scoring, question parsing), Menu file (provides the menu options including performance statistics, survey, exit, start, account) Feedback file (handles API calls)
- Error handling: 
If the user does an invalid input --> warn them and redisply the question. Make sure not to crash
If the user enters an incorrect password --> warn them and ask them to retry
If the user goes below zero score --> can't go below zero, minimum score should be zero
If user enters a large amount of question numbers that isn't supported --> give them the max questions and tell them that's the largest it can go up to
App should not crash at any errors should handle everything smoothly and warn the user

Other feature notes
- A local login system that prompts users for a username and password (or allows them to enter a new username and password). The passwords should not be easily discoverable.
- A score history file that tracks performance and other useful statistics over time for each user. This file should not be human-readable and should be relatively secure. (This means someone could look at the file and perhaps find out usernames but not passwords or scores.)
- Users should somehow be able to provide feedback on whether they like a question or not, and this should inform what questions they get next.
- The questions should exist in their own human-readable .json file so that they can be easily modified. (This lets you use the project for studying other subjects if you wish; all you have to do is generate the question bank.)

Acceptance criteria. The implementation is done if: 
- App runs smoothly without any errors
- All errors result in the user getting warned
- Has memory for username and password 
- Supports local login and logout
- API is connected and provides feedback