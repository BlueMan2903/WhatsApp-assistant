import time
import whatsapp  

# --- Configuration ---
     
POLLING_INTERVAL_SECONDS = 2 # How often to check for new messages

# --- The Hardcoded AI Script ---
def get_ai_response(user_message):
    food = ["פיצה", "שווארמה", "סושי"]
    greetings = ["הי", "מה קורה", "שלום"]
    order = ["להזמין", "הזמנה"]
    user_message_lower = user_message.lower().strip()

    print(f"   Processing received message: '{user_message_lower}'")

    if any(word in user_message_lower for word in greetings):
        return "היי נשמה, איך אפשר לעזור?"
    elif any(word in user_message_lower for word in order):
        return "אין בעיה. מה תרצה להזמין?"
    elif any(word in user_message_lower for word in food):
        return "סבבה. משלוח או בא לקחת?"
    elif "משלוח" in user_message_lower:
        return "אוקיי מה הכתובת?"
    elif "שבט זבולון" in user_message_lower:
        return "אצלך עד 45 דקות"
    elif "בא לקחת" in user_message_lower:
        return "תבוא עוד חצי שעה"
    else:
        # Default response if no keywords match
        return f"על מה אתה מדבר אחי"

# --- Main Simulation Loop ---
def run_whatsapp_polling_demo():
    """Runs the main loop polling WhatsApp and responding."""
    print("--- Live WhatsApp Demo AI Simulation (Polling) ---")
    print(f"Watching for messages from: {whatsapp.MY_PERSONAL_WHATSAPP_NUMBER}")
    print(f"Sent to Twilio Number:     {whatsapp.TWILIO_WHATSAPP_NUMBER}")
    print(f"Using send_msg from:       whatsapp.py")
    print(f"Polling interval:          {POLLING_INTERVAL_SECONDS} seconds")
    print("Press Ctrl+C to stop the script.")

    last_processed_message_sid = whatsapp.client.messages.list(
                                    from_=whatsapp.MY_PERSONAL_WHATSAPP_NUMBER,
                                    to=whatsapp.TWILIO_WHATSAPP_NUMBER,
                                    limit=1 # We only need the very latest one
                                )[0].sid
    
    messages_list = whatsapp.client.messages.list()

    while True:
        try:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{current_time}] Checking for new messages...")

            # Fetch the latest message *from* your personal number *to* the Twilio number
            # We access the 'client' instance initialized within the imported 'whatsapp' module
            messages = whatsapp.client.messages.list(
                from_=whatsapp.MY_PERSONAL_WHATSAPP_NUMBER,
                to=whatsapp.TWILIO_WHATSAPP_NUMBER,
                limit=1 # We only need the very latest one
            )

            print("last MESSAGE: ", messages[0].body)

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
    run_whatsapp_polling_demo()
