import paramiko
import smtplib
import ssl
import datetime
from stat import S_ISDIR

from secrets import MAIL_SERVER, MAIL_SERVER_USER, MAIL_SERVER_PASSWORD
from secrets import MAIL_SENDER_EMAIL, MAIL_RECEIVER_EMAIL
from secrets import NAS_SERVER, NAS_USER, NAS_PASSWORD


paramiko.util.log_to_file("paramiko.log")
THRESHOLD = 6  # days
DIRS_TO_CHECK = ['NAS/Backup/rpi3-influxdb',
                 'NAS/Backup/grafana',
                 'NAS/Backup/rpi3-unifi']


def send_mail(message):
    print('Sending eMail')

    port = 465  # For SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(MAIL_SERVER, port, context=context) as server:
        server.login(MAIL_SERVER_USER, MAIL_SERVER_PASSWORD)
        server.sendmail(MAIL_SENDER_EMAIL, MAIL_RECEIVER_EMAIL, message)


def generate_message(files):
    print('Generating message')

    message = ''
    overall_result = 'OK'

    for f in files:
        file_result = 'OK'
        if f['age'] > THRESHOLD:
            file_result = 'WARNING'
            overall_result = 'WARNING'

        message += f"{f['dir']}: {file_result}\nOldest entry ({f['filename']}) is {f['age']} days old and {f['size']/1000} kb in size.\n\n"

    message = f"Subject: Backup Check {overall_result}\n\n{message}"

    return message


def get_newest_files(paths):
    print('Analyzing files')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(NAS_SERVER, 22, NAS_USER, NAS_PASSWORD)

    # Using the SSH client, create a SFTP client.
    sftp = ssh.open_sftp()
    # Keep a reference to the SSH client in the SFTP client as to prevent the former from
    # being garbage collected and the connection from being closed.
    sftp.sshclient = ssh

    result = []

    for path in paths:
        print('Processing ' + path)
        files = sftp.listdir_attr(path)

        if len(files) == 0:
            continue

        files.sort(key=lambda f: f.st_mtime, reverse=True)

        newest = files[0]
        # print(newest)

        size = 0
        if S_ISDIR(newest.st_mode):
            files = sftp.listdir_attr(path + '/' + newest.filename)
            for f in files:
                size += f.st_size
        else:
            size = newest.st_size
        #print("Size: " + str(size / 1000) + " kb")

        now = datetime.datetime.now()
        file_time = datetime.datetime.fromtimestamp(newest.st_mtime)
        elapsed = now - file_time
        #print("Days old: " + str(elapsed.days))

        entry = {
            "filename": newest.filename,
            "dir": path,
            "size": size,
            "age": elapsed.days
        }
        result.append(entry)

    # Close
    if sftp:
        sftp.close()
    if ssh:
        ssh.close()

    return result


def main():
    files = get_newest_files(DIRS_TO_CHECK)
    message = generate_message(files)
    send_mail(message)


if __name__ == "__main__":
    main()
