import paramiko
import smtplib
import ssl
from stat import S_ISDIR, S_ISREG

from secrets import MAIL_SERVER, MAIL_SERVER_USER, MAIL_SERVER_PASSWORD
from secrets import MAIL_SENDER_EMAIL, MAIL_RECEIVER_EMAIL
from secrets import NAS_SERVER, NAS_USER, NAS_PASSWORD


paramiko.util.log_to_file("paramiko.log")

#DIRS_TO_CHECK = ['NAS/Backup/rpi3-influxdb',
#                 'NAS/Backup/rpi3-unifi']
DIRS_TO_CHECK = ['NAS/Backup/rpi3-influxdb/']

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


def generate_message(files):
    pass


def get_newest_files(paths):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAS_SERVER, 22, NAS_USER, NAS_PASSWORD)

    # Using the SSH client, create a SFTP client.
    sftp = ssh.open_sftp()
    # Keep a reference to the SSH client in the SFTP client as to prevent the former from
    # being garbage collected and the connection from being closed.
    sftp.sshclient = ssh

    for path in paths:
        print(path)
        files = sftp.listdir_attr(path)

        files.sort(key=lambda f: f.st_mtime, reverse=True)

        newest = files[0]
        print(newest)

        #for f in files:
        #    print(f.filename)

    # Close
    if sftp:
        sftp.close()
    if ssh:
        ssh.close()


def main():
    files = get_newest_files(DIRS_TO_CHECK)
    #message = generate_message(files)
    #send_mail(message)


if __name__ == "__main__":
    main()
