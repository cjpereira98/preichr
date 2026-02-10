import time
import os
import sys
import win32com.client as win32

# Add the directory three levels up to the system path to allow importing FirefoxIntegration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from config.config import TEST_MODE, TEST_EMAIL

class OutlookIntegration:
    def __init__(self):
        self.outlook = win32.Dispatch('outlook.application')
        self.namespace = self.outlook.GetNamespace('MAPI')

    def create_email(self, to_addresses, subject, body, cc_addresses=None, bcc_addresses=None, attachments=None, send_immediately=False):
        mail = self.outlook.CreateItem(0)  # 0: olMailItem
        
        mail.Subject = subject
        mail.Body = body + "\n\nCreated and sent by MICHAEL"
        if TEST_MODE:
            mail.To = TEST_EMAIL
            mail.CC = ''
            mail.BCC = ''
            send_immediately = False
        else:
            mail.To = ';'.join(to_addresses)
            if cc_addresses:
                mail.CC = ';'.join(cc_addresses)
            if bcc_addresses:
                mail.BCC = ';'.join(bcc_addresses)
        if attachments:
            for attachment in attachments:
                print(f"Attaching {attachment}")
                mail.Attachments.Add(attachment)

        if send_immediately:
            mail.Send()
        else:
            mail.Save()

    def create_html_email(self, to_addresses, subject, html_body, cc_addresses=None, bcc_addresses=None, attachments=None, send_immediately=False):
        mail = self.outlook.CreateItem(0)  # 0: olMailItem
        print(TEST_MODE)
        print(TEST_EMAIL)
        if TEST_MODE:
            mail.To = TEST_EMAIL
            mail.CC = ''
            mail.BCC = ''
            send_immediately = False
        else:
            mail.To = ';'.join(to_addresses)
            if cc_addresses:
                mail.CC = ';'.join(cc_addresses)
            if bcc_addresses:
                mail.BCC = ';'.join(bcc_addresses)
        mail.Subject = subject
        mail.HTMLBody = html_body + "<p><br><br>Created and sent by MICHAEL</p>"

        
        if attachments:
            for attachment in attachments:
                mail.Attachments.Add(attachment)

        if send_immediately:
            mail.Send()
        else:
            mail.Save()

# Example usage
if __name__ == "__main__":
    oi = OutlookIntegration()
    oi.create_email(
        to_addresses=['example@example.com'],
        subject='Test Email',
        body='This is a test email.',
        #cc_addresses=['cc@example.com'],
        #bcc_addresses=['bcc@example.com'],
        #attachments=['path/to/attachment.xlsx'],
        send_immediately=False
    )

    time.sleep(10000)
