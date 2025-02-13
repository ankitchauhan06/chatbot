from flask import Flask, request, jsonify, send_from_directory
import time
from difflib import get_close_matches  # To handle typo correction
import smtplib  # To send an email notification for agent requests
from email.mime.text import MIMEText

# Initialize Flask app
app = Flask(__name__)

# Company Contact Details
company_contact = {
    "email": "ycusgroup@gmail.com",
    "phone": "+91-8828076093",
    "agent_response_time": "Our agents typically respond within 10 minutes during business hours."
}

# Sample responses
responses = {
    "greeting": "👋 Hello! How can I assist you with your accounting or financial services today?",
    "tax_info": "🧾 I can help you calculate your taxes. Please provide your income details and tax filing status.",
    "accounting_services": (
        "📊 We offer the following services:\n"
        "1️⃣. Direct Tax Filing\n"
        "2️⃣. Indirect Tax Filing\n"
        "3️⃣. Bookkeeping\n"
        "4️⃣. Financial Planning\n"
        "5️⃣. Consulting\n"
        "6️⃣. Financial Services\n"
        "Please type the number of the service you'd like to know more about, or type 'exit' to leave this menu."
    ),
    "financial_services": (
        "💼 Here are the Financial Services we offer:\n"
        "1️⃣. Investment Planning\n"
        "2️⃣. Retirement Planning\n"
        "3️⃣. Risk Management\n"
        "4️⃣. Debt Management\n"
        "Please type the number of the Financial Service you'd like to know more about, or type 'exit' to leave this menu."
    ),
    "support_hours": "⏰ Our support is available from 9 AM to 6 PM, Monday to Friday.",
    "how_are_you": "😊 I'm doing great, thank you for asking! How can I assist you today?",
    "bot_name": "🤖 I'm your Financial Assistant Bot, here to help with your accounting and financial inquiries.",
    "fallback": (
        "❓ I'm sorry, I didn't understand that. Would you like to connect with a human agent?\n"
        "1️⃣. Chat with an Agent 💬\n"
        "2️⃣. Call us at 📞 {phone}\n"
        "3️⃣. Email us at ✉️ {email}\n"
        "Please type the number of your choice. Please type the number of the service you'd like to know more about, or type 'exit' to leave this menu."
    ).format(phone=company_contact["phone"], email=company_contact["email"]),
    "farewell": "👋 Goodbye! It was a pleasure assisting you. Have a great day! 🌟"
}

# Keywords mapping for typo correction
keywords = {
    "hello": ["helo", "hallo", "hey"],
    "hi": ["hii", "hay"],
    "how are you": ["how r u", "hw are u", "how r u?"],
    "name": ["what is your name", "who are you", "ur name"],
    "tax": ["taks", "tex", "income tax"],
    "services": ["servic", "serves", "serveces"],
    "support": ["suport", "suppot", "suprt"],
    "hours": ["hrs", "hourse", "hour"],
    "bye": ["bye", "by", "goodbye", "see you", "later"]
}

# Stateful interaction tracking
current_state = None

# Function to correct typos in user query
def correct_typos(user_query):
    for word, typo_list in keywords.items():
        for typo in typo_list:
            if typo in user_query:
                user_query = user_query.replace(typo, word)
    return user_query

# Function to notify agent via email
def notify_agent(user_message):
    try:
        sender_email = "ycusgroup@gmail.com"  # Replace with bot's email
        recipient_email = company_contact["email"]
        subject = "User Request to Connect with an Agent"
        body = f"A user requested to connect with an agent.🛎️\n\nUser Message:\n{user_message}"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = recipient_email

        # SMTP setup (configure with your email provider)
        smtp_server = "smtp.yourprovider.com"  # Replace with your SMTP server
        smtp_port = 587  # Replace with your SMTP server port
        smtp_password = "your-email-password"  # Replace with your email password

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, smtp_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Agent notified successfully. ✅")
    except Exception as e:
        print(f"Failed to notify agent: {e}")

# Function to simulate typing and get response
def get_response(user_query):
    global current_state

    # Simulate typing
    print("Bot is typing...", end="\r")
    time.sleep(1)

    # Correct typos
    user_query = correct_typos(user_query.strip().lower())

    # Check for farewell (bye, goodbye, etc.)
    if any(farewell in user_query for farewell in keywords["bye"]):
        return responses["farewell"]

    # Handle agent request
    if current_state == "contact_agent":
        if user_query == "1":
            notify_agent(user_query)  # Notify agent via email
            return (
                "🔗 Connecting you to a live agent. Please hold on while we notify our team. "
                f"{company_contact['agent_response_time']}"
            )
        elif user_query == "2":
            return f"📞 You can call us at {company_contact['phone']} for immediate assistance."
        elif user_query == "3":
            return f"✉️ Please email us at {company_contact['email']} with your query."
        elif user_query == "exit":
            current_state = None
            return "🚪 Exiting contact options. How else can I help you?"
        else:
            return "❌ Invalid choice. Please select a valid option (1, 2, or 3)."

    # Handle user selection for financial services
    if current_state == "financial_services":
        if user_query == "1":
            return "📈 Investment Planning helps you grow your wealth through strategic investments."
        elif user_query == "2":
            return "🏖️ Retirement Planning helps you secure a financially stable retirement."
        elif user_query == "3":
            return "⚠️ Risk Management identifies and mitigates financial risks effectively."
        elif user_query == "4":
            return "💳 Debt Management helps you manage and reduce your debts systematically."
        elif user_query == "exit":
            current_state = None  # Exit the menu and return to main flow
            return "🚪 Exiting Financial Services. How else can I assist you?"
        else:
            return responses["financial_services"]  # Always return the Financial Services list if invalid input.

    # Handle user selection for accounting services
    if current_state == "accounting_services":
        if user_query == "1":
            return "🧾 Direct taxes are levied directly on an individual's or organization's income or wealth. Examples include Income Tax, Corporate Tax, and Wealth Tax. Filing direct taxes involves."
        elif user_query == "2":
            return "🧾 Indirect taxes are collected on goods and services and passed on to the government by intermediaries (e.g., retailers). Examples include GST (Goods and Services Tax), VAT (Value Added Tax), and Sales Tax. Filing indirect taxes involves."
        elif user_query == "3":
            return "📚 Bookkeeping involves maintaining accurate financial records for your business."
        elif user_query == "4":
            return "📋 Financial Planning assists you in creating a roadmap for your financial goals."
        elif user_query == "5":
            return "💡 Consulting provides expert advice to optimize your financial strategies."
        elif user_query == "6":
            current_state = "financial_services"  # Switch to financial services
            return responses["financial_services"]
        elif user_query == "exit":
            current_state = None  # Exit the menu and return to main flow
            return "🚪 Exiting Accounting Services. How else can I assist you?"
        else:
            return responses["accounting_services"]  # Always return the Accounting Services list if invalid input.

    # Main conversation flow
    if not user_query:
        return responses["fallback"]
    if "agent" in user_query or "talk to agent" in user_query:
        current_state = "contact_agent"
        return responses["fallback"]
    elif any(keyword in user_query for keyword in ['hello', 'hi', 'hey']):
        return responses["greeting"]
    elif any(keyword in user_query for keyword in ['how are you']):
        return responses["how_are_you"]
    elif any(keyword in user_query for keyword in ['name']):
        return responses["bot_name"]
    elif any(keyword in user_query for keyword in ['tax', 'income']):
        return responses["tax_info"]
    elif "financial services" in user_query:
        current_state = "financial_services"  # Set state to financial services
        return responses["financial_services"]
    elif "services" in user_query:
        current_state = "accounting_services"  # Set state to accounting services
        return responses["accounting_services"]
    elif any(keyword in user_query for keyword in ['support', 'hours']):
        return responses["support_hours"]
    else:
        current_state = "contact_agent"
        return responses["fallback"]

# API endpoint to handle chatbot interactions
@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.json.get("message")
        if user_input:
            response = get_response(user_input)
            return jsonify({"response": response})
        return jsonify({"response": "Please provide a valid message."})
    return jsonify({"response": "Please use POST method to interact with the chatbot."})

@app.route("/notify_agent", methods=["POST"])
def agent_contact():
    user_message = request.json.get("message")
    if user_message:
        notify_agent(user_message)
        return jsonify({"response": "Your request has been sent to our agent. We'll get back to you shortly."})
    return jsonify({"response": "Please provide a valid message to notify the agent."})
    
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/")
def home():
    return """
    <html>
        <head>
            <title>🤖 Financial and Accounting Services Chatbot</title>
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center; background-color: #f4f4f9; color: #333;">
            <h1>🤝 Welcome to the Financial and Accounting Services Chatbot! 💼</h1>
            <p>📩 Type a message to interact with the chatbot via the <strong>/chat</strong> endpoint.</p>
            <p>🔍 Need help? Just ask about our services! 🧾</p>
            <p>📞 Contact us: +91-8828076093 | 📧 ycusgroup@gmail.com</p>
            <p>👨‍💻 Powered by your friendly AI Assistant! 🎉</p>
        </body>
    </html>
    """
@app.route("/chat_ui")
def chat_ui():
    return """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Chatbot</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f4f4f9;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        #chat-container {
            width: 100%;
            max-width: 600px;
            background: #fff;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }

        #chatbox {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f9f9f9;
        }

        .message {
            margin: 10px 0;
            display: flex;
            align-items: center;
        }

        .message.bot {
            justify-content: flex-start;
        }

        .message.user {
            justify-content: flex-end;
        }

        .message-content {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 10px;
            font-size: 14px;
            line-height: 1.5;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .message.bot .message-content {
            background: #e0e0e0;
            color: #333;
            border-radius: 10px 10px 10px 0;
        }

        .message.user .message-content {
            background: #0078d7;
            color: #fff;
            border-radius: 10px 10px 0 10px;
        }

        #input-container {
            display: flex;
            padding: 10px;
            background: #fff;
            border-top: 1px solid #ddd;
        }

        #message {
            flex: 1;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
            outline: none;
        }

        #send {
            background: #0078d7;
            border: none;
            color: white;
            padding: 10px 15px;
            margin-left: 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: background-color 0.3s;
        }

        #send:hover {
            background: #005bb5;
        }

        #chatbox::-webkit-scrollbar {
            width: 8px;
        }

        #chatbox::-webkit-scrollbar-thumb {
            background: #cccccc;
            border-radius: 4px;
        }

        #chatbox::-webkit-scrollbar-thumb:hover {
            background: #999999;
        }
    </style>
    <script>
        async function sendMessage() {
            const messageInput = document.getElementById("message");
            const chatbox = document.getElementById("chatbox");
            const userMessage = messageInput.value.trim();

            if (!userMessage) return;

            appendMessage("user", userMessage);
            messageInput.value = "";

            appendMessage("bot", "Bot is typing...");
            const botTypingElement = chatbox.lastChild;

            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message: userMessage })
                });
                const data = await response.json();
                botTypingElement.remove();
                appendMessage("bot", data.response);
            } catch (error) {
                console.error("Error fetching bot response:", error);
                botTypingElement.remove();
                appendMessage("bot", "Sorry, something went wrong. Please try again later.");
            }
        }

        function appendMessage(sender, text) {
            const chatbox = document.getElementById("chatbox");
            const messageElement = document.createElement("div");
            messageElement.className = "message " + sender;  // Fixed class name assignment
            messageElement.innerHTML = '<div class="message-content">' + text + '</div>';
            chatbox.appendChild(messageElement);
            chatbox.scrollTop = chatbox.scrollHeight;
        }
        
</script>
</head>
<body>
    <div id="chat-container">
        <div id="chatbox"></div>
        <div id="input-container">
            <input type="text" id="message" placeholder="Type your message here..." onkeypress="if(event.key === 'Enter') sendMessage()" />
            <button id="send" onclick="sendMessage()">Send</button>
        </div>
    </div>
</body>
</html>
"""


if __name__ == '__main__':
    # This block should be indented properly
    app.run(debug=True)
