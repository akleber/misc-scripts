import paramiko
import smtplib
import ssl

from secrets import MAIL_SERVER, MAIL_SERVER_USER, MAIL_SERVER_PASSWORD
from secrets import MAIL_SENDER_EMAIL, MAIL_RECEIVER_EMAIL
from secrets import NAS_SERVER, NAS_USER, NAS_PASSWORD


paramiko.util.log_to_file("paramiko.log")

DIRS_TO_CHECK = ['/volume1/NAS/Backup/rpi3-influxdb',
                 '/volume1/NAS/Backup/rpi3-unifi']

THRESHOLD = 6  # days


EMAIL_TEMPLATE = '''
Backup Check {check_result}.
/directory/unifi OK! Oldest file is 6 days old and is 123b in size.
/directory/influxdv WARNING! Oldest file is 15 days old and is 0b in size.
'''


def send_mail(message):
    port = 465  # For SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(MAIL_SERVER, port, context=context) as server:
        server.login(MAIL_SERVER_USER, MAIL_SERVER_PASSWORD)
        server.sendmail(MAIL_SENDER_EMAIL, MAIL_RECEIVER_EMAIL, message)


def main():
    # Open a transport
    host, port = NAS_SERVER, 22
    transport = paramiko.Transport((host, port))

    # Auth
    username, password = NAS_USER, NAS_PASSWORD
    transport.connect(None, username, password)

    # Go!
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Download
    filepath = "/etc/passwd"
    localpath = "/home/remotepasswd"
    sftp.get(filepath, localpath)

    # Upload
    filepath = "/home/foo.jpg"
    localpath = "/home/pony.jpg"
    sftp.put(localpath, filepath)

    # Close
    if sftp:
        sftp.close()
    if transport:
        transport.close()


if __name__ == "__main__":
    main()
