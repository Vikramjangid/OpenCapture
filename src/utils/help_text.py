
APP_TITLE = "OpenCapture"
VERSION = "1.0.0"

FAQ_TEXT = """
<style>
    h2 { color: #f0f0f0; margin-bottom: 10px; }
    h3 { color: #5dade2; margin-top: 15px; margin-bottom: 5px; }
    p { font-size: 13px; line-height: 1.4; color: #cccccc; margin-bottom: 10px; }
    ul { margin-left: -15px; color: #cccccc; }
    li { margin-bottom: 5px; }
    b { color: #f0f0f0; }
    .shortcut-table { margin-top: 10px; width: 100%; border-collapse: collapse; }
    .shortcut-table td { padding: 4px; color: #cccccc; }
    .shortcut-table th { text-align: left; color: #5dade2; padding-bottom: 5px; }
</style>

<h2>Quick Start Guide</h2>

<h3>1. Capture</h3>
<ul>
    <li><b>Region Capture:</b> Select `Capture Region` to drag and select a precise area.</li>
    <li><b>Full Screen:</b> Use `Capture [Monitor]` buttons for instant desktop snapshots.</li>
</ul>

<h3>2. Edit & Annotate</h3>
<ul>
    <li><b>Tools:</b> Use Arrow, Rectangle, and Text tools to highlight key info.</li>
    <li><b>Blur:</b> Obscure sensitive data with the Blur tool.</li>
    <li><b>Crop/Resize:</b> Trim and adjust your image dimensions perfectly.</li>
</ul>

<h3>3. Share</h3>
<ul>
    <li><b>Copy (Ctrl+C):</b> Copy directly to clipboard for Slack, Teams, or Email.</li>
    <li><b>Save (Ctrl+S):</b> Save your capture as a file to your local drive.</li>
</ul>

<h3>4. Video Recording</h3>
<ul>
    <li><b>Record Screen:</b> Toggle between Screen/Region mode.</li>
    <li><b>Audio:</b> Records Microphone (default) and System Audio.</li>
    <li><b>Webcam:</b> Enable Picture-in-Picture webcam overlay.</li>
    <li><b>Editor:</b> Trim, Playback, and Export your video to MP4 or GIF.</li>
</ul>

<hr style="border: 1px solid #444; margin: 15px 0;">

<h3>Keyboard Shortcuts</h3>
<table class="shortcut-table">
    <tr><th>Action</th><th>Shortcut</th></tr>
    <tr><td>Save Image</td><td><b>Ctrl + S</b></td></tr>
    <tr><td>Copy to Clipboard</td><td><b>Ctrl + C</b></td></tr>
    <tr><td>Undo</td><td><b>Ctrl + Z</b></td></tr>
    <tr><td>Redo</td><td><b>Ctrl + Shift + Z</b></td></tr>
</table>

<hr style="border: 1px solid #444; margin: 15px 0;">

<h3>FAQ</h3>
<p><b>Q: Where are my captures saved?</b><br>
A: Captures are only saved to disk when you click "Save". If you use "Copy", they remain in the clipboard.</p>

<p><b>Q: How do I exit deeply?</b><br>
A: Right-click the System Tray icon (bottom right) and select <b>Quit</b>.</p>
"""

ABOUT_TEXT = f"""
<h2>{APP_TITLE}</h2>
<p style="font-size: 14px; color: #aaa;">Version {VERSION}</p>
<p>A professional, lightweight screen capture and annotation tool designed for efficiency.</p>
<br>
<p><b>Credits:</b></p>
<p>Developed by <b>Vikram Jangid</b> (vikramjangid11@gmail.com)</p>
<p><i>OpenCapture</i></p>
"""
