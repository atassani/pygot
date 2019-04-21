import smtplib, ssl
import socket
import datetime

def sendEmail(config, theTorrent):
    # Send email notification
    port = 587
    smtp_server = "smtp.gmail.com"
    message = """\
    Subject: Episode %s started


    The episode is available and has been sent to Transmission.
    Title = %s
    Seeds = %s
    Size  = %s
    Age   = %s
    File  = %s

    Sent from %s at %s
    """ % (config.episode, theTorrent.title, theTorrent.seeds, theTorrent.size, theTorrent.age, theTorrent.file,
            socket.gethostname(), datetime.datetime.now())

    context = ssl.create_default_context()
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo() # Can be omitted
        server.starttls() # Secure the connection
        server.ehlo() # Can be omitted
        server.login(config.sender_email, config.email_password)
        server.sendmail(config.sender_email, config.receiver_email, message)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()
