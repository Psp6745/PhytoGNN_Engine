# routes/chatbot.py
from flask import Blueprint, request, jsonify, render_template, session, current_app
from services.chatbot_service import ChatbotService
import traceback
import sys
import os

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chatbot')
def show_chatbot():
    if 'session_id' not in session:
        import uuid
        session['session_id'] = str(uuid.uuid4())
    return render_template('chatbot.html')

@chatbot_bp.route('/chatbot/query', methods=['POST'])
def query():
    """
    NLP Query Controller with explicit traceback debugging enabled.
    Returns exact error data back to the browser interface.
    """
    user_query = ""
    try:
        data = request.get_json() or {}
        user_query = data.get('message', '').strip()
        
        if not user_query:
            return jsonify({"response": "🤖 **System Copilot:** Message input cannot be empty."})
            
        session_id = session.get('session_id', 'default_session')
        
        # Route query to NLP engine
        response_text = ChatbotService.query_bot(user_query, session_id)
        return jsonify({"response": response_text})
        
    except Exception as e:
        # 1. Capture the traceback stack
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_list = traceback.extract_tb(exc_traceback)
        
        # 2. Locate the causing function in the stack
        causing_function = "unknown"
        if tb_list:
            # The last frame in the traceback points to the exact function
            causing_function = tb_list[-1].name

        tb_string = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        # 3. Print the explicit Debug Card to the Flask Terminal
        print("\n" + "="*40)
        print("CHATBOT ERROR DETECTED")
        print(f"User Query:\n{user_query}\n")
        print(f"Function:\n{causing_function}()\n")
        print(f"Exception Type:\n{exc_type.__name__}\n")
        print(f"Message:\n{str(e)}\n")
        print(f"Full Traceback:\n{tb_string}")
        print("="*40 + "\n")

        # 4. Return the exact exception message to the browser temporarily
        debug_response = f"""
        ⚠️ **DEBUG MODE: EXCEPTION DETECTED**
        <div style="background-color: rgba(239, 68, 68, 0.1); border: 1px solid var(--accent-crimson); padding: 12px; border-radius: 8px; font-family: monospace; font-size: 0.85rem; line-height: 1.5; margin-top: 8px; color: var(--accent-crimson);">
            <strong>Exception:</strong> {exc_type.__name__}<br/>
            <strong>Message:</strong> {str(e)}<br/>
            <strong>Function:</strong> {causing_function}()<br/>
            <hr style="border:none; border-top:1px solid rgba(239, 68, 68, 0.2); margin: 8px 0;"/>
            <strong>Traceback:</strong><br/>
            <pre style="margin: 0; white-space: pre-wrap; font-size: 0.75rem;">{tb_string}</pre>
        </div>
        """
        return jsonify({"response": debug_response})