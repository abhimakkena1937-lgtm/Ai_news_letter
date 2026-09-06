from email_sender import send_newsletter


html = """
<h1>AI Daily</h1>

<p>This is a test email from your AI newsletter.</p>

<p>If you received this, email delivery is working.</p>
"""


response = send_newsletter(
    to_email="abhimakkena1937@gmail.com",
    subject="AI Daily — Test",
    html=html
)

print("Email sent!")
print(response)