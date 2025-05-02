import time
import whatsapp  # Import your whatsapp.py module
# This assumes whatsapp.py successfully initializes the 'client' object
# and makes it available, potentially as whatsapp.client

# --- Configuration ---
# IMPORTANT: Ensure these match the numbers used in your whatsapp.py and your demo setup
MY_PERSONAL_WHATSAPP_NUMBER = 'whatsapp:+972547958073' # The number you will send messages FROM during the demo
TWILIO_WHATSAPP_NUMBER = 'whatsapp:+14155238886'      # Your Twilio WhatsApp number (receiving messages TO)

POLLING_INTERVAL_SECONDS = 10 # How often to check for new messages (adjust as needed)

# --- The Hardcoded AI Script ---
def get_ai_response(user_message):
    """
    Determines the AI's response based on the user's message.
    This is where the hardcoded script logic lives.
    """
    user_message_lower = user_message.lower().strip() # Make matching case-insensitive and remove whitespace

    print(f"   Processing received message: '{user_message_lower}'")

    if any()
    if "הי" in user_message_lower or "מה קורה" in user_message_lower:
        return "Hello! This is the live WhatsApp demo AI. How may I assist?"
    elif "how are you" in user_message_lower:
        return "Running smoothly on this polling script! Ready for your next command."
    elif "help" in user_message_lower or "what can you do" in user_message_lower:
        return "I'm a demo script. I react to keywords like 'hello', 'how are you', 'project status', 'joke', or 'bye'."
    elif "project status" in user_message_lower:
        return "Demo Project Status: Active and responding via WhatsApp!"
    elif "joke" in user_message_lower:
        return "Why did the WhatsApp message blush? Because it saw the notification status change to 'read'! (Hardcoded humor!)"
    elif "thank you" in user_message_lower or "thanks" in user_message_lower:
        return "You're welcome! Happy to demonstrate."
    elif "bye" in user_message_lower or "exit" in user_message_lower or "quit" in user_message_lower:
        return "Acknowledged. Goodbye for now! (The script continues polling unless stopped manually)."
    else:
        # Default response if no keywords match
        return f"I received '{user_message}', but my script doesn't have a specific reply for that. Try asking for 'help'."

# --- Main Simulation Loop ---
def run_whatsapp_polling_demo():
    """Runs the main loop polling WhatsApp and responding."""
    print("--- Live WhatsApp Demo AI Simulation (Polling) ---")
    print(f"Watching for messages from: {MY_PERSONAL_WHATSAPP_NUMBER}")
    print(f"Sent to Twilio Number:     {TWILIO_WHATSAPP_NUMBER}")
    print(f"Using send_msg from:       whatsapp.py")
    print(f"Polling interval:          {POLLING_INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop the script.")

    last_processed_message_sid = None

    while True:
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{current_time}] Checking for new messages...")

            # Fetch the latest message *from* your personal number *to* the Twilio number
            # We access the 'client' instance initialized within the imported 'whatsapp' module
            messages = whatsapp.client.messages.list(
                from_=MY_PERSONAL_WHATSAPP_NUMBER,
                to=TWILIO_WHATSAPP_NUMBER,
                limit=1 # We only need the very latest one
            )

            if not messages:
                print("   No messages found from your number yet.")
                time.sleep(POLLING_INTERVAL_SECONDS)
                continue # Go to next loop iteration

            latest_message = messages[0]
            print(f"   Latest message SID: {latest_message.sid}, Status: {latest_message.status}, Direction: {latest_message.direction}")

            # Check if it's a new message we haven't processed and if it's actually incoming
            if latest_message.sid != last_processed_message_sid:
                print(f"   -> New message detected (SID: {latest_message.sid})")

                # Make sure it's an incoming message ('inbound') and not one we sent ('outbound-api', etc.)
                if latest_message.direction == 'inbound':
                    message_body = latest_message.body
                    print(f"   Received: '{message_body}'")

                    # Get the hardcoded response
                    response_text = get_ai_response(message_body)

                    # Send the response back using the function from whatsapp.py
                    print(f"   🤖 Sending reply: '{response_text}'")
                    try:
                        whatsapp.send_msg(response_text) # This uses your existing function
                        print(f"   Reply sent successfully via whatsapp.py")
                    except Exception as send_error:
                        print(f"!!! Error sending message via whatsapp.py: {send_error}")

                    # Update the SID of the last processed message *after attempting to process*
                    last_processed_message_sid = latest_message.sid

                else:
                    # It's a new SID, but not an inbound message (could be an outgoing one)
                    print(f"   Ignoring message (Direction: {latest_message.direction}).")
                    # Still update the last SID to prevent reprocessing if status changes later
                    last_processed_message_sid = latest_message.sid
            else:
                print("   No new messages since last check.")

            # Wait before polling again
            time.sleep(POLLING_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            print("\n--- Simulation stopped by user (Ctrl+C) ---")
            break
        except AttributeError:
             print("\n!!! Error: Could not access 'client' attribute in the imported 'whatsapp' module.")
             print("    Please ensure 'whatsapp.py' initializes 'client = Client(...)' at the module level.")
             break
        except Exception as e:
            print(f"\n!!! An unexpected error occurred: {e}")
            print(f"    Will retry after {POLLING_INTERVAL_SECONDS * 2} seconds...")
            time.sleep(POLLING_INTERVAL_SECONDS * 2) # Wait a bit longer after an error

# --- Start the script ---
if __name__ == "__main__":
    print("Verifying whatsapp module and client...")
    try:
        # Attempt to access the client to ensure it's loaded.
        # Fetching messages requires the client.
        if hasattr(whatsapp, 'client') and whatsapp.client:
             print("   Twilio client found in whatsapp module.")
             run_whatsapp_polling_demo()
        else:
             print("!!! Error: Could not find initialized 'client' in whatsapp.py.")
             print("    Make sure 'client = Client(account_sid, auth_token)' is run when whatsapp.py is imported.")
    except ImportError:
         print("!!! Error: Could not import 'whatsapp.py'. Make sure it's in the same directory.")
    except Exception as setup_error:
        print(f"!!! An error occurred during setup: {setup_error}")