import yagmail

class Mail:
  @staticmethod
  def send(sender, receiver, subject, body):
    # sender = 'thegoodzone.help@gmail.com:the best school'
    # receiver = "mo.err17@gmail.com"

    # subject = "موضوع الايميل يلا"
    # body = "Hello there from Yagmail"

    email = {'to': receiver, 'subject': subject, 'contents': body}

    yag = yagmail.SMTP(*sender.split(':'))
    yag.send(**email)
