#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
# from __future__ import unicode_literals

import os
import io
import sys
import cgi
import cgitb
import codecs
import time
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

############# Debugging + Setup #############

# cgitb.enable()

# Apply utf-8 codecs on stdout
# After this, print() should work just fine.
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

# Since this is CGI, we are going to need to print this anyway,
# so let's do it here and be done with it.
print("Content-type: text/html charset=UTF-8\n\n")

############ Paths ###############

# Make sure that these are correct!
TEMPLATE_PATH = "./cgi-bin/template.html"
EMAIL_PREFECTURE_CSV = "./cgi-bin/data.csv"

############# Main Script #############


TXT_REPORT = """
ΔΙΚΤΥΟ ΣΥΜΒΟΥΛΩΝ ΜΗΧΑΝΙΚΩΝ

ΑΠΟΤΕΛΕΣΜΑΤΑ ΥΠΟΛΟΓΙΣΜΩΝ ΕΠΙΔΟΤΗΣΗΣ ΠΡΟΓΡΑΜΜΑΤΟΣ ΕΞΟΙΚΟΝΟΜΩ ΚΑΤ ΟΙΚΩΝ 2018

Δηλώσατε {type_eisod} εισόδημα ύψους €{eisod:.2f} και επιφάνεια ακινήτου {emvado:.2f} m2.

Το ποσοστό επιδότησης λόγω εισοδήματος είναι {pososto_eisod:.2f}% και προσαυξάνεται κατά {pososto_paidia:.2f}% λόγω παιδιών.
Το τελικό ποσοστό που δικαιούστε είναι {pososto_tel:.2f}% και το μέγιστο ποσό επιδότησης ανέρχεται στα €{poso_epidot:.2f}.

Για οποιαδήποτε πληροφορία επικοινωνήστε μαζί μας στο τηλ. 211 215 20 20 ή στο info@neteng.gr.

Με εκτίμηση Δίκτυο Συμβούλων Μηχανικών
www.neteng.gr
""".strip().encode("utf-8")

HTML_REPORT = """
<p>ΔΙΚΤΥΟ ΣΥΜΒΟΥΛΩΝ ΜΗΧΑΝΙΚΩΝ</p>
<p>Αποτελέσματα Υπολογισμών Επιδότησης Προγράμματος Εξοικονομώ Κατ'Οίκων 2018</p>
<br>
<p>Δηλώσατε {type_eisod} εισόδημα ύψους €{eisod:.2f} και επιφάνεια ακινήτου {emvado:.2f} m2.</p>
<p>Το ποσοστό επιδότησης λόγω εισοδήματος είναι {pososto_eisod:.2f}% και προσαυξάνεται κατά {pososto_paidia:.2f}% λόγω παιδιών.
   Το τελικό ποσοστό που δικαιούστε είναι {pososto_tel:.2f}% και το μέγιστο ποσό επιδότησης ανέρχεται στα €{poso_epidot:.2f}.
<p>
<p>Για οποιαδήποτε πληροφορία επικοινωνήστε μαζί μας στο τηλ. 211 215 20 20 ή στο info@neteng.gr.</p>
<br>
<p>Με εκτίμηση Δίκτυο Συμβούλων Μηχανικών<p>
<p>www.neteng.gr<p>
""".strip().encode("utf-8")


CLIMATIC_ZONES = {
    'Ηράκλειο':'Ζώνη Α',
    'Χανιά':'Ζώνη Α',
    'Ρέθυμνο':'Ζώνη Α',
    'Λασίθι':'Ζώνη Α',
    'Κυκλάδες':'Ζώνη Α',
    'Δωδεκάνησα':'Ζώνη Α',
    'Σάμος':'Ζώνη Α',
    'Μεσσηνία':'Ζώνη Α',
    'Λακωνία':'Ζώνη Α',
    'Αργολίδα':'Ζώνη Α',
    'Ζάκυνθος':'Ζώνη Α',
    'Κεφαλονιά':'Ζώνη Α',
    'Ιθάκη':'Ζώνη Α',
    'Κορινθία':'Ζώνη Β',
    'Ηλεία':'Ζώνη Β',
    'Αχαΐα':'Ζώνη Β',
    'Αιτωλοακαρνανία':'Ζώνη Β',
    'Φθιώτιδα':'Ζώνη Β',
    'Φωκίδα':'Ζώνη Β',
    'Βοιωτία':'Ζώνη Β',
    'Αττική':'Ζώνη Β',
    'Εύβοια':'Ζώνη Β',
    'Μαγνησία':'Ζώνη Β',
    'Σποράδες':'Ζώνη Β',
    'Λέσβος':'Ζώνη Β',
    'Χίος':'Ζώνη Β',
    'Κέρκυρα':'Ζώνη Β',
    'Μαγνησία':'Ζώνη Β',
    'Σποράδες':'Ζώνη Β',
    'Λέσβος':'Ζώνη Β',
    'Χίος':'Ζώνη Β',
    'Κέρκυρα':'Ζώνη Β',
    'Λευκάδα':'Ζώνη Β',
    'Θεσπρωτία':'Ζώνη Β',
    'Πρέβεζα':'Ζώνη Β',
    'Αρτα':'Ζώνη Β',
    'Αρκαδία':'Ζώνη Γ',
    'Ευρυτανία':'Ζώνη Γ',
    'Ιωάννινα':'Ζώνη Γ',
    'Λάρισα':'Ζώνη Γ',
    'Καρδίτσα':'Ζώνη Γ',
    'Τρίκαλα':'Ζώνη Γ',
    'Πιερία':'Ζώνη Γ',
    'Ημαθία':'Ζώνη Γ',
    'Πέλλα':'Ζώνη Γ',
    'Θεσσαλονίκη':'Ζώνη Γ',
    'Κιλκίς':'Ζώνη Γ',
    'Χαλκιδική':'Ζώνη Γ',
    'Σέρρες':'Ζώνη Γ',
    'Καβάλα':'Ζώνη Γ',
    'Δράμα':'Ζώνη Γ',
    'Θάσος':'Ζώνη Γ',
    'Σαμοθράκη':'Ζώνη Γ',
    'Πιερία':'Ζώνη Γ',
    'Ξάνθη':'Ζώνη Γ',
    'Ροδόπη':'Ζώνη Γ',
    'Έβρος':'Ζώνη Γ',
    'Έβρος':'Ζώνη Γ',
    'Γρεβενά':'Ζώνη Δ',
    'Κοζάνη':'Ζώνη Δ',
    'Καστοριά':'Ζώνη Δ'
}


class Template(string.Template):
    delimiter = '%%'


def get_user_input():
    """ Return the input from the HTML form. """
    form = cgi.FieldStorage()
    type_eisod =  form.getvalue('typos_eisod').encode('utf-8')
    eisod = float(form.getvalue('eisod').encode('utf-8'))
    paidia = int(form.getvalue('paidia').encode('utf-8'))
    emvado = float(form.getvalue('emvado').encode('utf-8'))
    topo = form.getvalue('topo').encode('utf-8')
    email = form.getvalue('email').encode('utf-8')
    return (type_eisod, eisod, paidia, emvado, topo, email)


def calc_pososta(type_eisod, eisod, paidia):
    """ Calculates the percentages. """
    if type_eisod == "Ατομικό":
        if eisod <= 10000:
            pososto_eisod = 0.6
            max_pososto = 0.7
        elif 10000 < eisod <= 15000 :
            pososto_eisod = 0.5
            max_pososto = 0.7
        elif 15000 < eisod <= 20000 :
            pososto_eisod = 0.4
            max_pososto = 0.7
        elif 20000 < eisod <= 25000 :
            max_pososto = 0.7
            pososto_eisod = 0.35
        elif 25000 < eisod <= 30000 :
            pososto_eisod = 0.3
            max_pososto = 0.5
        elif 30000 < eisod <= 35000 :
            pososto_eisod = 0.25
            max_pososto = 0.5
        else:
            pososto_eisod = 0
            max_pososto = 0
    else:
        if type_eisod == "Οικογενειακό":
            if eisod <= 20000:
                pososto_eisod = 0.6
                max_pososto = 0.7
            elif 20000 < eisod <= 25000 :
                pososto_eisod = 0.5
                max_pososto = 0.7
            elif 25000 < eisod <= 30000 :
                pososto_eisod = 0.4
                max_pososto = 0.7
            elif 30000 < eisod <= 35000 :
                max_pososto = 0.7
                pososto_eisod = 0.35
            elif 35000 < eisod <= 40000 :
                pososto_eisod = 0.3
                max_pososto = 0.5
            elif 40000 < eisod <= 45000 :
                pososto_eisod = 0.25
                max_pososto = 0.5
            else:
                pososto_eisod = 0
                max_pososto = 0
    pososto_paidia = 0.05 * paidia
    pososto_tel = min(max_pososto, pososto_eisod + pososto_paidia)
    return (pososto_eisod, pososto_paidia, pososto_tel, max_pososto)


def calc_epidotisi(emvado, pososto_tel):
    max_epidothsh= min(25000, 250 * emvado)
    poso_epidot = max_epidothsh * pososto_tel
    daneio = max_epidothsh - poso_epidot
    return (max_epidothsh, poso_epidot, daneio)


def save_email_prefecture(email, prefecture):
    """ Creates a .csv file storing the email and the prefecture of the users """
    line = "%s, %s\n" % (email, prefecture)
    with codecs.open(EMAIL_PREFECTURE_CSV, "ab", "utf-8") as fd:
        fd.write(line.decode("utf-8"))


def create_html_output(eisod, pososto_eisod, pososto_paidia, pososto_tel, poso_epidot, atopo, daneio, max_epidothsh):
    with codecs.open(TEMPLATE_PATH,'r','utf-8') as fd:
        template = Template(fd.read())
    html = template.safe_substitute(
        eisod=eisod,
        pososto_eisod=pososto_eisod,
        pososto_paidia=pososto_paidia,
        pososto_tel=pososto_tel,
        poso_epidot=poso_epidot,
        atopo=atopo,
        daneio=daneio,
        max_epidothsh=max_epidothsh,
    )
    return html


def send_email(sender, recipient, subject, html, txt):
    # connect to the SMTP server
    try:
        server = smtplib.SMTP_SSL('mail.neteng.gr:465')
        # server.login(sender, 'wrong_password')
        server.login(sender, os.environ["EMAIL_PASSWORD"])
    except:
        print("<p>Couldn't connect to the SMTP server.</p>")
        return

    # create the email
    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(txt, "plain"))
    msg.attach(MIMEText(html, "html"))
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    # send the email
    try:
        server.sendmail(sender, recipient, msg.as_string())
    except:
        print("<p>Couldn't send the email.</p>")
    else:
        print("<p>Email sent succesfully.</p>")
    finally:
        server.quit()


def main():
    type_eisod, eisod, paidia, emvado, topo, email = get_user_input()

    # make calculations
    atopo = CLIMATIC_ZONES[topo]
    pososto_eisod, pososto_paidia, pososto_tel, max_pososto = calc_pososta(type_eisod, eisod, paidia)
    max_epidothsh, poso_epidot, daneio = calc_epidotisi(emvado, pososto_tel)

    # Save user's email
    save_email_prefecture(email, topo)

    # Show output
    results_html = create_html_output(eisod, pososto_eisod, pososto_paidia, pososto_tel, poso_epidot, atopo, daneio, max_epidothsh)
    print(results_html.encode("utf-8"))

    # Send email report
    txt_report = TXT_REPORT.format(**locals()).encode("utf-8")
    html_report = HTML_REPORT.format(**locals()).encode("utf-8")
    send_email("info@neteng.gr", email, "Αποτελέσματα Υπολογισμών Εξοικονομώ 2018", html_report, txt_report)


if __name__ == "__main__":
    main()
