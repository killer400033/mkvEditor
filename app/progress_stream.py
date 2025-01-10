import threading

progress_listener = {"message": "", "error": ""}
listener_event = threading.Event()
message_timer = None
error_timer = None

def reset_message():
    global progress_listener
    progress_listener["message"] = ""
    listener_event.set()

def reset_error():
    global progress_listener
    progress_listener["error"] = ""
    listener_event.set()

def progress_message(message):
    global progress_listener, message_timer
    progress_listener["message"] = message
    listener_event.set()

    if message_timer:
        message_timer.cancel()

    message_timer = threading.Timer(10.0, reset_message)
    message_timer.start()

def progress_error(error):
    global progress_listener, error_timer
    progress_listener["error"] = error
    listener_event.set()

    if error_timer:
        error_timer.cancel()

    error_timer = threading.Timer(5.0, reset_error)
    error_timer.start()
