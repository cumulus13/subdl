import webview
import keyboard
import threading
import clipboard
import sys


# URL of the IMDb trailer

# JavaScript code to inject custom CSS
js_code = """
const style = document.createElement('style');
style.innerHTML = `
    :root {
        --ipt-font-family: Roboto,Helvetica,Arial,sans-serif;
        --ipt-font-root-size: 50%;
    }
`;
document.head.appendChild(style);
"""

def inject_js(window):
    window.evaluate_js(js_code)

def setup_keyboard_shortcuts(window):
    # Listen for 'q' and 'esc' keys to exit the application
    keyboard.add_hotkey('q', lambda: exit_app(window))
    keyboard.add_hotkey('esc', lambda: exit_app(window))
    
def is_html(content):
    """Check if the input is an HTML code."""
    return "<html" in content.lower() or "<!doctype html>" in content.lower()

def exit_app(window):
    print("Exiting application...")
    window.destroy()

def show(content): 
    # Create and configure the browser window
    #window = webview.create_window('IMDb Trailer Browser', url, width=720, height=480, resizable=False)
    # Create and configure the browser window
    if is_html(content):
        # If content is HTML, create a window with HTML code
        window = webview.create_window('Custom HTML Viewer', html=content, width=720, height=480, resizable=False)
    else:
        # If content is a URL, create a window with the URL
        window = webview.create_window('IMDb Trailer Browser', content, width=720, height=480, resizable=False)
    
    window.events.loaded += lambda: inject_js(window)  # Inject CSS when the page is loaded

    # Start keyboard shortcuts in a background thread
    keyboard_thread = threading.Thread(target=setup_keyboard_shortcuts, args=(window,))
    keyboard_thread.start()

    # Start the webview application in the main thread
    webview.start()

if __name__ == '__main__':
    url = sys.argv[1]
    if url == 'c':
        url = clipboard.paste()    
    show(url)