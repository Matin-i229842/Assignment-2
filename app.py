import streamlit as st
import requests
import random
import matplotlib.pyplot as plt

# Function to fetch quiz questions from the web
def fetch_questions():
    url = "https://opentdb.com/api.php?amount=5&category=17&type=multiple"  # Fetch 5 questions
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        questions = []
        for item in data["results"]:
            question = {
                "question": item["question"],
                "options": item["incorrect_answers"] + [item["correct_answer"]],
                "answer": item["correct_answer"]
            }
            random.shuffle(question["options"])  # Shuffle answer options
            questions.append(question)
        return questions
    else:
        st.error("⚠️ Failed to fetch questions from the web.")
        return []

# Quiz App Function
def quiz_app():
    st.title("🧠 Personal Finance Quiz")
    st.write("Test your financial literacy with this interactive quiz!")

    # Load questions dynamically
    if "questions" not in st.session_state:
        st.session_state.questions = fetch_questions()
        st.session_state.score = 0
        st.session_state.current_question = 0
        st.session_state.answers = []

    # Get current question
    if st.session_state.current_question < len(st.session_state.questions):
        q = st.session_state.questions[st.session_state.current_question]
        st.subheader(f"Q{st.session_state.current_question + 1}: {q['question']}")

        # Display options
        user_choice = st.radio("Select your answer:", q["options"])

        # Submit button
        if st.button("Submit Answer"):
            st.session_state.answers.append(user_choice)
            if user_choice == q["answer"]:
                st.session_state.score += 1
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect! The correct answer is: {q['answer']}")

            st.session_state.current_question += 1

    # Show final score
    else:
        st.subheader("Quiz Completed! 🎉")
        st.write(f"Your Final Score: **{st.session_state.score} / {len(st.session_state.questions)}**")
        st.pyplot(plot_score(st.session_state.score, len(st.session_state.questions)))

        # Reset Button
        if st.button("Restart Quiz"):
            st.session_state.questions = fetch_questions()
            st.session_state.score = 0
            st.session_state.current_question = 0
            st.session_state.answers = []

# Score Visualization
def plot_score(score, total):
    fig, ax = plt.subplots()
    ax.bar(["Correct", "Incorrect"], [score, total - score], color=["green", "red"])
    ax.set_ylabel("Number of Questions")
    ax.set_title("Quiz Performance")
    return fig

# Run App
if __name__ == "__main__":
    quiz_app()

