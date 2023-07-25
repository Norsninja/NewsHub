from ftplib import FTP

def upload_to_ftp(local_file_path, ftp_host, ftp_user, ftp_password, ftp_dir='', ftp_filename=''):
    print(f"Connecting to FTP server {ftp_host}...")
    ftp = FTP(ftp_host) 
    ftp.login(ftp_user, ftp_password)
    print(f"Connected to FTP server {ftp_host}.")

    if ftp_dir:
        print(f"Changing directory to {ftp_dir}...")
        ftp.cwd(ftp_dir)

    with open(local_file_path, 'rb') as file:
        print(f"Uploading file as {ftp_filename}...")
        ftp.storbinary(f'STOR {ftp_filename}', file)
        print(f"File uploaded as {ftp_filename}.")

    ftp.quit()
    print(f"Disconnected from FTP server {ftp_host}.")