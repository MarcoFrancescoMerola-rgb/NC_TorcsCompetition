######################## IMPORT #########################
import smtplib

####################### FUNCTION ########################
def sendEmail():
    content = ("Addestramento terminato.\nControllare i parametri!\n")
    mail = smtplib.SMTP('smtp.gmail.com',587)
    mail.ehlo()
    mail.starttls()
    mail.login('natcompgruppo1@gmail.com','rTjPsZrL4gH3yUQ')
    mail.sendmail('natcompgruppo1@gmail.com','d.spigapiena@studenti.unisa.it',content) 
    mail.sendmail('natcompgruppo1@gmail.com','m.merola31@studenti.unisa.it',content) 
    mail.close()
    print("Email sent")