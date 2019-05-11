#
#    This file is part of Centralized.
#
#    Centralized is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Centralized is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Centralized.  If not, see <https://www.gnu.org/licenses/>.
#

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


def send_email(recipient_list, password):
    # Define to/from
    sender = os.environ['ORG_EMAIL']

    # Create message
    msg = MIMEMultipart('alternative')


    msg['Subject'] = "Centralized.pw administrator registration code."
    msg['From'] = sender
    msg['To'] = ", ".join(recipient_list)


    html = ("Hello!<br><br>"
               "You have been made administrator of your company's <a href='www.centralized.pw'>centralized</a> deployment.<br>"
                "Here's your password, please change it once you login: <b>{}</b><br><br>"
                "Best regards.<br>"
                "Centralized.pw team."
                "<img src='cid:image1'><br>centralized.pw"
            ).format(password)
    part1 = MIMEText("Message text", 'text')
    part2 = MIMEText(html, 'html')

    ImgFileName = "/opt/centralized/api/logo.gif"
    img_data = open(ImgFileName, 'rb').read()

    image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
    image.add_header('Content-ID', '<image1>')
    msg.attach(image)

    msg.attach(part1)
    msg.attach(part2)

    # Create server object with SSL option
    server = smtplib.SMTP_SSL(os.environ['SMTP_SERVER'], os.environ['SMTP_PORT'])

    # Perform operations via server
    server.login(sender, os.environ['SMTP_PASSWORD']) # Second part is SMTP password

    server.sendmail(sender, recipient_list, msg.as_string())
    server.quit()

