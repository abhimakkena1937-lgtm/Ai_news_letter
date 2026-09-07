from email_sender import send_newsletter

html = """
<html>
<body>
    <h1>AI Daily Image Test</h1>

    <p>If you can see the image below, inline images are working.</p>

    <img
        src="https://www.python.org/static/community_logos/python-logo.png"
        width="300"
    >

</body>
</html>
"""

send_newsletter(
    to_email="abhimakkena1937@gmail.com",
    subject="AI Daily — Inline Image Test",
    html=html,
)

print("Test email sent")